import os
import json
from openai import AsyncOpenAI
from .base import BaseAgent

class ArchitectAgent(BaseAgent):
    def __init__(self):
        self.client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )
        self.model = os.getenv("LLM_MODEL", "google/gemini-2.0-flash-exp")

    async def generate_tool(self, requirement: str) -> dict:
        system_prompt = """You are a Senior Python Architect.
Your goal is to write a single, self-contained Python function that solves a specific financial problem.

Requirements:
1. The code must be pure Python. High-standard, typed.
2. It should not use external APIs usually, unless asked.
3. You must return a JSON object with:
   - "name": function name (snake_case)
   - "description": what it does
   - "python_code": the full python code string. The function should be named 'run'.
   - "json_schema": the JSON schema for the arguments of the function.

Example Output:
{
  "name": "calculate_roi",
  "description": "Calculates Return on Investment",
  "python_code": "def run(revenue: float, cost: float) -> float:\n    return ((revenue - cost) / cost) * 100",
  "json_schema": {
    "type": "object",
    "properties": {
      "revenue": {"type": "number"},
      "cost": {"type": "number"}
    },
    "required": ["revenue", "cost"]
  }
}
"""
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Create a tool for: {requirement}"}
            ],
            response_format={"type": "json_object"}
        )
        
        try:
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            return {"error": str(e)}

    async def process_message(self, message: str, context=None) -> str:
        # Not used primarily for chat, but for specific generation
        return "I am the Architect. I build tools."
