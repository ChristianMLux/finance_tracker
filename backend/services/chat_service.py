import firebase_admin
from firebase_admin import firestore
import logging
from datetime import datetime
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self):
        try:
            self.db = firestore.client()
        except Exception as e:
            logger.error(f"Error initializing Firestore client: {e}")
            self.db = None

    async def add_message(self, user_id: str, chat_id: str, role: str, content: str, component: Optional[Dict] = None):
        """
        Adds a message to the Firestore chat history.
        """
        if not self.db:
            logger.warning("Firestore is not initialized. Message not saved.")
            return

        try:
            # Construct the message document
            message_data = {
                "role": role,
                "content": content,
                "timestamp": firestore.SERVER_TIMESTAMP,
                "createdAt": datetime.utcnow().isoformat()
            }
            if component:
                message_data["component"] = component

            # Path: users/{user_id}/chats/{chat_id}/messages
            # We use .add() to generate an auto-ID for the message
            self.db.collection("users").document(user_id)\
                .collection("chats").document(chat_id)\
                .collection("messages").add(message_data)
                
            logger.info(f"Message from {role} saved to chat {chat_id}")
        except Exception as e:
            logger.error(f"Failed to save message to Firestore: {e}")

    async def get_recent_messages(self, user_id: str, chat_id: str, limit: int = 10) -> List[Dict[str, str]]:
        """
        Retrieves the most recent messages for context.
        Returns a list of dicts: [{'role': 'user', 'content': '...'}, ...]
        Ordered by timestamp ASCENDING (oldest to newest) for LLM context.
        """
        if not self.db:
            return []

        try:
            # Query: users/{user_id}/chats/{chat_id}/messages
            # Order by timestamp DESC to get recent, then reverse
            docs = self.db.collection("users").document(user_id)\
                .collection("chats").document(chat_id)\
                .collection("messages")\
                .order_by("timestamp", direction=firestore.Query.DESCENDING)\
                .limit(limit)\
                .stream()

            messages = []
            for doc in docs:
                data = doc.to_dict()
                messages.append({
                    "role": data.get("role", "user"),
                    "content": data.get("content", ""),
                    "component": data.get("component", None)
                })
            
            # Reverse to get chronological order
            return messages[::-1]
        except Exception as e:
            logger.error(f"Failed to retrieve chat history: {e}")
            return []

chat_service = ChatService()
