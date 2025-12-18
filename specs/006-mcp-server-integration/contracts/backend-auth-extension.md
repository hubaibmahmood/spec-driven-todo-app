# Backend Authentication Extension Contract

**Feature**: 006-mcp-server-integration
**Date**: 2025-12-18
**Purpose**: Document required modifications to FastAPI backend for dual authentication support

---

## Overview

The FastAPI backend currently validates user session tokens via the `get_current_user` dependency (better-auth integration). To support MCP server requests, the backend must be extended to accept service-to-service authentication using a dedicated service token plus user context propagation via headers.

---

## Current Authentication Flow

```python
# backend/src/api/dependencies.py (current implementation)
async def get_current_user(session_token: str = Depends(cookie_or_header_session)) -> str:
    """
    Validate user session token via better-auth UserSession table.

    Args:
        session_token: Session token from better-auth (Cookie or Authorization header)

    Returns:
        User ID if session is valid and not expired

    Raises:
        HTTPException 401: Invalid or expired session
    """
    async with get_db() as db:
        result = await db.execute(
            select(UserSession).where(UserSession.token == session_token)
        )
        session = result.scalar_one_or_none()

        if not session:
            raise HTTPException(status_code=401, detail="Invalid session token")

        if session.expires_at < datetime.now():
            raise HTTPException(status_code=401, detail="Session expired")

        return session.user_id
```

---

## Required Extension: Dual Authentication Support

### Design Decision

**Approach**: Create a separate dependency function `get_service_auth` for MCP server requests.

**Rationale**:
- Clear separation of concerns: user authentication vs. service authentication
- Easy to audit service-to-service calls separately
- No risk of breaking existing frontend authentication
- Explicit opt-in for endpoints that support service auth

**Rejected Alternative**: Modify `get_current_user` to support both flows
- Risk: Mixing two authentication patterns increases complexity
- Maintenance: Harder to reason about which flow is active
- Security: Potential for logic errors in conditional flow

---

## New Dependency: get_service_auth

### Implementation

```python
# backend/src/api/dependencies.py (new function)
from fastapi import Header, HTTPException, status
from src.config import settings

async def get_service_auth(
    authorization: str = Header(...),
    x_user_id: str = Header(..., alias="X-User-ID")
) -> str:
    """
    Validate service-to-service authentication for MCP server requests.

    Authentication flow:
    1. Validate Authorization header contains Bearer token
    2. Validate token matches SERVICE_AUTH_TOKEN environment variable
    3. Extract user ID from X-User-ID header
    4. Return user ID for downstream authorization

    Args:
        authorization: Authorization header (e.g., "Bearer <token>")
        x_user_id: User ID from MCP session via X-User-ID header

    Returns:
        User ID string from X-User-ID header

    Raises:
        HTTPException 401: Missing or invalid service token
        HTTPException 400: Missing X-User-ID header
    """
    # Validate Authorization header format
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header format. Expected: Bearer <token>"
        )

    # Extract token from "Bearer <token>"
    token = authorization[7:]  # Remove "Bearer " prefix

    # Validate service token
    if token != settings.service_auth_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid service authentication token"
        )

    # Validate X-User-ID header is present
    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing X-User-ID header"
        )

    # Return user ID for downstream use
    return x_user_id
```

### Configuration Extension

```python
# backend/src/config.py (add to Settings class)
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # ... existing settings ...

    # Service authentication
    service_auth_token: str  # Required for MCP server integration

    class Config:
        env_file = ".env"
```

### Environment Variable

```env
# backend/.env
SERVICE_AUTH_TOKEN=<secret-service-token>
```

**Security Requirements**:
- Token must be at least 32 characters
- Token must be randomly generated (not derived from other secrets)
- Token must be stored in environment variable, never in code
- Token should be rotated periodically (manual process initially)

---

## Endpoint Modification Strategy

### Option A: Keep Existing Endpoints Unchanged (Recommended)

**Approach**: Do NOT modify existing `/tasks` endpoints. Instead, MCP server uses existing endpoints with service authentication.

**Rationale**:
- Minimal backend changes
- MCP server is a trusted service acting on behalf of users
- Existing authorization logic (user_id filtering) remains intact

**Implementation**: No endpoint changes required. MCP server dependency injection uses `Depends(get_service_auth)` instead of `Depends(get_current_user)`.

**Example**:
```python
# backend/src/api/routers/tasks.py (NO CHANGES to existing endpoints)
# Existing endpoints continue to use: current_user: str = Depends(get_current_user)

# MCP server calls existing endpoints with:
# Headers: {
#     "Authorization": "Bearer <SERVICE_AUTH_TOKEN>",
#     "X-User-ID": "<user_id>"
# }
# Backend dependency get_current_user extracts user_id from session
```

**Wait, this doesn't work!** Existing `get_current_user` validates session tokens, not service tokens. We need to modify the endpoints.

### Option B: Dual Dependency Support (Chosen Approach)

**Approach**: Modify task endpoints to accept EITHER user session OR service token.

