# Research: MCP Server Integration

**Feature**: 006-mcp-server-integration
**Date**: 2025-12-18
**Purpose**: Document technology decisions, alternatives considered, and best practices for MCP server implementation

---

## 1. MCP Python SDK Selection

### Decision
Use **FastMCP** (official MCP Python SDK by Anthropic)

### Rationale
- Official SDK maintained by Anthropic ensures protocol compliance
- Built-in support for HTTP transport (required by FR-002)
- Pythonic async/await patterns match FastAPI backend architecture
- Strong typing support with Pydantic integration
- Active development and community support

### Alternatives Considered
1. **Custom MCP protocol implementation**
   - Rejected: Significant development effort, protocol compliance risk, maintenance burden
2. **mcp-python (community SDK)**
   - Rejected: Less mature, smaller community, unofficial

### References
- FastMCP documentation: https://github.com/jlowin/fastmcp
- MCP specification: https://spec.modelcontextprotocol.io/

---

## 2. HTTP Client Library

### Decision
Use **httpx** with async support

### Rationale
- Full async/await support matches FastAPI backend patterns (FR-019)
- Built-in timeout configuration (FR-023)
- Automatic retry logic support via httpx-retry extension
- Better connection pooling than requests
- Type-safe with mypy support

### Alternatives Considered
1. **aiohttp**
   - Rejected: More complex API, less intuitive for request/response patterns
2. **requests**
   - Rejected: Synchronous only, would block MCP server operations

### Implementation Notes
- Configure default timeout: 30 seconds (FR-023)
- Use httpx.AsyncClient with connection pooling
- Implement retry middleware with exponential backoff (1s, 2s) for up to 2 retries (FR-024)

### References
- httpx documentation: https://www.python-httpx.org/
- httpx async guide: https://www.python-httpx.org/async/

---

## 3. Service Authentication Pattern

### Decision
Use **Bearer token in Authorization header + X-User-ID header** pattern

### Rationale
- Separates service authentication (who is calling) from user context (on whose behalf)
- Enables backend to validate service identity independently of user identity
- Standard HTTP header approach, no custom protocol
- Backend can enforce service-only endpoints separately from user endpoints

### Alternatives Considered
1. **JWT with embedded user claims**
   - Rejected: Couples service and user identity, harder to audit, token rotation complexity
2. **API key in query parameter**
   - Rejected: Less secure (logged in URLs), not standard practice
3. **Mutual TLS (mTLS)**
   - Rejected: Overkill for development, complex certificate management

### Implementation Notes
- SERVICE_AUTH_TOKEN stored in environment variable (FR-016)
- Backend must validate: (1) service token is present and valid, (2) X-User-ID header is present
- Backend modification required in `get_current_user` dependency (FR-021)

### Backend Modification Requirements
Current `get_current_user` dependency validates user session tokens via better-auth. Must be extended to support dual authentication:

**Option A: Separate dependency** (Recommended)
```python
async def get_service_auth(
    authorization: str = Header(...),
    x_user_id: str = Header(..., alias="X-User-ID")
) -> str:
    """Validate service token and return user ID from header."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "Invalid authorization header")

    token = authorization.split(" ")[1]
    if token != settings.SERVICE_AUTH_TOKEN:
        raise HTTPException(401, "Invalid service token")

    return x_user_id

# MCP endpoints use: current_user: str = Depends(get_service_auth)
# Frontend endpoints use: current_user: str = Depends(get_current_user)
```

**Option B: Unified dependency with conditional logic**
- Rejected: Mixes two authentication flows, harder to maintain and audit

---

## 4. MCP Tool Parameter Validation

### Decision
Use **Pydantic models for tool parameters** with JSON schema validation

### Rationale
- Pydantic provides automatic JSON schema generation (FR-013)
- Type-safe validation with field-level error messages (FR-026)
- Integrates seamlessly with FastMCP tool decorators
- Consistent with backend API validation patterns
- Fail-fast validation before backend calls (FR-013)

