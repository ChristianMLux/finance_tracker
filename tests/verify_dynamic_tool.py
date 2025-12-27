import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.agents.manager import ManagerAgent
from dotenv import load_dotenv

import logging
load_dotenv()

logging.basicConfig(filename='verify.log', level=logging.INFO, filemode='w')


from backend.database import engine
from backend import models

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

async def main():
    await init_db()
    agent = ManagerAgent()
    
    # Query that requires a new tool
    query = "Calculate the monthly payment for a $500,000 loan at 4.5% annual interest for 30 years."
    
    print(f"User Query: {query}")
    print("-" * 50)
    
    response = await agent.process_message(query)
    
    print("-" * 50)
    print(f"Agent Response: {response}")

if __name__ == "__main__":
    asyncio.run(main())
