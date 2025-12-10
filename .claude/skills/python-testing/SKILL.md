---
name: python-testing
description: Comprehensive Python testing with pytest, including unit tests, integration tests, async testing, fixtures, parametrization, mocking, and coverage analysis. Use when writing tests, improving test coverage, setting up test infrastructure, or debugging test failures.
allowed-tools: Read, Edit, Bash, Glob, Grep
---

# Python Testing with Pytest

## Overview

This skill provides comprehensive guidance for writing professional-grade Python tests using pytest, with special focus on FastAPI async testing, fixtures, parametrization, mocking, and achieving high test coverage.

## When to Use

- Writing unit tests for functions and classes
- Creating integration tests for API endpoints
- Setting up test fixtures and test data
- Implementing parametrized tests
- Mocking external dependencies
- Testing async functions
- Improving test coverage
- Debugging failing tests
- Setting up CI/CD test pipelines

## Testing Principles

### 1. Arrange-Act-Assert (AAA) Pattern

```python
def test_user_creation():
    # Arrange: Set up test data
    user_data = {"email": "test@example.com", "username": "testuser"}

    # Act: Execute the code being tested
    user = create_user(user_data)

    # Assert: Verify the results
    assert user.email == "test@example.com"
    assert user.username == "testuser"
    assert user.id is not None
```

### 2. Test Organization

```
tests/
├── conftest.py              # Shared fixtures
├── __init__.py
├── test_models/             # Model tests
│   ├── __init__.py
│   └── test_user.py
├── test_services/           # Service tests
│   ├── __init__.py
│   └── test_user_service.py
├── test_repositories/       # Repository tests
│   ├── __init__.py
│   └── test_user_repository.py
└── test_endpoints/          # API endpoint tests
    ├── __init__.py
    ├── test_auth.py
    └── test_users.py
```

### 3. Test Naming Conventions

```python
# Good: Descriptive names that explain what's being tested
def test_create_user_with_valid_data_returns_user():
    ...

def test_get_user_with_invalid_id_raises_not_found():
    ...

def test_update_user_without_permission_raises_forbidden():
    ...

# Bad: Vague or unclear names
def test_user():
    ...

def test_1():
    ...
```

## Pytest Basics

### Installing Pytest

```bash
pip install pytest pytest-asyncio pytest-cov httpx
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific file
pytest tests/test_users.py

# Run specific test
pytest tests/test_users.py::test_create_user

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=app tests/

# Run and stop at first failure
pytest -x

# Run failed tests from last run
pytest --lf

# Run tests matching pattern
pytest -k "test_user"
```

## Fixtures

### Basic Fixtures

```python
# conftest.py
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture
def sample_user_data():
    """Provide sample user data."""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "SecurePass123!"
    }

@pytest.fixture
async def db_session():
    """Provide database session for tests."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session
```

### Fixture Scopes

```python
@pytest.fixture(scope="function")  # Default: new instance per test
def function_fixture():
    return {}

@pytest.fixture(scope="class")  # Shared within test class
def class_fixture():
    return {}

@pytest.fixture(scope="module")  # Shared within module
def module_fixture():
    return {}

@pytest.fixture(scope="session")  # Shared across entire test session
def session_fixture():
    return {}
```

### Fixture Cleanup

```python
@pytest.fixture
async def database():
    """Database fixture with cleanup."""
    # Setup
    db = await create_database()

    yield db

    # Teardown (runs after test)
    await db.close()
    await cleanup_database()
```

## FastAPI Testing

### Test Client Setup

```python
# conftest.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.fixture
async def async_client():
    """Async HTTP client for testing FastAPI."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
```

### Testing Endpoints

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_user(async_client: AsyncClient):
    """Test user creation endpoint."""
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "SecurePass123!"
    }

    response = await async_client.post("/api/v1/users/", json=user_data)

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["username"] == user_data["username"]
    assert "id" in data
    assert "password" not in data  # Password should not be in response

