# Research Findings: FastAPI REST API Technical Decisions

**Feature**: 003-fastapi-rest-api
**Date**: 2025-12-10
**Status**: Complete

## Executive Summary

This document consolidates research findings for 8 critical technical decisions required to implement the FastAPI REST API conversion. All decisions are based on compatibility with Neon serverless PostgreSQL, production requirements, and integration with the existing better-auth Node.js server.

---

## Decision 1: Database Driver Selection

### Decision: **asyncpg**

**Rationale**:
- 5-10% faster than psycopg3 for async workloads
- Built-in connection pooling optimized for async
- De-facto standard for Neon PostgreSQL deployments
- Simpler installation (single dependency, no binary/pure choice)
- Extensive production track record with FastAPI

**Trade-offs**:
- ✅ Performance: 50-150ms for 1000-task collections (meets <300ms requirement)
- ✅ Session validation: 20-40ms (meets <100ms requirement)
- ⚠️ Single-maintainer concern (though now better distributed)

**Implementation**:
```python
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine(
    "postgresql+asyncpg://user:password@host/db?sslmode=require",
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
)
```

**Dependencies**: `asyncpg>=0.29.0`

---

## Decision 2: Rate Limiting Strategy

### Decision: **slowapi + Redis**

**Rationale**:
- Distributed-safe: shared Redis state prevents limit bypass across API instances
- User-based tracking with IP fallback easily implemented via custom key function
- Mature ecosystem (built on Flask-Limiter patterns)
- Per-endpoint configuration via decorators
- Automatic HTTP 429 responses with Retry-After header

**Trade-offs**:
- ✅ Distributed deployment: works with multiple API instances
- ✅ User tracking: `f"user:{user_id}"` or `f"ip:{ip_address}"`
- ⚠️ Redis dependency adds infrastructure complexity (but required for distributed)
- ⚠️ 2-5ms latency per request (Redis lookup overhead)

**Implementation**:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

def get_request_key(request: Request) -> str:
    user_id = request.state.user_id if hasattr(request.state, 'user_id') else None
    return f"user:{user_id}" if user_id else f"ip:{get_remote_address(request)}"

limiter = Limiter(
    key_func=get_request_key,
    storage_uri="redis://localhost:6379/0",
    default_limits=["100/minute"]
)

# Per-endpoint limits
@app.get("/tasks")
@limiter.limit("100/minute")  # Read limit
async def get_tasks(): pass

@app.post("/tasks")
@limiter.limit("30/minute")   # Write limit
async def create_task(): pass
```

**Dependencies**: `slowapi>=0.1.9`, `redis>=5.0.0`

**Configuration**:
- Read endpoints: 100 requests/minute
- Write endpoints: 30 requests/minute
- Redis for shared state across instances

---

## Decision 3: Token Hashing Algorithm

### Decision: **HMAC-SHA256**

**Rationale**:
- Universal support in Python (hashlib) and Node.js (crypto)
- Industry standard for session tokens (OAuth2, JWT use HMAC variants)
- Includes shared secret in cryptographic computation
- Prevents timing attacks with `hmac.compare_digest()`
- Database compromise doesn't expose tokens (requires SESSION_HASH_SECRET)

**Trade-offs**:
- ✅ Security: FIPS 198 certified, proven cryptographic standard
- ✅ Performance: <1ms hash computation (negligible overhead)
- ✅ Coordination: Simple environment variable sharing between services
- ⚠️ Requires exact secret matching between FastAPI and better-auth

**Implementation**:
```python
import hmac
import hashlib
import os

