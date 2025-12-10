# Quickstart Guide: FastAPI REST API

**Feature**: 003-fastapi-rest-api
**Audience**: Developers setting up local development environment
**Time**: 15-20 minutes

## Prerequisites

- Python 3.12+ installed
- UV package manager installed (`pip install uv`)
- Neon PostgreSQL account (or local PostgreSQL)
- Git repository cloned
- better-auth server running (for full authentication flow)

---

## Step 1: Install Dependencies

```bash
# Navigate to project root
cd /path/to/todo-app

# Install production dependencies
uv add fastapi uvicorn sqlalchemy asyncpg alembic slowapi redis pydantic pydantic-settings python-dotenv

# Install development dependencies
uv add --dev pytest pytest-asyncio pytest-cov httpx factory-boy faker pytest-mock ruff mypy
```

---

## Step 2: Configure Environment Variables

Create `.env` file in project root:

```bash
# .env
# Database (Neon PostgreSQL)
DATABASE_URL=postgresql+asyncpg://user:password@host.neon.tech/todo_db?sslmode=require

# Session Authentication (MUST match better-auth server)
SESSION_HASH_SECRET=change-this-to-32-character-secret-key-in-production

# CORS Configuration
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:3000

# SQLAlchemy Pool Settings
SQLALCHEMY_POOL_SIZE=3
SQLALCHEMY_POOL_OVERFLOW=5
SQLALCHEMY_POOL_TIMEOUT=15
SQLALCHEMY_POOL_RECYCLE=1800
SQLALCHEMY_ECHO=true

# Rate Limiting
REDIS_URL=redis://localhost:6379/0

# Application
DEBUG=true
```

**Generate SESSION_HASH_SECRET**:
```bash
openssl rand -hex 32
```

---

## Step 3: Set Up Database Schema

### Initialize Alembic

```bash
# Initialize Alembic (if not already done)
uv run alembic init alembic
```

### Create Initial Migration

```bash
# Generate migration for tasks table
uv run alembic revision --autogenerate -m "Create tasks table"

# Review generated migration in alembic/versions/

# Apply migration to database
uv run alembic upgrade head
```

### Verify Database

```bash
# Connect to your Neon database
psql "postgresql://user:password@host.neon.tech/todo_db?sslmode=require"

# Check tables
\dt

# Expected output:
#  Schema |      Name       | Type  |  Owner
# --------+-----------------+-------+---------
#  public | alembic_version | table | user
#  public | tasks           | table | user
#  public | users           | table | user (auth server)
#  public | user_sessions   | table | user (auth server)

# Check tasks table schema
\d tasks
```

---

## Step 4: Start Redis (for Rate Limiting)

### Using Docker

```bash
docker run -d -p 6379:6379 --name redis-dev redis:7-alpine
```

### Using Homebrew (macOS)

```bash
brew install redis
brew services start redis
```

### Verify Redis

```bash
redis-cli ping
# Expected: PONG
```

---

## Step 5: Run FastAPI Application

### Development Server

```bash
# Start Uvicorn with hot reload
uv run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
✓ Database connection pool initialized
  Pool size: 3
INFO:     Application startup complete.
```

### Test Health Endpoint

```bash
curl http://localhost:8000/health

# Expected:
# {"status":"ok","timestamp":"2025-12-10T12:34:56Z"}
```

---

## Step 6: Interactive API Documentation

Open in browser:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Test endpoints interactively:
1. Click "Authorize" button
2. Enter Bearer token from better-auth
3. Try GET /tasks, POST /tasks, etc.

---

## Step 7: Run Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Run specific test file
uv run pytest tests/integration/test_tasks.py

# Run with verbose output
uv run pytest -v

# Run only integration tests
uv run pytest -m integration
```

**Expected Output**:
```
==================== test session starts ====================
collected 45 items

tests/unit/test_validators.py ......                   [ 13%]
tests/contract/test_api_schemas.py .........            [ 33%]
tests/integration/test_tasks.py ....................    [100%]

==================== 45 passed in 2.34s ====================
```

---

## Step 8: Code Quality Checks

### Linting

```bash
# Run ruff linter
uv run ruff check src tests

# Auto-fix issues
uv run ruff check --fix src tests
```

### Type Checking

```bash
# Run mypy type checker
uv run mypy src
```

### Format Code

```bash
# Format with ruff
uv run ruff format src tests
```

---

## API Usage Examples

### Create Task

```bash
curl -X POST http://localhost:8000/tasks \
  -H "Authorization: Bearer YOUR_SESSION_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries", "description": "Milk, eggs, bread"}'
```

**Response** (201 Created):
```json
{
  "id": 1,
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "created_at": "2025-12-10T12:00:00Z",
  "updated_at": "2025-12-10T12:00:00Z"
}
```

### Get All Tasks

```bash
curl -X GET http://localhost:8000/tasks \
  -H "Authorization: Bearer YOUR_SESSION_TOKEN"
```

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": false,
    "created_at": "2025-12-10T12:00:00Z",
    "updated_at": "2025-12-10T12:00:00Z"
  }
]
```

### Update Task

```bash
curl -X PUT http://localhost:8000/tasks/1 \
  -H "Authorization: Bearer YOUR_SESSION_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'
```

### Delete Task

```bash
curl -X DELETE http://localhost:8000/tasks/1 \
  -H "Authorization: Bearer YOUR_SESSION_TOKEN"
```

**Response** (204 No Content)

---

## Common Issues & Solutions

