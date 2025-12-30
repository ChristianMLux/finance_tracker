from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional, List, Any

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

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    id: str
    full_name: Optional[str] = None

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    role: Optional[str] = None # Admin only in real app, but useful here/dev

class User(UserBase):
    id: str
    full_name: Optional[str] = None
    role: str
    subscription_status: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# Tool Schemas
class ToolBase(BaseModel):
    name: str
    title: Optional[str] = None
    description: Optional[str] = None
    python_code: Optional[str] = None
    json_schema: Optional[str] = None
    dependencies: Optional[str] = "[]"
    is_active: Optional[int] = 1
    status: Optional[str] = "temporary"
    creator_id: Optional[str] = None

class ToolCreate(ToolBase):
    pass

class Tool(ToolBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)

class ToolExecutionRequest(BaseModel):
    args: dict

