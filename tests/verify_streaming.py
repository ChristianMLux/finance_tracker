
import httpx
import asyncio
import json

async def test_streaming():
    url = "http://localhost:8000/chat"
    message = "How much did I spend on food?"
    print(f"Sending message: {message} to {url}")
    
    try:
        async with httpx.AsyncClient() as client:
            async with client.stream("POST", url, params={"message": message}, timeout=30.0) as response:
                if response.status_code != 200:
                    print(f"Error: Status code {response.status_code}")
                    print(await response.aread())
                    return

                print("Connected! Receiving stream...")
                async for line in response.aiter_lines():
                    if line.strip():
                        try:
                            data = json.loads(line)
                            print(f"[RECEIVED] Type: {data.get('type')} | Content: {data.get('content')[:50]}...")
                        except json.JSONDecodeError:
                            print(f"[RAW] {line}")
    except Exception as e:
        print(f"Connection failed: {e}")
        print("Ensure the server is running: uvicorn backend.main:app --reload")

if __name__ == "__main__":
    asyncio.run(test_streaming())
