
import json
import logging
import traceback
from e2b_code_interpreter import Sandbox

logger = logging.getLogger(__name__)

async def execute_tool_logic(code: str, args: dict, dependencies: list = [], status_callback=None):
    """
    Executes a Python tool in an E2B sandbox.
    Returns a dict: { "output": str, "visualization": dict | None, "logs": list[str], "error": str | None }
    """
    logs = []

    try:
        if status_callback:
            await status_callback("log", f"Initializing sandbox for tool execution...")
        
        async def on_log(msg):
            logs.append(msg)
            if status_callback:
                await status_callback("log", msg)

        # We can't reuse sandbox across requests easily unless we manage a pool.
        # For now, create a new one per request (standard E2B pattern for isolation).
        # Note: Sandbox.create() is synchronous in the Python SDK (but wraps async calls?) 
        # Actually Sandbox.create() context manager.
        with Sandbox.create() as sb:
            # 1. Install Dependencies
            if dependencies:
                if status_callback:
                    await status_callback("log", f"Installing dependencies: {dependencies}...")
                for dep in dependencies:
                    sb.commands.run(f"pip install -q {dep}")

            # Base64 encode args to prevent string escaping issues in the wrapper
            import base64
            args_b64 = base64.b64encode(json.dumps(args).encode('utf-8')).decode('utf-8')
            
            # Robust execution wrapper
            wrapper = f"""
import json
import inspect
import sys
import base64

# Redirect stdout to capture prints
# (E2B captures it automatically, but we want to ensure we get the final return value clearly)

{code}

# Introspection to prevent 'unexpected keyword argument' errors
try:
    sig = inspect.signature(run)
    valid_params = sig.parameters.keys()
    
    # Safe decoding of args
    raw_args = json.loads(base64.b64decode('{args_b64}').decode('utf-8'))
    
    filtered_args = {{k: v for k, v in raw_args.items() if k in valid_params}}
    
    result = run(**filtered_args)
    
    # Print the result JSON-encoded as the LAST line
    print(json.dumps(result))
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"Error: {{e}}")
"""
            res = sb.run_code(wrapper)
            
            if res.error:
                return {"output": None, "visualization": None, "logs": logs, "error": res.error.value}
            
            # Process Output
            stdout = res.logs.stdout
            
            output_lines = []
            if stdout:
                 if isinstance(stdout, list):
                     output_lines = [str(line) for line in stdout]
                 else:
                     output_lines = str(stdout).strip().split('\n')
            
            # Filter logs
            final_result_str = None
            viz_payload = None
            
            if not output_lines or not output_lines[-1].strip():
                final_result_str = "Tool executed but returned no output."
            else:
                final_result_str = output_lines[-1]
                # Log intermediate steps
                for log_line in output_lines[:-1]:
                    if log_line.strip():
                        logs.append(log_line)
                        if status_callback:
                            await status_callback("log", f"Tool: {log_line}")

            # Check for explicitly printed error in stdout
            if "Error:" in final_result_str and "{" not in final_result_str:
                 return {"output": None, "visualization": None, "logs": logs, "error": final_result_str}

            # Try to parse as JSON to check for visualization
            try:
                result_json = json.loads(final_result_str)
                if isinstance(result_json, dict) and "_visualization" in result_json:
                    viz_data = result_json.pop("_visualization")
                    viz_payload = {"type": "chart", "data": viz_data}
                    final_result_str = json.dumps(result_json)
            except json.JSONDecodeError:
                pass 
            
            return {
                "output": final_result_str,
                "visualization": viz_payload,
                "logs": logs,
                "error": None
            }

    except Exception as e:
        tb = traceback.format_exc()
        logger.error(f"Tool execution error: {tb}")
        return {"output": None, "visualization": None, "logs": logs, "error": str(e)}
