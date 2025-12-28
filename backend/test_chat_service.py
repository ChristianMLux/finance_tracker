import asyncio
import sys
import os
import logging

# Configure logging to stdout
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add current path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# Initialize Firebase (Simulate what main.py/auth.py does)
import firebase_admin
from firebase_admin import credentials
from dotenv import load_dotenv

load_dotenv()

# We need to init firebase_admin before importing ChatService if it relies on global app
if not firebase_admin._apps:
    project_id = os.getenv("NEXT_PUBLIC_FIREBASE_PROJECT_ID")
    options = {}
    if project_id:
        options['projectId'] = project_id
    try:
        firebase_admin.initialize_app(options=options)
        print(f"Firebase initialized with project: {project_id}")
    except Exception as e:
        print(f"Firebase init error: {e}")

from backend.services.chat_service import chat_service

async def test_chat_write():
    user_id = "n9JHLo5iHcef3ZyFuycFk5jacT33" # User ID from logs
    chat_id = "test_chat_debug"
    
    print(f"Attempting to write message for user {user_id}...")
    
    try:
        if not chat_service.db:
             print("ERROR: ChatService.db is None!")
             return

        await chat_service.add_message(user_id, chat_id, "user", "Debug message test")
        print("Write returned. Checking if it exists...")
        
        # Verify read
        msgs = await chat_service.get_recent_messages(user_id, chat_id)
        if msgs and msgs[-1]['content'] == "Debug message test":
            print("SUCCESS: Message verified in Firestore!")
        else:
            print(f"FAILURE: Message not found. History: {msgs}")
            
    except Exception as e:
        print(f"EXCEPTION: {e}")

if __name__ == "__main__":
    asyncio.run(test_chat_write())