### Issue: Database Connection Error

```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solution**:
- Verify `DATABASE_URL` in `.env`
- Check Neon PostgreSQL is accessible
- Verify `sslmode=require` parameter
- Test connection with `psql` directly

### Issue: Redis Connection Error

```
redis.exceptions.ConnectionError: Error connecting to Redis
```

**Solution**:
- Start Redis: `docker start redis-dev` or `brew services start redis`
- Verify `REDIS_URL` in `.env`
- Test with `redis-cli ping`

### Issue: 401 Unauthorized on All Endpoints

```json
{
  "type": "authentication_error",
  "title": "Authentication failed",
  "status": 401,
  "detail": "Invalid or missing authentication credentials"
}
```

**Solution**:
- Verify `SESSION_HASH_SECRET` matches better-auth server
- Check session token is valid (not expired)
- Verify token is sent in `Authorization: Bearer <token>` header
- Check `user_sessions` table has valid session records

### Issue: Rate Limit Immediately Triggered

```json
{
  "type": "rate_limit_exceeded",
  "status": 429,
  "detail": "Too many requests"
}
```

**Solution**:
- Clear Redis: `redis-cli FLUSHDB`
- Verify `REDIS_URL` points to correct database
- Check rate limit configuration in code

### Issue: Tests Failing with "Event Loop Closed"

```
RuntimeError: Event loop is closed
```

**Solution**:
- Ensure `pytest.ini` has `asyncio_mode = "auto"`
- Use `@pytest.mark.asyncio` on all async test functions
- Check fixtures use `async def` for async operations

---

## Development Workflow

### Making Schema Changes

1. Update SQLAlchemy model in `src/models/database.py`
2. Generate migration: `uv run alembic revision --autogenerate -m "description"`
3. Review generated migration in `alembic/versions/`
4. Apply migration: `uv run alembic upgrade head`
5. Run tests to verify

### Adding New Endpoint

1. **Write test first** (TDD):
   ```python
   # tests/integration/test_new_feature.py
   @pytest.mark.asyncio
   async def test_new_endpoint(client, authenticated_user):
       response = await client.get("/new-endpoint")
       assert response.status_code == 200
   ```

2. **Run test** (should fail):
   ```bash
   uv run pytest tests/integration/test_new_feature.py
   ```

3. **Implement endpoint**:
   ```python
   # src/api/routers/tasks.py
   @router.get("/new-endpoint")
   async def new_endpoint():
       return {"status": "ok"}
   ```

4. **Run test** (should pass):
   ```bash
   uv run pytest tests/integration/test_new_feature.py
   ```

5. **Refactor** if needed while keeping tests green

---

## Project Structure Reference

```
todo-app/
├── src/
│   ├── api/
│   │   ├── main.py              # FastAPI app
│   │   ├── dependencies.py       # Dependency injection
│   │   ├── routers/
│   │   │   ├── tasks.py         # Task endpoints
│   │   │   └── health.py        # Health check
│   │   ├── middleware/
│   │   │   ├── auth.py          # Session validation
│   │   │   └── rate_limit.py    # Rate limiting
│   │   └── schemas/
│   │       ├── task.py          # Pydantic models
│   │       └── error.py         # Error responses
│   ├── models/
│   │   ├── task.py              # Task dataclass (CLI)
│   │   └── database.py          # SQLAlchemy models
│   ├── services/
│   │   ├── task_service.py      # Business logic
│   │   └── auth_service.py      # Session validation
│   ├── database/
│   │   ├── connection.py        # Async engine
│   │   ├── repository.py        # Task repository
│   │   └── migrations/          # Alembic versions
│   └── cli/                     # Existing CLI (preserved)
├── tests/
│   ├── conftest.py              # Fixtures
│   ├── factories.py             # Test data
│   ├── unit/
│   ├── contract/
│   └── integration/
├── alembic/
│   ├── env.py                   # Alembic config
│   └── versions/                # Migration scripts
├── alembic.ini
├── .env
├── .env.example
└── pyproject.toml
```

---

## Next Steps

1. **Authentication Setup**: Coordinate with better-auth server team to share `SESSION_HASH_SECRET`
2. **Production Deployment**: Configure production environment variables
3. **Monitoring**: Set up logging and error tracking
4. **CI/CD**: Configure GitHub Actions for automated testing
5. **Documentation**: Generate OpenAPI docs for frontend team

---

## Helpful Commands

```bash
# Start development server
uv run uvicorn src.api.main:app --reload

# Run tests with coverage
uv run pytest --cov=src

# Database migrations
uv run alembic revision --autogenerate -m "message"
uv run alembic upgrade head
uv run alembic downgrade -1

# Code quality
uv run ruff check src tests
uv run mypy src
uv run ruff format src tests

# Redis management
redis-cli FLUSHDB        # Clear all rate limit data
redis-cli KEYS "user:*"  # View rate limit keys

# Database console
psql "$DATABASE_URL"
```

---

## Support

- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **OpenAPI Spec**: http://localhost:8000/openapi.json
- **Project Issues**: https://github.com/your-org/todo-app/issues

---

**Quickstart Complete!** 🎉

You now have a fully functional FastAPI REST API with:
- ✅ PostgreSQL persistence (Neon)
- ✅ Session authentication (better-auth integration)
- ✅ Rate limiting (Redis-backed)
- ✅ CORS configuration
- ✅ Error handling
- ✅ Test suite
- ✅ Interactive API docs
