from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from .database import engine, Base, get_db
from . import auth # Initialize Firebase Admin EARLY
from . import models, schemas, crud, agents
from .routers import analytics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Async Database Initialization
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    yield

app = FastAPI(title="Finance Tracker API", lifespan=lifespan)

app.include_router(analytics.router)

# Configure CORS
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Finance Tracker API is running"}


@app.get("/users/me", response_model=schemas.User)
async def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user

@app.put("/users/me", response_model=schemas.User)
async def update_user_me(user_update: schemas.UserUpdate, current_user: models.User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await crud.update_user(db, current_user.id, user_update)

@app.delete("/users/me/data")
async def clear_user_data(current_user: models.User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await crud.delete_user_data(db, current_user.id)
    return {"status": "success", "message": "All user data deleted"}

@app.post("/expenses/", response_model=schemas.Expense)
async def create_expense(expense: schemas.ExpenseCreate, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return await crud.create_expense(db=db, expense=expense, user_id=current_user.id)

@app.get("/expenses/", response_model=list[schemas.Expense])
async def read_expenses(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return await crud.get_expenses(db, user_id=current_user.id, skip=skip, limit=limit)

import asyncio
import json
from fastapi.responses import StreamingResponse

@app.post("/chat")
async def chat(message: str, chat_id: str = "default", current_user: models.User = Depends(get_current_user)):
    queue = asyncio.Queue()
    
    async def callback(log_type, content):
        # Format as NDJSON line
        data = json.dumps({"type": log_type, "content": content})
        await queue.put(data + "\n")

    async def background_worker():
        try:
            response = await agents.manager_agent.process_message(message, user_id=current_user.id, chat_id=chat_id, status_callback=callback)
            # Final response
            await queue.put(json.dumps({"type": "response", "content": response}) + "\n")
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            await queue.put(json.dumps({"type": "error", "content": "Internal processing error."}) + "\n")
        finally:
            await queue.put(None) # Sentinel to stop stream

    # Start the agent in background
    asyncio.create_task(background_worker())

    async def stream_generator():
        while True:
            item = await queue.get()
            if item is None:
                break
            yield item
    
    return StreamingResponse(stream_generator(), media_type="application/x-ndjson")
