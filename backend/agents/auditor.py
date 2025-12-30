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
        self.model = os.getenv("LLM_MODEL", "google/gemini-3-flash-preview")

    async def semantic_review(self, code: str, name: str) -> tuple[bool, str]:
        """
        Uses an LLM to review the code for financial logic and transparency.
        """
        system_prompt = """You are a Senior Financial Auditor & QA Engineer.
Your job is to REJECT Python code if it violates safety, logic, or financial correctness rules.

### AUDIT CATEOGRIES:

1. **Logical Sanity Checks (CRITICAL)**:
   - **Math Realism**: Validate growth rates. If $10k becomes >$100k in 5 years without high risk, REJECT.
   - **Negative Net Worth Guard**: If a standard long-only investment strategy results in NEGATIVE net worth (e.g., -$4k), REJECT IMMEDITALEY. Investment values cannot drop below zero without leverage/shorting.
   - **Unit Confusion**: Check for "8 vs 0.08" errors. If the code uses an input > 1.0 as a raw multiplier for interest, REJECT it and demand sanitization.
   - **Negative Values**: Ensure assets don't become negative unless explicitly modeled (shorting/debt).
   - **Fair Comparison**: In "Debt vs Invest" scenarios, ensure both strategies run for the SAME duration and account for the SAME starting capital.
   - **Smoke Tests (The "Sniff" Test)**:
        - **Total Interest Ceiling**: The financial benefit of paying off a debt CANNOT exceed the Total Interest payable on that debt.
        - **Rate Arbitrage**: If `(Market Return * (1 - TaxRate)) > Loan Rate`, then the "Invest" strategy MUST win mathematically.
        - **Spread Integrity (CRITICAL)**: Check the magnitude of the win.
            - Calculate simple spread profit: `TheoreticProfit = Principal * abs(NetInvestRate - LoanRate) * LoanTerm`.
            - If the tool's reported `Difference` is > 5x `TheoreticProfit`, it is a **Compounding Hallucination**.
            - *Example*: On $25k loan, 2 years, with 0.3% spread (6.8% vs 6.5%). Max divergence should be ~$300-$500. If tool claims $9,000 difference, **REJECT IT**.
        - **Delta Sanity**: For short loan terms (<3 years), the difference between strategies typically cannot exceed 10% of the principal.
        - **Day 0 Sanity Check**: At T=0 (or Year 1), the Net Worth difference between strategies MUST be negligible (< $1000). If Strategy B is "$7000 ahead" in Year 1, you failed to count the Cash Asset in Strategy A. **REJECT**.
2. **Transparency & Logging**:
   - The code MUST use `print()` to log every assumption (Tax Rate, Inflation) at the start.
   - "Hidden Math" is forbidden.

3. **Bad Financial Logic**:
   - **Lazy Portfolios**: Reject flat 1/N weightings (e.g. "25% in each of 4 random stocks") unless requested.
   - **Compounding**: Reject Simple Interest `P*(1+rt)` for multi-year periods. Mst use `P*(1+r)**t`.

4. **Safety & Security**:
   - `requests.get` is allowed for benign APIs.
   - REJECT malicious URLs or file operations outside the sandbox.
   - **Dependencies**: `yfinance`, `duckduckgo-search` are PREFERRED.

5. **Risk Profile Compliance**:
   - If user is "Risk Averse", REJECT logic that suggests >50% allocation to Crypto or unchecked Equities.

### OUTPUT FORMAT:
Analyze the code.
If valid, return JSON: {{"approved": true}}
If invalid, return JSON: {{"approved": false, "reason": "LOGIC ERROR: [Explanation]... FIX: [Suggestion]..."}}
"""

        try:
            prompt = system_prompt.format(code=code)
            response = await self.client.chat.completions.create(
                model=os.getenv("LLM_MODEL", "google/gemini-3-flash-preview"),
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": f"Audit this tool: {name}\n\n{code}"}
                ],
                response_format={"type": "json_object"}
            )
            result = json.loads(response.choices[0].message.content)
            if not result.get("approved"):
                reason = result.get("reason", "Unknown policy violation")
                logger.warning(f"Semantic Audit Failed for {name}: {reason}")
                return False, reason
            return True, ""
        except Exception as e:
            logger.error(f"Semantic review error: {e}")
            return True, "" # Fail open if LLM fails, relying on Sandbox safety

    async def validate_tool(self, tool_data: dict) -> tuple[bool, str]:
        """
        Validates the tool by running it in a sandbox.
        """
        code = tool_data.get("python_code")
        name = tool_data.get("name")
        deps = tool_data.get("dependencies", [])

        if not code:
            return False, "No code provided"

        logger.info(f"Auditing tool: {name}")

        # 1. Semantic Review (LLM)
        approved, critique = await self.semantic_review(code, name)
        if not approved:
            return False, critique

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
                            return False, f"Dependency install failed: {install_result.stderr}"

                # 3. Define the code
                sandbox.run_code(code)
                
                # 4. Check if 'run' function is defined
                check_result = sandbox.run_code("if 'run' not in locals(): raise Exception('Function run not defined')")
                if check_result.error:
                     logger.error(f"Audit failed (Runtime): {check_result.error}")
                     return False, f"Runtime error: {check_result.error}"
                
                return True, ""
        except Exception as e:
            logger.error(f"Sandbox execution failed: {e}")
            return False, f"Sandbox execution error: {str(e)}"

    async def process_message(self, message: str, context=None, status_callback=None) -> str:
        return "I verify code."
