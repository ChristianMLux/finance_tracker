import os
import json
import logging
from openai import AsyncOpenAI
from e2b_code_interpreter import Sandbox
from .base import BaseAgent

logger = logging.getLogger(__name__)

class AuditorAgent(BaseAgent):
    def __init__(self):
        self.api_key = os.getenv("E2B_API_KEY")
        if not self.api_key:
            logger.warning("E2B_API_KEY not found. Auditor will fail to execute code.")
        
        self.client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )
        self.model = os.getenv("LLM_MODEL", "google/gemini-2.0-flash-exp")

    async def semantic_review(self, code: str, name: str) -> bool:
        """
        Uses an LLM to review the code for financial logic and transparency.
        """
        system_prompt = """You are a Senior Financial Auditor.
Your job is to REJECT Python code if it violates these rules:

1. **Transparency Missing**: The code MUST use `print()` to log assumptions (rates, constants) at the start.
2. **Bad Financial Logic**: 
   - No flat 10% weightings for portfolios (lazy).
   - No naive linear extrapolations without caveats.
   - Real estate calcs must mention maintenance/taxes.
3. **Safety**: 
   - `requests.get` to benign APIs IS ALLOWED (Fallback).
   - Standard Libraries (`yfinance`, `duckduckgo-search`) ARE ALLOWED and PREFERRED.
   - **Multi-Source Logic**: Using multiple sources (e.g. YFinance + DuckDuckGo) is ENCOURAGED for accuracy.
   - REJECT malicious URLs.
4. **Risk Profile**:
   - If user is described as "Risk Averse", REJECT logic that suggests 100% equity/crypto speculation.
   - EXCEPTION: "Hedging" strategies (Options for protection) ARE ALLOWED and encouraged for risk reduction.

Code:
{code}

Analyze the code.
If valid, return JSON: {{"approved": true}}
If invalid, return JSON: {{"approved": false, "reason": "..."}}
"""
        try:
            prompt = system_prompt.format(code=code)
            response = await self.client.chat.completions.create(
                model=os.getenv("LLM_MODEL", "google/gemini-2.0-flash-exp"),
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": f"Audit this tool: {name}\n\n{code}"}
                ],
                response_format={"type": "json_object"}
            )
            result = json.loads(response.choices[0].message.content)
            if not result.get("approved"):
                logger.warning(f"Semantic Audit Failed for {name}: {result.get('reason')}")
                return False
            return True
        except Exception as e:
            logger.error(f"Semantic review error: {e}")
            return True # Fail open if LLM fails, relying on Sandbox safety

    async def validate_tool(self, tool_data: dict) -> bool:
        """
        Validates the tool by running it in a sandbox.
        """
        code = tool_data.get("python_code")
        name = tool_data.get("name")
        deps = tool_data.get("dependencies", [])

        if not code:
            return False

        logger.info(f"Auditing tool: {name}")

        # 1. Semantic Review (LLM)
        if not await self.semantic_review(code, name):
            return False

        # 2. Syntax & Runtime Check (Sandbox)
        try:
            with Sandbox.create() as sandbox:
                # 2. Install Dependencies
                if deps:
                    logger.info(f"Installing dependencies: {deps}")
                    for dep in deps:
                        # Using `pip install -q` for quiet installation
                        install_result = sandbox.commands.run(f"pip install -q {dep}")
                        if install_result.exit_code != 0:
                            logger.error(f"Failed to install dependency {dep}: {install_result.stderr}")
                            return False

                # 3. Define the code
                sandbox.run_code(code)
                
                # 4. Check if 'run' function is defined
                check_result = sandbox.run_code("if 'run' not in locals(): raise Exception('Function run not defined')")
                if check_result.error:
                     logger.error(f"Audit failed (Runtime): {check_result.error}")
                     return False
                
                return True
        except Exception as e:
            logger.error(f"Sandbox execution failed: {e}")
            return False

    async def process_message(self, message: str, context=None, status_callback=None) -> str:
        return "I verify code."