@pytest.mark.asyncio
async def test_get_user(async_client: AsyncClient):
    """Test getting a user by ID."""
    # First create a user
    user_data = {"email": "test@example.com", "username": "testuser", "password": "pass"}
    create_response = await async_client.post("/api/v1/users/", json=user_data)
    user_id = create_response.json()["id"]

    # Then get the user
    response = await async_client.get(f"/api/v1/users/{user_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    assert data["email"] == user_data["email"]

@pytest.mark.asyncio
async def test_get_nonexistent_user(async_client: AsyncClient):
    """Test getting a non-existent user returns 404."""
    response = await async_client.get("/api/v1/users/99999")

    assert response.status_code == 404
    data = response.json()
    assert "error" in data or "detail" in data
```

## Async Testing

### Testing Async Functions

```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    """Test an async function."""
    result = await some_async_function()
    assert result == expected_value

@pytest.mark.asyncio
async def test_async_repository(db_session):
    """Test async repository methods."""
    repository = UserRepository(db_session)

    user = await repository.create(user_data)
    assert user.id is not None

    found_user = await repository.get_by_id(user.id)
    assert found_user.email == user.email
```

### Async Fixtures

```python
@pytest.fixture
async def sample_user(db_session):
    """Create a sample user in the database."""
    repository = UserRepository(db_session)
    user_data = UserCreate(
        email="test@example.com",
        username="testuser",
        password="SecurePass123!"
    )
    user = await repository.create(user_data)
    return user
```

## Parametrized Tests

### Basic Parametrization

```python
import pytest

@pytest.mark.parametrize("input_value,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
    (4, 8),
])
def test_double(input_value, expected):
    """Test doubling function with multiple inputs."""
    assert double(input_value) == expected
```

### Multiple Parameters

```python
@pytest.mark.parametrize("email,username,should_pass", [
    ("valid@example.com", "validuser", True),
    ("invalid-email", "validuser", False),
    ("valid@example.com", "ab", False),  # username too short
    ("valid@example.com", "", False),  # empty username
])
async def test_user_validation(email, username, should_pass):
    """Test user validation with various inputs."""
    user_data = {"email": email, "username": username, "password": "pass123"}

    if should_pass:
        user = UserCreate(**user_data)
        assert user.email == email
    else:
        with pytest.raises(ValidationError):
            UserCreate(**user_data)
```

### Parametrized Fixtures

```python
@pytest.fixture(params=["sqlite", "postgresql", "mysql"])
def database_url(request):
    """Test with multiple database types."""
    return {
        "sqlite": "sqlite:///./test.db",
        "postgresql": "postgresql://localhost/test",
        "mysql": "mysql://localhost/test"
    }[request.param]
```

## Mocking and Patching

### Mocking External APIs

```python
from unittest.mock import AsyncMock, patch
import pytest

@pytest.mark.asyncio
@patch("app.services.external_api.fetch_data")
async def test_service_with_mocked_api(mock_fetch):
    """Test service that calls external API."""
    # Setup mock
    mock_fetch.return_value = {"data": "mocked_value"}

    # Test
    service = MyService()
    result = await service.process_data()

    # Verify
    assert result == "processed_mocked_value"
    mock_fetch.assert_called_once()
```

### Mocking Database

```python
@pytest.mark.asyncio
async def test_service_with_mocked_repository():
    """Test service with mocked repository."""
    # Create mock repository
    mock_repo = AsyncMock()
    mock_repo.get_by_id.return_value = User(
        id=1,
        email="test@example.com",
        username="testuser"
    )

    # Test service with mocked repository
    service = UserService(mock_repo)
    user = await service.get_user(1)

    assert user.id == 1
    mock_repo.get_by_id.assert_called_once_with(1)
```

### Mocking Dependencies

```python
from fastapi import Depends

def mock_get_current_user():
    """Mock authentication dependency."""
    return {"id": 1, "username": "testuser"}

async def test_protected_endpoint(async_client):
    """Test endpoint with mocked auth."""
    app.dependency_overrides[get_current_user] = mock_get_current_user

    response = await async_client.get("/api/v1/profile")

    assert response.status_code == 200

    # Clean up
    app.dependency_overrides.clear()
```

## Exception Testing

### Testing Expected Exceptions

```python
import pytest
from fastapi import HTTPException

@pytest.mark.asyncio
async def test_get_nonexistent_user_raises_exception():
    """Test that getting non-existent user raises exception."""
    service = UserService(repository)

    with pytest.raises(HTTPException) as exc_info:
        await service.get_user(99999)

    assert exc_info.value.status_code == 404
    assert "not found" in str(exc_info.value.detail).lower()
```

### Testing Validation Errors

```python
from pydantic import ValidationError

def test_invalid_email_raises_validation_error():
    """Test that invalid email raises validation error."""
    with pytest.raises(ValidationError) as exc_info:
        UserCreate(
            email="invalid-email",
            username="testuser",
            password="pass123"
        )

    errors = exc_info.value.errors()
    assert any(error["loc"] == ("email",) for error in errors)
