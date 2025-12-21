import asyncio
import os
import sys

# Add project root to path so we can import backend
# Assuming this script is in <root>/tests/
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, '..')
sys.path.append(project_root)

from backend.agents.manager import ManagerAgent
from backend.database import SessionLocal
from backend import models

async def main():
    print("Initializing ManagerAgent...")
    # Initialize the agent
    agent = ManagerAgent()
    
    print("\nXXX PRE-TEST CLEANUP XXX")
    # Optional: cleanup test data to make verification cleaner? 
    # For now, we will just add unique markers or just simply add.
    
    # 1. Test Creation
    print("\n>>> TEST 1: Create new expense entries")
    # "Add $50 for groceries today"
    query_1 = "Add $50 for groceries today"
    print(f"User: {query_1}")
    response_1 = await agent.process_message(query_1)
    print(f"Agent: {response_1}")
    
    # Verify in DB
    db = SessionLocal()
    # Check for the latet expense with amount 50 and category groceries
    latest_expense = db.query(models.Expense).filter(
        models.Expense.amount == 50.0, 
        models.Expense.category.ilike("%groceries%")
    ).order_by(models.Expense.id.desc()).first()
    
    if latest_expense:
        print(f"[PASS] Verified in DB: ID={latest_expense.id}, Amount={latest_expense.amount}, Category={latest_expense.category}, Date={latest_expense.date}")
    else:
        print("[FAIL] Could not find cost in DB")
    db.close()

    # 2. Test Query by Date/Category
    print("\n>>> TEST 2: Query expenses (by date range, category)")
    # "How much did I spend on groceries this month?"
    query_2 = "How much did I spend on groceries this month?"
    print(f"User: {query_2}")
    response_2 = await agent.process_message(query_2)
    print(f"Agent: {response_2}")

    # 3. Test Query by Amount
    print("\n>>> TEST 3: Query expenses (by amount)")
    # "Show me all expenses greater than $40"
    # This tests if the agent can filter by amount (either via tool or post-processing)
    query_3 = "Show me all expenses greater than $40"
    print(f"User: {query_3}")
    response_3 = await agent.process_message(query_3)
    print(f"Agent: {response_3}")

    # 4. Test Insights/Summary
    print("\n>>> TEST 4: Provide spending summaries and insights")
    # "Summarize my spending habits"
    query_4 = "Summarize my spending habits for this month"
    print(f"User: {query_4}")
    response_4 = await agent.process_message(query_4)
    print(f"Agent: {response_4}")

if __name__ == "__main__":
    asyncio.run(main())
