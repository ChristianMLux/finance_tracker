from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from datetime import datetime, timedelta

from backend.database import get_db
from backend.models import Expense, User
from backend.auth import get_current_user

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/allocation")
async def get_allocation(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns expenses grouped by category.
    """
    stmt = (
        select(Expense.category, func.sum(Expense.amount).label("total"))
        .where(Expense.user_id == current_user.id)
        .group_by(Expense.category)
    )
    result = await db.execute(stmt)
    # Result rows are keyed by column name/label
    data = [{"name": row.category, "value": row.total} for row in result.all() if row.category]
    return data

@router.get("/cashflow")
async def get_cashflow(
    days: int = 180,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns total expenses grouped by month for the last N days.
    """
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # We use a universal approach for month extraction compatible with SQLite and Postgres for basic 'YYYY-MM'
    # For SQLite, func.strftime('%Y-%m', Expense.date)
    # For Postgres, func.to_char(Expense.date, 'YYYY-MM')
    # Since we might be running on either, we can check a bit or just use a python fallback if necessary?
    # No, we really want SQL aggregation.
    
    # Let's assume Postgres as per roadmap, but provide a safe fallback or use a conditional compilation if we were fancy.
    # Given the roadmap says "Postgres (Cloud SQL)", I will use Postgres syntax but...
    # The user might be running tests on SQLite.
    
    # Check dialect? 
    # Or just use `func.strftime` which works on SQLite. Postgres has `to_char`.
    # Let's try `func.to_char` first as it's the target. If it fails on SQLite tests... well, the environment defaults to SQLite.
    # Actually, SQLite does NOT support `to_char`.
    
    # Workaround: Use `extract('year', ...)` and `extract('month', ...)` which is standard SQL.
    
    # Use standard extract which works on both SQLite and Postgres (mostly)
    # We fetch year/month and format in Python to avoid dialect-specific string concat functions
    stmt = (
        select(
            func.extract('year', Expense.date).label('year'),
            func.extract('month', Expense.date).label('month'),
            func.sum(Expense.amount).label('total')
        )
        .where(
            Expense.user_id == current_user.id,
            Expense.date >= start_date
        )
        .group_by('year', 'month')
        .order_by('year', 'month')
    )
    
    result = await db.execute(stmt)
    
    data = []
    for row in result.all():
        # row has year, month, total (year/month are floats or decimals often returned by extract)
        month_str = f"{int(row.year)}-{int(row.month):02d}"
        data.append({
            "name": month_str,
            "value": row.total
        })
        
    return data
