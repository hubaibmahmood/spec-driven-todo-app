---
name: fastapi-to-mcp
description: Convert FastAPI backend endpoints into MCP (Model Context Protocol) server using Python SDK. Supports 4 auth patterns including service-to-service for microservices. Automatically discovers endpoints via OpenAPI schema, generates MCP tools with proper typing, retry logic, error handling, and creates production-ready MCP server. Use for AI chatbot interfaces, microservices integration, or enabling natural language task management.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# FastAPI to MCP Server Converter

## Overview

This skill automatically converts your FastAPI backend into a Model Context Protocol (MCP) server, exposing your REST API endpoints as AI-accessible tools. The generated MCP server runs alongside your FastAPI application and enables AI agents (like Claude) to interact with your backend through natural language.

## When to Use This Skill

**Invoke this skill when:**
- User wants to "create an MCP server" or "add MCP support"
- Building AI chatbot interfaces for existing FastAPI apps
- Enabling natural language interaction with backend operations
- Exposing FastAPI endpoints as tools for AI agents
- Converting REST APIs to AI-accessible interfaces
- Building AI-powered task management or CRUD operations

**Keywords that trigger this skill:**
- "MCP server", "Model Context Protocol"
- "AI chatbot for FastAPI", "natural language interface"
- "convert FastAPI to MCP", "expose endpoints to AI"
- "Claude Code tools from API"

## What This Skill Does

1. **Discovers FastAPI Endpoints**: Parses OpenAPI/Swagger schema from your running FastAPI app
2. **Generates MCP Server**: Creates Python MCP server using FastMCP library
3. **Maps Endpoints to Tools**: Converts each FastAPI endpoint to an MCP tool with proper schemas
4. **Preserves Authentication**: Maintains your existing auth patterns (user_id, JWT, etc.)
5. **Creates Production Structure**: Generates ready-to-deploy MCP server with tests and config

## Architecture

```
┌─────────────────┐
│   AI Agent      │
│ (Claude Code)   │
└────────┬────────┘
         │ MCP Protocol
         ▼
┌─────────────────┐
│  MCP Server     │
│  (Python SDK)   │
└────────┬────────┘
         │ HTTP/ASGI
         ▼
┌─────────────────┐
│  FastAPI App    │
│  (Existing API) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   PostgreSQL    │
│   (Database)    │
└─────────────────┘
```

## Prerequisites

**Required in your project:**
- ✅ FastAPI application running with `/docs` endpoint
- ✅ OpenAPI schema accessible at `/openapi.json`
- ✅ Python 3.12+
- ✅ SQLAlchemy models (recommended)

**Not required:**
- Running server (skill can start FastAPI temporarily for schema extraction)
- Specific folder structure (skill adapts to your layout)

## Process Flow

### Phase 1: Discovery & Analysis

1. **Locate FastAPI app**
   - Search for FastAPI application file (`main.py`, `app.py`, etc.)
   - Identify app instance (`app = FastAPI()`)
   - Read router configuration

2. **Extract OpenAPI schema**
   - Start FastAPI temporarily if not running
   - Fetch `/openapi.json` or read from docs
   - Parse endpoints, request/response schemas, descriptions

3. **Analyze authentication patterns**
   - Detect `Depends()` usage in routes
   - Identify user identification methods (user_id, JWT, session)
   - Map authentication to MCP tool parameters

### Phase 2: Generation

