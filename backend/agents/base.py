from typing import Any, List, Dict, Optional
from abc import ABC, abstractmethod

class BaseAgent(ABC):
    @abstractmethod
    async def process_message(self, message: str, context: Optional[Dict[str, Any]] = None, status_callback: Optional[Any] = None) -> str:
        """
        Process a user message and return a response.
        :param message: The user's input message.
        :param context: Optional context (e.g. from previous agents).
        :param status_callback: Optional async callable to report status/logs. Signature: async def callback(log_type: str, content: str).
        :return: string response
        """
        pass
