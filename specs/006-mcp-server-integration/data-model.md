# Data Model: MCP Server Integration

**Feature**: 006-mcp-server-integration
**Date**: 2025-12-18
**Purpose**: Document data structures, schemas, and state management for MCP server

---

## Overview

The MCP server is **stateless** and does not persist any data. All data structures are transient, used only for:
1. Tool parameter validation (incoming requests from AI)
2. Backend API communication (requests to FastAPI)
3. Tool response formatting (outgoing responses to AI)

The source of truth is the FastAPI backend's PostgreSQL database.

---

## 1. Configuration Model

### Purpose
Store environment configuration and runtime settings

### Schema
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """MCP server configuration from environment variables."""

    # Required
    service_auth_token: str  # Service authentication token for backend API
    fastapi_base_url: str    # Base URL of FastAPI backend (e.g., http://localhost:8000)

    # Optional with defaults
    mcp_log_level: str = "INFO"      # Logging level (DEBUG, INFO, WARNING, ERROR)
    mcp_server_port: int = 3000      # HTTP port for MCP server
    backend_timeout: float = 30.0    # Timeout for backend requests (seconds)
    backend_max_retries: int = 2     # Number of retry attempts

    class Config:
        env_file = ".env"
        case_sensitive = False

# Singleton instance
settings = Settings()
```

### Validation Rules
- `service_auth_token`: Must not be empty (FR-016)
- `fastapi_base_url`: Must be valid HTTP/HTTPS URL (FR-017)
- `mcp_log_level`: Must be one of DEBUG, INFO, WARNING, ERROR (FR-022)
- `backend_timeout`: Must be > 0, default 30.0 seconds (FR-023)
- `backend_max_retries`: Must be >= 0, default 2 (FR-024)

---

## 2. Task Schema (Tool Parameters & Responses)

### Purpose
Define task data structure for MCP tool parameters and responses. Mirrors backend schema but optimized for AI interaction.

### TaskResponse Schema
```python
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
from enum import Enum

class PriorityLevel(str, Enum):
    """Task priority levels."""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    URGENT = "Urgent"

