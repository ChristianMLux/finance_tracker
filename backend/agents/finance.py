from datetime import datetime
import json
import os
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from openai import AsyncOpenAI
from dotenv import load_dotenv

from .. import models, database
from .base import BaseAgent

logger = logging.getLogger(__name__)

load_dotenv()

client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

async def get_expenses_tool(db: AsyncSession, category: str = None, date: str = None, end_date: str = None):
    query = select(models.Expense)
    if category:
        query = query.filter(models.Expense.category.ilike(f"%{category}%"))
    
    if date:
        try:
            start_date_obj = datetime.strptime(date, "%Y-%m-%d")
            query = query.filter(models.Expense.date >= start_date_obj)
        except ValueError:
            logger.warning(f"Invalid start date format: {date}")
            
    if end_date:
        try:
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
            # Set to end of day for inclusive range
            end_date_obj = end_date_obj.replace(hour=23, minute=59, second=59)
            query = query.filter(models.Expense.date <= end_date_obj)
        except ValueError:
            logger.warning(f"Invalid end_date format: {end_date}")
            
    result = await db.execute(query)
    expenses = result.scalars().all()
    if not expenses:
        return "No expenses found matching criteria."
        
    return [f"{e.date.date()} - {e.description or 'Expense'} (${e.amount}) in {e.category}" for e in expenses]

async def add_expense_tool(db: AsyncSession, amount: float, category: str, description: str = None):
    expense = models.Expense(
        amount=amount,
        category=category,
        description=description,
        date=datetime.utcnow()
    )
    db.add(expense)
    await db.commit()
    return f"Added expense: ${amount} for {category}"

finance_tools = [
    {
        "type": "function",
        "function": {
            "name": "get_expenses",
            "description": "Get a list of expenses, optionally filtered by category or date.",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {"type": "string", "description": "Filter by category (e.g. food, transport)"},
                    "date": {"type": "string", "description": "Filter by start date (YYYY-MM-DD). If requesting 'last month', this is the 1st of last month."},
                    "end_date": {"type": "string", "description": "Filter by end date (YYYY-MM-DD). If requesting 'last month', this is the last day of last month."}
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
    }
]

class FinanceAgent(BaseAgent):
    async def process_message(self, message: str, context=None) -> str:
        async with database.AsyncSessionLocal() as db:
            try:
                system_prompt = f"""You are a friendly and insightful Financial Assistant aimed at helping users manage their money better.
Your goal is not just to report numbers, but to provide context and helpful feedback.
Today is {datetime.now().strftime("%Y-%m-%d")}.

GUIDELINES:
1.  **Be Conversational**: Use natural language. Instead of "Expenses: $50", say "You spent $50 on..."
2.  **Add Value**: If appropriate, comment on the spending (e.g., "That looks standard," or "This seems higher than usual").
3.  **Be Encouraging**: Financial tracking can be stressful. Maintain a supportive and positive tone.
4.  **Handling No Data**: If no expenses are found, be helpful. E.g., "I couldn't find any [category] expenses for that period. Would you like to check a different date range?"

IMPORTANT DATA RULES:
- When handling date queries like "last month", calculate the exact start (1st) and end (last day) of the previous month relative to today.
- ALWAYS use both 'date' (start) and 'end_date' when a specific time range is implied.
- References to 'this month' mean from the 1st of the current month until today.
"""
                msg_history = [{"role": "system", "content": system_prompt}]
                
                if context:
                    msg_history.append({"role": "system", "content": f"Context from previous agents: {json.dumps(context)}"})
                    
                msg_history.append({"role": "user", "content": message})
                
                response = await client.chat.completions.create(
                    model="google/gemini-3-flash-preview", 
                    messages=msg_history,
                    tools=finance_tools,
                    tool_choice="auto"
                )

                tool_calls = response.choices[0].message.tool_calls

                if tool_calls:
                    msg_history.append(response.choices[0].message)
                    
                    for tool_call in tool_calls:
                        function_name = tool_call.function.name
                        function_args = json.loads(tool_call.function.arguments)
                        
                        tool_result = ""
                        
                        if function_name == "get_expenses":
                            tool_result = str(await get_expenses_tool(db, **function_args))
                        elif function_name == "add_expense":
                            tool_result = await add_expense_tool(db, **function_args)
                        
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
                logger.error(f"Finance Agent Logic Error: {e}", exc_info=True)
                return "I apologize, but I encountered an error accessing your financial data."
