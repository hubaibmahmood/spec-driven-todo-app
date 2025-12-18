# Microservices Authentication Patterns for FastAPI-to-MCP

This document describes advanced authentication patterns for microservices architectures, specifically for MCP servers that need to communicate with FastAPI backends in a service-to-service manner.

## Pattern 4: Service-to-Service Authentication (Microservices)

**When to use:**
- ✅ Microservices architecture with multiple services
- ✅ MCP server is a separate service from FastAPI backend
- ✅ Need to preserve user context across service boundaries
- ✅ Security-critical systems requiring service authentication

**Architecture:**
```
┌─────────────────┐
│   AI Agent      │
│ (Claude Code)   │
└────────┬────────┘
         │ user_id in session
         ▼
┌─────────────────┐
│  MCP Server     │ ← Service Identity: SERVICE_AUTH_TOKEN
│  (Service)      │ ← User Context: X-User-ID header
└────────┬────────┘
         │ Bearer {SERVICE_AUTH_TOKEN} + X-User-ID: {user_id}
         ▼
┌─────────────────┐
│  FastAPI Backend│ ← Validates: service token + user context
│  (Service)      │ ← Enforces: data isolation per user
└────────┬────────┘
         ▼
┌─────────────────┐
│   Database      │
└─────────────────┘
```

### Key Concepts

1. **Dual Authentication**:
   - **Service Identity**: `Authorization: Bearer {SERVICE_AUTH_TOKEN}` (who is calling)
   - **User Context**: `X-User-ID: {user_id}` (on whose behalf)

2. **Security Requirements**:
   - SERVICE_AUTH_TOKEN must be 32+ characters
   - Constant-time token comparison (prevent timing attacks)
   - Token stored only in environment variables
   - Token never logged

3. **Data Isolation**:
   - Backend enforces user-level permissions
   - Service token grants access, user context defines scope
   - Each user can only access their own data

## Implementation

### Step 1: Generate SERVICE_AUTH_TOKEN

```bash
# Generate secure 32+ character token
python -c "import secrets; print(secrets.token_urlsafe(32))"
# Output: dOQqrfQZH7DtQhAeEoKzwPo3DkvfqB2p-OxRuwXN3uk
```

### Step 2: MCP Server Configuration

**mcp-server/src/config.py:**
```python
"""MCP server configuration from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """MCP server configuration loaded from environment variables."""

    # Required fields
    service_auth_token: str
    fastapi_base_url: str

    # Optional fields with defaults
    mcp_log_level: str = "INFO"
    mcp_server_port: int = 3000
    backend_timeout: float = 30.0
    backend_max_retries: int = 2

    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore",
    }


# Singleton instance
settings = Settings()
```

**mcp-server/.env:**
```env
SERVICE_AUTH_TOKEN=dOQqrfQZH7DtQhAeEoKzwPo3DkvfqB2p-OxRuwXN3uk
FASTAPI_BASE_URL=http://localhost:8000
MCP_LOG_LEVEL=INFO
MCP_SERVER_PORT=3000
```

### Step 3: MCP Server HTTP Client with Retry Logic

