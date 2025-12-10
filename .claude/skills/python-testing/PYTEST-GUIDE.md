# Comprehensive Pytest Guide

## Advanced Pytest Features

### Markers

Mark tests for selective execution:

```python
import pytest

@pytest.mark.slow
def test_slow_operation():
    """Test that takes a long time."""
    ...

@pytest.mark.integration
async def test_database_integration():
    """Integration test requiring database."""
    ...

@pytest.mark.skip(reason="Feature not implemented yet")
def test_future_feature():
    """Test for upcoming feature."""
    ...

@pytest.mark.skipif(sys.version_info < (3, 10), reason="Requires Python 3.10+")
def test_new_python_feature():
    ...

@pytest.mark.xfail(reason="Known bug #123")
def test_known_issue():
    """Test expected to fail."""
    ...
```

**Run specific markers:**
```bash
pytest -m "not slow"           # Skip slow tests
pytest -m "integration"        # Only integration tests
pytest -m "slow or integration"  # Either slow or integration
```

### Custom Markers

```python
# pytest.ini or pyproject.toml
[tool.pytest.ini_options]
markers = [
    "slow: marks tests as slow",
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests",
    "smoke: marks tests as smoke tests"
]
```

## Fixtures Deep Dive

### Fixture Dependencies

```python
@pytest.fixture
def database():
    db = create_database()
    yield db
    db.close()

@pytest.fixture
def user_repository(database):
    """Fixture that depends on database fixture."""
    return UserRepository(database)

@pytest.fixture
def user_service(user_repository):
    """Fixture that depends on user_repository."""
    return UserService(user_repository)

def test_user_creation(user_service):
    """Test using the entire fixture chain."""
    user = user_service.create_user(...)
    assert user.id is not None
```

### Fixture Factories

```python
@pytest.fixture
def user_factory(db_session):
    """Factory fixture for creating multiple users."""
    created_users = []

    async def _create_user(**kwargs):
        defaults = {
            "email": f"user{len(created_users)}@example.com",
            "username": f"user{len(created_users)}",
            "password": "pass123"
        }
        user_data = {**defaults, **kwargs}
        user = await create_user(db_session, user_data)
        created_users.append(user)
        return user

    yield _create_user

    # Cleanup all created users
    for user in created_users:
        await delete_user(db_session, user.id)

# Usage
async def test_multiple_users(user_factory):
    user1 = await user_factory(username="alice")
    user2 = await user_factory(username="bob")
    user3 = await user_factory(email="charlie@example.com")

    assert len([user1, user2, user3]) == 3
```

### Autouse Fixtures

```python
@pytest.fixture(autouse=True)
def reset_database():
    """Automatically run before each test."""
    clear_database()
    yield
    # Cleanup after test
```

### Fixture Finalization

```python
@pytest.fixture
def resource():
    """Fixture with explicit finalization."""
    res = acquire_resource()

    def fin():
        release_resource(res)

    request.addfinalizer(fin)
    return res
```

## Parametrization Advanced

### Parametrize with IDs

```python
@pytest.mark.parametrize(
    "user_data,expected_status",
    [
        ({"email": "valid@example.com", "username": "valid"}, 201),
        ({"email": "invalid", "username": "valid"}, 422),
        ({"email": "valid@example.com", "username": ""}, 422),
    ],
    ids=["valid_data", "invalid_email", "empty_username"]
)
async def test_user_creation(user_data, expected_status, async_client):
    response = await async_client.post("/users/", json=user_data)
    assert response.status_code == expected_status
```

### Parametrize Fixtures

```python
@pytest.fixture(params=[
    {"role": "admin", "permissions": ["read", "write", "delete"]},
    {"role": "user", "permissions": ["read"]},
    {"role": "guest", "permissions": []},
])
def user_with_role(request):
    """Parametrized fixture for different user roles."""
    return create_user(**request.param)

def test_permissions(user_with_role):
    """Test runs once for each role."""
    assert user_with_role.role in ["admin", "user", "guest"]
```

