from fastapi import HTTPException
import os
import json
import requests
from sqlalchemy.orm import Session
from datetime import datetime
from . import models, schemas, database
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

# --- Tools ---

def get_expenses_tool(db: Session, category: str = None, date: str = None):
    query = db.query(models.Expense)
    if category:
        query = query.filter(models.Expense.category.ilike(f"%{category}%"))
    # Date filtering is simplified for this demo
    if date:
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            query = query.filter(models.Expense.date >= date_obj)
        except:
            pass
            
    expenses = query.all()
    return [f"{e.date.date()} - {e.description or 'Expense'} (${e.amount}) in {e.category}" for e in expenses]

def add_expense_tool(db: Session, amount: float, category: str, description: str = None):
    expense = models.Expense(
        amount=amount,
        category=category,
        description=description,
        date=datetime.utcnow()
    )
    db.add(expense)
    db.commit()
    return f"Added expense: ${amount} for {category}"

def convert_currency_tool(amount: float, from_currency: str, to_currency: str):
    # Mocking external API for demo stability and speed, or use real one
    # Real implementation would use: https://open.er-api.com/v6/latest/{from_currency}
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

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_expenses",
            "description": "Get a list of expenses, optionally filtered by category or date.",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {"type": "string", "description": "Filter by category (e.g. food, transport)"},
                    "date": {"type": "string", "description": "Filter by start date (YYYY-MM-DD)"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_expense",
            "description": "Add a new expense entry.",
            "parameters": {
                "type": "object",
                "properties": {
                    "amount": {"type": "number", "description": "Amount of the expense"},
                    "category": {"type": "string", "description": "Category of the expense"},
                    "description": {"type": "string", "description": "Description of the expense"}
                },
                "required": ["amount", "category"]
            }
        }
    },
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

class FinanceAgent:
    async def process_message(self, message: str):
        # We need a db session here. For simplicity in this singleton, we open one per request context
        # In main.py we can pass it, but for now let's create a fresh one or manage it.
        # Ideally, process_message should accept `db: Session`.
        # I will update the class structure to rely on injection or local scope used properly.
        
        # Let's assume we pass DB session or handle it inside
        db = database.SessionLocal()
        
        try:
            messages = [{"role": "system", "content": "You are a helpful financial assistant capable of tracking expenses and converting currencies. Use the available tools to answer user requests. Today is " + datetime.now().strftime("%Y-%m-%d")},
                        {"role": "user", "content": message}]
            
            response = await client.chat.completions.create(
                model="google/gemini-3-flash-preview", 
                messages=messages,
                tools=tools,
                tool_choice="auto"
            )

            tool_calls = response.choices[0].message.tool_calls

            if tool_calls:
                messages.append(response.choices[0].message)
                
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    tool_result = ""
                    
                    if function_name == "get_expenses":
                        tool_result = str(get_expenses_tool(db, **function_args))
                    elif function_name == "add_expense":
                        tool_result = add_expense_tool(db, **function_args)
                    elif function_name == "convert_currency":
                        tool_result = convert_currency_tool(**function_args)
                    
                    messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": tool_result,
                    })
                
                # Get final response
                second_response = await client.chat.completions.create(
                    model="google/gemini-3-flash-preview",
                    messages=messages
                )
                return second_response.choices[0].message.content
            
            return response.choices[0].message.content

        except Exception as e:
            print(f"Agent Logic Error: {e}")
            return "I apologize, but I encountered an error processing your request."
        finally:
            db.close()

finance_agent = FinanceAgent()