1. **Create MCP server structure** (choose based on project complexity)

   **Option A: Simple Structure** (for quick prototypes, <5 tools):
   ```
   mcp-server/
   ├── __init__.py
   ├── main.py              # MCP server entry point
   ├── tools.py             # ALL tool definitions in one file
   ├── client.py            # FastAPI HTTP client
   ├── config.py            # Configuration
   ├── pyproject.toml       # Dependencies
   └── tests/
       └── test_tools.py    # Tool tests
   ```

   **Option B: Structured (Microservices)** 🆕 (for production, 5+ tools, microservices):
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
   │   ├── contract/          # Schema validation tests
   │   ├── unit/              # Component tests
   │   └── integration/       # End-to-end tests
   ├── pyproject.toml
   ├── .env
   ├── .env.example
   └── README.md
   ```
   **Recommendation**: Use Option B for microservices (Pattern 4)

2. **Generate tool definitions**
   - Convert each endpoint to MCP tool
   - Map Pydantic models to JSON schemas
   - Preserve descriptions and examples
   - Add proper type annotations

3. **Create integration layer**
   - HTTP client for FastAPI communication
   - Error handling and retries
   - Response transformation

4. **Write configuration**
   - Environment variables (API URL, ports)
   - Logging configuration
   - Transport settings (stdio, HTTP, SSE)

### Phase 3: Testing & Documentation

1. **Generate tests**
   - pytest fixtures for MCP client
   - Test each tool against FastAPI endpoints
   - Integration tests with real database

2. **Create documentation**
   - README with setup instructions
   - Tool usage examples
   - Deployment guide

3. **Integration with Spec-Kit Plus**
   - Suggest ADR for architectural decision
   - Create PHR for generation process
   - Update constitution with MCP patterns

## Tool Mapping Strategy

### Endpoint → Tool Conversion Rules

| FastAPI Endpoint | MCP Tool Name | Parameters | Output |
|------------------|---------------|------------|--------|
| `POST /tasks` | `create_task` | `user_id`, `title`, `description` | `task_id`, `status` |
| `GET /tasks` | `list_tasks` | `user_id`, `status` (optional) | Array of tasks |
| `PUT /tasks/{id}` | `update_task` | `user_id`, `task_id`, `title`, `description` | Updated task |
| `DELETE /tasks/{id}` | `delete_task` | `user_id`, `task_id` | `status`, `message` |
| `PATCH /tasks/{id}/complete` | `complete_task` | `user_id`, `task_id` | Completed task |

### Schema Mapping

**FastAPI Pydantic → MCP JSON Schema:**
```python
# FastAPI Model
class TaskCreate(BaseModel):
    title: str = Field(..., max_length=200)
    description: str | None = Field(None, max_length=1000)

# Generated MCP Tool Schema
{
    "type": "object",
    "properties": {
        "user_id": {"type": "string", "description": "User identifier"},
        "title": {"type": "string", "maxLength": 200, "description": "Task title"},
        "description": {"type": "string", "maxLength": 1000, "description": "Task description"}
    },
    "required": ["user_id", "title"]
}
```

## Authentication Handling

**IMPORTANT**: Choose the authentication pattern that matches your architecture:

| Pattern | Use Case | Complexity | Backend Changes |
|---------|----------|------------|-----------------|
| **Pattern 1: user_id** | Simple apps, prototypes | Low | None |
| **Pattern 2: Session** | Traditional web apps | Low | None |
| **Pattern 3: JWT** | Modern APIs | Medium | None |
| **Pattern 4: Service-to-Service** 🆕 | **Microservices** | High | **Required** |

### Pattern 1: user_id Parameter (Simple Apps)

**When to use:** Stateless operations, multi-tenant systems, prototypes

```python
# FastAPI Endpoint
@router.post("/tasks")
async def create_task(
    user_id: str,
    task: TaskCreate,
    db: AsyncSession = Depends(get_db)
):
    return await task_service.create(user_id, task, db)

# Generated MCP Tool
@mcp.tool()
async def create_task(user_id: str, title: str, description: str = None) -> dict:
    """Create a new task for the specified user."""
    response = await http_client.post(
        "/tasks",
        params={"user_id": user_id},
        json={"title": title, "description": description}
    )
    return response.json()
```

### Pattern 2: Session-Based Auth

**When to use:** Traditional web apps with sessions

```python
# MCP Server Configuration
config = {
    "session_token": os.getenv("API_SESSION_TOKEN"),
    "session_cookie": "session_id"
}

# Generated Tool
async def create_task(title: str, description: str = None) -> dict:
    """Create task using session authentication."""
    response = await http_client.post(
        "/tasks",
        json={"title": title, "description": description},
        cookies={"session_id": config["session_token"]}
    )
    return response.json()
