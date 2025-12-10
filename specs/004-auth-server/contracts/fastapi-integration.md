# FastAPI Integration Contract

**Feature**: 004-auth-server
**Phase**: 1 (Design & Contracts)
**Date**: 2025-12-10

## Overview

This document defines the contract between the better-auth Node.js authentication server and the FastAPI backend application. It specifies how FastAPI validates session tokens, extracts user information, and protects endpoints.

---

## Integration Architecture

```
┌──────────────┐
│   Frontend   │
│   (Browser)  │
└──────┬───────┘
       │
       │ 1. POST /api/auth/signin
       │    (email, password)
       ▼
┌─────────────────────┐
│   Auth Server       │
│   (Node.js/Express) │
│   Port: 3000        │
└──────┬──────────────┘
       │
       │ 2. Set-Cookie: better-auth.session_token
       │    Returns: { user, session }
       │
       ▼
┌──────────────┐
│   Frontend   │ 3. Extract session.token from response
└──────┬───────┘
       │
       │ 4. GET /api/todos
       │    Authorization: Bearer <token>
       ▼
┌─────────────────────┐
│   API Server        │
│   (FastAPI/Python)  │
│   Port: 8000        │
└──────┬──────────────┘
       │
       │ 5. Query database:
       │    SELECT user FROM user_sessions WHERE token = <token>
       ▼
┌─────────────────────┐
│   PostgreSQL        │
│   (Neon Serverless) │
└─────────────────────┘
```

---

## Token Flow

### 1. Authentication (Auth Server)

**Endpoint**: `POST /api/auth/signin`

**Request**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Response** (Status 200):
```json
{
  "user": {
    "id": "clh1234567890",
    "email": "user@example.com",
    "emailVerified": true,
    "name": "John Doe"
  },
  "session": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expiresAt": "2025-01-17T12:00:00Z"
  }
}
```

**Cookies Set**:
```
Set-Cookie: better-auth.session_token=eyJhbGc...; HttpOnly; Secure; SameSite=None; Path=/; Max-Age=604800
```

---

### 2. Frontend Token Extraction

**Frontend extracts token** from response body (NOT from cookie):

```typescript
// Frontend (React/Next.js example)
const response = await fetch('https://auth.yourdomain.com/api/auth/signin', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email, password }),
  credentials: 'include',  // ⚠️ Required to receive cookies
});

const { user, session } = await response.json();
const token = session.token;  // Extract token from response body

// Store token in localStorage or memory
localStorage.setItem('authToken', token);
```

---

### 3. API Requests to FastAPI

**Frontend sends token in Authorization header**:

```typescript
const response = await fetch('https://api.yourdomain.com/api/todos', {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${token}`,  // ⚠️ Bearer scheme required
    'Content-Type': 'application/json',
  },
});
```

**Important**:
- **Do NOT** use cookies for FastAPI requests
- **Use** `Authorization: Bearer <token>` header
- FastAPI extracts token from header, not cookies

---

### 4. Token Validation in FastAPI

#### 4.1 Dependency Function

**File**: `backend/src/auth/dependencies.py`

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from typing import Optional

from src.database.connection import get_db
from src.auth.models import User, Session as UserSession

# Security scheme for extracting Bearer token
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Dependency to validate session token and retrieve current user.

    **FR-004c**: Extract and validate token from Authorization header

    Args:
        credentials: HTTP Bearer token from Authorization header
        db: Async database session

    Returns:
        User: Authenticated user object

    Raises:
        HTTPException 401: If token is invalid, expired, or user not found
    """
    token = credentials.credentials  # Extract token from "Bearer <token>"

    # Query database for session
    stmt = (
        select(UserSession, User)
        .join(User, UserSession.user_id == User.id)
        .where(UserSession.token == token)
        .where(UserSession.expires_at > datetime.utcnow())
    )

    result = await db.execute(stmt)
    row = result.one_or_none()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    session, user = row

    # Optional: Check if email is verified (FR-001)
    if not user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email verification required",
        )

    return user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    Dependency for optional authentication (public endpoints with user context).

    Returns:
        Optional[User]: User if authenticated, None otherwise
    """
    if not credentials:
        return None

    try:
        # Reuse get_current_user logic
        token = credentials.credentials
        stmt = (
            select(UserSession, User)
            .join(User, UserSession.user_id == User.id)
            .where(UserSession.token == token)
            .where(UserSession.expires_at > datetime.utcnow())
        )
        result = await db.execute(stmt)
        row = result.one_or_none()
        return row[1] if row else None
    except Exception:
        return None
```

#### 4.2 Protected Endpoint Example

