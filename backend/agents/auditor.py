import os
import logging
from e2b_code_interpreter import Sandbox
from .base import BaseAgent

logger = logging.getLogger(__name__)

class AuditorAgent(BaseAgent):
    def __init__(self):
        self.api_key = os.getenv("E2B_API_KEY")
        if not self.api_key:
            logger.warning("E2B_API_KEY not found. Auditor will fail to execute code.")

    async def validate_tool(self, tool_data: dict) -> bool:
        """
        Validates the tool by running it in a sandbox.
        """
        code = tool_data.get("python_code")
        if not code:
            return False

        logger.info(f"Auditing tool: {tool_data.get('name')}")

        try:
            with Sandbox.create() as sandbox:
                # 1. Define the code
                sandbox.run_code(code)
                
                # 2. Check if 'run' function is defined
                check_result = sandbox.run_code("if 'run' not in locals(): raise Exception('Function run not defined')")
                if check_result.error:
                     logger.error(f"Audit failed: {check_result.error}")
                     return False
                
                return True
        except Exception as e:
            logger.error(f"Sandbox execution failed: {e}")
            return False

    async def process_message(self, message: str, context=None) -> str:
        return "I verify code."