```

### Pattern 3: JWT Bearer Token

**When to use:** Modern APIs with JWT auth

```python
# Generated Tool
async def create_task(user_id: str, title: str, description: str = None) -> dict:
    """Create task with JWT authentication."""
    # Get JWT token for user (from config or auth service)
    jwt_token = await get_jwt_token(user_id)

    response = await http_client.post(
        "/tasks",
        json={"title": title, "description": description},
        headers={"Authorization": f"Bearer {jwt_token}"}
    )
    return response.json()
```

### Pattern 4: Service-to-Service Authentication 🆕 (Microservices)

**When to use:**
- ✅ Microservices architecture (MCP server as separate service)
- ✅ Need service identity + user context
- ✅ Security-critical systems
- ✅ Data isolation requirements

**⚠️ REQUIRES BACKEND MODIFICATIONS**

**Architecture:**
```
MCP Server (Service Identity: SERVICE_AUTH_TOKEN)
     ↓ Headers: Authorization: Bearer {token} + X-User-ID: {user_id}
FastAPI Backend (Validates: service token + user context)
     ↓ Enforces: data isolation per user
Database
```

**Generated MCP Client:**
```python
# mcp-server/src/client.py
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

class BackendClient:
    def _build_headers(self, user_id: str) -> dict[str, str]:
        """Build service auth headers."""
        return {
            "Authorization": f"Bearer {settings.service_auth_token}",
            "X-User-ID": user_id,
            "Content-Type": "application/json",
        }

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=2))
    async def _request(self, method: str, endpoint: str, user_id: str, json=None):
        """Make request with retry logic."""
        headers = self._build_headers(user_id)
        response = await self.client.request(method, endpoint, headers=headers, json=json)
        return response
```

**Generated Backend Dependency:**
```python
# backend/src/api/dependencies.py (AUTO-GENERATED)
import hmac

async def get_current_user_or_service(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    x_user_id: Optional[str] = Header(None, alias="X-User-ID"),
    db: AsyncSession = Depends(get_db),
) -> str:
    """Dual authentication: service OR user session."""

    # Service flow (MCP server)
    if x_user_id is not None:
        token = credentials.credentials
        if not hmac.compare_digest(token, settings.SERVICE_AUTH_TOKEN):
            raise HTTPException(401, "Invalid service token")
        return x_user_id

    # User session flow (frontend)
    user_id = await validate_session(credentials.credentials, db)
    if not user_id:
        raise HTTPException(401, "Invalid session")
    return user_id
```

**Skill will:**
1. ✅ Generate SERVICE_AUTH_TOKEN (32+ chars)
2. ✅ Create MCP client with service auth
3. ✅ Generate backend dependency modifications
4. ✅ Update all endpoints to use dual auth
5. ✅ Add retry logic with exponential backoff
6. ✅ Implement AI-friendly error taxonomy

**See [MICROSERVICES_PATTERNS.md](MICROSERVICES_PATTERNS.md) for complete guide**

### Production Patterns (Integrated from Real Implementation)

Based on successful production deployment (Spec 006: Todo App MCP Server), the following patterns are now integrated into the skill templates:

#### Error Taxonomy (7 Types)

AI-friendly error classification for better error handling and user communication:

| Error Type | HTTP Status | When to Use | AI Message Example |
|------------|-------------|-------------|-------------------|
| `authentication_error` | 401 | Service token invalid | "Unable to authenticate with backend. Check SERVICE_AUTH_TOKEN configuration." |
| `authorization_error` | 403 | User lacks permission | "You don't have permission to access this task. It may belong to another user." |
| `not_found_error` | 404 | Resource doesn't exist | "Task not found with ID: 123. It may have been deleted or doesn't belong to you." |
| `validation_error` | 422 | Invalid input data | "Title must be between 1 and 200 characters. Received: empty string." |
| `backend_error` | 500 | Server-side error | "Backend service encountered an error. Please try again in a moment." |
| `timeout_error` | Timeout | Request timeout | "Request timed out after 30 seconds. Backend may be experiencing high load." |
| `connection_error` | Network | Connection failed | "Unable to connect to backend service. Check FASTAPI_BASE_URL and network." |

**Implementation** (available in schemas.template):
```python
ERROR_TYPES = {
    "authentication_error": "authentication_error",
    "authorization_error": "authorization_error",
    "not_found_error": "not_found_error",
    "validation_error": "validation_error",
    "backend_error": "backend_error",
    "timeout_error": "timeout_error",
    "connection_error": "connection_error",
}

