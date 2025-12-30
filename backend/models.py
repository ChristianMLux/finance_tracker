from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True) # Firebase UID
    email = Column(String, unique=True, index=True)
    full_name = Column(String, nullable=True)
    role = Column(String, default="free") # free, pro, platinum, admin
    subscription_status = Column(String, default="active") # active, cancelled, past_due
    created_at = Column(DateTime, default=datetime.utcnow)

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), index=True, nullable=True)
    amount = Column(Float, nullable=False)
    category = Column(String, index=True)
    description = Column(String)
    date = Column(DateTime, default=datetime.utcnow)

class Tool(Base):
    __tablename__ = "tools"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    title = Column(String, index=True, nullable=True) # User-friendly name
    description = Column(String)
    python_code = Column(String)
    json_schema = Column(String) # Storing schema as JSON string
    dependencies = Column(String, default="[]") # Storing list of dependencies as JSON string
    is_active = Column(Integer, default=1) # 1 for active, 0 for inactive
    status = Column(String, default="temporary") # temporary, saved, public
    creator_id = Column(String, ForeignKey("users.id"), nullable=True)
