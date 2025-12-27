
import asyncio
import httpx
import sys

API_URL = "http://127.0.0.1:8000"

async def main():
    async with httpx.AsyncClient(timeout=10.0) as client:
        # 1. Create unique expense
        data = {
            "amount": 99.99,
            "category": "Other",
            "description": "VERIFICATION_CHECK_LATEST"
        }
        print(f"Adding expense: {data}")
        resp = await client.post(f"{API_URL}/expenses/", json=data)
        if resp.status_code != 200:
            print(f"Failed to create: {resp.text}")
            return

        # 2. Fetch list
        print("Fetching expenses...")
        resp = await client.get(f"{API_URL}/expenses/")
        items = resp.json()
        
        # 3. Verify
        if not items:
            print("No items returned")
            return
            
        first_item = items[0]
        print(f"First item in list: {first_item}")
        
        if first_item['description'] == "VERIFICATION_CHECK_LATEST":
            print("SUCCESS: Newest item is first!")
        else:
            print("FAILURE: Newest item is NOT first.")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