class ErrorResponse(BaseModel):
    """Standardized error response for AI agents."""
    error_type: str  # From ERROR_TYPES
    message: str     # Human-readable for AI
    details: Optional[dict] = None  # Structured data
    suggestions: List[str] = []     # Actionable steps
```

**Benefits**:
- AI agents can explain errors clearly to users
- Consistent error format across all tools
- Actionable suggestions for error resolution
- Structured for programmatic handling

#### Test Organization (Contract/Unit/Integration)

Production-ready test structure for comprehensive validation:

```
tests/
├── conftest.py              # Shared pytest fixtures
├── contract/                # Schema validation tests
│   └── test_task_schemas.py    # Pydantic model validation
├── unit/                    # Component tests
│   ├── test_client.py           # HTTP client tests
│   └── test_config.py           # Configuration tests
└── integration/             # End-to-end workflow tests
    ├── test_user_context.py     # Data isolation tests (SC-001)
    └── test_workflows.py        # Cross-tool workflows (SC-002-004)
```

**Test Types**:
1. **Contract Tests**: Validate that Pydantic schemas match backend API contracts
2. **Unit Tests**: Test individual components in isolation with mocks
3. **Integration Tests**: Test complete workflows with mocked backend

**Pattern 4 Specific Tests**:
- User context propagation and isolation
- Service auth header validation
- Retry logic verification
- Structured logging validation

#### Context-Based User Extraction

Modern pattern using FastMCP Context instead of direct parameters:

```python
from fastmcp import Context

async def list_tasks(ctx: Context) -> list[dict]:
    """List tasks - user ID extracted from context."""
    # Extract user_id from MCP session context
    user_id = getattr(ctx.request_context, "user_id", None) or "test_user_123"

    # Use user_id for backend request
    client = BackendClient()
    response = await client.get_tasks(user_id)
    return response.json()
```

**Benefits**:
- Cleaner tool signatures (no user_id parameter pollution)
- Centralized user extraction logic
- Easy to add test fallbacks
- Supports future MCP session improvements

#### Modular Tool Structure

For Pattern 4 or projects with 5+ tools, use modular structure:

```
src/tools/
├── __init__.py
├── list_tasks.py        # One file per tool
├── create_task.py
├── update_task.py
├── mark_completed.py
└── delete_task.py
```

**Each tool file contains**:
- Complete error handling (all 7 error types)
- Structured logging with audit fields
- Context-based user extraction
- Resource cleanup (finally block)
- Comprehensive docstrings with examples

**When to use**:
- ✅ Microservices architecture (Pattern 4)
- ✅ 5+ tools
- ✅ Team collaboration (reduces merge conflicts)
- ✅ Independent tool testing

**When NOT to use**:
- ❌ Simple prototypes
- ❌ < 5 tools
- ❌ Solo developer, quick iteration

## Generated Code Structure

### main.py (MCP Server Entry Point)

```python
"""MCP Server for [Your App Name]

Auto-generated by fastapi-to-mcp skill
Generated: 2025-12-17
"""

import asyncio
from mcp.server.fastmcp import FastMCP, Icon
from tools import register_tools
from config import settings

# Initialize MCP server
mcp = FastMCP(
    name=settings.MCP_SERVER_NAME,
    version="1.0.0",
    website_url=settings.FASTAPI_BASE_URL,
)

# Register all tools from FastAPI endpoints
register_tools(mcp)