### Alternatives Considered
1. **Manual dict validation**
   - Rejected: Error-prone, no type safety, verbose
2. **JSON Schema directly**
   - Rejected: Less Pythonic, no type hints

### Implementation Notes
- Define Pydantic models in `mcp-server/src/schemas/task.py`
- Mirror backend schemas but optimized for AI tool parameters
- Include field descriptions for AI assistant understanding
- Validation errors return structured format: `{type, fields[], suggested_corrections}` (FR-026)

---

## 5. Error Handling and Translation

### Decision
Translate backend HTTP errors into **AI-friendly error messages**

### Rationale
- Backend returns RFC 7807 Problem Details (structured errors)
- AI assistants need natural language explanations
- Preserve error details (404, 401, 403, 422) for debugging (FR-014)
- Enable AI to communicate errors to users effectively

### Error Translation Strategy

| Backend Status | MCP Error Type | AI Message Format |
|----------------|----------------|-------------------|
| 401 Unauthorized | authentication_error | "Unable to authenticate. Please sign in again." |
| 403 Forbidden | authorization_error | "You don't have permission to access this task." |
| 404 Not Found | not_found_error | "Task {task_id} not found or doesn't belong to you." |
| 422 Validation | validation_error | "Invalid input: {field-level details}" |
| 500 Server Error | backend_error | "Backend service unavailable. Please try again later." |
| Timeout | timeout_error | "Request timed out after 30 seconds. Please try again." |
| Connection Error | connection_error | "Unable to connect to backend service." |

### Implementation Notes
- Log all errors at INFO level with full context (FR-018)
- Include request ID for traceability
- Preserve backend error details in logs for debugging

---

## 6. Logging Strategy

### Decision
Use **Python logging module** with structured JSON logging

### Rationale
- Standard library, no external dependencies
- Configurable via environment variable MCP_LOG_LEVEL (FR-022)
- Structured logging enables log aggregation and analysis
- INFO level default for production observability (FR-018)

### Logging Requirements (FR-018)
All backend API calls must log:
- Timestamp (ISO 8601 format)
- Endpoint path
- HTTP method
- HTTP status code
- User ID (from X-User-ID header)
- Request ID (correlation)
- Error details (when failures occur)
- Request/response payload (at DEBUG level only)

### Implementation Notes
```python
logger.info(
    "Backend API call completed",
    extra={
        "timestamp": datetime.now().isoformat(),
        "endpoint": "/tasks",
        "method": "GET",
        "status_code": 200,
        "user_id": user_id,
        "request_id": request_id,
        "duration_ms": duration
    }
)
```

---

## 7. Retry and Timeout Strategy

### Decision
Implement **exponential backoff with 2 retries and 30-second timeout**

### Rationale
- FR-023: 30-second timeout for all backend requests
- FR-024: 2 retries with exponential backoff (1s, 2s)
- Handles transient network failures gracefully (FR-025)
- Prevents cascade failures with circuit breaker pattern

### Implementation
```python
# Using httpx with tenacity for retries
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),  # Initial + 2 retries
    wait=wait_exponential(multiplier=1, min=1, max=2),  # 1s, 2s
    reraise=True
)
async def call_backend(client: httpx.AsyncClient, ...):
    response = await client.request(
        method=method,
        url=url,
        timeout=30.0,  # FR-023
        ...
    )
    return response
```

### Error Handling
- After 3 attempts (initial + 2 retries), raise structured error
- Log each retry attempt with attempt number
- Return timeout_error or connection_error to AI client (FR-025)

---

## 8. Testing Strategy

### Decision
Three-tier testing: **Contract → Unit → Integration**

### Rationale
- Contract tests validate MCP tool interfaces (inputs/outputs)
- Unit tests validate components in isolation (client, auth)
- Integration tests validate end-to-end flows with backend
- Matches backend testing structure (constitution principle)
- TDD workflow: write tests first for each tool

