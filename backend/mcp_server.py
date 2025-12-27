import asyncio
import json
import logging
from contextlib import asynccontextmanager
from typing import Any

from mcp.server.fastmcp import FastMCP
from e2b_code_interpreter import Sandbox

from backend.database import get_db, AsyncSessionLocal
from backend import crud

# Config
SERVER_NAME = "FinanceFoundry"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP
mcp = FastMCP(SERVER_NAME)

async def execute_tool_in_sandbox(code: str, arguments: dict):
    logger.info("Executing tool in sandbox...")
    try:
        # We need to pass the arguments into the script.
        # The script is expected to have a 'run(**kwargs)' function.
        # We will create a wrapper.
        
        # Convert arguments to a string representation that Python can parse
        # Be careful with strings vs numbers. json.dumps is safest.
        args_json = json.dumps(arguments)
        
        wrapper_code = f"""
import json
{code}

args = json.loads('{args_json}')
result = run(**args)
print(json.dumps(result))
"""
        # Run in E2B
        with Sandbox() as sandbox:
            # Check for generic libraries if needed? For now assume standard env + basic libs.
            # If the tool needs 'numpy', we might need to install it.
            # For this MVP, we won't auto-install unless specified in tool metadata (which we haven't fully implemented).
            
            execution = sandbox.run_code(wrapper_code)
            
            if execution.error:
                raise Exception(f"Sandbox Error: {execution.error.name}: {execution.error.value}\n{execution.error.traceback}")
            
            # Parse output
            try:
                return json.loads(execution.logs.stdout)
            except:
                return execution.logs.stdout
                
    except Exception as e:
        logger.error(f"Execution failed: {e}")
        return str(e)

@mcp.tool()
async def dynamic_tool_handler(tool_name: str, arguments: dict) -> Any:
    """
    Universal handler for dynamic tools.
    In a real MCP implementation, we might register each tool separately,
    but for dynamic lists, a router or a refresh mechanism is needed.
    FastMCP allows adding tools dynamically or we can just have a 'run_dynamic_tool' meta-tool.
    
    HOWEVER, the Requirement says: "The Manager now sees `calculate_loan_amortization`".
    So we want to register them as distinct tools.
    """
    pass

# We need to register tools at startup.
# Note: In a long-running process, we might want a background task to refresh this list.

async def register_tools_from_db():
    async with AsyncSessionLocal() as db:
        tools = await crud.get_all_tools(db)
        for tool in tools:
            logger.info(f"Registering tool: {tool.name}")
            
            # We need to capture 'tool' in the closure
            # Python loop variable capture warning! Use default arg.
            
            async def handler(arguments: dict, _code=tool.python_code):
                return await execute_tool_in_sandbox(_code, arguments)
            
            # Register it
            # FastMCP.add_tool takes: name, description, fn, schema?
            # mcp.tool is a decorator. mcp.add_tool is the method.
            
            # construct schema? 
            # If tool.json_schema is a string, parse it.
            # The SDK might expect a Pydantic model or a dict.
            
            mcp.add_tool(
                name=tool.name,
                description=tool.description,
                fn=handler,
                # schema=... # FastMCP infers from type hints usually. 
                # If we want dynamic schema, we might need to use lower level SDK or 
                # check if FastMCP supports explicit schema override.
                # For now, let's skip schema enforcement at generic level and trust the Agent 
                # or pass 'arguments: dict' which implies proper usage.
            )

if __name__ == "__main__":
    # Initialize the database tools
    # We use a run_until_complete to ensure they are registered before the server starts receiving requests
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(register_tools_from_db())
    except Exception as e:
        logger.error(f"Failed to register tools on startup: {e}")

    # Standard execution (Stdio)
    # To run with SSE, you would typically use an ASGI wrapper or the 'mcp' CLI tools.
    # For example: uvicorn backend.mcp_server:mcp.asgi_app
    mcp.run()