def main():
    """Entry point for MCP server."""
    # Choose transport based on use case:
    # - "stdio": For local Claude Code integration (default)
    # - "streamable-http": For web-based clients
    # - "sse": For server-sent events
    mcp.run(transport=settings.MCP_TRANSPORT)

if __name__ == "__main__":
    main()
```

### tools.py (Generated Tool Definitions)

```python
"""MCP Tools generated from FastAPI endpoints

Each tool corresponds to a FastAPI endpoint and maintains
the same request/response structure.
"""

from typing import Optional
from client import APIClient
from config import settings

def register_tools(mcp: FastMCP):
    """Register all FastAPI endpoints as MCP tools."""

    client = APIClient(base_url=settings.FASTAPI_BASE_URL)

    @mcp.tool()
    async def create_task(
        user_id: str,
        title: str,
        description: Optional[str] = None
    ) -> dict:
        """Create a new task.

        Args:
            user_id: User identifier who owns the task
            title: Task title (max 200 characters)
            description: Optional task description

        Returns:
            dict: Created task with id, status, and title

        Example:
            >>> await create_task("user123", "Buy groceries", "Milk, eggs, bread")
            {"task_id": 5, "status": "created", "title": "Buy groceries"}
        """
        response = await client.post(
            "/tasks",
            params={"user_id": user_id},
            json={"title": title, "description": description}
        )
        return response

    @mcp.tool()
    async def list_tasks(
        user_id: str,
        status: Optional[str] = "all"
    ) -> list[dict]:
        """Retrieve tasks for a user.

        Args:
            user_id: User identifier
            status: Filter by status ("all", "pending", "completed")

        Returns:
            list[dict]: Array of task objects

        Example:
            >>> await list_tasks("user123", "pending")
            [{"id": 1, "title": "Buy groceries", "completed": false}, ...]
        """
        response = await client.get(
            "/tasks",
            params={"user_id": user_id, "status": status}
        )
        return response

    # Additional tools generated here...
```

### client.py (FastAPI HTTP Client)

```python
"""HTTP client for FastAPI backend communication."""

import httpx
from typing import Any, Optional
from config import settings

class APIClient:
    """Async HTTP client for FastAPI endpoints."""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.AsyncClient(
            base_url=base_url,
            timeout=30.0,
            follow_redirects=True
        )

    async def post(
        self,
        path: str,
        json: Optional[dict] = None,
        params: Optional[dict] = None,
        headers: Optional[dict] = None
    ) -> Any:
        """POST request to FastAPI endpoint."""
        response = await self.client.post(
            path,
            json=json,
            params=params,
            headers=headers
        )
        response.raise_for_status()
        return response.json()

    async def get(
        self,
        path: str,
        params: Optional[dict] = None,
        headers: Optional[dict] = None
    ) -> Any:
        """GET request to FastAPI endpoint."""
        response = await self.client.get(
            path,
            params=params,
            headers=headers
        )
        response.raise_for_status()
        return response.json()

    # Additional methods (put, delete, patch) generated here...

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
```

### config.py (Configuration)

```python
"""MCP Server configuration."""

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """MCP Server settings."""

    # MCP Server
    MCP_SERVER_NAME: str = "Todo App MCP Server"
    MCP_TRANSPORT: str = "stdio"  # stdio, streamable-http, sse
    MCP_PORT: int = 8001

    # FastAPI Backend
    FASTAPI_BASE_URL: str = "http://localhost:8000"
    FASTAPI_API_PREFIX: str = "/api/v1"

    # Authentication
    AUTH_METHOD: str = "user_id"  # user_id, jwt, session

    class Config:
        env_file = ".env"
        env_prefix = "MCP_"

settings = Settings()
```

### pyproject.toml (Dependencies)

```toml
[project]
name = "todo-app-mcp-server"
version = "1.0.0"
description = "MCP Server for Todo App FastAPI backend"
requires-python = ">=3.12"

dependencies = [
    "fastmcp>=0.5.0",
    "httpx>=0.27.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "python-dotenv>=1.0.0",
    "tenacity>=8.0.0",  # For retry logic (Pattern 4)
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "pytest-cov>=4.1.0",
]