### Test Coverage Requirements
1. **Contract Tests** (tests/contract/)
   - Validate tool parameter schemas
   - Validate tool response schemas
   - Validate error response formats

2. **Unit Tests** (tests/unit/)
   - HTTP client configuration (timeout, retries)
   - Service authentication logic
   - Error translation logic
   - Parameter validation

3. **Integration Tests** (tests/integration/)
   - Each of 5 tools: list, create, update, delete, bulk_delete
   - Authentication flows (valid/invalid service token)
   - User context propagation (X-User-ID header)
   - Error scenarios (404, 401, 403, 422)
   - Network failures (timeout, connection refused)

### Test Fixtures (conftest.py)
- Mock httpx client for unit tests
- Test backend server for integration tests
- Sample task data factories
- Authentication fixtures (valid/invalid tokens)

---

## 9. Environment Configuration

### Decision
Use **pydantic-settings** for configuration management

### Rationale
- Type-safe configuration with validation
- Automatic .env file loading
- Matches backend configuration pattern
- Clear error messages for missing required variables

### Required Environment Variables
```env
# Required
SERVICE_AUTH_TOKEN=<secret-token>      # Service authentication token (FR-016)
FASTAPI_BASE_URL=http://localhost:8000 # Backend API base URL (FR-017)

# Optional
MCP_LOG_LEVEL=INFO                     # Logging level (FR-022)
MCP_SERVER_PORT=3000                   # MCP server HTTP port
```

### Implementation
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    service_auth_token: str
    fastapi_base_url: str
    mcp_log_level: str = "INFO"
    mcp_server_port: int = 3000

    class Config:
        env_file = ".env"
        case_sensitive = False
```

---

## 10. MCP Tool Descriptions

### Decision
Provide **detailed, AI-optimized tool descriptions**

### Rationale
- AI assistants use descriptions to understand tool purpose
- Clear descriptions improve tool selection accuracy
- Include parameter descriptions with examples
- Specify return value structure

### Tool Description Template
```python
@mcp.tool()
async def list_tasks(
    # User context injected by MCP framework
) -> list[dict]:
    """
    Retrieve all tasks for the authenticated user.

    Returns a list of tasks with the following fields:
    - id: Task identifier (integer)
    - title: Task title (string)
    - description: Task description (string, optional)
    - completed: Completion status (boolean)
    - priority: Priority level (Low, Medium, High, Urgent)
    - due_date: Due date (ISO 8601 string, optional)
    - created_at: Creation timestamp (ISO 8601 string)
    - updated_at: Last update timestamp (ISO 8601 string)

    Use this tool when the user asks "what's on my todo list?" or
    "show me my tasks".
    """
    ...

@mcp.tool()
async def mark_task_completed(
    task_id: int,
    # User context injected by MCP framework
) -> dict:
    """
    Mark a task as completed.

    This is a focused tool for the common operation of marking tasks complete.
    For other task updates (title, description, priority, due_date), use update_task.

    Use this tool when the user says "mark task X as done" or "complete the milk task".
    """
    ...
```

---

## Summary

All technical unknowns from Technical Context have been resolved:

1. ✅ MCP SDK: FastMCP (official Python SDK)
2. ✅ HTTP Client: httpx with async support
3. ✅ Authentication: Bearer token + X-User-ID header pattern
4. ✅ Validation: Pydantic models with JSON schema
5. ✅ Error Handling: Structured translation to AI-friendly messages
6. ✅ Logging: Python logging with structured JSON (INFO level default)
7. ✅ Retry/Timeout: Exponential backoff (2 retries, 30s timeout)
8. ✅ Testing: Contract → Unit → Integration (TDD workflow)
9. ✅ Configuration: pydantic-settings with .env support
10. ✅ Tool Descriptions: AI-optimized with detailed parameter docs (5 tools: list, create, update, delete, mark_completed)

**Next Phase**: Proceed to Phase 1 (Design & Contracts) to generate data models and API contracts.
