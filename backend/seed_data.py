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

async def init_db():
    async with engine.begin() as conn:
        # Create tables
        await conn.run_sync(models.Base.metadata.create_all)

async def seed_data():
    await init_db()
    
    async with AsyncSessionLocal() as db:
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

        print("Seeding data...")
        
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
                date=date
            )
            db.add(expense)
            print(f"Added: {description} (${amount}) - {date.date()}")
        
        await db.commit()
    
    print("Seeding complete!")

if __name__ == "__main__":
    # Windows-specific fix for asyncio event loop policy if needed, 
    # but usually standard run works for simple scripts unless conflicts.
    # Python 3.8+ on Windows defaults to ProactorEventLoop which is fine.
    
    # Run the seed function
    asyncio.run(seed_data())