[project.scripts]
mcp-server = "main:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

## Integration with Spec-Kit Plus

### Automatic ADR Suggestion

After generating the MCP server, the skill will suggest creating an ADR:

```
📋 Architectural decision detected: FastAPI to MCP Server Integration

This decision involves:
- Exposing FastAPI endpoints as AI-accessible tools
- Choosing MCP transport layer (stdio vs HTTP)
- Authentication pattern for AI agents
- Deployment architecture (same container vs separate)

Document reasoning and tradeoffs? Run `/sp.adr fastapi-mcp-integration`
```

### PHR Creation

The skill automatically creates a Prompt History Record:

```yaml
---
id: 25
title: Generate MCP Server from FastAPI Backend
stage: implementation
date: 2025-12-17
surface: agent
model: claude-sonnet-4-5
feature: ai-chatbot-interface
branch: feature/mcp-server
user: developer
command: Skill:fastapi-to-mcp
labels: ["mcp", "fastapi", "code-generation", "ai-integration"]
links:
  spec: specs/ai-chatbot-interface/spec.md
  adr: history/adr/fastapi-mcp-integration.md
---

## Prompt
Create MCP server for Todo App FastAPI backend

## Response
Generated MCP server at `mcp-server/` with 5 tools:
- create_task, list_tasks, update_task, delete_task, complete_task
...
```

## Usage Instructions

### Step 1: Invoke the Skill

**User says:**
> "Create an MCP server for my FastAPI todo app"

**Skill automatically:**
1. Discovers your FastAPI app structure
2. Extracts OpenAPI schema
3. Generates MCP server code
4. Creates configuration files
5. Writes tests
6. Suggests ADR for documentation

### Step 2: Review Generated Code

The skill will show you:
- Generated file structure
- Tool definitions
- Configuration options

### Step 3: Test MCP Server

```bash
# Navigate to MCP server directory
cd mcp-server

# Install dependencies
uv sync

# Run tests
pytest tests/

# Start MCP server
uv run mcp-server
```

### Step 4: Integrate with Claude Code

Add to your Claude Code configuration:

```json
{
  "mcpServers": {
    "todo-app": {
      "command": "uv",
      "args": ["run", "mcp-server"],
      "cwd": "/path/to/project/mcp-server"
    }
  }
}
```

### Step 5: Use in Claude Code

```
# Claude Code can now use your tools
> Add a task: "Buy groceries - milk, eggs, bread"

[Claude uses create_task tool]
✓ Task created: "Buy groceries" (ID: 5)

> Show all my pending tasks

[Claude uses list_tasks tool]
Found 3 pending tasks:
1. Buy groceries
2. Call mom
3. Review PR #42
```

## Advanced Features

### Custom Tool Transformations

If you need custom logic (beyond simple endpoint mapping), create `transformations.py`:

```python
# mcp-server/transformations.py

def transform_create_task(fastapi_response: dict) -> dict:
    """Transform FastAPI response to more AI-friendly format."""
    return {
        "task_id": fastapi_response["id"],
        "status": "created",
        "title": fastapi_response["title"],
        "created_at": fastapi_response["created_at"],
        "message": f"Successfully created task: {fastapi_response['title']}"
    }

TRANSFORMATIONS = {
    "create_task": transform_create_task,
    # Add more transformations as needed
}
```

### Error Handling

Generated tools include comprehensive error handling:

```python
@mcp.tool()
async def create_task(user_id: str, title: str, description: str = None) -> dict:
    """Create a new task."""
    try:
        response = await client.post("/tasks", ...)
        return response
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            return {"error": "Authentication failed", "status": "unauthorized"}
        elif e.response.status_code == 400:
            return {"error": e.response.json().get("detail"), "status": "bad_request"}
        else:
            return {"error": "Server error", "status": "error"}
    except httpx.RequestError as e:
        return {"error": f"Connection failed: {str(e)}", "status": "connection_error"}
```

### Logging Configuration

