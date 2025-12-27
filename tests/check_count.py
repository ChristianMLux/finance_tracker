
import asyncio
import sys
import os

# Add project root to sys.path
sys.path.append(os.getcwd())

from backend.database import AsyncSessionLocal
from backend import models
from sqlalchemy import func, select

async def main():
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(func.count(models.Expense.id)))
        count = res.scalar()
        print(f"Total expenses in DB: {count}")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
