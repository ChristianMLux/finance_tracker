from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from .database import Base

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    category = Column(String, index=True)
    description = Column(String)
    date = Column(DateTime, default=datetime.utcnow)

class Tool(Base):
    __tablename__ = "tools"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)
    python_code = Column(String)
    json_schema = Column(String) # Storing schema as JSON string
    dependencies = Column(String, default="[]") # Storing list of dependencies as JSON string
    is_active = Column(Integer, default=1) # 1 for active, 0 for inactive
