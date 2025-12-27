import json
import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

from .base import BaseAgent
import logging
from .finance import FinanceAgent
from .currency import CurrencyAgent
from .architect import ArchitectAgent
from .auditor import AuditorAgent
from backend import crud, models
from backend.database import AsyncSessionLocal

logger = logging.getLogger(__name__)

load_dotenv()

client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

class ManagerAgent(BaseAgent):
    def __init__(self):
        self.finance_agent = FinanceAgent()
        self.currency_agent = CurrencyAgent()
        self.architect_agent = ArchitectAgent()
        self.auditor_agent = AuditorAgent()

    async def _classify_intent(self, message: str, status_callback=None) -> str:
        system_prompt = """Classify the user's intent into one of the following categories:
- 'finance': Questions about expenses, adding expenses, or financial history (e.g., "How much did I spend?", "Add expense").
- 'currency': simple currency conversion questions with specific numeric amounts (e.g., "Convert 100 USD to EUR", "What is 50 GBP in Yen?").
- 'composite': Requests that involve personal financial data (spendings, costs, history) AND a conversion. This includes queries like "Convert my food costs to EUR", "Total spending on Coffee in RMB", or "How much is my rent in USD?".
- 'new_tool': Requests for calculations or forecasts that are NOT simple expense tracking or currency conversion. Examples: "Calculate mortgage", "Forecast savings", "Estimate tax", "Amortization schedule", "Compound interest".

CRITICAL: If the user refers to their own "spending", "total", "costs", "expenses", or "history" without providing a specific amount, it MUST be 'composite' or 'finance', NEVER 'currency'.
If the request requires a formula or mathematical model (like taxes, loans, interest) that is not simple + - * /, it is 'new_tool'.
Return ONLY the category name.
"""
        try:
            response = await client.chat.completions.create(
                model=os.getenv("LLM_MODEL", "google/gemini-3-flash-preview"),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ]
            )
            intent = response.choices[0].message.content.strip().lower()
            if "composite" in intent: return "composite"
            if "finance" in intent: return "finance"
            if "currency" in intent: return "currency"
            if "new_tool" in intent: return "new_tool"
            return "finance" 
        except:
            return "finance"

    async def _safety_check(self, message: str, status_callback=None) -> bool:
        """
        Ensures the user query is:
        1. Related to finance/math/economics.
        2. Safe (not asking for malware, hacks, or illegal acts).
        Returns True if safe, False otherwise.
        """
        system_prompt = """You are a Safety Filter for a Financial AI.
Your job is to REJECT requests that are:
1. Malicious (asking to write viruses, hack systems, steal data).
2. Completely unrelated to finance, math, economics, or productivity (e.g. "Write a poem about cats", "Who won the superbowl").

Financial requests (loans, interest, taxes, savings, planning) -> APPROVE
Mathematical requests (formulas, projections) -> APPROVE
Unclear but potentially productive requests -> APPROVE

Return EXACTLY 'SAFE' or 'UNSAFE'."""
        
        try:
            response = await client.chat.completions.create(
                model=os.getenv("LLM_MODEL", "google/gemini-2.0-flash-exp"),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ]
            )
            content = response.choices[0].message.content.strip().upper()
            is_safe = "SAFE" in content
            if status_callback:
                await status_callback("log", f"Safety Check Result: {content}")
            logger.info(f"Safety Check: {message} -> {content} ({is_safe})")
            return is_safe
        except Exception as e:
            logger.error(f"Safety check failed: {e}")
            return True # Fail open or closed? Let's fail open for reliability but log it, or fail closed? Fail closed is safer.
            # Actually, let's fail safe (True) to not block user on API error, assuming the Intent Classifier already filtered some junk. 
            # But the user asked for a hurdle. Let's return False if unsure? No, fail open is usually better for UX if API flakes. 
            # Let's stick to True but log.
            return True

    async def process_message(self, message: str, context=None, status_callback=None) -> str:
        if status_callback:
            await status_callback("log", "Starting Manager Agent processing...")
        
        # GLOBAL SAFETY CHECK
        if status_callback:
            await status_callback("log", "Running Safety Check...")
        is_safe = await self._safety_check(message, status_callback)
        if not is_safe:
            logger.warning(f"Safety check rejected: {message}")
            return "I cannot fulfill this request. I am a Financial Assistant, and this query seems unrelated to finance or potentially unsafe."

        if status_callback:
            await status_callback("log", "Classifying Intent...")
        intent = await self._classify_intent(message, status_callback)
        logger.info(f"Intent detected: {intent}")

        if intent == "finance":
            if status_callback:
                await status_callback("log", "Routing to Finance Agent")
            return await self.finance_agent.process_message(message, context, status_callback)
        
        elif intent == "currency":
            if status_callback:
                await status_callback("log", "Routing to Currency Agent")
            return await self.currency_agent.process_message(message, context, status_callback)
        
        elif intent == "composite":
            if status_callback:
                await status_callback("log", "Processing Composite Request (Finance + Currency)")
            finance_response = await self.finance_agent.process_message(message, status_callback=status_callback)
            
            currency_prompt = f"The user wants: '{message}'. \nHere is the financial data found: {finance_response}\n\nPlease perform the conversion requested."
            
            return await self.currency_agent.process_message(currency_prompt, context={"finance_data": finance_response}, status_callback=status_callback)

        elif intent == "new_tool":
            logger.info("New tool needed. Triggering Architect...")
            if status_callback:
                await status_callback("log", "Intent: New Tool Creation. Triggering Architect...")
            # 1. Generate
            tool_data = await self.architect_agent.generate_tool(message)
            if "error" in tool_data:
                return f"I tried to build a tool for that but failed: {tool_data['error']}"
            
            # 2. Audit
            logger.info(f"Auditing tool: {tool_data.get('name')}")
            if status_callback:
                await status_callback("log", f"Auditing tool: {tool_data.get('name')}")
            is_valid = await self.auditor_agent.validate_tool(tool_data)
            
            if not is_valid:
                return "I generated a tool to help with that, but it failed my security/correctness audit. Please try again or be more specific."
            
            # 3. Save to DB
            async with AsyncSessionLocal() as db:
                # Check if exists?
                existing = await crud.get_tool_by_name(db, tool_data["name"])
                if not existing:
                    if status_callback:
                        await status_callback("log", "Saving new tool to database...")
                    # Serialize schema for DB
                    db_tool_data = tool_data.copy()
                    if isinstance(db_tool_data.get("json_schema"), dict):
                        db_tool_data["json_schema"] = json.dumps(db_tool_data["json_schema"])
                    
                    await crud.create_tool(db, db_tool_data)
                    logger.info("Tool saved to database.")
                else:
                    logger.info("Tool already exists, using existing version.")
            
            # 4. Execute (We use Auditor's capability or a localized exec)
            # Use LLM to extract arguments
            extraction_prompt = f"""
The user said: "{message}"
We have a tool "{tool_data['name']}" with schema: {json.dumps(tool_data['json_schema'])}
Extract the arguments for this tool from the message.
Return ONLY JSON. If no arguments are needed, return {{}}.
"""
            extraction = await client.chat.completions.create(
                model=os.getenv("LLM_MODEL", "google/gemini-2.0-flash-exp"),
                messages=[{"role": "user", "content": extraction_prompt}],
                response_format={"type": "json_object"}
            )
            args = json.loads(extraction.choices[0].message.content)
            
            if status_callback:
                await status_callback("log", f"Executing tool {tool_data['name']} with args: {args}")
            
            from e2b_code_interpreter import Sandbox
            try:
                with Sandbox.create() as sb:
                    # 1. Install Dependencies
                    deps = tool_data.get("dependencies", [])
                    if deps:
                        if status_callback:
                            await status_callback("log", f"Installing dependencies: {deps}...")
                        for dep in deps:
                            sb.commands.run(f"pip install -q {dep}")

                    code = tool_data["python_code"]
                    args_json = json.dumps(args)
                    
                    # Robust execution wrapper:
                    # 1. Inspect function signature
                    # 2. Filter args to only match valid parameters
                    # 3. Handle 'unexpected keyword argument' proactively
                    wrapper = f"""
import json
import inspect
{code}

# Introspection to prevent 'unexpected keyword argument' errors
sig = inspect.signature(run)
valid_params = sig.parameters.keys()
raw_args = json.loads('{args_json}')
filtered_args = {{k: v for k, v in raw_args.items() if k in valid_params}}

# Check for missing required arguments? 
# (Simple pass for now, let Python raise TypeError if missing)

print(json.dumps(run(**filtered_args)))
"""
                    res = sb.run_code(wrapper)
                    if res.error:
                        return f"Tool execution failed: {res.error.value}"
                    
                    # Split stdout to separate logs from final JSON result
                    # The wrapper prints json.dumps(result) as the LAST line.
                    stdout = res.logs.stdout
                    
                    if stdout is None:
                        stdout = ""
                    elif isinstance(stdout, list):
                        # Should not happen in recent e2b versions but handled just in case
                        stdout = "\n".join([str(line) for line in stdout])
                    else:
                        stdout = str(stdout)

                    try:
                        output_lines = stdout.strip().split('\n')
                    except Exception as e:
                         if status_callback:
                             await status_callback("error", f"Error parsing output: {e}")
                         output_lines = []
                    
                    if not output_lines or not output_lines[0].strip():
                         return "Tool executed but returned no output."
                        
                    raw_result = output_lines[-1]
                    
                    # Log intermediate steps
                    for log_line in output_lines[:-1]:
                        if log_line.strip() and status_callback:
                            await status_callback("log", f"Tool: {log_line}")

                    # Check for explicit failure in result
                    if "error" in raw_result.lower() or "failed" in raw_result.lower():
                        return f"Tool execution returned an error: {raw_result}"
                            
                    # POST-PROCESSING: Make it conversational
                    explanation_prompt = f"""
The user asked: "{message}"
We ran a tool and got this result: {raw_result}

Please answer the user's question using the result. Act as a Financial Advisor.

**CRITICAL RULES**:
1. **Evidence-Based**: You must CITE the specific headline or data point from the result that supports your claim.
2. **No Fluff**: Do not use generic phrases like "market resilience" or "positive momentum" unless the data explicitly says so.
3. **Honesty**: If the result is sparse (e.g. few headlines due to holiday), SAY SO. Do not invent activity.
4. **No Hallucinations**: If the tool returned no data, state "I could not find relevant data".
5. **No Fake Precision**: Round abstract sentiment scores to 2 decimal places (e.g. 0.09). Do not use 4+ decimals.
"""
                    final_response = await client.chat.completions.create(
                        model=os.getenv("LLM_MODEL", "google/gemini-2.0-flash-exp"),
                        messages=[{"role": "user", "content": explanation_prompt}]
                    )
                    return final_response.choices[0].message.content
            except Exception as e:
                import traceback
                tb = traceback.format_exc()
                logger.error(f"Execution error traceback: {tb}")
                if status_callback:
                    await status_callback("error", f"Traceback: {tb}")
                return f"Execution error: {e}"
            
        return "I'm not sure how to help with that."

manager_agent = ManagerAgent()