**Implementation**:
```python
# backend/src/api/dependencies.py (new union dependency)
from typing import Union
from fastapi import Depends

async def get_current_user_or_service(
    authorization: str = Header(None),
    session_token: str = Depends(cookie_or_header_session),
    x_user_id: str = Header(None, alias="X-User-ID")
) -> str:
    """
    Support both user session authentication and service authentication.

    Precedence:
    1. If X-User-ID header present → service auth flow (validate service token)
    2. Else → user session flow (validate session token)

    Returns:
        User ID from either session or X-User-ID header
    """
    # Service auth flow (MCP server)
    if x_user_id is not None:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(401, "Service auth requires Authorization header")

        token = authorization[7:]
        if token != settings.service_auth_token:
            raise HTTPException(401, "Invalid service token")

        return x_user_id

    # User session flow (frontend)
    else:
        return await get_current_user(session_token)
```

**Endpoint Modification**:
```python
# backend/src/api/routers/tasks.py (UPDATE all endpoints)
# Change from:
#   current_user: str = Depends(get_current_user)
# To:
#   current_user: str = Depends(get_current_user_or_service)

@router.get("/", response_model=list[TaskResponse])
async def get_all_tasks(
    repository: TaskRepository = Depends(get_task_repository),
    current_user: str = Depends(get_current_user_or_service)  # CHANGED
) -> list[TaskResponse]:
    ...
```

---

## Security Considerations

### 1. Service Token Validation

**Requirement**: Service token must be validated on EVERY request
**Implementation**: Constant-time comparison to prevent timing attacks

```python
import hmac

def validate_service_token(provided_token: str, expected_token: str) -> bool:
    """Constant-time token comparison to prevent timing attacks."""
    return hmac.compare_digest(provided_token, expected_token)
```

### 2. User Context Validation

**Requirement**: X-User-ID header must be present and non-empty
**Implementation**: Explicit validation in `get_service_auth`

### 3. Audit Logging

**Requirement**: Log all service-authenticated requests for audit trail
**Implementation**:
```python
logger.info(
    "Service authenticated request",
    extra={
        "auth_type": "service",
        "user_id": x_user_id,
        "endpoint": request.url.path,
        "method": request.method,
        "timestamp": datetime.utcnow().isoformat()
    }
)
```

### 4. Rate Limiting

**Consideration**: Should service-authenticated requests have separate rate limits?
**Decision**: Not initially. Service auth uses same rate limits as user auth. Can be revisited if MCP server generates excessive traffic.

---

## Testing Requirements

### Unit Tests

```python
# backend/tests/unit/test_dependencies.py
async def test_get_service_auth_valid_token():
    """Valid service token with X-User-ID returns user ID."""
    user_id = await get_service_auth(
        authorization="Bearer valid-service-token",
        x_user_id="user_123"
    )
    assert user_id == "user_123"

async def test_get_service_auth_invalid_token():
    """Invalid service token raises 401."""
    with pytest.raises(HTTPException) as exc:
        await get_service_auth(
            authorization="Bearer invalid-token",
            x_user_id="user_123"
        )
    assert exc.value.status_code == 401

async def test_get_service_auth_missing_user_id():
    """Missing X-User-ID header raises 400."""
    with pytest.raises(HTTPException) as exc:
        await get_service_auth(
            authorization="Bearer valid-service-token",
            x_user_id=None
        )
    assert exc.value.status_code == 400
```

### Integration Tests

```python
# backend/tests/integration/test_service_auth.py
async def test_list_tasks_with_service_auth(client, test_user_id):
    """GET /tasks with service auth returns user's tasks."""
    response = await client.get(
        "/tasks",
        headers={
            "Authorization": f"Bearer {settings.service_auth_token}",
            "X-User-ID": test_user_id
        }
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)

async def test_list_tasks_with_invalid_service_token(client, test_user_id):
    """GET /tasks with invalid service token returns 401."""
    response = await client.get(
        "/tasks",
        headers={
            "Authorization": "Bearer invalid-token",
            "X-User-ID": test_user_id
        }
    )
    assert response.status_code == 401
```

---

## Migration Plan

### Phase 1: Add Service Auth Support (Non-Breaking)
1. Add `service_auth_token` to Settings
2. Implement `get_service_auth` dependency
3. Implement `get_current_user_or_service` union dependency
4. Add unit tests for new dependencies
5. Deploy backend with feature flag (service auth disabled)

### Phase 2: Update Endpoints (Non-Breaking)
1. Update all `/tasks` endpoints to use `get_current_user_or_service`
2. Add integration tests for service auth flows
3. Verify existing frontend authentication still works
4. Deploy backend update

### Phase 3: Enable MCP Server (Additive)
1. Configure SERVICE_AUTH_TOKEN in environment
2. Deploy MCP server
3. Test MCP tools end-to-end
4. Monitor logs for service auth requests

---

## Summary

**Backend modifications required**:

1. **Configuration** (`backend/src/config.py`):
   - Add `service_auth_token: str` to Settings

2. **Dependencies** (`backend/src/api/dependencies.py`):
   - Add `get_service_auth()` function for service token validation
   - Add `get_current_user_or_service()` union dependency

3. **Endpoints** (`backend/src/api/routers/tasks.py`):
   - Update all endpoints to use `Depends(get_current_user_or_service)`

4. **Tests**:
   - Add unit tests for service auth dependencies
   - Add integration tests for service-authenticated requests

5. **Environment** (`backend/.env`):
   - Add `SERVICE_AUTH_TOKEN` environment variable

**No breaking changes**: Existing frontend authentication continues to work unchanged.
