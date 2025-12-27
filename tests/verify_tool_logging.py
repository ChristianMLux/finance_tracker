
import httpx
import asyncio
import json

async def test_new_tool_logging():
    url = "http://localhost:8002/chat"
    # A request that requires a new tool
    message = "Calculate the future value of a $1000 investment growing at 5% annually for 10 years, compounding monthly."
    print(f"Sending message: {message} to {url}")
    
    try:
        async with httpx.AsyncClient() as client:
            async with client.stream("POST", url, params={"message": message}, timeout=60.0) as response:
                if response.status_code != 200:
                    print(f"Error: Status code {response.status_code}")
                    return

                print("Connected! Receiving stream...")
                async for line in response.aiter_lines():
                    if line.strip():
                        try:
                            data = json.loads(line)
                            log_type = data.get('type')
                            content = data.get('content')
                            
                            if log_type == 'log':
                                # Highlight our new tool logs
                                if "Tool:" in content:
                                    print(f"[TOOL LOG] {content}")
                                else:
                                    print(f"[LOG] {content}")
                            else:
                                print(f"[{log_type}] {content[:100]}...")
                                
                        except json.JSONDecodeError:
                            print(f"[RAW] {line}")
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_new_tool_logging())