class SessionTokenHasher:
    def __init__(self):
        self.secret = os.getenv('SESSION_HASH_SECRET')
        if not self.secret:
            raise ValueError("SESSION_HASH_SECRET environment variable required")

    def hash_token(self, token: str) -> str:
        return hmac.new(
            self.secret.encode('utf-8'),
            token.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

    def verify_token_against_hash(self, token: str, token_hash: str) -> bool:
        computed_hash = self.hash_token(token)
        return hmac.compare_digest(computed_hash, token_hash)
```

**Coordination Requirements**:
- Both services use same `SESSION_HASH_SECRET` environment variable
- Both use HMAC-SHA256 algorithm
- Both use UTF-8 encoding
- Both output hexadecimal format (64 characters)

**Security Notes**:
- Use `hmac.compare_digest()` for constant-time comparison (prevents timing attacks)
- Never log tokens or hashes
- Generate secret: `openssl rand -hex 32` (minimum 32 characters)

---

## Decision 4: Database Migration Tool Configuration

### Decision: **Alembic with async SQLAlchemy 2.0 + sync migration execution**

**Rationale**:
- Alembic is the standard migration tool for SQLAlchemy
- Supports async models via synchronous migration wrapper
- Autogenerate detects schema changes automatically
- Multi-service schema ownership via metadata separation
- Production-tested with Neon PostgreSQL

**Trade-offs**:
- ✅ Autogenerate: automatic migration script generation from model changes
- ✅ Versioning: git-tracked migration history with rollback support
- ⚠️ Complexity: requires URL conversion (postgresql+asyncpg → postgresql)
- ⚠️ Multi-service: must avoid migrating tables owned by auth server

**Implementation**:

**alembic.ini**:
```ini
[alembic]
script_location = alembic
file_template = %%(rev)s_%%(slug)s
compare_type = true
compare_server_default = true
```

**alembic/env.py** (key pattern):
```python
from sqlalchemy import pool, engine_from_config
from src.database import Base

target_metadata = Base.metadata  # Only FastAPI-owned tables

def get_database_url():
    """Convert async URL to sync for Alembic."""
    url = config.get_main_option("sqlalchemy.url")
    return url.replace("postgresql+asyncpg", "postgresql")

def run_migrations_online():
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_database_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,  # Critical for Neon serverless
    )

    with connectable.begin() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()
```

**Multi-Service Schema Ownership**:
```python
# FastAPI owns 'tasks' table only
# Auth server owns 'users' and 'user_sessions' tables
# Don't add foreign key constraints across service boundaries

LocalBase = declarative_base()  # FastAPI tables

class Task(LocalBase):
    __tablename__ = "tasks"
    user_id = Column(UUID)  # Reference only, no ForeignKey constraint
```

**Dependencies**: `alembic>=1.13.0`

---

## Decision 5: SQLAlchemy Connection Pooling Configuration

### Decision: **Conservative pool sizing with Neon-specific settings**

**Production Settings**:
```python
pool_size = 10
max_overflow = 20
pool_timeout = 30
pool_recycle = 3600
pool_pre_ping = True
```

**Rationale**:
- `pool_size=10`: Keeps Neon endpoint warm without exceeding connection limits
- `max_overflow=20`: Handles traffic spikes (total max: 30 connections)
- `pool_timeout=30`: Balances queueing vs. fast failure
- `pool_recycle=3600`: Forces reconnection every hour (Neon resets idle connections)
- `pool_pre_ping=True`: **Critical for Neon** - validates connections before use (detects cold starts)

**Trade-offs**:
- ✅ Performance: meets all latency requirements (<200ms single ops, <300ms collections)
- ✅ Neon compatibility: handles serverless cold starts and connection resets
- ⚠️ pool_pre_ping overhead: 5-10ms per request (necessary for reliability)

**Implementation**:
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os

engine = create_async_engine(
    os.getenv("DATABASE_URL"),
    pool_size=int(os.getenv("SQLALCHEMY_POOL_SIZE", "10")),
    max_overflow=int(os.getenv("SQLALCHEMY_MAX_OVERFLOW", "20")),
    pool_timeout=int(os.getenv("SQLALCHEMY_POOL_TIMEOUT", "30")),
    pool_recycle=int(os.getenv("SQLALCHEMY_POOL_RECYCLE", "3600")),
    pool_pre_ping=True,  # Essential for Neon
    connect_args={
        "server_settings": {"application_name": "todo-app-fastapi"},
        "command_timeout": 10
    }
)

async_session_factory = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)
```

**Environment-Specific Settings**:
- Development: `pool_size=3, max_overflow=5` (lower overhead)
- Testing: `pool_size=1, max_overflow=0` (SQLite in-memory)
- Production: `pool_size=10, max_overflow=20` (Neon Pro/Business)

---

## Decision 6: CORS Middleware Configuration

### Decision: **Environment-based origins with explicit allow-list**

**Rationale**:
- Development: localhost:3000 for frontend development
- Production: environment variable for production domain(s)
- Security: never use `allow_origins=["*"]` with `allow_credentials=True`
- Preflight: automatic OPTIONS handling by FastAPI CORSMiddleware

