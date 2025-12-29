import sys
import os
import asyncio
import logging
import uuid
from backend import crud, schemas, models # Import here to ensure models are registered

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

logging.basicConfig(level=logging.INFO)
logging.getLogger("multipart").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("aiosqlite").setLevel(logging.WARNING)

async def test_startup():
    print("--- STARTING CHECK ---")
    
    from backend.database import AsyncSessionLocal

    target_uid = "Plim3lw1zvXnvFywbCdi078trFy2"
    random_email = f"test_{uuid.uuid4().hex[:6]}@test.com"

    # 1. Create User with Unique Email
    try:
        print(f"[CHECK] Creating User {target_uid} with {random_email}...")
        async with AsyncSessionLocal() as db:
            # Check if exists first (should be None)
            user = await crud.get_user(db, target_uid)
            if user:
                 print("   [INFO] User already exists (Unexpected from previous check)")
            else:
                 user_create = schemas.UserCreate(id=target_uid, email=random_email)
                 user = await crud.create_user_if_not_exists(db, user_create)
                 print(f"   [OK] Created User: {user.id}")
                 
                 # Cleanup
                 await db.delete(user)
                 await db.commit()
                 print("   [OK] Cleanup Success")

    except Exception as e:
        print(f"   [FAIL] Creation Error: {e}")
        import traceback
        traceback.print_exc()

    print("--- DONE ---")

if __name__ == "__main__":
    asyncio.run(test_startup())