```python
from fastapi import APIRouter, Depends
from src.auth.dependencies import get_current_user
from src.auth.models import User

router = APIRouter()

@router.get("/todos")
async def list_todos(
    current_user: User = Depends(get_current_user)  # ⚠️ Required authentication
):
    """
    List todos for authenticated user.

    **FR-005**: FastAPI integration with authentication middleware
    """
    return {
        "todos": [],
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "name": current_user.name,
        }
    }
```

#### 4.3 Optional Authentication Example

```python
@router.get("/public-todos")
async def list_public_todos(
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    List public todos (authentication optional).
    """
    if current_user:
        # Show personalized content
        return {"todos": [], "personalized": True}
    else:
        # Show generic content
        return {"todos": [], "personalized": False}
```

---

## Database Schema Contract

### Required Tables in Shared PostgreSQL

Both auth server and API server must have access to these tables:

#### users

```sql
CREATE TABLE users (
    id VARCHAR PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    email_verified BOOLEAN DEFAULT FALSE,
    password VARCHAR NULL,
    name VARCHAR(100) NULL,
    image VARCHAR(500) NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### user_sessions

```sql
CREATE TABLE user_sessions (
    id VARCHAR PRIMARY KEY,
    user_id VARCHAR NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    ip_address TEXT NULL,  -- ⚠️ Use TEXT, NOT INET
    user_agent VARCHAR(500) NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_sessions_token ON user_sessions(token);
CREATE INDEX idx_sessions_expires_at ON user_sessions(expires_at);
```

### Schema Sync Guarantees

1. **Auth Server (Prisma)**: Defines and owns schema
2. **API Server (Alembic)**: Mirrors schema exactly
3. **Validation**: Run sync script to detect mismatches

```bash
# Validate schema sync
bash .claude/skills/better-auth-setup/scripts/sync-schemas.sh
```

**Critical Type Mappings**:

| Prisma Type | PostgreSQL Type | SQLAlchemy Type |
|-------------|-----------------|-----------------|
| `String` | `VARCHAR` | `sa.String()` |
| `String` (ipAddress) | `TEXT` | `sa.Text()` ⚠️ |
| `Boolean` | `BOOLEAN` | `sa.Boolean()` |
| `DateTime` | `TIMESTAMP` | `sa.DateTime()` |
| `Int` | `INTEGER` | `sa.Integer()` |

---

## Error Handling Contract

### Error Response Format

All authentication errors follow this format:

```json
{
  "error": "ERROR_CODE",
  "message": "Human-readable error message",
  "details": {
    // Optional additional context
  }
}
```

### Standard Error Codes

| HTTP Status | Error Code | Message | When to Use |
|-------------|------------|---------|-------------|
| 401 | `MISSING_TOKEN` | Authorization header is required | No Authorization header |
| 401 | `INVALID_TOKEN` | Session token is invalid or expired | Token not found in database or expired |
| 401 | `MALFORMED_TOKEN` | Authorization header format is invalid | Not "Bearer <token>" format |
| 403 | `EMAIL_NOT_VERIFIED` | Email verification required | User.emailVerified is false |
| 403 | `INSUFFICIENT_PERMISSIONS` | User lacks required permissions | Future: role-based access control |
| 404 | `USER_NOT_FOUND` | User account does not exist | Session valid but user deleted |
| 500 | `DATABASE_ERROR` | Database connection failed | Database query error |

### FastAPI Error Responses

```python
from fastapi import HTTPException, status

# 401 Unauthorized
raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid or expired session token",
    headers={"WWW-Authenticate": "Bearer"},
)

# 403 Forbidden
raise HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Email verification required",
)

# 404 Not Found
raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="User account does not exist",
)
```

---

## Performance Contract

### Latency Budgets

| Operation | Target Latency (p95) | Acceptable Latency (p99) |
|-----------|----------------------|--------------------------|
| Token validation (database lookup) | < 50ms | < 100ms |
| Protected endpoint (total) | < 200ms | < 500ms |
| Session creation (signin) | < 300ms | < 600ms |

### Database Connection Pooling

**Neon Serverless PostgreSQL**:
- **Connection pooling**: Enabled by default
- **Max connections**: 100 (shared across both services)
- **Idle timeout**: 10 seconds

**FastAPI Configuration**:

```python
# backend/src/database/connection.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=10,        # ⚠️ Max 10 connections per API instance
    max_overflow=5,      # Allow 5 additional connections
    pool_pre_ping=True,  # Verify connection health
    pool_recycle=3600,   # Recycle connections after 1 hour
)

async_session_maker = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_db() -> AsyncSession:
    async with async_session_maker() as session:
        yield session