class TaskResponse(BaseModel):
    """Task data returned to AI assistant."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Unique task identifier")
    title: str = Field(..., description="Task title", max_length=200)
    description: Optional[str] = Field(None, description="Detailed task description")
    completed: bool = Field(..., description="Whether task is completed")
    priority: PriorityLevel = Field(..., description="Task priority level")
    due_date: Optional[datetime] = Field(None, description="Task due date (ISO 8601 format)")
    created_at: datetime = Field(..., description="Timestamp when task was created")
    updated_at: datetime = Field(..., description="Timestamp when task was last updated")
    user_id: str = Field(..., description="User who owns this task")
```

### CreateTaskParams Schema
```python
class CreateTaskParams(BaseModel):
    """Parameters for create_task tool."""

    title: str = Field(
        ...,
        description="Task title (required)",
        min_length=1,
        max_length=200,
        examples=["Buy milk", "Finish project report"]
    )
    description: Optional[str] = Field(
        None,
        description="Detailed task description (optional)",
        examples=["Pick up 2% milk from grocery store"]
    )
    priority: PriorityLevel = Field(
        PriorityLevel.MEDIUM,
        description="Task priority level (default: Medium)"
    )
    due_date: Optional[datetime] = Field(
        None,
        description="Task due date in ISO 8601 format (optional)",
        examples=["2025-12-20T10:00:00Z"]
    )
```

### UpdateTaskParams Schema
```python
class UpdateTaskParams(BaseModel):
    """Parameters for update_task tool.

    Note: Completion status is handled by mark_task_completed tool.
    This tool is for updating title, description, priority, and due_date.
    """

    task_id: int = Field(..., description="ID of task to update", gt=0)
    title: Optional[str] = Field(
        None,
        description="New task title (optional)",
        min_length=1,
        max_length=200
    )
    description: Optional[str] = Field(
        None,
        description="New task description (optional, null to clear)"
    )
    priority: Optional[PriorityLevel] = Field(
        None,
        description="New priority level (optional)"
    )
    due_date: Optional[datetime] = Field(
        None,
        description="New due date in ISO 8601 format (optional, null to clear)"
    )
```

### DeleteTaskParams Schema
```python
class DeleteTaskParams(BaseModel):
    """Parameters for delete_task tool."""

    task_id: int = Field(..., description="ID of task to delete", gt=0)
```

### MarkTaskCompletedParams Schema
```python
class MarkTaskCompletedParams(BaseModel):
    """Parameters for mark_task_completed tool.

    This is a focused tool for marking tasks complete.
    For other task updates, use UpdateTaskParams.
    """

    task_id: int = Field(..., description="ID of task to mark as completed", gt=0)
```

---

## 3. Error Response Schema

### Purpose
Standardize error responses returned to AI assistants

### ErrorResponse Schema
```python
class ErrorResponse(BaseModel):
    """Structured error response for AI consumption."""

    error_type: str = Field(..., description="Error type identifier")
    message: str = Field(..., description="Human-readable error message for AI")
    details: Optional[dict] = Field(None, description="Additional error context")
    suggestions: Optional[list[str]] = Field(None, description="Suggested next actions")

# Error type taxonomy (FR-014, FR-026)
ERROR_TYPES = {
    "authentication_error": "Service authentication failed",
    "authorization_error": "User not authorized to access this resource",
    "not_found_error": "Requested resource not found",
    "validation_error": "Input validation failed",
    "backend_error": "Backend service error",
    "timeout_error": "Request timed out",
    "connection_error": "Unable to connect to backend service"
}
```

### Validation Error Details (FR-026)
```python
class ValidationErrorDetail(BaseModel):
    """Detailed validation error for a specific field."""

    field: str = Field(..., description="Name of the invalid field")
    message: str = Field(..., description="Error message for this field")
    received_value: Optional[str] = Field(None, description="Value that was rejected")
    suggestion: Optional[str] = Field(None, description="Suggested correction")

# Example validation error response:
{
    "error_type": "validation_error",
    "message": "Task creation failed due to invalid input",
    "details": {
        "fields": [
            {
                "field": "title",
                "message": "Title cannot be empty",
                "received_value": "",
                "suggestion": "Provide a task title (1-200 characters)"
            },
            {
                "field": "due_date",
                "message": "Invalid datetime format",
                "received_value": "tomorrow",
                "suggestion": "Use ISO 8601 format: 2025-12-20T10:00:00Z"
            }
        ]
    },
    "suggestions": [
        "Provide a valid title (1-200 characters)",
        "Format due_date as ISO 8601 datetime"
    ]
}
```

---

## 4. Backend API Request Models

### Purpose
Define request structures for communicating with FastAPI backend

### BackendAuthHeaders
```python
from typing import TypedDict

class BackendAuthHeaders(TypedDict):
    """Headers for authenticated backend requests."""

    Authorization: str      # Bearer {SERVICE_AUTH_TOKEN}
    X-User-ID: str         # User ID from MCP session context
    Content-Type: str      # application/json
```

### BackendTaskCreateRequest
```python
# Matches backend TaskCreate schema
{
    "title": str,
    "description": Optional[str],
    "priority": str,  # "Low" | "Medium" | "High" | "Urgent"
    "due_date": Optional[str]  # ISO 8601 datetime
}
```

### BackendTaskUpdateRequest
```python
# Matches backend TaskUpdate schema
# Note: Completion status handled by CompletionUpdate schema via PATCH endpoint
{
    "title": Optional[str],
    "description": Optional[str],
    "priority": Optional[str],
    "due_date": Optional[str]
}
```

### BackendCompletionUpdateRequest
```python
# Matches backend CompletionUpdate schema for PATCH endpoint
{
    "completed": bool
}
```

---

## 5. User Context Model

### Purpose
Store user context extracted from MCP session

### UserContext Schema
```python
class UserContext(BaseModel):
    """User context from MCP session."""

    user_id: str = Field(..., description="Authenticated user identifier")
    session_id: Optional[str] = Field(None, description="MCP session identifier")

# Extraction from MCP request context
def extract_user_context(mcp_request) -> UserContext:
    """Extract user context from MCP request."""
    # MCP framework provides user context in request metadata
    user_id = mcp_request.meta.get("user_id")
    if not user_id:
        raise ValueError("Missing user context in MCP request")

    return UserContext(
        user_id=user_id,
        session_id=mcp_request.meta.get("session_id")
    )
```

---

## 6. Logging Event Models

### Purpose
Structure log events for observability (FR-018)

### BackendRequestLogEvent
```python
class BackendRequestLogEvent(BaseModel):
    """Structured log event for backend API calls."""

    timestamp: datetime = Field(default_factory=datetime.utcnow)
    event_type: str = "backend_request"
    request_id: str
    user_id: str
    method: str           # GET, POST, PUT, DELETE
    endpoint: str         # /tasks, /tasks/123
    status_code: Optional[int] = None
    duration_ms: Optional[float] = None
    error: Optional[str] = None

    def to_log_dict(self) -> dict:
        """Convert to dict for JSON logging."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "event": self.event_type,
            "request_id": self.request_id,
            "user_id": self.user_id,
            "method": self.method,
            "endpoint": self.endpoint,
            "status_code": self.status_code,
            "duration_ms": self.duration_ms,
            "error": self.error
        }
