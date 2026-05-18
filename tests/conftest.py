"""
Pytest configuration and shared fixtures.
"""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from main import app
from src.database.db import get_db
from src.database.models import Base, User, Contact
from src.schemas import UserCache
from src.services.dependencies import get_current_user

TEST_DB_URL = "sqlite+aiosqlite:///./test.db"

test_engine = create_async_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)

@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_db():
    """Create all tables before tests; drop them after."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def db_session():
    """Provide a clean async DB session for each test."""
    async with TestingSessionLocal() as session:
        yield session

@pytest.fixture
def mock_user() -> UserCache:
    """A regular user object used across tests."""
    return UserCache(
        id=1,
        username="testuser",
        email="test@example.com",
        avatar=None,
        confirmed=True,
        created_at="2024-01-01",
        role="user",
    )

@pytest.fixture
def mock_admin() -> UserCache:
    """An admin user object used across tests."""
    return UserCache(
        id=2,
        username="adminuser",
        email="admin@example.com",
        avatar=None,
        confirmed=True,
        created_at="2024-01-01",
        role="admin",
    )

@pytest_asyncio.fixture
async def client(db_session: AsyncSession, mock_user: UserCache):
    """
    Async HTTP test client with overridden DB and auth dependencies.
    Authenticated as a regular user by default.
    """
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_current_user] = lambda: mock_user
 
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
 
    app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def admin_client(db_session: AsyncSession, mock_admin: UserCache):
    """
    Async HTTP test client authenticated as admin.
    """
    from src.services.dependencies import require_role
 
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_current_user] = lambda: mock_admin
 
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
 
    app.dependency_overrides.clear()

@pytest.fixture(autouse=True)
def mock_redis(monkeypatch):
    """
    Globally mock Redis client so tests don't need a running Redis instance.
    """
    fake_redis = AsyncMock()
    fake_redis.get = AsyncMock(return_value=None)
    fake_redis.set = AsyncMock(return_value=True)
    fake_redis.delete = AsyncMock(return_value=True)
 
    monkeypatch.setattr("src.services.dependencies.redis_client", fake_redis)
    monkeypatch.setattr("src.api.users.redis_client", fake_redis)
    return fake_redis