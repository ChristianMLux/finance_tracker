import json
import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

from .base import BaseAgent
import logging
from .finance import FinanceAgent
from .currency import CurrencyAgent

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

    async def _classify_intent(self, message: str) -> str:
        system_prompt = """Classify the user's intent into one of the following categories:
- 'finance': Questions about expenses, adding expenses, or financial history (e.g., "How much did I spend?", "Add expense").
- 'currency': simple currency conversion questions (e.g., "Convert 100 USD to EUR").
- 'composite': Requests that require getting financial data AND converting it (e.g., "Convert my food costs to EUR", "How much is my travel spending in GBP").

Return ONLY the category name.
"""
        try:
            response = await client.chat.completions.create(
                model="google/gemini-3-flash-preview",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ]
            )
            intent = response.choices[0].message.content.strip().lower()
            if "composite" in intent: return "composite"
            if "finance" in intent: return "finance"
            if "currency" in intent: return "currency"
            return "finance" 
        except:
            return "finance"

    async def process_message(self, message: str, context=None) -> str:
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
            
        return "I'm not sure how to help with that."

manager_agent = ManagerAgent()
