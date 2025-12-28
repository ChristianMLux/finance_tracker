import sys
import os
import random
import asyncio
from datetime import datetime, timedelta

# Add the current directory to sys.path to allow imports from backend
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from backend.database import AsyncSessionLocal, engine, Base
from backend import models

from sqlalchemy.future import select

async def init_db():
    async with engine.begin() as conn:
        # Create tables
        await conn.run_sync(models.Base.metadata.create_all)

async def seed_data():
    await init_db()
    
    async with AsyncSessionLocal() as db:
        # 1. Fetch existing users to link data to
        result = await db.execute(select(models.User))
        users = result.scalars().all()

        if not users:
            print("No users found in the database.")
            print("Please log in to the application at least once to create a user record.")
            return

        print("\nFound the following users:")
        for idx, user in enumerate(users):
            print(f"{idx + 1}. {user.email} (ID: {user.id})")
        
        selected_user = None
        if len(users) == 1:
            selected_user = users[0]
            print(f"\nOnly one user found. Automatically selecting: {selected_user.email}")
        else:
            while True:
                try:
                    choice = int(input("\nSelect user number to seed data for: "))
                    if 1 <= choice <= len(users):
                        selected_user = users[choice - 1]
                        break
                    else:
                        print("Invalid selection.")
                except ValueError:
                    print("Please enter a number.")
        
        print(f"\nGenerating data for user: {selected_user.email}...")

        categories = [
            "Food", "Transport", "Entertainment", "Utilities", "Shopping", 
            "Health", "Travel", "Education"
        ]
        
        descriptions = {
            "Food": ["Lunch at Cafe", "Groceries", "Dinner with friends", "Coffee", "Snacks"],
            "Transport": ["Uber ride", "Bus ticket", "Gas station", "Train ticket", "Car maintenance"],
            "Entertainment": ["Movie night", "Netflix subscription", "Concert tickets", "Video game", "Spotify"],
            "Utilities": ["Electric bill", "Water bill", "Internet bill", "Phone bill"],
            "Shopping": ["New shirt", "Electronics", "Home decor", "Gifts"],
            "Health": ["Pharmacy", "Gym membership", "Doctor visit"],
            "Travel": ["Flight booking", "Hotel stay", "Souvenirs"],
            "Education": ["Online course", "Books", "Stationery"]
        }
        
        # Generate ~25 items
        for _ in range(25):
            category = random.choice(categories)
            description = random.choice(descriptions.get(category, ["Misc"]))
            
            # Random amount between 5 and 150, rounded to 2 decimals
            amount = round(random.uniform(5.0, 150.0), 2)
            
            # Random date within last 30 days
            days_ago = random.randint(0, 30)
            date = datetime.utcnow() - timedelta(days=days_ago)
            
            expense = models.Expense(
                amount=amount,
                category=category,
                description=description,
                date=date,
                user_id=selected_user.id 
            )
            db.add(expense)
            print(f"Added: {description} (${amount}) - {date.date()}")
        
        await db.commit()

async def seed_tools():
    # Helper to seed tools if they don't exist
    async with AsyncSessionLocal() as db:
        # Check if tools exist
        result = await db.execute(select(models.Tool))
        tools = result.scalars().all()
        
        if tools:
            print("Tools already seeded.")
            return

        print("Seeding tools...")
        
        finance_tools = [
            {
                "name": "get_expenses",
                "title": "Expense Tracker",
                "description": "Analyze your spending habits and view expense history.",
                "python_code": "# Native tool",
                "is_active": 1
            },
            {
                "name": "add_expense",
                "title": "Quick Add",
                "description": "Quickly add a new expense to your log.",
                "python_code": "# Native tool",
                "is_active": 1
            },
            {
                "name": "loan_calculator",
                "title": "Loan Calculator",
                "description": "Calculate monthly payments and amortization schedules.",
                "python_code": "# Dynamic tool placeholder",
                "is_active": 1
            }
        ]

        for tool_data in finance_tools:
            tool = models.Tool(**tool_data)
            db.add(tool)
        
        await db.commit()
        print("Tools seeded successfully!")
    
    print("\nSeeding complete!")

async def main():
    if len(sys.argv) > 1 and sys.argv[1] == "tools_only":
        await seed_tools()
    else:
        # Default behavior (interactive expense seeding + tools)
        await seed_data()
        await seed_tools()

if __name__ == "__main__":
    # Windows-specific fix for asyncio event loop policy if needed, 
    # but usually standard run works for simple scripts unless conflicts.
    # Python 3.8+ on Windows defaults to ProactorEventLoop which is fine.
    
    # Run the seed function
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
