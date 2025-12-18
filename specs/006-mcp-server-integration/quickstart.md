# Quickstart Guide: MCP Server Integration

**Feature**: 006-mcp-server-integration
**Date**: 2025-12-18
**Audience**: Developers implementing MCP server from scratch

---

## Overview

This guide walks through the complete implementation of the MCP server that exposes FastAPI todo backend as AI-accessible tools. Follow the steps in order, using TDD principles.

---

## Prerequisites

Before starting:
- ✅ FastAPI backend running at `http://localhost:8000`
- ✅ PostgreSQL database accessible (Neon serverless)
- ✅ Python 3.12+ installed
- ✅ UV package manager installed
- ✅ Service authentication token generated (random 32+ character string)

---

## Step 1: Project Initialization

### 1.1 Create MCP Server Directory

```bash
cd /path/to/todo-app
mkdir mcp-server
cd mcp-server
```

### 1.2 Initialize UV Package

```bash
uv init --package .
```

This creates:
- `pyproject.toml`
- `src/` directory
- Basic package structure

### 1.3 Update pyproject.toml

```toml
[project]
name = "mcp-server"
version = "0.1.0"
description = "MCP server for Todo API AI integration"
requires-python = ">=3.12"
dependencies = [
    "fastmcp>=0.1.0",
    "httpx>=0.25.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "python-dotenv>=1.0.0",
    "tenacity>=8.0.0",  # For retry logic
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.23.0",
    "pytest-cov>=4.1.0",
    "pytest-mock>=3.12.0",
    "httpx>=0.25.0",  # For testing
    "ruff>=0.1.0",
    "mypy>=1.7.0",
]

[project.scripts]
mcp-server = "src.server:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

### 1.4 Install Dependencies

```bash
uv sync
```

---

## Step 2: Environment Configuration

### 2.1 Create .env File

```bash
# mcp-server/.env
SERVICE_AUTH_TOKEN=your-32-character-random-token-here
FASTAPI_BASE_URL=http://localhost:8000
MCP_LOG_LEVEL=INFO
MCP_SERVER_PORT=3000
```

### 2.2 Create .env.example

```bash
# mcp-server/.env.example
SERVICE_AUTH_TOKEN=<generate-random-token>
FASTAPI_BASE_URL=http://localhost:8000
MCP_LOG_LEVEL=INFO
MCP_SERVER_PORT=3000
```

### 2.3 Implement Configuration (src/config.py)

**Test First** (`tests/unit/test_config.py`):
```python
import pytest
from src.config import Settings

def test_settings_load_from_env(monkeypatch):
    """Settings loads from environment variables."""
    monkeypatch.setenv("SERVICE_AUTH_TOKEN", "test-token-123")
    monkeypatch.setenv("FASTAPI_BASE_URL", "http://localhost:8000")

    settings = Settings()
    assert settings.service_auth_token == "test-token-123"
    assert settings.fastapi_base_url == "http://localhost:8000"

def test_settings_defaults():
    """Settings applies default values for optional fields."""
    settings = Settings(
        service_auth_token="test",
        fastapi_base_url="http://localhost:8000"
    )
    assert settings.mcp_log_level == "INFO"
    assert settings.mcp_server_port == 3000
```

**Implementation** (`src/config.py`):
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    service_auth_token: str
    fastapi_base_url: str
    mcp_log_level: str = "INFO"
    mcp_server_port: int = 3000
    backend_timeout: float = 30.0
    backend_max_retries: int = 2

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
```

---

## Step 3: Pydantic Schemas

### 3.1 Create Task Schemas (src/schemas/task.py)

**Test First** (`tests/contract/test_task_schemas.py`):
```python
from src.schemas.task import (
    PriorityLevel, TaskResponse, CreateTaskParams,
    UpdateTaskParams, DeleteTaskParams, BulkDeleteTasksParams
)
from datetime import datetime

def test_create_task_params_validation():
    """CreateTaskParams validates required title."""
    params = CreateTaskParams(title="Buy milk")
    assert params.title == "Buy milk"
    assert params.priority == PriorityLevel.MEDIUM

def test_create_task_params_rejects_empty_title():
    """CreateTaskParams rejects empty title."""
    import pytest
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        CreateTaskParams(title="")
```

**Implementation** (`src/schemas/task.py`):
```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum

class PriorityLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    URGENT = "Urgent"

class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    completed: bool
    priority: PriorityLevel
    due_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    user_id: str

class CreateTaskParams(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    priority: PriorityLevel = PriorityLevel.MEDIUM
    due_date: Optional[datetime] = None

class UpdateTaskParams(BaseModel):
    task_id: int = Field(..., gt=0)
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    completed: Optional[bool] = None
    priority: Optional[PriorityLevel] = None
    due_date: Optional[datetime] = None

class DeleteTaskParams(BaseModel):
    task_id: int = Field(..., gt=0)

class BulkDeleteTasksParams(BaseModel):
    task_ids: list[int] = Field(default_factory=list)

class BulkDeleteResponse(BaseModel):
    deleted: list[int]
    not_found: list[int]
```

