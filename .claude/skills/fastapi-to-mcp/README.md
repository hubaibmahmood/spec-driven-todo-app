# FastAPI to MCP Server Converter

## Overview

This skill converts your FastAPI backend into a **production-ready MCP Server microservice** for AI agent integration in microservices architectures.

The generated MCP Server:
- Exposes your FastAPI endpoints as AI-accessible tools
- Acts as middleware between AI agents and your FastAPI backend
- Supports service-to-service authentication
- Propagates user context via headers
- Works with better-auth session management

## What This Skill Generates

**One Microservice:** MCP Server (HTTP-based FastAPI application)

The MCP Server is called by your AI Agent Service (implemented separately) and forwards requests to your existing FastAPI backend with proper authentication and user context.

## Quick Start

### 1. Invoke the Skill

Simply tell Claude Code what you want:

```
User: "Create an MCP server for my FastAPI todo app"
```

Claude will automatically:
- Locate your FastAPI application
- Extract OpenAPI schema
- Generate complete MCP server structure
- Create configuration and tests

### 2. Review Generated Structure

```
your-project/
├── app/                     # Your existing FastAPI app
└── mcp-server/             # Generated MCP server
    ├── main.py             # MCP server entry point
    ├── tools.py            # Generated tool definitions
    ├── client.py           # FastAPI HTTP client
    ├── config.py           # Configuration management
    ├── pyproject.toml      # Dependencies
    ├── .env.example        # Environment template
    ├── README.md           # Usage instructions
    └── tests/
        └── test_tools.py   # Generated tests
```

### 3. Run the MCP Server

```bash
cd mcp-server

# Install dependencies
uv sync

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run tests
pytest tests/

# Start MCP server
uv run mcp-server
```

### 4. Integrate with Claude Code

Add to your Claude Code configuration (`~/.claude/config.json`):

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

## Features

### ✅ Automatic Discovery
- Parses FastAPI OpenAPI schema
- Extracts endpoint information, parameters, and responses
- Identifies authentication patterns
- Generates appropriate MCP tool names

### ✅ Production-Ready Generation
- Complete project structure with dependencies
- Type-safe with full annotations
- Comprehensive error handling
- Connection pooling and HTTP/2 support
- Logging and monitoring built-in

### ✅ Authentication Support
- **User ID Parameter**: Multi-tenant systems
- **JWT Bearer Token**: OAuth2 integration
- **Session Cookies**: Traditional web apps
- **Better-Auth**: Integration with better-auth

### ✅ Testing & Documentation
- pytest tests for each tool
- Integration tests with FastAPI
- Complete README with usage examples
- API reference documentation

### ✅ Spec-Kit Plus Integration
- Automatic PHR (Prompt History Record) creation
- ADR (Architectural Decision Record) suggestions
- Project constitution updates

## Example: Todo App Conversion

### FastAPI Endpoints

```python
# app/api/routes/tasks.py

@router.post("/tasks")
async def create_task(
    user_id: str,
    task: TaskCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new task."""
    return await task_service.create(db, user_id, task)

@router.get("/tasks")
async def list_tasks(
    user_id: str,
    status: str = "all",
    db: AsyncSession = Depends(get_db)
):
    """List tasks for a user."""
    return await task_service.list(db, user_id, status)
```

### Generated MCP Tools

```python
# mcp-server/tools.py (generated)

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
    """
    try:
        response = await client.post(
            "/api/v1/tasks",
            params={"user_id": user_id},
            json={"title": title, "description": description}
        )
        return response
    except httpx.HTTPStatusError as e:
        return _handle_http_error(e)
    except httpx.RequestError as e:
        return _handle_connection_error(e)

@mcp.tool()
async def list_tasks(
    user_id: str,
    status: str = "all"
) -> list[dict]:
    """List tasks for a user.

    Args:
        user_id: User identifier
        status: Filter by status (all, pending, completed)

    Returns:
        list[dict]: Array of task objects
    """
    try:
        response = await client.get(
            "/api/v1/tasks",
            params={"user_id": user_id, "status": status}
        )
        return response
    except httpx.HTTPStatusError as e:
        return _handle_http_error(e)
    except httpx.RequestError as e:
        return _handle_connection_error(e)
```

### Using the Tools with Claude Code

