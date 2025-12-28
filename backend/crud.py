from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from . import models, schemas

async def get_expenses(db: AsyncSession, user_id: str, skip: int = 0, limit: int = 100):
    result = await db.execute(select(models.Expense).where(models.Expense.user_id == user_id).order_by(models.Expense.date.desc()).offset(skip).limit(limit))
    return result.scalars().all()

async def create_expense(db: AsyncSession, expense: schemas.ExpenseCreate, user_id: str):
    db_expense = models.Expense(**expense.model_dump(), user_id=user_id)
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

# User CRUD
async def get_user(db: AsyncSession, user_id: str):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    return result.scalars().first()

async def create_user_if_not_exists(db: AsyncSession, user: schemas.UserCreate):
    db_user = await get_user(db, user.id)
    if not db_user:
        db_user = models.User(**user.model_dump())
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
    return db_user

async def update_user(db: AsyncSession, user_id: str, user_update: schemas.UserUpdate):
    db_user = await get_user(db, user_id)
    if db_user:
        update_data = user_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_user, key, value)
        await db.commit()
        await db.refresh(db_user)
    return db_user

async def delete_user_data(db: AsyncSession, user_id: str):
    # Delete all expenses
    await db.execute(models.Expense.__table__.delete().where(models.Expense.user_id == user_id))
    # Delete other user-specific data if any (e.g. tools created by user?) 
    # For now just expenses.
    await db.commit()
