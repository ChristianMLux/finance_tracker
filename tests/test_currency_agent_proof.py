import asyncio
import os
import sys

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, '..')
sys.path.append(project_root)

from backend.agents.manager import ManagerAgent

async def main():
    print("Initializing ManagerAgent...")
    agent = ManagerAgent()
    
    # 1. Test Simple Conversion
    print("\n>>> TEST 1: Simple Conversion")
    query_1 = "Convert 50 USD to EUR"
    print(f"User: {query_1}")
    response_1 = await agent.process_message(query_1)
    print(f"Agent: {response_1}")
    
    if "EUR" in response_1 and "Rate:" in response_1:
         print("[PASS] Conversion successful with rate info.")
    else:
         print("[FAIL] Response format unexpected.")

    # 2. Test Rate Inquiry (implied via 1 unit or explicit question)
    print("\n>>> TEST 2: Exchange Rate Inquiry")
    query_2 = "What is the exchange rate for GBP to JPY?"
    print(f"User: {query_2}")
    response_2 = await agent.process_message(query_2)
    print(f"Agent: {response_2}")
    
    if "JPY" in response_2 and ("Rate:" in response_2 or "rate" in response_2.lower()):
         print("[PASS] Rate inquiry handled.")
    else:
         print("[FAIL] Response format unexpected.")

    # 3. Test Multi-Currency
    print("\n>>> TEST 3: Other Currencies (EUR to CAD)")
    query_3 = "Convert 100 EUR to CAD"
    print(f"User: {query_3}")
    response_3 = await agent.process_message(query_3)
    print(f"Agent: {response_3}")
    
    if "CAD" in response_3:
        print("[PASS] CAD conversion successful.")
    else:
        print("[FAIL] CAD conversion failed.")

if __name__ == "__main__":
    asyncio.run(main())