```
User: "Add a task: Buy groceries - milk, eggs, bread"

Claude: [Uses create_task tool]
✓ Task created: "Buy groceries" (ID: 5)

User: "Show all my pending tasks"

Claude: [Uses list_tasks tool]
Found 3 pending tasks:
1. Buy groceries
2. Call mom
3. Review PR #42

User: "Mark the first task as done"

Claude: [Uses complete_task tool]
✓ Task "Buy groceries" marked as completed
```

## Configuration Options

### MCP Server Settings

```bash
# .env file

# MCP Server
MCP_SERVER_NAME="Todo App MCP Server"
MCP_TRANSPORT=stdio              # stdio, streamable-http, sse
MCP_PORT=8001                    # For HTTP transports

# FastAPI Backend
MCP_FASTAPI_BASE_URL=http://localhost:8000
MCP_FASTAPI_API_PREFIX=/api/v1
MCP_FASTAPI_TIMEOUT=30.0

# Authentication
MCP_AUTH_METHOD=user_id          # user_id, jwt, session
# MCP_JWT_SECRET=your-secret
# MCP_SESSION_TOKEN=your-token

# Performance
MCP_HTTP_MAX_CONNECTIONS=100
MCP_HTTP_MAX_KEEPALIVE=20

# Logging
MCP_LOG_LEVEL=INFO
MCP_LOG_FILE=mcp-server.log
```

### Transport Options

#### Stdio (Default - For Claude Code)

```python
# Best for: Local Claude Code integration
MCP_TRANSPORT=stdio
```

```json
{
  "mcpServers": {
    "my-app": {
      "command": "uv",
      "args": ["run", "mcp-server"]
    }
  }
}
```

#### Streamable HTTP (For Web Clients)

```python
# Best for: Web-based clients, remote access
MCP_TRANSPORT=streamable-http
MCP_PORT=8001
```

Access at: `http://localhost:8001/mcp`

#### SSE (Server-Sent Events)

```python
# Best for: Real-time updates, event streaming
MCP_TRANSPORT=sse
MCP_PORT=8001
```

## Advanced Usage

### Custom Tool Transformations

Add custom logic to transform FastAPI responses:

```python
# mcp-server/transformations.py (create this file)

def transform_create_task(response: dict) -> dict:
    """Transform create_task response for better AI understanding."""
    return {
        "status": "success",
        "task_id": response["id"],
        "title": response["title"],
        "message": f"Created task '{response['title']}' with ID {response['id']}"
    }

TRANSFORMATIONS = {
    "create_task": transform_create_task,
}
```

Then update `tools.py` to use transformations.

### Rate Limiting

Add rate limiting to tools:

```python
# mcp-server/rate_limiter.py

from collections import defaultdict
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window = timedelta(seconds=window_seconds)
        self.requests = defaultdict(list)

    def is_allowed(self, user_id: str) -> bool:
        now = datetime.now()
        user_requests = self.requests[user_id]

        # Remove old requests
        user_requests[:] = [
            req for req in user_requests
            if now - req < self.window
        ]

        if len(user_requests) >= self.max_requests:
            return False

        user_requests.append(now)
        return True

limiter = RateLimiter(max_requests=100, window_seconds=60)
```

### Caching Responses

Cache frequently accessed data:

```python
# mcp-server/cache.py

from functools import lru_cache
from datetime import datetime, timedelta

cache = {}

def cached_tool(ttl_seconds: int = 300):
    """Decorator to cache tool results."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{args}:{kwargs}"

            # Check cache
            if cache_key in cache:
                value, timestamp = cache[cache_key]
                if datetime.now() - timestamp < timedelta(seconds=ttl_seconds):
                    return value

            # Execute and cache
            result = await func(*args, **kwargs)
            cache[cache_key] = (result, datetime.now())
            return result

        return wrapper
    return decorator

# Usage in tools.py
@cached_tool(ttl_seconds=60)
@mcp.tool()
async def get_user_stats(user_id: str) -> dict:
    """Get user statistics (cached for 1 minute)."""
    return await client.get(f"/api/v1/users/{user_id}/stats")
```

## Microservices Deployment Pattern

### Using MCP Server in Microservices Architecture

When deploying in a microservices environment with an AI Agent Service, consider these patterns:

#### Option 1: HTTP Transport for Service-to-Service Communication

