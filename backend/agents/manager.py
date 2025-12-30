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
from .interpreter import InterpreterAgent
from backend import crud, models
from backend.database import AsyncSessionLocal
from backend.services.chat_service import chat_service

logger = logging.getLogger(__name__)

load_dotenv(".env.local")
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
        self.interpreter_agent = InterpreterAgent()

    async def _classify_intent(self, message: str, history: list = [], status_callback=None) -> str:
        system_prompt = """Classify the user's intent into one of the following categories:
- 'finance': Questions about expenses, adding expenses, or financial history (e.g., "How much did I spend?", "Add expense").
- 'currency': simple currency conversion questions with specific numeric amounts (e.g., "Convert 100 USD to EUR", "What is 50 GBP in Yen?").
- 'composite': Requests that involve personal financial data (spendings, costs, history) AND a conversion. This includes queries like "Convert my food costs to EUR", "Total spending on Coffee in RMB", or "How much is my rent in USD?".
- 'new_tool': Requests for calculations or forecasts that are NOT simple expense tracking or currency conversion. Examples: "Calculate mortgage", "Forecast savings", "Estimate tax", "Amortization schedule", "Compound interest".

CRITICAL: If the user refers to their own "spending", "total", "costs", "expenses", or "history" without providing a specific amount, it MUST be 'composite' or 'finance', NEVER 'currency'.
If the request requires a formula or mathematical model (like taxes, loans, interest) that is not simple + - * /, it is 'new_tool'.
Return ONLY the category name.
"""
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add history context to help with "that" references (e.g., "What is that in Euro?")
        for msg in history:
            # Skip system/tool messages if they exist in history (keep it simple for classifier)
            if msg.get("role") in ["user", "assistant"]:
                messages.append({"role": msg["role"], "content": msg["content"]})
        
        messages.append({"role": "user", "content": message})

        try:
            response = await client.chat.completions.create(
                model=os.getenv("LLM_MODEL", "google/gemini-3-flash-preview"),
                messages=messages
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
                model=os.getenv("LLM_MODEL", "google/gemini-3-flash-preview"),
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
            # Fail open to ensure user experience isn't blocked by transient API errors
            return True

    async def process_message(self, message: str, user_id: str = None, chat_id: str = "default", context=None, status_callback=None) -> str:
        if status_callback:
            await status_callback("log", "Starting Manager Agent processing...")

        # Persist User Message
        if user_id:
             await chat_service.add_message(user_id, chat_id, "user", message)

        # Retrieve Context from Firestore
        history = []
        if user_id:
            try:
                # Get last 10 messages for context
                full_history = await chat_service.get_recent_messages(user_id, chat_id, limit=10)
                
                # Exclude the current message if it was already saved to avoid duplication in context
                history = full_history[:-1] if full_history and full_history[-1]['content'] == message else full_history
            except Exception as e:
                logger.error(f"Failed to retrieve history: {e}")
        
        # GLOBAL SAFETY CHECK
        if status_callback:
            await status_callback("log", "Running Safety Check...")
        is_safe = await self._safety_check(message, status_callback)
        if not is_safe:
            logger.warning(f"Safety check rejected: {message}")
            return "I cannot fulfill this request. I am a Financial Assistant, and this query seems unrelated to finance or potentially unsafe."

        # SHORTCUT: Detection of Automated Analysis Requests
        # If the message starts with our known preamble, skip classification and go straight to analysis.
        if message.strip().startswith("Here is the financial data") or "Please analyze this data" in message:
             logger.info("Detected automated analysis request. Routing to Interpreter Agent.")
             if status_callback:
                 await status_callback("log", "Routing to Interpreter Agent...")
             
             response = await self.interpreter_agent.process_message(message, status_callback=status_callback)
             if user_id: await chat_service.add_message(user_id, chat_id, "assistant", response)
             return response

        if status_callback:
            await status_callback("log", "Classifying Intent...")
        
        intent = await self._classify_intent(message, history=history, status_callback=status_callback)
        logger.info(f"Intent detected: {intent}")

        if intent == "finance":
            if status_callback:
                await status_callback("log", "Routing to Finance Agent")
            # Pass history as context
            response = await self.finance_agent.process_message(message, user_id=user_id, context=history, status_callback=status_callback)
            if user_id: 
                logger.info(f"Saving Finance Agent response to history for user {user_id}, chat {chat_id}")
                await chat_service.add_message(user_id, chat_id, "assistant", response)
                logger.info("Response saved successfully.")
            return response
        
        elif intent == "currency":
            if status_callback:
                await status_callback("log", "Routing to Currency Agent")
            response = await self.currency_agent.process_message(message, context=history, status_callback=status_callback)
            if user_id: await chat_service.add_message(user_id, chat_id, "assistant", response)
            return response
        
        elif intent == "composite":
            if status_callback:
                await status_callback("log", "Processing Composite Request (Finance + Currency)")
            # Finance needs history too?
            finance_response = await self.finance_agent.process_message(message, user_id=user_id, context=history, status_callback=status_callback)
            
            currency_prompt = f"The user wants: '{message}'. \nHere is the financial data found: {finance_response}\n\nPlease perform the conversion requested."
            
            # Context for currency now includes finance data AND history
            combined_context = {"history": history, "finance_data": finance_response}
            response = await self.currency_agent.process_message(currency_prompt, context=combined_context, status_callback=status_callback)
            if user_id: await chat_service.add_message(user_id, chat_id, "assistant", response)
            return response

        elif intent == "new_tool":
            logger.info("New tool needed. Triggering Architect...")
            if status_callback:
                await status_callback("log", "Intent: New Tool Creation. Triggering Architect...")
            # 1. Generate
            # 1b. Generation Loop (Architect -> Auditor feedback)
            max_retries = 3
            attempt = 0
            feedback = ""
            is_valid = False
            critique_reason = ""
            
            while attempt <= max_retries:
                if feedback:
                    prompt_with_feedback = f"{message}\n\n<agent_critique>\n{feedback}\n</agent_critique>"
                    logger.info(f"Retrying Architect with feedback (Attempt {attempt})")
                    if status_callback:
                         await status_callback("log", f"Auditor rejected tool. Retrying Architect with feedback...")
                else:
                    prompt_with_feedback = message

                tool_data = await self.architect_agent.generate_tool(prompt_with_feedback)
                
                if "error" in tool_data:
                    logger.error(f"Architect error: {tool_data['error']}")
                    if attempt == max_retries:
                         response = f"I tried to build a tool for that but failed: {tool_data['error']}"
                         if user_id: await chat_service.add_message(user_id, chat_id, "assistant", response)
                         return response
                    attempt += 1
                    continue

                # 2. Audit
                logger.info(f"Auditing tool: {tool_data.get('name')}")
                if status_callback:
                    await status_callback("log", f"Auditing tool (Logic/Safety Check)...")
                
                is_valid, critique_reason = await self.auditor_agent.validate_tool(tool_data)
                
                if is_valid:
                    break # Success!
                
                # Failed - Construct feedback
                feedback = f"Your previous tool code was rejected by the Auditor.\nCritique: {critique_reason}\nFix: Address the critique and ensure mathematical correctness."
                attempt += 1
            
            if not is_valid:
                 response = f"I generated a tool to help with that, but it repeatedly failed my quality assurance audit.\n\nReason: {critique_reason}\n\nPlease try a slightly different request."
                 if user_id: await chat_service.add_message(user_id, chat_id, "assistant", response)
                 return response
            
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
                    
                    if user_id:
                        db_tool_data["creator_id"] = user_id
                    db_tool_data["status"] = "temporary"

                    
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
                model=os.getenv("LLM_MODEL", "google/gemini-3-flash-preview"),
                messages=[{"role": "user", "content": extraction_prompt}],
                response_format={"type": "json_object"}
            )
            args = json.loads(extraction.choices[0].message.content)
            
            # --- ARGUMENT VALIDATION ---
            required_fields = tool_data.get("json_schema", {}).get("required", [])
            # Check for missing keys OR null values
            missing_fields = [f for f in required_fields if f not in args or args[f] is None]
            
            if missing_fields:
                logger.warning(f"Tool execution blocked. Missing args: {missing_fields}")
                # Fallback response
                readable_missing = ", ".join(missing_fields)
                response = f"I have built the tool **{tool_data.get('title', tool_data['name'])}**, but I need more information to run it.\n\nPlease provide: **{readable_missing}**.\n\nAlternatively, you can input them manually below:"
                response += f"\n\n[Open Tool at /tools/{tool_data['name']}](/tools/{tool_data['name']})"
                
                if user_id:
                     await chat_service.add_message(user_id, chat_id, "assistant", response)
                return response
            # ---------------------------

            if status_callback:
                await status_callback("log", f"Executing tool {tool_data['name']} with args: {args}")
            
            # 4. Execute Service
            try:
                from backend.services.tool_execution import execute_tool_logic
                
                if status_callback:
                    await status_callback("log", f"Executing tool {tool_data['name']} with args: {args}")

                result = await execute_tool_logic(
                    code=tool_data["python_code"],
                    args=args,
                    dependencies=tool_data.get("dependencies", []),
                    status_callback=status_callback
                )
                
                if result.get("error"):
                    response_msg = f"Tool created, but execution failed: {result['error']}"
                    if user_id: await chat_service.add_message(user_id, chat_id, "assistant", response_msg)
                    return response_msg

                # Check for chart
                has_chart = result.get("visualization") is not None
                
                output_text = result.get("output", "")
                if output_text is None: output_text = "No output returned."

                # Use Interpreter Agent to format the result
                interpreter_ctx = f"Here is the financial data from the tool '{tool_data.get('title', tool_data['name'])}' calculation: \nInput: {json.dumps(args)}\nOutput: {output_text}\n"
                
                if has_chart:
                    interpreter_ctx += "\nA chart was also generated."

                formatted_analysis = await self.interpreter_agent.process_message(interpreter_ctx, status_callback=status_callback)

                # Construct Final Response
                response = formatted_analysis
                
                if has_chart:
                    response += "\n\n(A chart was generated. Click the tool link to view it interactively.)"

                # Standardize link format for frontend parsing
                response += f"\n\n[Open Tool at /tools/{tool_data['name']}](/tools/{tool_data['name']})"

                if user_id: 
                    # If we really want to support components, we need to update how add_message works or pass extra data.
                    # For now, let's just save the text.
                    await chat_service.add_message(user_id, chat_id, "assistant", response)
                
                return response

            except Exception as e:
                logger.error(f"Tool execution failed: {e}")
                err_msg = f"Tool created, but execution failed: {str(e)}"
                if user_id: await chat_service.add_message(user_id, chat_id, "assistant", err_msg)
                return err_msg

            
            # Fallback / General Chat / Analysis Request
            return await self._handle_analysis_request(message, user_id, chat_id, status_callback)


manager_agent = ManagerAgent()