**mcp-server/src/client.py:**
```python
"""HTTP client for FastAPI backend communication."""

import logging
from datetime import datetime
from typing import Any, Optional

import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from .config import settings

logger = logging.getLogger(__name__)


class BackendClient:
    """HTTP client for communicating with FastAPI backend."""

    def __init__(self):
        """Initialize backend client with configuration."""
        self.base_url = settings.fastapi_base_url
        self.timeout = settings.backend_timeout
        self.max_retries = settings.backend_max_retries
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
        )

    def _build_headers(self, user_id: str) -> dict[str, str]:
        """Build headers for authenticated backend requests.

        Args:
            user_id: User ID from MCP session context

        Returns:
            Dictionary of HTTP headers
        """
        return {
            "Authorization": f"Bearer {settings.service_auth_token}",
            "X-User-ID": user_id,
            "Content-Type": "application/json",
        }

    @retry(
        stop=stop_after_attempt(3),  # Initial + 2 retries
        wait=wait_exponential(multiplier=1, min=1, max=2),  # 1s, 2s backoff
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError)),
        reraise=True,
    )
    async def _request(
        self,
        method: str,
        endpoint: str,
        user_id: str,
        json: Optional[dict[str, Any]] = None,
    ) -> httpx.Response:
        """Make HTTP request to backend with retry logic.

        Args:
            method: HTTP method (GET, POST, PUT, PATCH, DELETE)
            endpoint: API endpoint path
            user_id: User ID for context propagation
            json: Optional JSON body

        Returns:
            HTTP response

        Raises:
            httpx.TimeoutException: Request timed out after retries
            httpx.ConnectError: Connection failed after retries
        """
        start_time = datetime.now()
        headers = self._build_headers(user_id)

        try:
            response = await self.client.request(
                method=method,
                url=endpoint,
                headers=headers,
                json=json,
            )

            duration_ms = (datetime.now() - start_time).total_seconds() * 1000

            # Log successful request
            logger.info(
                "Backend API call completed",
                extra={
                    "timestamp": datetime.now().isoformat(),
                    "endpoint": endpoint,
                    "method": method,
                    "status_code": response.status_code,
                    "user_id": user_id,
                    "duration_ms": duration_ms,
                },
            )

            return response

        except (httpx.TimeoutException, httpx.ConnectError) as e:
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000

            # Log failed request
            logger.error(
                "Backend API call failed",
                extra={
                    "timestamp": datetime.now().isoformat(),
                    "endpoint": endpoint,
                    "method": method,
                    "user_id": user_id,
                    "duration_ms": duration_ms,
                    "error": str(e),
                },
            )
            raise

    async def get_tasks(self, user_id: str) -> httpx.Response:
        """Retrieve all tasks for the user."""
        return await self._request("GET", "/tasks", user_id)

    async def create_task(
        self, user_id: str, task_data: dict[str, Any]
    ) -> httpx.Response:
        """Create a new task."""
        return await self._request("POST", "/tasks", user_id, json=task_data)

    async def close(self):
        """Close the HTTP client connection."""
        await self.client.aclose()
```

### Step 4: Backend Configuration

**backend/src/config.py:**
```python
class Settings(BaseSettings):
    """Application settings."""

    # ... existing config ...

    # Service Authentication
    SERVICE_AUTH_TOKEN: str = ""  # Service-to-service authentication token
```

**backend/.env:**
```env
# Same token as MCP server
SERVICE_AUTH_TOKEN=dOQqrfQZH7DtQhAeEoKzwPo3DkvfqB2p-OxRuwXN3uk
```

### Step 5: Backend Dual Authentication Dependencies

**backend/src/api/dependencies.py:**
```python
"""FastAPI dependencies for dependency injection."""

import hmac
from typing import Optional

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.database.connection import get_db
from src.services.auth_service import validate_session

security = HTTPBearer()


async def get_service_auth(
    authorization: str = Header(...),
    x_user_id: str = Header(..., alias="X-User-ID"),
) -> str:
    """
    Validate service authentication token and return user ID from header.

    This dependency is used for service-to-service authentication (e.g., MCP server).

    Args:
        authorization: Authorization header (Bearer {SERVICE_AUTH_TOKEN})
        x_user_id: User ID from X-User-ID header

    Returns:
        User ID string from X-User-ID header

    Raises:
        HTTPException: 401 if service token is invalid
        HTTPException: 400 if X-User-ID header is missing
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization.split(" ", 1)[1]

    # Use constant-time comparison to prevent timing attacks
    if not settings.SERVICE_AUTH_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Service authentication not configured",
        )

    if not hmac.compare_digest(token, settings.SERVICE_AUTH_TOKEN):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid service authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing X-User-ID header",
        )

    return x_user_id


async def get_current_user_or_service(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    x_user_id: Optional[str] = Header(None, alias="X-User-ID"),
    db: AsyncSession = Depends(get_db),
) -> str:
    """
    Authenticate user via either service token or user session.

    This dependency supports dual authentication:
    - If X-User-ID header is present: use service authentication flow
    - Otherwise: use standard user session authentication flow

    Args:
        credentials: HTTP Authorization credentials (Bearer token)
        x_user_id: Optional X-User-ID header for service authentication
        db: Database session

    Returns:
        User ID string

    Raises:
        HTTPException: 401 if authentication fails
    """
    # Service authentication flow (MCP server)
    if x_user_id is not None:
        if credentials is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authorization header for service authentication",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = credentials.credentials

        # Validate service token
        if not settings.SERVICE_AUTH_TOKEN:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Service authentication not configured",
            )

        if not hmac.compare_digest(token, settings.SERVICE_AUTH_TOKEN):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid service authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return x_user_id

    # Standard user session authentication flow
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    user_id = await validate_session(token, db)

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_id
```