### Combining Parametrizations

```python
@pytest.mark.parametrize("method", ["GET", "POST", "PUT", "DELETE"])
@pytest.mark.parametrize("auth", [True, False])
async def test_endpoint_access(method, auth, async_client):
    """Test each HTTP method with and without auth (8 test cases total)."""
    headers = {"Authorization": "Bearer token"} if auth else {}
    response = await async_client.request(method, "/api/resource", headers=headers)
    # Assert based on method and auth
```

## Mocking Strategies

### Mocking Classes

```python
from unittest.mock import Mock, AsyncMock

def test_service_with_mocked_repository():
    """Test service with fully mocked repository."""
    mock_repo = Mock()
    mock_repo.get_by_id.return_value = User(id=1, name="Test")
    mock_repo.create.return_value = User(id=2, name="New")

    service = UserService(mock_repo)
    user = service.get_user(1)

    assert user.id == 1
    mock_repo.get_by_id.assert_called_once_with(1)
```

### Patching

```python
from unittest.mock import patch

@patch("app.services.user_service.send_email")
async def test_user_registration_sends_email(mock_send_email):
    """Test that user registration sends welcome email."""
    service = UserService(repository)

    await service.register_user(user_data)

    mock_send_email.assert_called_once()
    args = mock_send_email.call_args
    assert "welcome" in args[0][0].lower()  # Email subject contains "welcome"
```

### Mock Return Values

```python
from unittest.mock import AsyncMock

# Simple return value
mock.method.return_value = "result"

# Side effect (different values on each call)
mock.method.side_effect = [1, 2, 3]

# Side effect (exception)
mock.method.side_effect = ValueError("Error message")

# Async mock
async_mock = AsyncMock()
async_mock.method.return_value = "async result"
```

### Spy Pattern

```python
from unittest.mock import patch

def test_function_calls():
    """Verify function is called with correct arguments."""
    with patch("module.function") as mock_function:
        mock_function.return_value = "result"

        # Run code that calls the function
        result = some_operation()

        # Verify calls
        mock_function.assert_called()
        mock_function.assert_called_once()
        mock_function.assert_called_with(arg1, arg2)
        mock_function.assert_called_once_with(arg1, arg2)
        assert mock_function.call_count == 1
```

## Database Testing

### In-Memory SQLite

```python
# conftest.py
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.db.base import Base

@pytest.fixture(scope="function")
async def db_engine():
    """Create in-memory database engine."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()

@pytest.fixture
async def db_session(db_engine):
    """Create database session."""
    async_session = sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session() as session:
        yield session
        await session.rollback()
```

### Transaction Rollback

```python
@pytest.fixture
async def db_session(db_engine):
    """Database session with automatic rollback."""
    connection = await db_engine.connect()
    transaction = await connection.begin()

    async_session = sessionmaker(
        bind=connection,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session() as session:
        yield session

    await transaction.rollback()
    await connection.close()
```

### Test Database Fixtures

```python
@pytest.fixture(scope="session")
async def test_database():
    """Create test database once per session."""
    # Create database
    await create_test_database()

    yield

    # Drop database
    await drop_test_database()

@pytest.fixture
async def clean_db(test_database, db_session):
    """Clean database before each test."""
    # Truncate all tables
    await truncate_all_tables(db_session)
    yield db_session
```

## Async Testing

### pytest-asyncio Configuration

```python
# pytest.ini or pyproject.toml
[tool.pytest.ini_options]
asyncio_mode = "auto"  # Automatically detect async tests
```

### Testing Async Context Managers

```python
@pytest.mark.asyncio
async def test_async_context_manager():
    """Test async context manager."""
    async with AsyncResource() as resource:
        result = await resource.do_something()
        assert result == expected
```

### Testing Async Generators

```python
@pytest.mark.asyncio
async def test_async_generator():
    """Test async generator."""
    items = []
    async for item in async_generator():
        items.append(item)

    assert len(items) == 10
```

