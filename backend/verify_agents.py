import asyncio
import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.getcwd())

from backend.agents.currency import CurrencyAgent
import logging

# Configure logging
logging.basicConfig(level=logging.ERROR)
root = logging.getLogger()
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.ERROR)
root.addHandler(handler)

async def main():
    load_dotenv()
    agent = CurrencyAgent()

    print("\n--- Verifying Currency Agent Conversation ---")
    query = "Convert 100 USD to EUR"
    print(f"User: {query}")
    response = await agent.process_message(query)
    print(f"Agent: {response}")

if __name__ == "__main__":
    asyncio.run(main())
