from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from . import models, schemas

async def get_expenses(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(models.Expense).order_by(models.Expense.date.desc()).offset(skip).limit(limit))
    return result.scalars().all()

async def create_expense(db: AsyncSession, expense: schemas.ExpenseCreate):
    db_expense = models.Expense(**expense.model_dump())
    db.add(db_expense)
    await db.commit()
    await db.refresh(db_expense)
    return db_expense

# Tool CRUD
async def get_tool_by_name(db: AsyncSession, name: str):
    result = await db.execute(select(models.Tool).where(models.Tool.name == name))
    return result.scalars().first()

async def create_tool(db: AsyncSession, tool_data: dict):
    # Ensure dependencies are serialized
    if "dependencies" in tool_data and isinstance(tool_data["dependencies"], list):
        import json
        tool_data["dependencies"] = json.dumps(tool_data["dependencies"])

    db_tool = models.Tool(**tool_data)
    db.add(db_tool)
    await db.commit()
    await db.refresh(db_tool)
    return db_tool

async def get_all_tools(db: AsyncSession):
    result = await db.execute(select(models.Tool).where(models.Tool.is_active == 1))
    return result.scalars().all()