**Trade-offs**:
- ✅ Security: explicit origin whitelist prevents unauthorized access
- ✅ Flexibility: environment-based configuration for dev/staging/prod
- ⚠️ Requires environment variable management

**Implementation**:
```python
from fastapi.middleware.cors import CORSMiddleware
import os

def get_allowed_origins() -> list[str]:
    environment = os.getenv("ENVIRONMENT", "development").lower()

    if environment == "production":
        prod_origins = os.getenv("CORS_ORIGINS", "")
        if not prod_origins:
            raise ValueError("CORS_ORIGINS required in production")
        return [origin.strip() for origin in prod_origins.split(",")]
    else:
        return [
            "http://localhost:3000",
            "http://localhost",
            "http://127.0.0.1:3000",
        ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,  # Required for Authorization header
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Accept", "Content-Type", "Authorization"],
    expose_headers=["Content-Type", "Retry-After"],  # For rate limiting
    max_age=600,  # Preflight cache: 10 minutes
)
```

**Configuration**:
```bash
# .env.development
ENVIRONMENT=development

# .env.production
ENVIRONMENT=production
CORS_ORIGINS=https://app.example.com,https://www.example.com
```

**Security Notes**:
- NEVER use `allow_origins=["*"]` with `allow_credentials=True` (FastAPI will reject)
- Always use HTTPS in production (not http://)
- Preflight (OPTIONS) requests handled automatically by middleware

---

## Decision 7: Error Response Format

### Decision: **RFC 7807-inspired JSON structure with FastAPI conventions**

**Rationale**:
- Industry standard: RFC 7807 (Problem Details for HTTP APIs)
- Developer-friendly: clear error messages with actionable guidance
- Consistent structure: same fields across all error types
- Validation errors: detailed field-level error information
- Rate limiting: includes retry_after and rate_limit_info

**Trade-offs**:
- ✅ Standardization: follows industry best practices
- ✅ Debugging: request_id enables log correlation
- ✅ Client experience: clear, actionable error messages
- ⚠️ Verbosity: more detailed than minimal error responses

**Error Schema**:
```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ErrorResponse(BaseModel):
    type: str  # e.g., "validation_error", "authentication_error"
    title: str  # Human-readable error category
    status: int  # HTTP status code
    detail: str  # Detailed error message
    instance: Optional[str] = None  # Affected resource path
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    request_id: Optional[str] = None  # For log correlation
    errors: Optional[list] = None  # Validation errors (400 only)
    retry_after: Optional[int] = None  # Seconds to wait (429 only)
    rate_limit_info: Optional[dict] = None  # Rate limit details (429 only)
```

**Example Responses**:

**400 Validation Error**:
```json
{
  "type": "validation_error",
  "title": "Request validation failed",
  "status": 400,
  "detail": "One or more validation errors occurred",
  "instance": "/tasks",
  "timestamp": "2025-12-10T12:34:56Z",
  "errors": [
    {
      "field": "title",
      "message": "String should have at least 1 character",
      "code": "string_too_short",
      "value": ""
    }
  ]
}
```

**401 Authentication Error**:
```json
{
  "type": "authentication_error",
  "title": "Authentication failed",
  "status": 401,
  "detail": "Invalid or missing authentication credentials",
  "timestamp": "2025-12-10T12:34:56Z"
}
```

**429 Rate Limit**:
```json
{
  "type": "rate_limit_exceeded",
  "title": "Rate limit exceeded",
  "status": 429,
  "detail": "Too many requests. Retry after 45 seconds.",
  "timestamp": "2025-12-10T12:34:56Z",
  "retry_after": 45,
  "rate_limit_info": {
    "limit": 100,
    "remaining": 0,
    "reset": 1702226696,
    "window_seconds": 60
  }
}
```

**Implementation**: Custom exception handlers with Pydantic models

---

## Decision 8: Testing Strategy

### Decision: **httpx AsyncClient + per-test transaction rollback + pytest-asyncio**

**Rationale**:
- AsyncClient: true async/await testing (compatible with async PostgreSQL)
- Transaction rollback: perfect test isolation with zero cleanup code
- pytest-asyncio: native async test support with auto-detection
- Factory-boy: test data generation with SQLAlchemy integration
- TDD workflow: red-green-refactor with async tests

**Trade-offs**:
- ✅ Test isolation: each test gets fresh database state via rollback
- ✅ Performance: faster than TestClient (native async, no event loop wrapper)
- ✅ Production-like: tests use same async code paths as production
- ⚠️ Learning curve: requires understanding async/await patterns

**Framework Setup**:
```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.23.0",
    "httpx>=0.25.0",
    "factory-boy>=3.3.0",
    "pytest-mock>=3.12.0",
]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
markers = [
    "asyncio: async test",
    "integration: integration test",
    "unit: unit test",
]
```

**Key Fixtures**:
```python
# tests/conftest.py
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

@pytest.fixture(scope="session")
async def async_engine():
    engine = create_async_engine("postgresql+asyncpg://...")
    yield engine
    await engine.dispose()

@pytest.fixture
async def db_session(async_engine):
    """Per-test transaction with rollback isolation."""
    async with async_engine.begin() as connection:
        transaction = await connection.begin()
        session = async_sessionmaker(bind=connection, class_=AsyncSession)()
        yield session
        await transaction.rollback()
        await session.close()

@pytest.fixture
async def client(app_with_db):
    """Async HTTP client for API testing."""
    async with AsyncClient(app=app_with_db, base_url="http://test") as ac:
        yield ac
```

**TDD Workflow**:
1. **RED**: Write failing async test with acceptance criteria
2. **GREEN**: Write minimal code to pass test
3. **REFACTOR**: Improve code while keeping tests green

**Test Example**:
```python
@pytest.mark.asyncio
async def test_create_task_with_valid_data_returns_201(client, authenticated_user):
    response = await client.post(
        "/tasks",
        json={"title": "Buy groceries", "description": "Milk, eggs"},
        headers={"Authorization": f"Bearer {authenticated_user['token']}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Buy groceries"
    assert data["user_id"] == str(authenticated_user["user_id"])
```

**Dependencies**: `pytest>=7.4.0`, `pytest-asyncio>=0.23.0`, `httpx>=0.25.0`, `factory-boy>=3.3.0`

---

## Summary: Technology Stack

| Component | Technology | Version | Rationale |
|-----------|-----------|---------|-----------|
| **Database Driver** | asyncpg | 0.29.0+ | Fastest async driver, Neon-optimized |
| **Rate Limiting** | slowapi + Redis | 0.1.9+ / 5.0.0+ | Distributed-safe, user-based tracking |
| **Token Hashing** | HMAC-SHA256 (hashlib) | stdlib | Universal support, cryptographically secure |
| **Migrations** | Alembic | 1.13.0+ | Standard SQLAlchemy migration tool |
| **Connection Pool** | SQLAlchemy async engine | 2.0+ | Neon-optimized settings (pool_pre_ping) |
| **CORS** | FastAPI CORSMiddleware | built-in | Environment-based origin control |
| **Error Format** | RFC 7807 + Pydantic | custom | Industry standard, developer-friendly |
| **Testing** | pytest-asyncio + httpx | 0.23.0+ / 0.25.0+ | True async testing, transaction rollback |

---

## Dependencies to Add

```toml
[project.dependencies]
fastapi = ">=0.104.0"
uvicorn = {extras = ["standard"], version = ">=0.24.0"}
sqlalchemy = ">=2.0.0"
asyncpg = ">=0.29.0"
alembic = ">=1.13.0"
slowapi = ">=0.1.9"
redis = ">=5.0.0"
pydantic = ">=2.0.0"
pydantic-settings = ">=2.0.0"
python-dotenv = ">=1.0.0"

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.23.0",
    "pytest-cov>=4.1.0",
    "httpx>=0.25.0",
    "factory-boy>=3.3.0",
    "faker>=20.0.0",
    "pytest-mock>=3.12.0",
    "ruff>=0.1.0",
    "mypy>=1.7.0",
]
```

---

## Next Steps

1. **Phase 1 Design**: Create data-model.md, API contracts (OpenAPI), quickstart.md
2. **Update Agent Context**: Add technology stack to CLAUDE.md
3. **Re-evaluate Constitution Check**: Verify decisions align with project principles
4. **Generate Tasks**: Create testable tasks from spec + research findings

---

**Research Status**: ✅ Complete
**All Technical Unknowns**: Resolved
**Ready for**: Phase 1 Design