### Step 6: Update FastAPI Endpoints

**backend/src/api/routers/tasks.py:**
```python
from src.api.dependencies import get_current_user_or_service  # Changed import

@router.get("/", response_model=list[TaskResponse])
async def get_all_tasks(
    repository: TaskRepository = Depends(get_task_repository),
    current_user: str = Depends(get_current_user_or_service)  # Changed dependency
) -> list[TaskResponse]:
    """Get all tasks for the authenticated user."""
    tasks = await repository.get_all_by_user(current_user)
    return [TaskResponse.model_validate(task) for task in tasks]

# Update ALL endpoints to use get_current_user_or_service
```

## Error Taxonomy for AI

MCP tools should translate backend errors into AI-friendly messages.

**mcp-server/src/schemas/task.py:**
```python
from pydantic import BaseModel, Field
from typing import Optional


class ErrorResponse(BaseModel):
    """Structured error response for AI consumption."""

    error_type: str = Field(..., description="Error type identifier")
    message: str = Field(..., description="Human-readable error message for AI")
    details: Optional[dict] = Field(None, description="Additional error context")
    suggestions: Optional[list[str]] = Field(None, description="Suggested next actions")


# Error type taxonomy
ERROR_TYPES = {
    "authentication_error": "Service authentication failed",
    "authorization_error": "User not authorized to access this resource",
    "not_found_error": "Requested resource not found",
    "validation_error": "Input validation failed",
    "backend_error": "Backend service error",
    "timeout_error": "Request timed out",
    "connection_error": "Unable to connect to backend service",
}
```

**Error translation in tools:**
```python
@mcp.tool()
async def list_tasks(user_id: str) -> dict:
    """Retrieve all tasks for the authenticated user."""
    try:
        response = await client.get_tasks(user_id)

        if response.status_code == 200:
            return {"tasks": response.json(), "status": "success"}
        elif response.status_code == 401:
            return {
                "error_type": "authentication_error",
                "message": "Unable to authenticate with backend service.",
                "suggestions": ["Check SERVICE_AUTH_TOKEN configuration"]
            }
        elif response.status_code == 403:
            return {
                "error_type": "authorization_error",
                "message": "You don't have permission to access these tasks.",
                "suggestions": ["Verify user_id is correct"]
            }
        else:
            return {
                "error_type": "backend_error",
                "message": f"Backend returned error: {response.status_code}",
                "details": {"status_code": response.status_code}
            }

    except httpx.TimeoutException:
        return {
            "error_type": "timeout_error",
            "message": "Request timed out after 30 seconds. Backend may be slow or unavailable.",
            "suggestions": ["Try again", "Check backend health"]
        }
    except httpx.ConnectError:
        return {
            "error_type": "connection_error",
            "message": "Unable to connect to backend service.",
            "suggestions": [
                "Verify FASTAPI_BASE_URL is correct",
                "Ensure backend is running"
            ]
        }
```