```

---

## 7. State Transitions

### MCP Tool Request Lifecycle

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. AI Client → MCP Server: Tool invocation with parameters     │
└───────────────────┬─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────────────┐
│ 2. MCP Server: Validate parameters (Pydantic)                  │
│    ├─ Invalid → Return validation_error to AI                  │
│    └─ Valid → Extract user context                             │
└───────────────────┬─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────────────┐
│ 3. MCP Server: Check user context                              │
│    ├─ Missing → Return authentication_error to AI              │
│    └─ Present → Build backend request                          │
└───────────────────┬─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────────────┐
│ 4. MCP Server → Backend: HTTP request with auth headers        │
│    Headers: Authorization: Bearer {token}, X-User-ID: {id}     │
└───────────────────┬─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────────────┐
│ 5. Backend Response                                             │
│    ├─ 200/201 → Parse response, return to AI                   │
│    ├─ 401 → Return authentication_error to AI                  │
│    ├─ 403 → Return authorization_error to AI                   │
│    ├─ 404 → Return not_found_error to AI                       │
│    ├─ 422 → Return validation_error to AI                      │
│    ├─ 500 → Return backend_error to AI                         │
│    ├─ Timeout → Return timeout_error to AI                     │
│    └─ Connection Error → Return connection_error to AI         │
└───────────────────┬─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────────────┐
│ 6. MCP Server: Log request (INFO level) with all details       │
└───────────────────┬─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────────────┐
│ 7. MCP Server → AI Client: Tool response (success or error)    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 8. Data Flow Diagrams

### Create Task Flow (FR-006, FR-027)

```
AI: "Add 'buy milk' to my todo list"
  ↓
MCP Tool: create_task(title="buy milk")
  ↓
Validate: CreateTaskParams {title: "buy milk"}
  ↓
POST /tasks
Headers: {Authorization: "Bearer {token}", X-User-ID: "{user_id}"}
Body: {title: "buy milk", priority: "Medium"}
  ↓
Backend: Create task in database
  ↓
Backend Response: 201 Created
{id: 123, title: "buy milk", completed: false, ...}
  ↓
MCP Response → AI: TaskResponse {id: 123, title: "buy milk", ...}
  ↓
AI → User: "I've added 'buy milk' to your todo list"
```

### List Tasks Flow (FR-005)

```
AI: "What's on my todo list?"
  ↓
MCP Tool: list_tasks()
  ↓
Extract user context from MCP session
  ↓
GET /tasks
Headers: {Authorization: "Bearer {token}", X-User-ID: "{user_id}"}
  ↓
Backend: Query tasks WHERE user_id = {user_id}
  ↓
Backend Response: 200 OK
[{id: 123, title: "buy milk", ...}, {id: 124, title: "finish report", ...}]
  ↓
MCP Response → AI: list[TaskResponse]
  ↓
AI → User: "You have 2 tasks: 1) buy milk 2) finish report"
```

---

## Summary

The MCP server uses the following key data models:

1. **Settings**: Environment configuration with validation
2. **Task Schemas**: CreateTaskParams, UpdateTaskParams, DeleteTaskParams, MarkTaskCompletedParams, TaskResponse
3. **Error Schemas**: ErrorResponse, ValidationErrorDetail with AI-friendly messages
4. **Backend Models**: Request headers and payloads matching FastAPI schemas (TaskCreate, TaskUpdate, CompletionUpdate)
5. **User Context**: User identity extracted from MCP session
6. **Logging Events**: Structured log events for observability

All models use **Pydantic** for validation, type safety, and JSON schema generation. The MCP server is **stateless** with no persistent storage.

**Tool Separation**:
- `update_task` handles title, description, priority, due_date changes (uses PUT /tasks/{id})
- `mark_task_completed` handles completion status changes (uses PATCH /tasks/{id})

**Next Phase**: Generate API contracts documenting tool interfaces and backend communication protocols.
