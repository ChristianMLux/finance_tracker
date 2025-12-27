import httpx
import os
import json
from openai import AsyncOpenAI
from dotenv import load_dotenv

import logging
from .base import BaseAgent

logger = logging.getLogger(__name__)

load_dotenv()

client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

async def convert_currency_tool(amount: float, from_currency: str, to_currency: str):
    try:
        url = f"https://open.er-api.com/v6/latest/{from_currency.upper()}"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url)
        data = resp.json()
        rate = data['rates'].get(to_currency.upper())
        if rate:
            converted = amount * rate
            return f"{amount} {from_currency.upper()} is {converted:.2f} {to_currency.upper()} (Rate: {rate})"
        else:
            return "Currency not found."
    except Exception as e:
        logger.error(f"Error converting currency: {e}", exc_info=True)
        return f"Error converting currency: {str(e)}"

currency_tools = [
    {
        "type": "function",
        "function": {
            "name": "convert_currency",
            "description": "Convert an amount from one currency to another.",
            "parameters": {
                "type": "object",
                "properties": {
                    "amount": {"type": "number"},
                    "from_currency": {"type": "string", "description": "Source currency code (USD, EUR)"},
                    "to_currency": {"type": "string", "description": "Target currency code (USD, EUR)"}
                },
                "required": ["amount", "from_currency", "to_currency"]
            }
        }
    }
]

class CurrencyAgent(BaseAgent):
    async def process_message(self, message: str, context=None, status_callback=None) -> str:
        try:
            system_prompt = """You are a helpful and efficient currency conversion assistant.
Your goal is to provide quick, accurate conversions in a friendly tone.

GUIDELINES:
1.  **Format clearly**: "X USD is approximately Y EUR."
2.  **Include the Rate**: Always mention the exchange rate used (e.g., "Exchange Rate: 1.00 USD = 0.92 EUR").
3.  **Be Polite**: Use phrases like "Here is the conversion for you" or "At the current rate..."
4.  **Assumptions**: If no amount is specified, assume 1 unit.
"""
            msg_history = [{"role": "system", "content": system_prompt}]
            
            if context:
                msg_history.append({"role": "system", "content": f"Context to consider: {json.dumps(context)}"})
                
            msg_history.append({"role": "user", "content": message})
            
            response = await client.chat.completions.create(
                model=os.getenv("LLM_MODEL", "google/gemini-3-flash-preview"), 
                messages=msg_history,
                tools=currency_tools,
                tool_choice="auto"
            )

            tool_calls = response.choices[0].message.tool_calls

            if tool_calls:
                msg_history.append(response.choices[0].message)
                
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    tool_result = ""
                    
                    if function_name == "convert_currency":
                        tool_result = await convert_currency_tool(**function_args)
                    
                    msg_history.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": tool_result,
                    })
                
                # Get final response
                second_response = await client.chat.completions.create(
                    model=os.getenv("LLM_MODEL", "google/gemini-3-flash-preview"),
                    messages=msg_history
                )
                return second_response.choices[0].message.content
            
            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Currency Agent Logic Error: {e}", exc_info=True)
            return "I apologize, but I encountered an error converting currency."