**Configure MCP Server:**
```env
# .env
MCP_TRANSPORT=streamable-http
MCP_PORT=8001
```

**AI Agent Service calls MCP Server:**
```python
# In your AI Agent Service
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# For HTTP transport
async with stdio_client(
    StdioServerParameters(
        command="uvicorn",
        args=["mcp-server.main:app", "--host", "0.0.0.0", "--port", "8001"]
    )
) as (read, write):
    async with ClientSession(read, write) as session:
        # Call MCP tools
        result = await session.call_tool("list_tasks", arguments={"user_id": user_id})
```

#### Option 2: User Context Propagation

If your FastAPI backend needs to know which user the request is for, update your backend's `get_current_user` dependency to support **both** user tokens (from frontend) and service tokens (from MCP):

**Backend Dependency Pattern:**
```python
# backend/src/api/dependencies.py

async def get_current_user(
    authorization: str = Header(...),
    x_user_id: str = Header(None),  # For service calls
    db: AsyncSession = Depends(get_db)
) -> str:
    """Support both user tokens and service tokens."""
    token = authorization.replace("Bearer ", "")

    # Check if service token
    if token == os.getenv("SERVICE_TOKEN"):
        if not x_user_id:
            raise HTTPException(400, "Service calls need X-User-ID")
        return x_user_id

    # Otherwise validate user session token
    return await validate_session(token, db)
```

**MCP Tools Include User Context:**
```python
# mcp-server/tools.py (modify generated file)

@mcp.tool()
async def list_tasks(user_id: str) -> dict:
    """List tasks - user_id passed from AI Agent."""
    client = APIClient(
        base_url=settings.FASTAPI_BASE_URL,
        auth_token=settings.SERVICE_TOKEN  # Use service token
    )

    # Include user context in header
    tasks = await client.get(
        "/tasks",
        headers={"X-User-ID": user_id}
    )
    return tasks
```

**Flow:**
1. User authenticates → Frontend has session token
2. Frontend → AI Agent: sends session token
3. AI Agent: validates token, extracts user_id
4. AI Agent → MCP Server: calls tools with user_id parameter
5. MCP Server → Backend: service token + X-User-ID header
6. Backend: validates service token, uses user_id for data

This keeps user session tokens secure (never sent to MCP or external services).

## Deployment

### Docker Compose

```yaml
# docker-compose.yml

services:
  fastapi:
    build: ./app
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql+asyncpg://user:pass@db/app

  mcp-server:
    build: ./mcp-server
    ports:
      - "8001:8001"
    environment:
      MCP_FASTAPI_BASE_URL: http://fastapi:8000
      MCP_TRANSPORT: streamable-http
      MCP_PORT: 8001
    depends_on:
      - fastapi
```

### Kubernetes

```yaml
# k8s/mcp-server-deployment.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-server
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: mcp-server
        image: your-registry/mcp-server:latest
        ports:
        - containerPort: 8001
        env:
        - name: MCP_FASTAPI_BASE_URL
          value: "http://fastapi-service:8000"
        - name: MCP_TRANSPORT
          value: "streamable-http"
```

## Troubleshooting

### Issue: Can't find FastAPI app

**Cause:** FastAPI app not in expected location

**Solution:**
```bash
# Specify app location
export MCP_FASTAPI_APP_PATH=/path/to/app.py

# Or ensure app is in standard location:
# - app/main.py
# - src/app.py
# - main.py
```

### Issue: OpenAPI schema not accessible

**Cause:** FastAPI server not running

**Solution:**
```bash
# Start FastAPI first
uvicorn app.main:app --reload

# Then regenerate MCP server
```

### Issue: Authentication errors

**Cause:** Incorrect auth configuration

**Solution:**
```bash
# Check .env file
cat mcp-server/.env

# For user_id auth (simplest)
MCP_AUTH_METHOD=user_id

# For JWT auth
MCP_AUTH_METHOD=jwt
MCP_JWT_SECRET=your-secret-key
MCP_JWT_TOKEN=generated-token

# Test auth manually
curl -H "Authorization: Bearer $JWT_TOKEN" \
  http://localhost:8000/api/v1/tasks
```

### Issue: Connection timeout

**Cause:** FastAPI not responding or wrong URL

