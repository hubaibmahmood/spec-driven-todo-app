# FastAPI Integration Patterns for MCP

Common patterns for integrating FastAPI backends with MCP servers.

## Table of Contents

- [Architecture Patterns](#architecture-patterns)
- [Authentication Integration](#authentication-integration)
- [Database Integration](#database-integration)
- [Error Handling](#error-handling)
- [Testing Patterns](#testing-patterns)
- [Deployment Patterns](#deployment-patterns)

## Architecture Patterns

### Pattern 1: Separate MCP Server (Recommended)

**When to use:** Production deployments, independent scaling, clear separation

```
┌──────────────┐
│  AI Agent    │
│ (Claude)     │
└──────┬───────┘
       │ MCP Protocol
       ▼
┌──────────────┐
│ MCP Server   │ ← Separate process
│ (Port 8001)  │
└──────┬───────┘
       │ HTTP
       ▼
┌──────────────┐
│ FastAPI      │ ← Your existing API
│ (Port 8000)  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  PostgreSQL  │
└──────────────┘
```

**Implementation:**

```python
# mcp-server/client.py
import httpx
from typing import Any

class FastAPIClient:
    """HTTP client for FastAPI backend."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.client = httpx.AsyncClient(
            base_url=base_url,
            timeout=30.0,
            follow_redirects=True
        )

    async def post(self, path: str, **kwargs) -> Any:
        """POST request."""
        response = await self.client.post(path, **kwargs)
        response.raise_for_status()
        return response.json()

    async def get(self, path: str, **kwargs) -> Any:
        """GET request."""
        response = await self.client.get(path, **kwargs)
        response.raise_for_status()
        return response.json()

# mcp-server/main.py
from mcp.server.fastmcp import FastMCP
from client import FastAPIClient

mcp = FastMCP("Todo App MCP")
fastapi_client = FastAPIClient("http://localhost:8000")

@mcp.tool()
async def create_task(user_id: str, title: str, description: str = None) -> dict:
    """Create a task via FastAPI."""
    return await fastapi_client.post(
        "/api/v1/tasks",
        params={"user_id": user_id},
        json={"title": title, "description": description}
    )
```

**Pros:**
- ✅ Independent deployment and scaling
- ✅ No changes to existing FastAPI code
- ✅ Clear separation of concerns
- ✅ Can restart either service independently

**Cons:**
- ⚠️ Network latency between services
- ⚠️ Need to manage two processes
- ⚠️ Duplicate authentication logic

### Pattern 2: Shared Database Access

**When to use:** Performance-critical, low latency requirements, complex queries

```
┌──────────────┐
│  AI Agent    │
└──────┬───────┘
       │
       ▼
┌──────────────┐     ┌──────────────┐
│ MCP Server   │     │  FastAPI     │
└──────┬───────┘     └──────┬───────┘
       │                    │
       └────────┬───────────┘
                │ Both connect directly
                ▼
         ┌──────────────┐
         │  PostgreSQL  │
         └──────────────┘
```

**Implementation:**

```python
# shared/db/session.py (used by both)
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+asyncpg://user:pass@localhost/db"

engine = create_async_engine(DATABASE_URL)
async_session_maker = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_db():
    async with async_session_maker() as session:
        yield session

# mcp-server/tools.py
from mcp.server.fastmcp import FastMCP
from shared.db.session import get_db
from shared.models.task import Task
from sqlalchemy import select

mcp = FastMCP("Todo App MCP")

@mcp.tool()
async def create_task(user_id: str, title: str, description: str = None) -> dict:
    """Create task with direct database access."""
    async with get_db() as db:
        task = Task(
            user_id=user_id,
            title=title,
            description=description
        )
        db.add(task)
        await db.commit()
        await db.refresh(task)

        return {
            "task_id": task.id,
            "status": "created",
            "title": task.title
        }
```

**Pros:**
- ✅ No network latency
- ✅ Can reuse SQLAlchemy models
- ✅ Access to full database capabilities
- ✅ Better performance

**Cons:**
- ⚠️ Duplicates business logic
- ⚠️ Tighter coupling
- ⚠️ Must maintain two codebases
- ⚠️ Risk of data inconsistency

### Pattern 3: Hybrid Approach

**When to use:** Balance between performance and maintainability

```python
# MCP server calls FastAPI for write operations (business logic)
# but reads directly from database for queries (performance)

@mcp.tool()
async def create_task(user_id: str, title: str) -> dict:
    """Create task via FastAPI (business logic)."""
    return await fastapi_client.post("/api/v1/tasks", ...)

@mcp.tool()
async def list_tasks(user_id: str, status: str = "all") -> list[dict]:
    """List tasks via direct database (performance)."""
    async with get_db() as db:
        stmt = select(Task).where(Task.user_id == user_id)
        if status != "all":
            stmt = stmt.where(Task.completed == (status == "completed"))
        result = await db.execute(stmt)
        tasks = result.scalars().all()
        return [{"id": t.id, "title": t.title, ...} for t in tasks]
```

## Authentication Integration

### Pattern 1: User ID Parameter (Stateless)

**Best for:** Multi-tenant systems, simple auth

```python
# FastAPI endpoint
@router.post("/tasks")
async def create_task(
    user_id: str,  # Required parameter
    task: TaskCreate,
    db: AsyncSession = Depends(get_db)
):
    # Verify user exists
    user = await user_repo.get(db, user_id)
    if not user:
        raise HTTPException(404, "User not found")

    return await task_service.create(db, user_id, task)

# MCP tool
@mcp.tool()
async def create_task(user_id: str, title: str, description: str = None) -> dict:
    """Create task for specified user."""
    return await fastapi_client.post(
        "/api/v1/tasks",
        params={"user_id": user_id},
        json={"title": title, "description": description}
    )
```

### Pattern 2: JWT Bearer Token

**Best for:** Secure APIs, OAuth2 integration

```python
# mcp-server/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    fastapi_base_url: str = "http://localhost:8000"
    jwt_secret: str  # From environment
    jwt_token: str | None = None  # Optional pre-generated token

    class Config:
        env_file = ".env"

settings = Settings()

# mcp-server/auth.py
import jwt
from datetime import datetime, timedelta

class JWTManager:
    """Manage JWT tokens for FastAPI authentication."""

    def __init__(self, secret: str):
        self.secret = secret

    def generate_token(self, user_id: str, expires_in: int = 3600) -> str:
        """Generate JWT token for user."""
        payload = {
            "sub": user_id,
            "exp": datetime.utcnow() + timedelta(seconds=expires_in),
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, self.secret, algorithm="HS256")

jwt_manager = JWTManager(settings.jwt_secret)

# mcp-server/client.py
class AuthenticatedClient:
    """FastAPI client with JWT authentication."""

    def __init__(self, base_url: str, jwt_manager: JWTManager):
        self.base_url = base_url
        self.jwt_manager = jwt_manager
        self.client = httpx.AsyncClient(base_url=base_url)

    async def post(self, path: str, user_id: str, **kwargs):
        """POST with JWT auth."""
        token = self.jwt_manager.generate_token(user_id)
        headers = {"Authorization": f"Bearer {token}"}
        response = await self.client.post(path, headers=headers, **kwargs)
        response.raise_for_status()
        return response.json()

# Usage in tools
@mcp.tool()
async def create_task(user_id: str, title: str) -> dict:
    """Create task with JWT authentication."""
    return await auth_client.post(
        "/api/v1/tasks",
        user_id=user_id,
        json={"title": title}
    )
```

### Pattern 3: Session-Based Auth

**Best for:** Traditional web apps

```python
# mcp-server/config.py
class Settings(BaseSettings):
    session_cookie: str = "session_id"
    session_token: str  # From environment or login

# mcp-server/client.py
class SessionClient:
    """FastAPI client with session cookie."""

    def __init__(self, base_url: str, session_token: str):
        self.client = httpx.AsyncClient(
            base_url=base_url,
            cookies={"session_id": session_token}
        )

    async def post(self, path: str, **kwargs):
        """POST with session cookie."""
        response = await self.client.post(path, **kwargs)
        response.raise_for_status()
        return response.json()
```

### Pattern 4: Better-Auth Integration

**Best for:** Projects using better-auth

```python
# mcp-server/better_auth_client.py
import httpx

class BetterAuthClient:
    """Client for better-auth protected FastAPI."""

    def __init__(self, base_url: str, auth_url: str):
        self.base_url = base_url
        self.auth_url = auth_url
        self.client = httpx.AsyncClient()
        self.access_token = None

    async def login(self, email: str, password: str):
        """Login and get access token."""
        response = await self.client.post(
            f"{self.auth_url}/api/auth/sign-in/email",
            json={"email": email, "password": password}
        )
        response.raise_for_status()
        data = response.json()
        self.access_token = data["token"]

    async def request(self, method: str, path: str, **kwargs):
        """Make authenticated request."""
        if not self.access_token:
            raise ValueError("Not authenticated. Call login() first.")

        headers = kwargs.get("headers", {})
        headers["Authorization"] = f"Bearer {self.access_token}"
        kwargs["headers"] = headers

        response = await self.client.request(
            method,
            f"{self.base_url}{path}",
            **kwargs
        )
        response.raise_for_status()
        return response.json()

# Initialize on startup
auth_client = BetterAuthClient(
    base_url="http://localhost:8000",
    auth_url="http://localhost:3000"
)

@mcp.on_startup()
async def startup():
    """Login on server startup."""
    await auth_client.login(
        email=os.getenv("API_USER_EMAIL"),
        password=os.getenv("API_USER_PASSWORD")
    )

@mcp.tool()
async def create_task(title: str, description: str = None) -> dict:
    """Create task with better-auth."""
    return await auth_client.request(
        "POST",
        "/api/v1/tasks",
        json={"title": title, "description": description}
    )
```

## Database Integration

### Sharing SQLAlchemy Models

```
project/
├── app/                  # FastAPI app
│   ├── main.py
│   ├── api/
│   └── services/
├── mcp-server/          # MCP server
│   ├── main.py
│   └── tools.py
└── shared/              # Shared code
    ├── models/          # SQLAlchemy models
    │   ├── task.py
    │   └── user.py
    ├── db/
    │   └── session.py   # Database session
    └── schemas/         # Pydantic schemas
        ├── task.py
        └── user.py
```

**Implementation:**

```python
# shared/models/task.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from shared.db.session import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(String(1000))
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# shared/schemas/task.py
from pydantic import BaseModel, Field
from datetime import datetime

class TaskBase(BaseModel):
    title: str = Field(..., max_length=200)
    description: str | None = Field(None, max_length=1000)

class TaskCreate(TaskBase):
    pass

class TaskResponse(TaskBase):
    id: int
    user_id: str
    completed: bool
    created_at: datetime

    class Config:
        from_attributes = True

# mcp-server/tools.py (using shared models)
from shared.models.task import Task
from shared.schemas.task import TaskResponse
from shared.db.session import get_db
from sqlalchemy import select

@mcp.tool()
async def list_tasks(user_id: str, status: str = "all") -> list[dict]:
    """List tasks using shared models."""
    async for db in get_db():
        stmt = select(Task).where(Task.user_id == user_id)

        if status == "pending":
            stmt = stmt.where(Task.completed == False)
        elif status == "completed":
            stmt = stmt.where(Task.completed == True)

        result = await db.execute(stmt)
        tasks = result.scalars().all()

        # Convert to Pydantic for validation
        return [TaskResponse.model_validate(t).model_dump() for t in tasks]
```

## Error Handling

### Unified Error Response Format

```python
# shared/schemas/error.py
from pydantic import BaseModel
from enum import Enum

class ErrorCode(str, Enum):
    """Standard error codes."""
    VALIDATION_ERROR = "validation_error"
    NOT_FOUND = "not_found"
    UNAUTHORIZED = "unauthorized"
    FORBIDDEN = "forbidden"
    SERVER_ERROR = "server_error"
    BAD_REQUEST = "bad_request"

class ErrorResponse(BaseModel):
    """Standard error response."""
    status: str = "error"
    error_code: ErrorCode
    message: str
    details: dict | None = None

# mcp-server/tools.py
from httpx import HTTPStatusError

@mcp.tool()
async def create_task(user_id: str, title: str) -> dict:
    """Create task with unified error handling."""
    try:
        return await fastapi_client.post(
            "/api/v1/tasks",
            params={"user_id": user_id},
            json={"title": title}
        )

    except HTTPStatusError as e:
        error_map = {
            400: ErrorCode.BAD_REQUEST,
            401: ErrorCode.UNAUTHORIZED,
            403: ErrorCode.FORBIDDEN,
            404: ErrorCode.NOT_FOUND,
            500: ErrorCode.SERVER_ERROR,
        }

        error_code = error_map.get(e.response.status_code, ErrorCode.SERVER_ERROR)

        return ErrorResponse(
            error_code=error_code,
            message=f"FastAPI error: {e.response.text}",
            details={"status_code": e.response.status_code}
        ).model_dump()

    except Exception as e:
        return ErrorResponse(
            error_code=ErrorCode.SERVER_ERROR,
            message="Unexpected error",
            details={"exception": str(e)}
        ).model_dump()
```

## Testing Patterns

### Integration Testing Setup

```python
# mcp-server/tests/conftest.py
import pytest
import asyncio
from httpx import AsyncClient
from mcp.client.session import ClientSession
from mcp.shared.memory import create_connected_server_and_client_session
from app.main import app as fastapi_app
from mcp_server.main import mcp

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def fastapi_client():
    """FastAPI test client."""
    async with AsyncClient(app=fastapi_app, base_url="http://test") as client:
        yield client

@pytest.fixture
async def mcp_client():
    """MCP test client."""
    async with create_connected_server_and_client_session(
        mcp,
        raise_exceptions=True
    ) as session:
        yield session

@pytest.fixture
async def test_user(fastapi_client):
    """Create test user."""
    response = await fastapi_client.post(
        "/api/v1/users",
        json={"email": "test@example.com", "password": "testpass"}
    )
    return response.json()

# mcp-server/tests/test_tools.py
@pytest.mark.asyncio
async def test_create_task(mcp_client, test_user):
    """Test create_task tool."""
    result = await mcp_client.call_tool(
        "create_task",
        {
            "user_id": test_user["id"],
            "title": "Test task",
            "description": "Test description"
        }
    )

    assert result.structuredContent["status"] == "created"
    assert result.structuredContent["task_id"] > 0
    assert result.structuredContent["title"] == "Test task"

@pytest.mark.asyncio
async def test_list_tasks(mcp_client, test_user):
    """Test list_tasks tool."""
    # Create some test tasks first
    for i in range(3):
        await mcp_client.call_tool(
            "create_task",
            {"user_id": test_user["id"], "title": f"Task {i}"}
        )

    # List tasks
    result = await mcp_client.call_tool(
        "list_tasks",
        {"user_id": test_user["id"], "status": "all"}
    )

    tasks = result.structuredContent
    assert len(tasks) == 3
    assert all(t["user_id"] == test_user["id"] for t in tasks)
```

## Deployment Patterns

### Docker Compose Setup

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: todoapp
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  fastapi:
    build:
      context: .
      dockerfile: Dockerfile.fastapi
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql+asyncpg://user:password@postgres/todoapp
    depends_on:
      - postgres
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000

  mcp-server:
    build:
      context: .
      dockerfile: Dockerfile.mcp
    ports:
      - "8001:8001"
    environment:
      FASTAPI_BASE_URL: http://fastapi:8000
      MCP_TRANSPORT: streamable-http
      MCP_PORT: 8001
    depends_on:
      - fastapi
    command: python mcp-server/main.py

volumes:
  postgres_data:
```

### Dockerfile for MCP Server

```dockerfile
# Dockerfile.mcp
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY mcp-server/pyproject.toml .
RUN pip install -e .

# Copy application
COPY mcp-server/ ./mcp-server/
COPY shared/ ./shared/

EXPOSE 8001

CMD ["python", "mcp-server/main.py"]
```

### Kubernetes Deployment

```yaml
# k8s/mcp-server-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-server
spec:
  replicas: 3
  selector:
    matchLabels:
      app: mcp-server
  template:
    metadata:
      labels:
        app: mcp-server
    spec:
      containers:
      - name: mcp-server
        image: your-registry/mcp-server:latest
        ports:
        - containerPort: 8001
        env:
        - name: FASTAPI_BASE_URL
          value: "http://fastapi-service:8000"
        - name: MCP_TRANSPORT
          value: "streamable-http"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: mcp-server-service
spec:
  selector:
    app: mcp-server
  ports:
  - port: 8001
    targetPort: 8001
  type: LoadBalancer
```

## Performance Optimization

### Connection Pooling Best Practices

```python
# Optimal settings for production
client = httpx.AsyncClient(
    base_url="http://fastapi:8000",
    limits=httpx.Limits(
        max_keepalive_connections=20,  # Keep connections alive
        max_connections=100,             # Max concurrent connections
        keepalive_expiry=30.0           # Keep alive for 30s
    ),
    timeout=httpx.Timeout(
        connect=5.0,   # Connection timeout
        read=30.0,     # Read timeout
        write=10.0,    # Write timeout
        pool=5.0       # Pool acquisition timeout
    ),
    http2=True  # Enable HTTP/2 for multiplexing
)
```

### Caching Strategy

```python
from aiocache import cached, Cache
from aiocache.serializers import JsonSerializer

@cached(
    ttl=300,  # 5 minutes
    cache=Cache.MEMORY,
    serializer=JsonSerializer()
)
@mcp.tool()
async def get_user_stats(user_id: str) -> dict:
    """Get user statistics (cached for 5 min)."""
    return await fastapi_client.get(f"/api/v1/users/{user_id}/stats")
```

## Further Reading

- [FastAPI Best Practices](https://fastapi.tiangolo.com/tutorial/)
- [SQLAlchemy Async Patterns](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [MCP Integration Patterns](https://modelcontextprotocol.io/docs/patterns)
