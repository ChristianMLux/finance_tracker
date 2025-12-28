import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy import text

from backend.main import app
from backend.database import Base, get_db
from backend.auth import verify_token
from backend.models import User, Expense
from datetime import datetime, timedelta

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def override_get_db():
    async with TestingSessionLocal() as db:
        yield db

async def override_verify_token():
    return {"uid": "test_user_123", "email": "test@example.com"}

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[verify_token] = override_verify_token

@pytest.fixture(scope="function")
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(scope="function")
async def db_session(init_db):
    async with TestingSessionLocal() as session:
        yield session

from httpx import AsyncClient, ASGITransport

@pytest.fixture(scope="function")
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

@pytest.mark.asyncio
async def test_analytics_allocation(client, db_session):
    # Seed data
    # Check if user exists, if not create
    result = await db_session.execute(text("SELECT * FROM users WHERE id = 'test_user_123'"))
    if not result.first():
        user = User(id="test_user_123", email="test@example.com", role="pro")
        db_session.add(user)
    
    # Add expenses
    e1 = Expense(user_id="test_user_123", amount=100.0, category="Food", description="Dinner", date=datetime.utcnow())
    e2 = Expense(user_id="test_user_123", amount=50.0, category="Food", description="Lunch", date=datetime.utcnow())
    e3 = Expense(user_id="test_user_123", amount=200.0, category="Transport", description="Taxi", date=datetime.utcnow())
    
    db_session.add_all([e1, e2, e3])
    await db_session.commit()

    response = await client.get("/analytics/allocation", headers={"Authorization": "Bearer mock_token"})
    assert response.status_code == 200
    data = response.json()
    
    # Verify aggregation
    food = next((item for item in data if item["name"] == "Food"), None)
    transport = next((item for item in data if item["name"] == "Transport"), None)
    
    assert food is not None
    assert transport is not None
    assert food["value"] == 150.0
    assert transport["value"] == 200.0

@pytest.mark.asyncio
async def test_analytics_cashflow(client, db_session):
    # Add expense in previous month
    today = datetime.utcnow()
    # Go back safely ~35 days
    last_month = today - timedelta(days=35)
    
    e4 = Expense(user_id="test_user_123", amount=300.0, category="Rent", description="Rent", date=last_month)
    db_session.add(e4)
    await db_session.commit()
    
    response = await client.get("/analytics/cashflow", headers={"Authorization": "Bearer mock_token"})
    assert response.status_code == 200
    data = response.json()
    
    # We expect at least two entries: Current Month and Last Month
    # Note: If today is Jan, last month is Dec.
    
    assert len(data) >= 1
    # Check total for Rent
    
    # Find the month entry for 'last_month'
    last_month_str = f"{last_month.year}-{last_month.month:02d}"
    entry = next((item for item in data if item["name"] == last_month_str), None)
    
    assert entry is not None
    assert entry["value"] >= 300.0