## Project Structure for Microservices

Recommended structure for maintainability:

```
mcp-server/
├── src/
│   ├── __init__.py
│   ├── server.py          # FastMCP server entry point
│   ├── config.py          # Environment configuration
│   ├── client.py          # HTTP client with retry logic
│   ├── tools/             # Separate file per tool
│   │   ├── __init__.py
│   │   ├── list_tasks.py
│   │   ├── create_task.py
│   │   ├── update_task.py
│   │   ├── delete_task.py
│   │   └── mark_completed.py
│   └── schemas/           # Pydantic schemas
│       ├── __init__.py
│       └── task.py
├── tests/
│   ├── conftest.py        # pytest fixtures
│   ├── contract/          # Contract tests (schema validation)
│   │   └── test_task_schemas.py
│   ├── unit/              # Unit tests (isolated components)
│   │   ├── test_client.py
│   │   └── test_config.py
│   └── integration/       # End-to-end tests
│       ├── test_list_tasks.py
│       ├── test_create_task.py
│       └── test_service_auth.py
├── pyproject.toml
├── .env
├── .env.example
└── README.md
```

## Testing Strategy

### Test Fixtures

**mcp-server/tests/conftest.py:**
```python
"""Pytest fixtures for MCP server tests."""

from unittest.mock import AsyncMock
import pytest


@pytest.fixture
def test_user_id() -> str:
    """Return test user ID."""
    return "test_user_123"


@pytest.fixture
def mock_httpx_client():
    """Create mocked httpx.AsyncClient."""
    return AsyncMock()


@pytest.fixture
def mock_backend_client():
    """Create mocked BackendClient."""
    return AsyncMock()


@pytest.fixture
def test_service_token() -> str:
    """Return test service authentication token."""
    return "test-service-token-for-testing-purposes"
```

**backend/tests/conftest.py additions:**
```python
@pytest.fixture
def mock_service_token():
    """Return valid SERVICE_AUTH_TOKEN for testing."""
    return "test-service-token-for-testing-purposes"


@pytest.fixture
def test_service_auth_headers(mock_service_token, sample_user_id):
    """Return headers for service authentication testing."""
    return {
        "Authorization": f"Bearer {mock_service_token}",
        "X-User-ID": sample_user_id,
    }
```

## Security Checklist

When implementing service-to-service authentication:

- [ ] SERVICE_AUTH_TOKEN is 32+ characters
- [ ] Token stored only in `.env` files
- [ ] Token never logged or printed
- [ ] Constant-time comparison (`hmac.compare_digest()`)
- [ ] X-User-ID validation on backend
- [ ] Data isolation enforced per user
- [ ] Structured logging without sensitive data
- [ ] Retry logic with exponential backoff
- [ ] Timeout configuration (30s default)
- [ ] Error messages are AI-friendly

## Benefits of This Pattern

1. **Security**: Service identity separate from user context
2. **Isolation**: Backend enforces user-level data access
3. **Auditability**: Know which service made request and for whom
4. **Scalability**: Multiple MCP servers can use same backend
5. **Flexibility**: Easy to add more services later
6. **Debugging**: Clear separation of concerns in logs

## When NOT to Use This Pattern

❌ **Single monolithic application** (use Pattern 1: user_id parameter)
❌ **Direct frontend → backend** (use Pattern 2: session or Pattern 3: JWT)
❌ **Simple prototypes** (adds complexity)
❌ **No user context needed** (simpler service auth sufficient)

## Summary

Service-to-service authentication with user context propagation is the **gold standard for microservices** communicating with FastAPI backends. It provides:

- ✅ Strong service authentication
- ✅ User context preservation
- ✅ Data isolation
- ✅ Security best practices
- ✅ Production-ready patterns

Use this pattern when building MCP servers as separate microservices that need to maintain user context while communicating with FastAPI backends.
