from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from . import models, schemas

async def get_expenses(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(models.Expense).offset(skip).limit(limit))
    return result.scalars().all()

async def create_expense(db: AsyncSession, expense: schemas.ExpenseCreate):
    db_expense = models.Expense(**expense.model_dump())
    db.add(db_expense)
    await db.commit()
    await db.refresh(db_expense)
    return db_expense
