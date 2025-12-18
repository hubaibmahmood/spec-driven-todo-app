"""Pytest configuration and shared fixtures."""

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from typing import AsyncGenerator

from src.api.main import app
from src.models.database import Base
from src.database.connection import get_db


# Test database URL (use PostgreSQL for testing to match production)
# Uses same Neon database but with different schema or separate test database
# Set TEST_DATABASE_URL in .env.test or use same DATABASE_URL from settings
import os
import ssl
from src.config import settings

# Clean the database URL for asyncpg (same as production code)
raw_db_url = os.getenv("TEST_DATABASE_URL", settings.DATABASE_URL)
if "?" in raw_db_url:
    # Remove query parameters that asyncpg doesn't understand
    TEST_DATABASE_URL = raw_db_url.split("?")[0]
else:
    TEST_DATABASE_URL = raw_db_url


def generate_test_user_id() -> str:
    """Generate a test user ID that mimics better-auth cuid format."""
    import secrets
    # Generate a cuid-like string for testing purposes
    return f"test_{secrets.token_hex(8)}"


@pytest_asyncio.fixture(scope="session")
async def async_engine():
    """Create async engine for testing with PostgreSQL.

    Uses the existing database schema (assumes migrations have been run).
    Test isolation is achieved through transaction rollback in db_session fixture.
    """
    # Create SSL context for Neon (same as production code)
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True,
        pool_pre_ping=True,  # Verify connections before using them
        connect_args={
            "ssl": ssl_context,
            "server_settings": {"application_name": "todo-app-tests"},
        },
    )

    yield engine

    # Dispose engine (don't drop tables - preserve database schema)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(async_engine) -> AsyncGenerator[AsyncSession, None]:
    """
    Create a new database session for each test with transaction rollback.

    This ensures test isolation - each test gets a fresh database state.
    Uses the same pattern as the production database connection.
    """
    async_session_maker = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session_maker() as session:
        # Start a transaction
        async with session.begin():
            yield session
            # Transaction will be rolled back automatically if not committed
            await session.rollback()


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
    """Generate a sample user ID string for testing (mimics better-auth cuid format)."""
    return generate_test_user_id()


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


@pytest.fixture
def mock_service_token():
    """Return valid SERVICE_AUTH_TOKEN for testing."""
    # Set the SERVICE_AUTH_TOKEN in settings for tests
    from src.config import settings
    token = "test-service-token-for-testing-purposes"
    settings.SERVICE_AUTH_TOKEN = token
    return token


@pytest.fixture
def test_service_auth_headers(mock_service_token, sample_user_id):
    """Return headers for service authentication testing."""
    return {
        "Authorization": f"Bearer {mock_service_token}",
        "X-User-ID": sample_user_id,
    }


@pytest.fixture
def test_user_context(sample_user_id):
    """Create test user context data."""
    return {
        "user_id": sample_user_id,
        "session_id": "test-session-123",
    }