**Solution:**
```bash
# Verify FastAPI is running
curl http://localhost:8000/health

# Check MCP config
grep FASTAPI_BASE_URL mcp-server/.env

# Increase timeout if needed
MCP_FASTAPI_TIMEOUT=60.0
```

## Best Practices

### 1. Keep MCP Server Stateless

✅ **Good**: Each tool call is independent
```python
@mcp.tool()
async def get_task(user_id: str, task_id: int) -> dict:
    return await client.get(f"/tasks/{task_id}", params={"user_id": user_id})
```

❌ **Bad**: Storing state between calls
```python
# Don't do this
current_user = None

@mcp.tool()
async def set_user(user_id: str):
    global current_user
    current_user = user_id
```

### 2. Provide Clear Descriptions

✅ **Good**: Detailed docstring
```python
@mcp.tool()
async def create_task(user_id: str, title: str, description: str = None) -> dict:
    """Create a new task for the specified user.

    This creates a task in the pending state. The task can be updated
    later using update_task or marked complete with complete_task.

    Args:
        user_id: The ID of the user who owns this task
        title: Task title (1-200 characters)
        description: Optional longer description (max 1000 characters)

    Returns:
        dict: Created task with fields: id, title, status, created_at

    Example:
        >>> create_task("user123", "Buy groceries", "Milk and eggs")
        {"id": 5, "title": "Buy groceries", "status": "pending", ...}
    """
```

### 3. Handle Errors Gracefully

Always return structured error responses:
```python
try:
    return await client.post("/tasks", ...)
except httpx.HTTPStatusError as e:
    return {
        "status": "error",
        "error_code": "http_error",
        "message": f"FastAPI returned {e.response.status_code}",
        "details": {"status_code": e.response.status_code}
    }
```

### 4. Log Important Operations

```python
import logging

logger = logging.getLogger(__name__)

@mcp.tool()
async def delete_task(user_id: str, task_id: int) -> dict:
    """Delete a task."""
    logger.info(f"Deleting task {task_id} for user {user_id}")
    try:
        result = await client.delete(f"/tasks/{task_id}", params={"user_id": user_id})
        logger.info(f"Successfully deleted task {task_id}")
        return result
    except Exception as e:
        logger.error(f"Failed to delete task {task_id}: {e}")
        raise
```

## Files Reference

### Generated Files

| File | Purpose |
|------|---------|
| `main.py` | MCP server entry point with startup/shutdown hooks |
| `tools.py` | Generated tool definitions from FastAPI endpoints |
| `client.py` | HTTP client for FastAPI communication |
| `config.py` | Configuration management with Pydantic settings |
| `pyproject.toml` | Project dependencies and metadata |
| `.env.example` | Environment variable template |
| `README.md` | Usage instructions and examples |
| `tests/test_tools.py` | pytest tests for all tools |

### Supporting Files (Skill)

| File | Purpose |
|------|---------|
| `SKILL.md` | Main skill documentation (what Claude reads) |
| `MCP_REFERENCE.md` | Complete MCP Python SDK reference |
| `FASTAPI_PATTERNS.md` | FastAPI integration patterns |
| `templates/` | Code generation templates |
| `scripts/openapi_parser.py` | OpenAPI schema parser |
| `examples/` | Example implementations |

## Contributing

This skill is part of your project's `.claude/skills` directory and can be customized for your specific needs.

### Customizing the Skill

1. **Edit templates**: Modify files in `templates/` to change generated code
2. **Update parser**: Enhance `scripts/openapi_parser.py` for better endpoint detection
3. **Add patterns**: Document new patterns in `FASTAPI_PATTERNS.md`

### Testing Changes

```bash
# Test OpenAPI parser
python .claude/skills/fastapi-to-mcp/scripts/openapi_parser.py \
  http://localhost:8000/openapi.json

# Regenerate MCP server
# (just ask Claude to create MCP server again)
```

## License

This skill is part of your project and follows your project's license.

## Support

- **Skill Documentation**: `.claude/skills/fastapi-to-mcp/SKILL.md`
- **MCP SDK Docs**: [GitHub](https://github.com/modelcontextprotocol/python-sdk)
- **FastAPI Docs**: [https://fastapi.tiangolo.com](https://fastapi.tiangolo.com)
- **Claude Code Docs**: [https://claude.com/claude-code](https://claude.com/claude-code)

---

Generated by the fastapi-to-mcp Claude Code skill.
