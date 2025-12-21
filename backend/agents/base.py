from typing import Any, List, Dict, Optional
from abc import ABC, abstractmethod

class BaseAgent(ABC):
    @abstractmethod
    async def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Process a user message and return a response.
        :param message: The user's input message.
        :param context: Optional context (e.g. from previous agents).
        :return: string response
        """
        pass
