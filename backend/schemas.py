from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional

class ExpenseBase(BaseModel):
    amount: float
    category: str
    description: Optional[str] = None
    date: Optional[datetime] = None


class ExpenseCreate(ExpenseBase):
    category: str = Field(..., max_length=100)
    description: Optional[str] = Field(None, max_length=100)

class Expense(ExpenseBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
