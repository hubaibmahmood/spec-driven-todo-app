"""Pytest configuration and shared fixtures."""

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from typing import AsyncGenerator
from uuid import uuid4

from src.api.main import app
from src.models.database import Base
from src.database.connection import get_db


# Test database URL (use SQLite for testing)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="session")
async def async_engine():
    """Create async engine for testing."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True,
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Drop all tables and dispose engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(async_engine) -> AsyncGenerator[AsyncSession, None]:
    """
    Create a new database session for each test with transaction rollback.

    This ensures test isolation - each test gets a fresh database state.
    """
    async_session_maker = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session_maker() as session:
        yield session
        # Rollback any pending transactions
        await session.rollback()
        await session.close()


@pytest_asyncio.fixture
async def test_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Create async HTTP client for testing with dependency overrides.

    Overrides the get_db dependency to use the test database session.
    """
    from fastapi.testclient import TestClient

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    # Use httpx.ASGITransport for FastAPI app testing
    from httpx import ASGITransport
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

    # Clean up dependency overrides
    app.dependency_overrides.clear()


@pytest.fixture
def sample_user_id():
    """Generate a sample user UUID for testing."""
    return uuid4()


@pytest.fixture
def sample_task_data():
    """Sample task data for testing."""
    return {
        "title": "Test Task",
        "description": "Test Description"
    }


@pytest.fixture
def sample_tasks_data():
    """Multiple sample tasks for testing."""
    return [
        {"title": "Task 1", "description": "Description 1"},
        {"title": "Task 2", "description": "Description 2"},
        {"title": "Task 3", "description": None},
    ]