```

### Caching Strategy (Future Enhancement)

**Current**: No caching (database lookup per request)

**Future** (if latency exceeds budget):
1. **Redis session cache**: Cache valid sessions for 5 minutes
2. **In-memory LRU cache**: Cache last 1000 sessions
3. **Hybrid**: Check cache first, fallback to database

---

## Security Contract

### Token Security

1. **Transmission**: Always use HTTPS in production
2. **Storage**: Never log full tokens (truncate to first 8 chars)
3. **Expiration**: Enforce `expires_at` check in database query
4. **Revocation**: Delete from database immediately on signout

### CORS Configuration

**Auth Server**:
```typescript
// auth-server/src/app.ts
app.use(cors({
  origin: process.env.CORS_ORIGINS.split(','),
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization'],
}));
```

**FastAPI**:
```python
# backend/src/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Environment Variables**:
```bash
# Both services must have matching CORS_ORIGINS
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com,https://yourdomain.github.io
```

---

## Testing Contract

### Integration Test Example

```python
# backend/tests/integration/test_auth_flow.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_protected_endpoint_requires_auth(client: AsyncClient):
    """Test that protected endpoints require authentication."""
    response = await client.get("/api/todos")

    assert response.status_code == 401
    assert response.json()["error"] == "MISSING_TOKEN"


@pytest.mark.asyncio
async def test_protected_endpoint_with_valid_token(client: AsyncClient, valid_session):
    """Test that protected endpoints accept valid tokens."""
    token = valid_session["token"]

    response = await client.get(
        "/api/todos",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert "todos" in response.json()


@pytest.mark.asyncio
async def test_protected_endpoint_with_expired_token(client: AsyncClient, expired_session):
    """Test that expired tokens are rejected."""
    token = expired_session["token"]

    response = await client.get(
        "/api/todos",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 401
    assert response.json()["error"] == "INVALID_TOKEN"
```

### Test Fixtures

```python
# backend/tests/conftest.py
import pytest
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.fixture
async def valid_session(db: AsyncSession):
    """Create a valid test session."""
    user = User(
        id="test_user_123",
        email="test@example.com",
        email_verified=True,
        password="hashed_password",
    )
    db.add(user)

    session = UserSession(
        id="test_session_123",
        user_id=user.id,
        token="test_token_abc123",
        expires_at=datetime.utcnow() + timedelta(days=7),
    )
    db.add(session)
    await db.commit()

    return {"token": session.token, "user_id": user.id}


@pytest.fixture
async def expired_session(db: AsyncSession):
    """Create an expired test session."""
    user = User(
        id="test_user_456",
        email="expired@example.com",
        email_verified=True,
    )
    db.add(user)

    session = UserSession(
        id="test_session_456",
        user_id=user.id,
        token="expired_token_xyz789",
        expires_at=datetime.utcnow() - timedelta(hours=1),  # Expired
    )
    db.add(session)
    await db.commit()

    return {"token": session.token, "user_id": user.id}
```

---

## Deployment Contract

### Environment Variables

**Required in both services**:

| Variable | Auth Server | API Server | Example |
|----------|-------------|------------|---------|
| `DATABASE_URL` | ✅ | ✅ | `postgresql://user:pass@neon.tech/db?sslmode=require` |
| `JWT_SECRET` | ✅ | ❌ | `your-secret-key-min-32-chars` |
| `CORS_ORIGINS` | ✅ | ✅ | `http://localhost:3000,https://yourdomain.com` |
| `NODE_ENV` / `ENVIRONMENT` | ✅ | ✅ | `production` |
| `RESEND_API_KEY` | ✅ | ❌ | `re_xxxxx` |
| `FRONTEND_URL` | ✅ | ✅ | `https://yourdomain.com` |

### Health Checks

Both services must expose health check endpoints:

**Auth Server**: `GET /health`
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2025-01-10T12:00:00Z"
}
```

**API Server**: `GET /health`
```python
@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}
```

---

## Migration Contract

### Schema Change Process

1. **Propose change**: Create issue describing schema change
2. **Update Prisma schema**: Modify `auth-server/prisma/schema.prisma`
3. **Generate Prisma migration**: Run `npx prisma migrate dev --name <name>`
4. **Create Alembic migration**: Manually create matching migration in `backend/src/database/migrations/`
5. **Validate sync**: Run sync script to verify schemas match
6. **Deploy**: Deploy auth server first, then API server

### Backward Compatibility

- **Additive changes**: Safe (add nullable columns)
- **Breaking changes**: Require coordinated deployment or versioning

---

## Summary

This contract ensures:

✅ **Consistent token flow**: Frontend → Auth Server → FastAPI → Database
✅ **Standardized error handling**: Common error codes and formats
✅ **Performance guarantees**: Latency budgets and connection pooling
✅ **Security**: HTTPS, token validation, CORS configuration
✅ **Testing**: Integration tests for auth flows
✅ **Deployment**: Health checks and environment variables

**Next Steps**: Generate `quickstart.md` with setup instructions