```python
# mcp-server/config.py (extended)

import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("mcp-server.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("mcp-server")
```

## Best Practices Applied

This skill follows 2025 MCP best practices:

1. ✅ **Focused Toolset**: Groups related operations into well-designed tools
2. ✅ **Security Scanning**: Includes dependency vulnerability checks
3. ✅ **Comprehensive Testing**: pytest tests for all tools
4. ✅ **Docker Ready**: Generates Dockerfile for containerization
5. ✅ **Documentation**: Clear API references and usage examples
6. ✅ **Detailed Logging**: Request/response logging for debugging
7. ✅ **Type Safety**: Full type annotations with mypy support

## Troubleshooting

### Issue: Can't find FastAPI app

**Solution:** Ensure your FastAPI app is in one of these locations:
- `app/main.py`
- `src/app.py`
- `main.py`
- `api/main.py`

Or specify path explicitly:
```bash
MCP_FASTAPI_APP_PATH=/path/to/app.py
```

### Issue: OpenAPI schema not accessible

**Solution:** Start FastAPI server first:
```bash
uvicorn app.main:app --reload
```

Then run skill again.

### Issue: Authentication not working

**Solution:** Check authentication pattern in generated `config.py`:
- For `user_id` param: Set `AUTH_METHOD=user_id`
- For JWT: Set `AUTH_METHOD=jwt` and provide token
- For session: Set `AUTH_METHOD=session` and provide session cookie

## Reference

For detailed information, see:
- [MCP_REFERENCE.md](MCP_REFERENCE.md) - Complete MCP SDK reference
- [FASTAPI_PATTERNS.md](FASTAPI_PATTERNS.md) - FastAPI integration patterns
- [MICROSERVICES_PATTERNS.md](MICROSERVICES_PATTERNS.md) 🆕 - **Service-to-service auth (Pattern 4)**
- [examples/todo-app-example.py](examples/todo-app-example.py) - Complete example
- [templates/](templates/) - Code generation templates

## Pattern Selection Guide

Choose the right authentication pattern for your project:

```
┌─────────────────────────────────────────────────┐
│ Is this a microservices architecture?          │
├─────────────────────────────────────────────────┤
│ YES → Pattern 4 (Service-to-Service)           │
│       - Requires backend modifications         │
│       - Best security & isolation               │
│       - See MICROSERVICES_PATTERNS.md           │
├─────────────────────────────────────────────────┤
│ NO → Is this a modern SPA with JWT?            │
│      YES → Pattern 3 (JWT Bearer)               │
│      NO → Traditional web app with sessions?    │
│           YES → Pattern 2 (Session)             │
│           NO → Pattern 1 (user_id param)        │
└─────────────────────────────────────────────────┘
```

## Quick Checklist

After skill execution, verify:

### General (All Patterns)
- [ ] MCP server directory created with proper structure
- [ ] All FastAPI endpoints mapped to MCP tools
- [ ] Tool schemas match FastAPI Pydantic models
- [ ] Authentication pattern correctly implemented
- [ ] Tests generated and passing
- [ ] Configuration file created with environment variables
- [ ] README documentation generated
- [ ] ADR suggested for architectural decision
- [ ] PHR created for generation process
- [ ] MCP server successfully runs with `uv run mcp-server`

### Pattern 4 (Service-to-Service) - Additional Checks
- [ ] SERVICE_AUTH_TOKEN generated (32+ characters)
- [ ] Token added to both mcp-server/.env and backend/.env
- [ ] Backend `config.py` updated with SERVICE_AUTH_TOKEN field
- [ ] Backend dependencies.py has `get_current_user_or_service()` function
- [ ] All task endpoints updated to use `get_current_user_or_service`
- [ ] Constant-time comparison (`hmac.compare_digest()`) used
- [ ] Retry logic with tenacity implemented (3 attempts, exponential backoff)
- [ ] Structured logging with all required fields
- [ ] Error taxonomy with 7 error types implemented
- [ ] X-User-ID header validation on backend
- [ ] Test fixtures for service auth created in both projects
