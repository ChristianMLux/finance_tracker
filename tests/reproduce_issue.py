
import asyncio
import httpx
import sys

API_URL = "http://127.0.0.1:8000"

async def main():
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. Check if backend is running
        try:
            resp = await client.get(f"{API_URL}/")
            print(f"Backend status: {resp.status_code}")
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Backend not reachable: {e}")
            return

        # 2. Add an expense
        expense_data = {
            "amount": 12.50,
            "category": "Food",
            "description": "Test Burrito"
        }
        print(f"Adding expense: {expense_data}")
        try:
            resp = await client.post(f"{API_URL}/expenses/", json=expense_data)
            print(f"Add response: {resp.status_code} {resp.text}")
        except Exception as e:
            print(f"Add failed: {e}")
            return

        # 3. Fetch expenses
        print("Fetching expenses...")
        try:
            resp = await client.get(f"{API_URL}/expenses/")
            expenses = resp.json()
            print(f"Found {len(expenses)} expenses")
            found = False
            for e in expenses:
                if e['description'] == "Test Burrito" and e['amount'] == 12.50:
                    print("Found created expense!")
                    found = True
                    break
            if not found:
                print("ERROR: Created expense NOT found in list!")
        except Exception as e:
            print(f"Fetch failed: {e}")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
