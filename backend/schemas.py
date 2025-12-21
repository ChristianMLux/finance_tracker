from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class ExpenseBase(BaseModel):
    amount: float
    category: str
    description: Optional[str] = None
    date: Optional[datetime] = None

class ExpenseCreate(ExpenseBase):
    pass

class Expense(ExpenseBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