---

## Step 4: HTTP Client for Backend Communication

### 4.1 Implement Backend Client (src/client.py)

**Test First** (`tests/unit/test_client.py`):
```python
import pytest
from unittest.mock import AsyncMock
from src.client import BackendClient

@pytest.mark.asyncio
async def test_backend_client_get_tasks():
    """BackendClient makes authenticated GET request."""
    client = BackendClient()
    # Mock httpx client
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json.return_value = []

    # Test actual implementation later
```

**Implementation** (`src/client.py`):
```python
import httpx
import logging
from typing import Any, Optional
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config import settings

logger = logging.getLogger(__name__)

class BackendClient:
    """HTTP client for FastAPI backend communication."""

    def __init__(self):
        self.base_url = settings.fastapi_base_url
        self.timeout = settings.backend_timeout
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout
        )

    def _build_headers(self, user_id: str) -> dict[str, str]:
        """Build authentication headers for backend requests."""
        return {
            "Authorization": f"Bearer {settings.service_auth_token}",
            "X-User-ID": user_id,
            "Content-Type": "application/json"
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=2),
        reraise=True
    )
    async def _request(
        self,
        method: str,
        path: str,
        user_id: str,
        json_data: Optional[dict] = None
    ) -> httpx.Response:
        """Make authenticated request to backend with retry logic."""
        headers = self._build_headers(user_id)
        start_time = datetime.utcnow()

        try:
            response = await self.client.request(
                method=method,
                url=path,
                headers=headers,
                json=json_data
            )

            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000

            logger.info(
                "Backend API call completed",
                extra={
                    "method": method,
                    "endpoint": path,
                    "status_code": response.status_code,
                    "user_id": user_id,
                    "duration_ms": duration_ms
                }
            )

            return response

        except httpx.TimeoutException as e:
            logger.error(f"Backend request timeout: {e}")
            raise
        except httpx.ConnectError as e:
            logger.error(f"Backend connection error: {e}")
            raise

    async def get_tasks(self, user_id: str) -> list[dict]:
        """GET /tasks - List all tasks for user."""
        response = await self._request("GET", "/tasks", user_id)
        response.raise_for_status()
        return response.json()

    async def create_task(self, user_id: str, task_data: dict) -> dict:
        """POST /tasks - Create new task."""
        response = await self._request("POST", "/tasks", user_id, json_data=task_data)
        response.raise_for_status()
        return response.json()

    async def update_task(self, user_id: str, task_id: int, task_data: dict) -> dict:
        """PUT /tasks/{task_id} - Update task (title, description, priority, due_date)."""
        response = await self._request("PUT", f"/tasks/{task_id}", user_id, json_data=task_data)
        response.raise_for_status()
        return response.json()

    async def mark_task_completed(self, user_id: str, task_id: int) -> dict:
        """PATCH /tasks/{task_id} - Mark task as completed."""
        response = await self._request(
            "PATCH",
            f"/tasks/{task_id}",
            user_id,
            json_data={"completed": True}
        )
        response.raise_for_status()
        return response.json()

    async def delete_task(self, user_id: str, task_id: int) -> None:
        """DELETE /tasks/{task_id} - Delete task."""
        response = await self._request("DELETE", f"/tasks/{task_id}", user_id)
        response.raise_for_status()
```

---

## Step 5: MCP Tools Implementation

### 5.1 Create list_tasks Tool (src/tools/list_tasks.py)

**Test First** (`tests/integration/test_list_tasks.py`):
```python
import pytest
from src.tools.list_tasks import list_tasks_handler

@pytest.mark.asyncio
async def test_list_tasks_returns_user_tasks(mock_backend_client, test_user_id):
    """list_tasks returns tasks for authenticated user."""
    # Mock backend response
    mock_backend_client.get_tasks.return_value = [
        {"id": 1, "title": "Test task", "completed": False}
    ]

    result = await list_tasks_handler(user_id=test_user_id)
    assert len(result) == 1
    assert result[0]["title"] == "Test task"
```

**Implementation** (`src/tools/list_tasks.py`):
```python
from fastmcp import FastMCP
from src.client import BackendClient
from src.schemas.task import TaskResponse

mcp = FastMCP()
backend_client = BackendClient()

@mcp.tool()
async def list_tasks(user_id: str) -> list[dict]:
    """
    Retrieve all tasks for the authenticated user.

    Returns a list of tasks with ID, title, description, completion status,
    priority, and due date.
    """
    tasks = await backend_client.get_tasks(user_id)
    return [TaskResponse(**task).model_dump() for task in tasks]
```