### Concurrent Async Tests

```python
import asyncio

@pytest.mark.asyncio
async def test_concurrent_operations():
    """Test multiple async operations running concurrently."""
    results = await asyncio.gather(
        async_operation_1(),
        async_operation_2(),
        async_operation_3()
    )

    assert len(results) == 3
    assert all(result is not None for result in results)
```

## Test Organization

### conftest.py Hierarchy

```
tests/
├── conftest.py              # Root fixtures (database, clients)
├── test_models/
│   ├── conftest.py          # Model-specific fixtures
│   └── test_user.py
├── test_services/
│   ├── conftest.py          # Service-specific fixtures
│   └── test_user_service.py
└── test_endpoints/
    ├── conftest.py          # Endpoint-specific fixtures (auth)
    ├── test_auth.py
    └── test_users.py
```

### Test Classes

```python
class TestUserCRUD:
    """Group related user CRUD tests."""

    @pytest.mark.asyncio
    async def test_create(self, service):
        ...

    @pytest.mark.asyncio
    async def test_read(self, service, sample_user):
        ...

    @pytest.mark.asyncio
    async def test_update(self, service, sample_user):
        ...

    @pytest.mark.asyncio
    async def test_delete(self, service, sample_user):
        ...
```

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.10, 3.11, 3.12]

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-cov

      - name: Run tests
        run: |
          pytest --cov=app --cov-report=xml --cov-report=term

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest
        language: system
        pass_filenames: false
        always_run: true
        args: ["-v", "--tb=short"]
```

## Performance Testing

### Test Execution Time

```python
import time

@pytest.mark.slow
def test_slow_operation():
    """Test that verifies operation completes in reasonable time."""
    start = time.time()

    # Run operation
    result = slow_operation()

    duration = time.time() - start
    assert duration < 5.0, f"Operation took {duration}s (should be < 5s)"
```

### pytest-benchmark

```python
def test_performance(benchmark):
    """Benchmark function performance."""
    result = benchmark(function_to_test, arg1, arg2)
    assert result == expected
```

## Debugging Tests

### Print Debug Output

```bash
# Show print statements
pytest -s

# Show local variables on failure
pytest --showlocals

# Enter debugger on failure
pytest --pdb

# Enter debugger at test start
pytest --trace
```

### Verbose Output

```bash
# Verbose test names
pytest -v

# Very verbose (show all output)
pytest -vv

# Show test durations
pytest --durations=10
```

## Best Practices Summary

### Test Coverage Goals

- **Minimum**: 80% overall coverage
- **Critical paths**: 100% coverage (auth, payments, data integrity)
- **Business logic**: 95%+ coverage
- **Edge cases**: Test all error conditions

### Writing Maintainable Tests

1. **One assertion per test** (or closely related assertions)
2. **Descriptive test names** (explain what and why)
3. **Use fixtures** for setup/teardown
4. **Independent tests** (no test depends on another)
5. **Fast tests** (mock slow operations)
6. **Clear failure messages** (assert with descriptive messages)

### Test Pyramid

```
      /\
     /  \        E2E Tests (Few)
    /----\       Integration Tests (Some)
   /------\      Unit Tests (Many)
  /--------\
```

- **Many unit tests**: Fast, isolated, specific
- **Some integration tests**: Test component interactions
- **Few E2E tests**: Test critical user journeys

### What to Test

✅ **Test:**
- Business logic
- Edge cases and boundaries
- Error handling
- Validation
- Authorization
- Data transformations
- Integration points

❌ **Don't test:**
- Framework internals
- Third-party library code
- Simple getters/setters
- Generated code

## Quick Reference

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific tests
pytest tests/test_users.py
pytest tests/test_users.py::test_create_user
pytest -k "test_user"

# Run marked tests
pytest -m "not slow"
pytest -m "integration"

# Debug
pytest -s --pdb
pytest --tb=short

# Performance
pytest --durations=10

# Parallel execution (requires pytest-xdist)
pytest -n auto
```
