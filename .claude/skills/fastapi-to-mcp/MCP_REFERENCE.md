# Model Context Protocol (MCP) Python SDK Reference

Complete reference for building MCP servers with the official Python SDK.

## Table of Contents

- [Overview](#overview)
- [FastMCP Quick Start](#fastmcp-quick-start)
- [Tool Definition](#tool-definition)
- [Server Configuration](#server-configuration)
- [Transport Options](#transport-options)
- [Error Handling](#error-handling)
- [Testing](#testing)
- [Best Practices](#best-practices)

## Overview

Model Context Protocol (MCP) enables AI agents to interact with external tools and data sources through a standardized interface. The Python SDK provides two APIs:

1. **FastMCP** (Recommended): High-level, decorator-based API
2. **Low-level Server API**: Manual request handling for advanced use cases

## FastMCP Quick Start

### Installation

```bash
pip install fastmcp httpx pydantic pydantic-settings
```

### Minimal Server

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("My Server")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

if __name__ == "__main__":
    mcp.run()  # Defaults to stdio transport
```

### Running the Server

```bash
# Stdio transport (for Claude Code)
python server.py

# HTTP transport (for web clients)
python server.py --transport streamable-http --port 8000

# SSE transport
python server.py --transport sse --port 8000
```

## Tool Definition

### Basic Tool

```python
@mcp.tool()
def greet(name: str) -> str:
    """Greet someone by name.

    Args:
        name: Person's name

    Returns:
        Greeting message
    """
    return f"Hello, {name}!"
```

**Key Points:**
- Docstring becomes tool description (required for good AI performance)
- Type hints are required and converted to JSON schema
- Return type must be specified

### Tool with Optional Parameters

```python
from typing import Optional

@mcp.tool()
def create_task(
    title: str,
    description: Optional[str] = None,
    priority: str = "medium"
) -> dict:
    """Create a new task.

    Args:
        title: Task title (required)
        description: Optional task description
        priority: Task priority (low, medium, high)

    Returns:
        Created task object
    """
    return {
        "id": 1,
        "title": title,
        "description": description,
        "priority": priority,
        "status": "created"
    }
```

### Tool with Complex Return Types

```python
from typing import List, Dict, Any
from pydantic import BaseModel

class Task(BaseModel):
    id: int
    title: str
    completed: bool

@mcp.tool()
def list_tasks(status: str = "all") -> List[Task]:
    """List tasks with optional filtering.

    Args:
        status: Filter by status (all, pending, completed)

    Returns:
        List of task objects
    """
    tasks = [
        Task(id=1, title="Buy groceries", completed=False),
        Task(id=2, title="Call mom", completed=True),
    ]

    if status == "pending":
        return [t for t in tasks if not t.completed]
    elif status == "completed":
        return [t for t in tasks if t.completed]
    return tasks
```

### Tool with Structured Output Schema

```python
import mcp.types as types

@mcp.tool()
async def get_weather(city: str) -> dict:
    """Get weather for a city.

    Returns structured weather data.
    """
    return {
        "temperature": 22,
        "condition": "sunny",
        "humidity": 60,
        "city": city
    }

# Define output schema (optional but recommended)
get_weather._output_schema = {
    "type": "object",
    "properties": {
        "temperature": {"type": "number"},
        "condition": {"type": "string"},
        "humidity": {"type": "number"},
        "city": {"type": "string"}
    },
    "required": ["temperature", "condition", "humidity", "city"]
}
```

### Async Tools

```python
import httpx

@mcp.tool()
async def fetch_url(url: str) -> str:
    """Fetch content from a URL.

    Args:
        url: URL to fetch

    Returns:
        Response content
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.text
```

## Server Configuration

### Server Metadata

```python
from mcp.server.fastmcp import FastMCP, Icon

mcp = FastMCP(
    name="My API Server",
    version="1.0.0",
    website_url="https://myapi.com",
    icons=[
        Icon(
            src="https://myapi.com/icon.png",
            mimeType="image/png"
        )
    ]
)
```

### Environment-Based Configuration

```python
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    server_name: str = "MCP Server"
    server_version: str = "1.0.0"
    transport: str = "stdio"
    port: int = 8000
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_prefix = "MCP_"

settings = Settings()

mcp = FastMCP(
    name=settings.server_name,
    version=settings.server_version
)

if __name__ == "__main__":
    mcp.run(transport=settings.transport)
```

### Custom Server Initialization

```python
mcp = FastMCP("My Server")

@mcp.on_startup()
async def startup():
    """Run on server startup."""
    print("Server starting...")
    # Initialize database connections
    # Load configurations
    # Start background tasks

@mcp.on_shutdown()
async def shutdown():
    """Run on server shutdown."""
    print("Server shutting down...")
    # Close database connections
    # Clean up resources
```

## Transport Options

### 1. Stdio Transport (Default)

**Use case:** Local integration with Claude Code

```python
mcp.run(transport="stdio")
```

**Client configuration (Claude Code):**
```json
{
  "mcpServers": {
    "my-server": {
      "command": "python",
      "args": ["server.py"],
      "cwd": "/path/to/server"
    }
  }
}
```

### 2. Streamable HTTP Transport

**Use case:** Web-based clients, remote access

```python
mcp.run(transport="streamable-http", port=8000)
```

**Access:** `http://localhost:8000/mcp`

**Client code:**
```python
from mcp.client.session import ClientSession
from mcp.client.streamableHttp import StreamableHTTPClientTransport

transport = StreamableHTTPClientTransport(
    url="http://localhost:8000/mcp"
)

async with ClientSession(transport.read, transport.write) as session:
    await session.initialize()
    result = await session.call_tool("add", {"a": 5, "b": 3})
    print(result)
```

### 3. SSE (Server-Sent Events) Transport

**Use case:** Real-time updates, event streaming

```python
mcp.run(transport="sse", port=8000)
```

## Error Handling

### Tool-Level Error Handling

```python
from httpx import HTTPStatusError, RequestError

@mcp.tool()
async def fetch_data(url: str) -> dict:
    """Fetch data from API."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}

    except HTTPStatusError as e:
        return {
            "status": "error",
            "error": f"HTTP {e.response.status_code}",
            "message": str(e)
        }

    except RequestError as e:
        return {
            "status": "error",
            "error": "connection_failed",
            "message": str(e)
        }

    except Exception as e:
        return {
            "status": "error",
            "error": "unexpected_error",
            "message": str(e)
        }
```

### Server-Level Error Handling

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("mcp-server")

@mcp.tool()
async def risky_operation(data: str) -> dict:
    """Operation that might fail."""
    try:
        logger.info(f"Processing: {data}")
        result = await process_data(data)
        logger.info(f"Success: {result}")
        return {"status": "success", "result": result}

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return {
            "status": "error",
            "error": type(e).__name__,
            "message": str(e)
        }
```

## Testing

### Testing with In-Memory Transport

```python
# test_server.py
import pytest
from mcp.client.session import ClientSession
from mcp.shared.memory import create_connected_server_and_client_session
from server import mcp

@pytest.fixture
async def client_session():
    """Create test client session."""
    async with create_connected_server_and_client_session(
        mcp,
        raise_exceptions=True
    ) as session:
        yield session

@pytest.mark.asyncio
async def test_add_tool(client_session: ClientSession):
    """Test add tool."""
    result = await client_session.call_tool("add", {"a": 5, "b": 3})

    assert result.structuredContent == {"result": 8}
    assert result.content[0].text == "8"

@pytest.mark.asyncio
async def test_list_tools(client_session: ClientSession):
    """Test tool listing."""
    tools = await client_session.list_tools()

    tool_names = [t.name for t in tools.tools]
    assert "add" in tool_names
    assert "greet" in tool_names
```

### Testing Against Real FastAPI Backend

```python
# test_integration.py
import pytest
import httpx
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioClientTransport, StdioServerParameters

@pytest.fixture
async def fastapi_server():
    """Start FastAPI server for testing."""
    # Start server in background
    process = await asyncio.create_subprocess_exec(
        "uvicorn", "app.main:app", "--port", "8000"
    )
    await asyncio.sleep(2)  # Wait for server to start

    yield "http://localhost:8000"

    # Cleanup
    process.terminate()
    await process.wait()

@pytest.fixture
async def mcp_client(fastapi_server):
    """Create MCP client connected to server."""
    transport = StdioServerParameters(
        command="python",
        args=["mcp_server/main.py"]
    )

    async with stdio_client(transport) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            yield session

@pytest.mark.asyncio
async def test_create_task(mcp_client, fastapi_server):
    """Test create_task tool."""
    result = await mcp_client.call_tool(
        "create_task",
        {
            "user_id": "test_user",
            "title": "Test task",
            "description": "Test description"
        }
    )

    assert result.structuredContent["status"] == "created"
    assert "task_id" in result.structuredContent
```

## Best Practices

### 1. Clear Tool Descriptions

```python
# ✅ Good: Comprehensive docstring
@mcp.tool()
def search_users(
    query: str,
    limit: int = 10,
    include_inactive: bool = False
) -> List[dict]:
    """Search for users by name or email.

    Searches across username and email fields using case-insensitive
    matching. Returns up to `limit` results.

    Args:
        query: Search term (matches username or email)
        limit: Maximum number of results (default: 10, max: 100)
        include_inactive: Include deactivated users (default: False)

    Returns:
        List of user objects with id, username, email, and is_active

    Example:
        >>> search_users("john", limit=5)
        [{"id": 1, "username": "john_doe", "email": "john@example.com", ...}]
    """
    # Implementation
    pass

# ❌ Bad: Minimal docstring
@mcp.tool()
def search_users(query: str, limit: int = 10) -> List[dict]:
    """Search users."""
    pass
```

### 2. Type Safety

```python
from typing import Literal
from pydantic import BaseModel, Field

class TaskStatus(str):
    """Valid task statuses."""
    PENDING = "pending"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class TaskCreate(BaseModel):
    """Task creation model."""
    title: str = Field(..., max_length=200, description="Task title")
    description: str | None = Field(None, max_length=1000)
    priority: Literal["low", "medium", "high"] = "medium"

@mcp.tool()
async def create_task(
    user_id: str,
    task: TaskCreate
) -> dict:
    """Create task with validated input."""
    # Pydantic validation ensures data integrity
    return {"id": 1, **task.model_dump()}
```

### 3. Resource Cleanup

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan():
    """Manage server lifecycle."""
    # Startup
    db = await init_database()
    http_client = httpx.AsyncClient()

    yield {"db": db, "http_client": http_client}

    # Shutdown
    await db.close()
    await http_client.aclose()

mcp = FastMCP("My Server")

@mcp.tool()
async def db_query(query: str) -> list:
    """Query database."""
    db = mcp.state["db"]
    return await db.fetch(query)
```

### 4. Structured Error Responses

```python
from enum import Enum
from pydantic import BaseModel

class ErrorCode(str, Enum):
    """Standard error codes."""
    UNAUTHORIZED = "unauthorized"
    NOT_FOUND = "not_found"
    VALIDATION_ERROR = "validation_error"
    SERVER_ERROR = "server_error"

class ErrorResponse(BaseModel):
    """Standard error response."""
    status: Literal["error"]
    error_code: ErrorCode
    message: str
    details: dict | None = None

class SuccessResponse(BaseModel):
    """Standard success response."""
    status: Literal["success"]
    data: dict

@mcp.tool()
async def get_user(user_id: int) -> ErrorResponse | SuccessResponse:
    """Get user by ID with structured response."""
    try:
        user = await fetch_user(user_id)
        if not user:
            return ErrorResponse(
                status="error",
                error_code=ErrorCode.NOT_FOUND,
                message=f"User {user_id} not found"
            )

        return SuccessResponse(
            status="success",
            data=user
        )

    except Exception as e:
        return ErrorResponse(
            status="error",
            error_code=ErrorCode.SERVER_ERROR,
            message="Internal server error",
            details={"exception": str(e)}
        )
```

### 5. Logging and Monitoring

```python
import logging
from functools import wraps
import time

logger = logging.getLogger("mcp-tools")

def logged_tool(func):
    """Decorator for logging tool execution."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.time()
        logger.info(f"Tool called: {func.__name__} with args={args}, kwargs={kwargs}")

        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start
            logger.info(
                f"Tool completed: {func.__name__} "
                f"in {duration:.2f}s with result={result}"
            )
            return result

        except Exception as e:
            duration = time.time() - start
            logger.error(
                f"Tool failed: {func.__name__} "
                f"after {duration:.2f}s with error={e}",
                exc_info=True
            )
            raise

    return wrapper

@mcp.tool()
@logged_tool
async def expensive_operation(data: str) -> dict:
    """Operation with automatic logging."""
    await asyncio.sleep(2)  # Simulate work
    return {"status": "success", "processed": len(data)}
```

## Performance Optimization

### 1. Connection Pooling

```python
import httpx

class APIClient:
    """HTTP client with connection pooling."""

    def __init__(self, base_url: str):
        self.client = httpx.AsyncClient(
            base_url=base_url,
            limits=httpx.Limits(
                max_keepalive_connections=20,
                max_connections=100
            ),
            timeout=httpx.Timeout(30.0),
            http2=True  # Enable HTTP/2
        )

    async def close(self):
        await self.client.aclose()

# Initialize once, reuse across tools
api_client = APIClient("http://localhost:8000")

@mcp.tool()
async def fetch_data(endpoint: str) -> dict:
    """Fetch data using pooled connection."""
    response = await api_client.client.get(endpoint)
    return response.json()
```

### 2. Caching

```python
from functools import lru_cache
from datetime import datetime, timedelta

# In-memory cache
cache = {}

def cached_tool(ttl_seconds: int = 60):
    """Cache tool results."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{args}:{kwargs}"

            # Check cache
            if cache_key in cache:
                cached_value, cached_time = cache[cache_key]
                if datetime.now() - cached_time < timedelta(seconds=ttl_seconds):
                    logger.info(f"Cache hit: {cache_key}")
                    return cached_value

            # Execute function
            result = await func(*args, **kwargs)

            # Update cache
            cache[cache_key] = (result, datetime.now())
            return result

        return wrapper
    return decorator

@mcp.tool()
@cached_tool(ttl_seconds=300)  # 5 minute cache
async def get_user_stats(user_id: str) -> dict:
    """Get user statistics (cached)."""
    # Expensive operation
    return await compute_stats(user_id)
```

## Security Considerations

### 1. Input Validation

```python
from pydantic import BaseModel, Field, validator

class SafeTaskInput(BaseModel):
    """Validated task input."""
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=1000)

    @validator("title")
    def validate_title(cls, v):
        """Prevent injection attacks."""
        if any(char in v for char in ["<", ">", "&", "script"]):
            raise ValueError("Invalid characters in title")
        return v.strip()

@mcp.tool()
async def create_task_safe(user_id: str, task: SafeTaskInput) -> dict:
    """Create task with validated input."""
    # Input is guaranteed safe
    return await create_task(user_id, task.dict())
```

### 2. Rate Limiting

```python
from collections import defaultdict
from datetime import datetime, timedelta

class RateLimiter:
    """Simple rate limiter."""

    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window = timedelta(seconds=window_seconds)
        self.requests = defaultdict(list)

    def is_allowed(self, user_id: str) -> bool:
        """Check if request is allowed."""
        now = datetime.now()
        user_requests = self.requests[user_id]

        # Remove old requests
        user_requests[:] = [
            req_time for req_time in user_requests
            if now - req_time < self.window
        ]

        # Check limit
        if len(user_requests) >= self.max_requests:
            return False

        user_requests.append(now)
        return True

limiter = RateLimiter(max_requests=10, window_seconds=60)

@mcp.tool()
async def rate_limited_operation(user_id: str, data: str) -> dict:
    """Operation with rate limiting."""
    if not limiter.is_allowed(user_id):
        return {
            "status": "error",
            "error": "rate_limit_exceeded",
            "message": "Too many requests. Try again later."
        }

    return await process_data(data)
```

## Further Reading

- [Official MCP Python SDK Documentation](https://github.com/modelcontextprotocol/python-sdk)
- [MCP Specification](https://modelcontextprotocol.io/specification)
- [FastMCP Examples](https://github.com/modelcontextprotocol/python-sdk/tree/main/examples)
- [MCP Best Practices 2025](https://www.marktechpost.com/2025/07/23/7-mcp-server-best-practices-for-scalable-ai-integrations-in-2025/)