### 5.2 Implement Remaining Tools

Follow the same TDD pattern for:
- `src/tools/create_task.py`
- `src/tools/update_task.py` (title, description, priority, due_date - no completion status)
- `src/tools/mark_completed.py` (dedicated tool for marking tasks complete)
- `src/tools/delete_task.py`

---

## Step 6: MCP Server Initialization

### 6.1 Create Server Entry Point (src/server.py)

```python
import logging
from fastmcp import FastMCP
from src.config import settings
from src.tools import list_tasks, create_task, update_task, mark_completed, delete_task

# Configure logging
logging.basicConfig(
    level=settings.mcp_log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Initialize MCP server
mcp = FastMCP(name="todo-mcp-server")

# Register tools
mcp.add_tool(list_tasks.list_tasks)
mcp.add_tool(create_task.create_task)
mcp.add_tool(update_task.update_task)
mcp.add_tool(mark_completed.mark_task_completed)
mcp.add_tool(delete_task.delete_task)

def main():
    """Run MCP server."""
    mcp.run(transport="http", port=settings.mcp_server_port)

if __name__ == "__main__":
    main()
```

---

## Step 7: Backend Modifications

### 7.1 Update Backend Dependencies

```python
# backend/src/api/dependencies.py

async def get_current_user_or_service(
    authorization: str = Header(None),
    session_token: str = Depends(cookie_or_header_session),
    x_user_id: str = Header(None, alias="X-User-ID")
) -> str:
    """Support both user session and service authentication."""
    # Service auth (MCP server)
    if x_user_id is not None:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(401, "Service auth requires Authorization header")

        token = authorization[7:]
        if token != settings.service_auth_token:
            raise HTTPException(401, "Invalid service token")

        return x_user_id

    # User session (frontend)
    return await get_current_user(session_token)
```

### 7.2 Update Task Endpoints

```python
# backend/src/api/routers/tasks.py

# Change all endpoints from:
#   current_user: str = Depends(get_current_user)
# To:
#   current_user: str = Depends(get_current_user_or_service)
```

---

## Step 8: Testing

### 8.1 Run Unit Tests

```bash
cd mcp-server
uv run pytest tests/unit -v
```

### 8.2 Run Integration Tests

```bash
# Start backend first
cd backend
uv run uvicorn src.api.main:app --reload

# In another terminal, run MCP tests
cd mcp-server
uv run pytest tests/integration -v
```

### 8.3 Test End-to-End

```bash
# Terminal 1: Backend
cd backend
uv run uvicorn src.api.main:app --reload

# Terminal 2: MCP Server
cd mcp-server
uv run mcp-server

# Terminal 3: Test with AI client (Claude Desktop)
# Configure Claude Desktop to connect to http://localhost:3000
```

---

## Step 9: Deployment Checklist

Before deploying to production:

- [ ] Generate secure SERVICE_AUTH_TOKEN (32+ characters)
- [ ] Configure environment variables in production
- [ ] Set MCP_LOG_LEVEL=INFO for production
- [ ] Test all 5 tools with real backend
- [ ] Verify error handling (401, 403, 404, 422, 500)
- [ ] Test timeout and retry logic
- [ ] Verify logging captures all required fields
- [ ] Run full test suite with 100% pass rate
- [ ] Document deployment process

---

## Common Issues & Solutions

### Issue 1: "Invalid service token"
**Cause**: SERVICE_AUTH_TOKEN mismatch between MCP server and backend
**Solution**: Ensure both services use the same token from environment

### Issue 2: "Missing X-User-ID header"
**Cause**: User context not extracted from MCP session
**Solution**: Verify MCP framework provides user context in request metadata

### Issue 3: Connection refused to backend
**Cause**: Backend not running or incorrect FASTAPI_BASE_URL
**Solution**: Start backend, verify URL in .env file

### Issue 4: Timeout errors
**Cause**: Backend response time > 30 seconds
**Solution**: Optimize backend queries, check database performance

---

## Next Steps

After completing implementation:

1. **Run `/sp.tasks`** to generate testable task breakdown
2. **Follow TDD workflow**: Write tests first, implement to pass
3. **Iterate incrementally**: One tool at a time
4. **Document as you go**: Update README with setup instructions

**Estimated Implementation Time**: 1-2 days for experienced Python developer following TDD

**Key Success Metrics**:
- All 5 tools functional
- Test coverage > 90%
- All acceptance scenarios passing
- Error handling validated
- Logging captures all required data
