from .base import BaseAgent
import os
import json
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

class InterpreterAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.name = "Interpreter Agent"

    async def process_message(self, message: str, context: dict = None, status_callback=None) -> str:
        
        system_prompt = """You are the **Interpreter Agent**.
Your SOLE purpose is to take raw data (JSON, text, or tool outputs) provided by the user and transform it into a beautiful, human-readable **Financial Report** in Markdown.

### Your Guidelines:
1.  **Strict Fidelity**: Do NOT invent facts. Use *only* the data provided. If data is missing for a section, omit that section or state "Data not available".
2.  **Formatting**:
    *   Use `## Headers` for sections.
    *   Use `**Bold**` for key figures.
    *   Use Lists for breakdowns.
    *   Format currency nicely (e.g., `$1,250.00`).
3.  **Tone**: Professional, insightful, and helpful. Act like a high-end Financial Advisor explaining a complex report to a client.
4.  **No Tech Speak**: Do NOT show raw JSON. Do NOT say "The tool returned...". Say "The analysis shows...".
5.  **Structure**:
    *   **Executive Summary**: A 1-sentence high-level takeaways.
    *   **Key Insights**: Bullet points of the most important findings.
    *   **Detailed Breakdown**: A structured view of the numbers.
    *   **Advice/Recommendation**: Actionable next steps based *strictly* on the data.

### Input Format:
The user will provide a message containing "Here is the financial data..." followed by a JSON block or raw text.

### Output Format:
Pure, clean Markdown. No code blocks for the text itself (unless showing a specific calculation snippet).
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ]

        if status_callback:
            await status_callback("log", "Interpreter Agent: analyzing data...")

        try:
            response = await client.chat.completions.create(
                model=os.getenv("LLM_MODEL", "google/gemini-3-flash-preview"),
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            if status_callback:
                await status_callback("error", f"Interpreter Agent failed: {e}")
            return f"Error interpreting data: {e}"
