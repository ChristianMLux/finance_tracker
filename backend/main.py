from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from .database import engine, Base, get_db
from . import models, schemas, crud, agents

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Async Database Initialization
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    yield

app = FastAPI(title="Finance Tracker API", lifespan=lifespan)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Finance Tracker API is running"}

@app.post("/expenses/", response_model=schemas.Expense)
async def create_expense(expense: schemas.ExpenseCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_expense(db=db, expense=expense)

@app.get("/expenses/", response_model=list[schemas.Expense])
async def read_expenses(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await crud.get_expenses(db, skip=skip, limit=limit)

@app.post("/chat")
async def chat(message: str):
    response = await agents.manager_agent.process_message(message)
    return {"response": response}
