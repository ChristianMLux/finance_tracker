import os
import asyncio
from dotenv import load_dotenv
from openai import AsyncOpenAI

# Force load .env from the root
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = current_dir # since we will run from root
env_path = os.path.join(root_dir, '.env')
load_dotenv(env_path)

api_key = os.getenv("OPENROUTER_API_KEY")
print(f"Loaded Key: {api_key[:10]}...{api_key[-5:] if api_key else 'None'}")

async def test_key():
    client = AsyncOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )
    
    try:
        response = await client.chat.completions.create(
            model="google/gemini-2.0-flash-exp:free", # Use a free model for testing auth
            messages=[{"role": "user", "content": "Hello"}],
        )
        print("Success! Response:", response.choices[0].message.content)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    asyncio.run(test_key())
