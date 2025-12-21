import requests
import os
import json
from openai import AsyncOpenAI
from dotenv import load_dotenv

from .base import BaseAgent

load_dotenv()

client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

def convert_currency_tool(amount: float, from_currency: str, to_currency: str):
    # Uses https://open.er-api.com/v6/latest/{from_currency}
    try:
        url = f"https://open.er-api.com/v6/latest/{from_currency.upper()}"
        resp = requests.get(url)
        data = resp.json()
        rate = data['rates'].get(to_currency.upper())
        if rate:
            converted = amount * rate
            return f"{amount} {from_currency.upper()} is {converted:.2f} {to_currency.upper()} (Rate: {rate})"
        else:
            return "Currency not found."
    except Exception as e:
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
    async def process_message(self, message: str, context=None) -> str:
        try:
            system_prompt = """You are a helpful currency conversion assistant. 
Use the available tools to convert currencies. 
"""
            msg_history = [{"role": "system", "content": system_prompt}]
            
            if context:
                msg_history.append({"role": "system", "content": f"Context to consider: {json.dumps(context)}"})
                
            msg_history.append({"role": "user", "content": message})
            
            response = await client.chat.completions.create(
                model="google/gemini-3-flash-preview", 
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
                        tool_result = convert_currency_tool(**function_args)
                    
                    msg_history.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": tool_result,
                    })
                
                # Get final response
                second_response = await client.chat.completions.create(
                    model="google/gemini-3-flash-preview",
                    messages=msg_history
                )
                return second_response.choices[0].message.content
            
            return response.choices[0].message.content

        except Exception as e:
            print(f"Currency Agent Logic Error: {e}")
            return "I apologize, but I encountered an error converting currency."
