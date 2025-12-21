import asyncio
import os
from dotenv import load_dotenv

# Load env vars
load_dotenv()

# Import the manager agent
from backend.agents.manager import manager_agent

async def main():
    print("--- Test 1: Finance Query ---")
    response_finance = await manager_agent.process_message("How much did I spend on food?")
    print(f"Response: {response_finance}\n")

    print("--- Test 2: Currency Query ---")
    response_currency = await manager_agent.process_message("Convert 100 USD to EUR")
    print(f"Response: {response_currency}\n")

    print("--- Test 3: Composite Query ---")
    response_composite = await manager_agent.process_message("Convert my food costs in EUR")
    print(f"Response: {response_composite}\n")

if __name__ == "__main__":
    asyncio.run(main())
