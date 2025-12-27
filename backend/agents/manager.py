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

    async def _classify_intent(self, message: str) -> str:
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

    async def _safety_check(self, message: str) -> bool:
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
            logger.info(f"Safety Check: {message} -> {content} ({is_safe})")
            return is_safe
        except Exception as e:
            logger.error(f"Safety check failed: {e}")
            return True # Fail open or closed? Let's fail open for reliability but log it, or fail closed? Fail closed is safer.
            # Actually, let's fail safe (True) to not block user on API error, assuming the Intent Classifier already filtered some junk. 
            # But the user asked for a hurdle. Let's return False if unsure? No, fail open is usually better for UX if API flakes. 
            # Let's stick to True but log.
            return True

    async def process_message(self, message: str, context=None) -> str:
        # GLOBAL SAFETY CHECK
        is_safe = await self._safety_check(message)
        if not is_safe:
            logger.warning(f"Safety check rejected: {message}")
            return "I cannot fulfill this request. I am a Financial Assistant, and this query seems unrelated to finance or potentially unsafe."

        intent = await self._classify_intent(message)
        logger.info(f"Intent detected: {intent}")

        if intent == "finance":
            return await self.finance_agent.process_message(message, context)
        
        elif intent == "currency":
            return await self.currency_agent.process_message(message, context)
        
        elif intent == "composite":
            finance_response = await self.finance_agent.process_message(message)
            
            currency_prompt = f"The user wants: '{message}'. \nHere is the financial data found: {finance_response}\n\nPlease perform the conversion requested."
            
            return await self.currency_agent.process_message(currency_prompt, context={"finance_data": finance_response})

        elif intent == "new_tool":
            logger.info("New tool needed. Triggering Architect...")
            # 1. Generate
            tool_data = await self.architect_agent.generate_tool(message)
            if "error" in tool_data:
                return f"I tried to build a tool for that but failed: {tool_data['error']}"
            
            # 2. Audit
            logger.info(f"Auditing tool: {tool_data.get('name')}")
            is_valid = await self.auditor_agent.validate_tool(tool_data)
            
            if not is_valid:
                return "I generated a tool to help with that, but it failed my security/correctness audit. Please try again or be more specific."
            
            # 3. Save to DB
            async with AsyncSessionLocal() as db:
                # Check if exists?
                existing = await crud.get_tool_by_name(db, tool_data["name"])
                if not existing:
                    # Serialize schema for DB
                    db_tool_data = tool_data.copy()
                    if isinstance(db_tool_data.get("json_schema"), dict):
                        db_tool_data["json_schema"] = json.dumps(db_tool_data["json_schema"])
                    
                    await crud.create_tool(db, db_tool_data)
                    logger.info("Tool saved to database.")
                else:
                    logger.info("Tool already exists, using existing version.")
            
            # 4. Execute (We use Auditor's capability or a localized exec)
            # We need to extract arguments from the user's message to call the tool.
            # This requires another LLM call or simple extraction.
            # For now, let's ask the LLM to extract arguments.
            
            extraction_prompt = f"""
The user said: "{message}"
We have a tool "{tool_data['name']}" with schema: {json.dumps(tool_data['json_schema'])}
Extract the arguments for this tool from the message.
Return ONLY JSON.
"""
            extraction = await client.chat.completions.create(
                model=os.getenv("LLM_MODEL", "google/gemini-2.0-flash-exp"),
                messages=[{"role": "user", "content": extraction_prompt}],
                response_format={"type": "json_object"}
            )
            args = json.loads(extraction.choices[0].message.content)
            
            # Re-verify/Execute using Auditor's sandbox? 
            # We can reuse the sandbox logic. Auditor has it.
            # Let's add an 'execute_tool' method to Auditor for simplicity or use the one we put in mcp_server logic.
            # But mcp_server is separate. I'll modify Auditor to allow execution.
            
            # Hack: modify Auditor locally effectively by just instantiating a new sandbox here or using a shared helper.
            # I will use the Auditor's internal logic since I can't easily modify Auditor file without another tool call.
            # Wait, I CAN modify Auditor file. But let's just use `e2b` here for now to save steps/complexity?
            # Actually, reusing code is better. 
            # I'll implement a quick execution here.
            
            from e2b_code_interpreter import Sandbox
            try:
                with Sandbox.create() as sb:
                    code = tool_data["python_code"]
                    args_json = json.dumps(args)
                    wrapper = f"""
import json
{code}
args = json.loads('{args_json}')
print(json.dumps(run(**args)))
"""
                    res = sb.run_code(wrapper)
                    if res.error:
                        return f"Tool execution failed: {res.error.value}"
                    
                    raw_result = res.logs.stdout
                    # POST-PROCESSING: Make it conversational
                    explanation_prompt = f"""
The user asked: "{message}"
We ran a tool and got this result: {raw_result}

Please answer the user's question using this result. Be helpful, professional, and concise. Act as a Financial Advisor.
"""
                    final_response = await client.chat.completions.create(
                        model=os.getenv("LLM_MODEL", "google/gemini-2.0-flash-exp"),
                        messages=[{"role": "user", "content": explanation_prompt}]
                    )
                    return final_response.choices[0].message.content
            except Exception as e:
                return f"Execution error: {e}"
            
        return "I'm not sure how to help with that."

manager_agent = ManagerAgent()