```

## Test Coverage

### Running Coverage

```bash
# Run tests with coverage
pytest --cov=app tests/

# Generate HTML coverage report
pytest --cov=app --cov-report=html tests/

# Show missing lines
pytest --cov=app --cov-report=term-missing tests/

# Fail if coverage below threshold
pytest --cov=app --cov-fail-under=80 tests/
```

### Coverage Configuration

```ini
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"
addopts = "--cov=app --cov-report=term-missing --cov-report=html"

[tool.coverage.run]
source = ["app"]
omit = [
    "*/tests/*",
    "*/migrations/*",
    "*/__init__.py"
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
]
```

## Testing Best Practices

### 1. Independent Tests

```python
# ✅ Good: Each test is independent
@pytest.mark.asyncio
async def test_create_user(async_client):
    user_data = {"email": "test1@example.com", ...}
    response = await async_client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 201

@pytest.mark.asyncio
async def test_get_user(async_client, sample_user):
    response = await async_client.get(f"/api/v1/users/{sample_user.id}")
    assert response.status_code == 200

# ❌ Bad: Tests depend on each other
user_id = None

def test_create_user_and_save_id():
    global user_id
    ...
    user_id = response.json()["id"]

def test_get_user_using_saved_id():
    response = client.get(f"/users/{user_id}")  # Depends on previous test
```

### 2. Clear Assertions

```python
# ✅ Good: Specific assertions with messages
assert response.status_code == 201, f"Expected 201, got {response.status_code}"
assert user.email == expected_email, f"Email mismatch: {user.email} != {expected_email}"

# ❌ Bad: Vague assertions
assert response
assert data
```

### 3. Test One Thing

```python
# ✅ Good: Each test focuses on one behavior
def test_user_email_validation():
    with pytest.raises(ValidationError):
        UserCreate(email="invalid", username="test", password="pass")

def test_user_username_length():
    with pytest.raises(ValidationError):
        UserCreate(email="test@example.com", username="ab", password="pass")

# ❌ Bad: Testing multiple things
def test_user_validation():
    # Tests email AND username AND password...
    ...
```

### 4. Use Fixtures for Setup

```python
# ✅ Good: Use fixtures for common setup
@pytest.fixture
async def authenticated_client(async_client, sample_user):
    token = generate_token(sample_user)
    async_client.headers = {"Authorization": f"Bearer {token}"}
    return async_client

@pytest.mark.asyncio
async def test_protected_endpoint(authenticated_client):
    response = await authenticated_client.get("/api/v1/profile")
    assert response.status_code == 200

# ❌ Bad: Duplicate setup in every test
async def test_protected_endpoint(async_client):
    user = await create_user(...)
    token = generate_token(user)
    async_client.headers = {"Authorization": f"Bearer {token}"}
    ...
```

## Testing Checklist

When writing tests, ensure you cover:

- [ ] **Happy path**: Valid inputs produce expected outputs
- [ ] **Edge cases**: Boundary values, empty inputs, None values
- [ ] **Error cases**: Invalid inputs raise appropriate exceptions
- [ ] **Authorization**: Users can only access/modify their own resources
- [ ] **Validation**: Pydantic validation works correctly
- [ ] **Database operations**: CRUD operations work as expected
- [ ] **Async behavior**: Async functions execute correctly
- [ ] **Side effects**: Background tasks, emails, external API calls
- [ ] **Performance**: Response times are acceptable
- [ ] **Idempotency**: Operations can be safely retried

## Reference

For advanced pytest features and patterns, see:
- [PYTEST-GUIDE.md](PYTEST-GUIDE.md) - Comprehensive pytest reference
- [scripts/run-tests.sh](scripts/run-tests.sh) - Test runner script

## Quick Examples

### Complete Test File Structure

```python
# tests/test_users.py
import pytest
from httpx import AsyncClient
from app.schemas.user import UserCreate

@pytest.mark.asyncio
class TestUserEndpoints:
    """Test suite for user endpoints."""

    async def test_create_user(self, async_client: AsyncClient):
        """Test user creation."""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "SecurePass123!"
        }

        response = await async_client.post("/api/v1/users/", json=user_data)

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == user_data["email"]

    async def test_list_users(self, async_client: AsyncClient, sample_user):
        """Test listing users."""
        response = await async_client.get("/api/v1/users/")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    async def test_get_user(self, async_client: AsyncClient, sample_user):
        """Test getting a specific user."""
        response = await async_client.get(f"/api/v1/users/{sample_user.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_user.id
```

Use this skill whenever you need to write or improve tests for your FastAPI application!
