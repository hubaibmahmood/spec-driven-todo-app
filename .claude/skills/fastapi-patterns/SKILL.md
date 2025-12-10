---
name: fastapi-patterns
description: FastAPI API design patterns, RESTful conventions, routing, middleware, dependency injection, and clean architecture. Use for designing APIs, structuring endpoints, implementing middleware, organizing routers, and following FastAPI best practices.
allowed-tools: Read, Edit, Bash, Glob, Grep
---

# FastAPI Design Patterns & Best Practices

## Overview

This skill provides comprehensive guidance for designing and building FastAPI applications following industry best practices, RESTful conventions, and clean architecture principles.

## When to Use

- Designing new API endpoints
- Structuring FastAPI projects
- Implementing middleware
- Setting up dependency injection
- Organizing routers and endpoints
- Following RESTful API conventions
- Implementing clean architecture patterns

## RESTful API Design

### Endpoint Naming Conventions

**Collections and Resources:**
```
GET    /api/v1/users          # List all users
POST   /api/v1/users          # Create new user
GET    /api/v1/users/{id}     # Get specific user
PUT    /api/v1/users/{id}     # Replace user
PATCH  /api/v1/users/{id}     # Update user
DELETE /api/v1/users/{id}     # Delete user
```

**Nested Resources:**
```
GET    /api/v1/users/{id}/posts        # Get user's posts
POST   /api/v1/users/{id}/posts        # Create post for user
GET    /api/v1/users/{id}/posts/{pid}  # Get specific post
```

**Key Principles:**
- Use lowercase plural nouns for collections (`/users`, not `/User` or `/user`)
- Use hierarchical structures for relationships
- Avoid verbs in endpoint names (use HTTP methods instead)
- Use hyphens for multi-word resources (`/user-profiles`, not `/userProfiles`)
- Keep URLs short and meaningful

### HTTP Methods

| Method | Purpose | Idempotent | Safe | Success Status |
|--------|---------|------------|------|----------------|
| GET | Retrieve resources | Yes | Yes | 200 OK |
| POST | Create resource | No | No | 201 Created |
| PUT | Replace entire resource | Yes | No | 200 OK / 204 No Content |
| PATCH | Partial update | No | No | 200 OK |
| DELETE | Remove resource | Yes | No | 204 No Content |

### HTTP Status Codes

**Success (2xx):**
- `200 OK` - Successful GET, PUT, PATCH
- `201 Created` - Successful POST (resource created)
- `204 No Content` - Successful DELETE or PUT with no response body

**Client Errors (4xx):**
- `400 Bad Request` - Invalid request syntax or validation error
- `401 Unauthorized` - Authentication required or failed
- `403 Forbidden` - Authenticated but not authorized
- `404 Not Found` - Resource doesn't exist
- `409 Conflict` - Resource conflict (duplicate, constraint violation)
- `422 Unprocessable Entity` - Validation error (Pydantic default)
- `429 Too Many Requests` - Rate limit exceeded

**Server Errors (5xx):**
- `500 Internal Server Error` - Unexpected server error
- `502 Bad Gateway` - Upstream service error
- `503 Service Unavailable` - Temporary server unavailability

## FastAPI Project Structure

### Recommended Directory Layout

```
fastapi-app/
├── app/
│   ├── __init__.py
│   ├── main.py                    # Application factory
│   ├── config.py                  # Configuration settings
│   │
│   ├── api/                       # API layer
│   │   ├── __init__.py
│   │   ├── dependencies.py        # Shared dependencies
│   │   └── v1/                    # API version 1
│   │       ├── __init__.py
│   │       ├── router.py          # Version router
│   │       └── endpoints/         # Endpoint modules
│   │           ├── __init__.py
│   │           ├── users.py
│   │           ├── auth.py
│   │           └── posts.py
│   │
│   ├── models/                    # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── post.py
│   │
│   ├── schemas/                   # Pydantic models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── post.py
│   │
│   ├── services/                  # Business logic
│   │   ├── __init__.py
│   │   ├── user_service.py
│   │   └── post_service.py
│   │
│   ├── repositories/              # Data access layer
│   │   ├── __init__.py
│   │   ├── user_repository.py
│   │   └── post_repository.py
│   │
│   ├── core/                      # Core functionality
│   │   ├── __init__.py
│   │   ├── security.py            # Auth utilities
│   │   └── config.py              # Settings
│   │
│   ├── db/                        # Database setup
│   │   ├── __init__.py
│   │   └── session.py             # Database session
│   │
│   └── middleware/                # Custom middleware
│       ├── __init__.py
│       ├── logging.py
│       └── timing.py
│
├── tests/                         # Test suite
│   ├── __init__.py
│   ├── conftest.py                # Pytest fixtures
│   ├── test_endpoints/
│   ├── test_services/
│   └── test_repositories/
│
├── alembic/                       # Database migrations
│   ├── versions/
│   └── env.py
│
├── .env                           # Environment variables
├── .env.example                   # Example environment file
├── requirements.txt               # Dependencies
├── pyproject.toml                 # Project config
├── Dockerfile                     # Docker image
└── README.md                      # Documentation
```

### Layer Responsibilities

**API Layer (`api/`):**
- Handle HTTP requests/responses
- Validate input (Pydantic models)
- Call service layer
- Return responses
- NO business logic

**Service Layer (`services/`):**
- Business logic
- Orchestrate repository calls
- Data transformation
- Apply business rules
- Transaction coordination

**Repository Layer (`repositories/`):**
- Database queries
- CRUD operations
- Query composition
- NO business logic

**Models (`models/`):**
- SQLAlchemy ORM models
- Database table definitions
- Relationships

**Schemas (`schemas/`):**
- Pydantic models
- Request/response validation
- Data serialization

## Dependency Injection Pattern

### Basic Dependency

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db

@router.get("/users/{user_id}")
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    # Use db session
    ...
```

### Service Layer Dependency

```python
# app/api/dependencies.py
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService

def get_user_repository(
    db: AsyncSession = Depends(get_db)
) -> UserRepository:
    return UserRepository(db)

def get_user_service(
    repository: UserRepository = Depends(get_user_repository)
) -> UserService:
    return UserService(repository)

# app/api/v1/endpoints/users.py
from fastapi import APIRouter, Depends
from app.api.dependencies import get_user_service
from app.services.user_service import UserService
from app.schemas.user import UserResponse

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    service: UserService = Depends(get_user_service)
):
    return await service.get_user(user_id)
```

### Authentication Dependency

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.security import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme)
) -> dict:
    try:
        payload = decode_token(token)
        return payload
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

@router.get("/profile")
async def get_profile(
    current_user: dict = Depends(get_current_user)
):
    return current_user
```

## Router Organization

### Creating Routers

```python
# app/api/v1/endpoints/users.py
from fastapi import APIRouter, Depends, status
from app.schemas.user import UserCreate, UserResponse

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}}
)

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate):
    """
    Create a new user.

    - **email**: valid email address
    - **username**: unique username
    - **password**: strong password (min 8 chars)
    """
    ...

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    """Get user by ID."""
    ...
```

### Composing Routers

```python
# app/api/v1/router.py
from fastapi import APIRouter
from app.api.v1.endpoints import users, auth, posts

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(posts.router, prefix="/posts", tags=["posts"])

# app/main.py
from fastapi import FastAPI
from app.api.v1.router import api_router

app = FastAPI(
    title="My API",
    description="API Documentation",
    version="1.0.0"
)

app.include_router(api_router, prefix="/api/v1")
```

## Middleware Implementation

### CORS Middleware

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Custom Logging Middleware

```python
import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        logger.info(f"Request: {request.method} {request.url}")

        response = await call_next(request)

        process_time = time.time() - start_time
        logger.info(f"Response: {response.status_code} ({process_time:.2f}s)")

        response.headers["X-Process-Time"] = str(process_time)
        return response

app.add_middleware(LoggingMiddleware)
```

### Error Handling Middleware

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": "An unexpected error occurred"
        }
    )
```

## Response Models & Validation

### Pydantic Schema Definition

```python
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

    @validator('password')
    def password_strength(cls, v):
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        return v

class UserUpdate(BaseModel):
    email: EmailStr | None = None
    username: str | None = None

class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # SQLAlchemy model support
        json_schema_extra = {
            "example": {
                "id": 1,
                "email": "user@example.com",
                "username": "johndoe",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00"
            }
        }
```

### Using Response Models

```python
from fastapi import APIRouter, status
from app.schemas.user import UserCreate, UserResponse

router = APIRouter()

@router.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    response_description="The created user"
)
async def create_user(user_data: UserCreate) -> UserResponse:
    # FastAPI automatically validates input and serializes output
    ...
```

## Error Handling Patterns

### Custom Exceptions

```python
# app/core/exceptions.py
class AppException(Exception):
    def __init__(self, message: str, status_code: int):
        self.message = message
        self.status_code = status_code

class NotFoundException(AppException):
    def __init__(self, resource: str, resource_id: int):
        super().__init__(
            f"{resource} with id {resource_id} not found",
            404
        )

class DuplicateException(AppException):
    def __init__(self, resource: str, field: str):
        super().__init__(
            f"{resource} with this {field} already exists",
            409
        )

# app/main.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.core.exceptions import AppException

app = FastAPI()

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message}
    )
```

### Using Custom Exceptions

```python
from app.core.exceptions import NotFoundException, DuplicateException

class UserService:
    async def get_user(self, user_id: int):
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise NotFoundException("User", user_id)
        return user

    async def create_user(self, user_data: UserCreate):
        existing = await self.repository.get_by_email(user_data.email)
        if existing:
            raise DuplicateException("User", "email")
        return await self.repository.create(user_data)
```

## Best Practices

### 1. Use Path Operations Decorators Correctly

```python
# ✅ Good: Specific response model and status code
@router.post("/users", response_model=UserResponse, status_code=201)
async def create_user(user_data: UserCreate) -> UserResponse:
    ...

# ❌ Bad: No response model or status code
@router.post("/users")
async def create_user(user_data: UserCreate):
    ...
```

### 2. Separate Concerns

```python
# ✅ Good: Clean separation
@router.get("/users/{user_id}")
async def get_user(
    user_id: int,
    service: UserService = Depends(get_user_service)
):
    return await service.get_user(user_id)

# ❌ Bad: Business logic in router
@router.get("/users/{user_id}")
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(404, "User not found")
    # ... more business logic ...
    return user
```

### 3. Use Proper HTTP Methods

```python
# ✅ Good: RESTful design
@router.post("/users", status_code=201)  # Create
@router.get("/users/{id}")                # Read
@router.put("/users/{id}")                # Replace
@router.patch("/users/{id}")              # Update
@router.delete("/users/{id}", status_code=204)  # Delete

# ❌ Bad: Using GET for mutations
@router.get("/users/delete/{id}")
@router.get("/users/update")
```

### 4. Document Your Endpoints

```python
# ✅ Good: Well documented
@router.post(
    "/users",
    response_model=UserResponse,
    status_code=201,
    summary="Create a new user",
    description="Create a new user with email, username, and password",
    response_description="The created user",
    tags=["users"]
)
async def create_user(user_data: UserCreate):
    """
    Create a new user with the following information:

    - **email**: valid email address
    - **username**: unique username (3-50 characters)
    - **password**: strong password (min 8 characters)

    Returns the created user with generated ID and timestamps.
    """
    ...
```

### 5. Use Dependency Injection

```python
# ✅ Good: Testable with DI
async def get_db():
    async with async_session_maker() as session:
        yield session

@router.get("/users/{id}")
async def get_user(id: int, db: AsyncSession = Depends(get_db)):
    ...

# ❌ Bad: Hard to test
from app.db import session

@router.get("/users/{id}")
async def get_user(id: int):
    # Direct dependency on global session
    ...
```

## Development and Testing Patterns

### Mock Authentication for Development

During development, before implementing real authentication, use consistent mock user IDs:

```python
# src/api/routers/tasks.py or src/api/dependencies.py

from uuid import UUID

# Fixed user ID for testing - all requests use the same user
MOCK_USER_ID = UUID("00000000-0000-0000-0000-000000000001")

async def get_current_user() -> UUID:
    """
    Temporary mock authentication dependency.

    Returns consistent user ID so all operations belong to the same user during testing.
    Replace with real authentication (session validation, JWT, etc.) in production.
    """
    return MOCK_USER_ID

# Usage in endpoints
@router.get("/tasks")
async def get_tasks(
    repository: TaskRepository = Depends(get_task_repository),
    current_user: UUID = Depends(get_current_user)  # ← Mock dependency
):
    return await repository.get_all_by_user(current_user)
```

**Why consistent mock IDs?**
- ✅ Ensures created resources can be retrieved in subsequent requests
- ✅ Prevents user isolation issues during manual testing
- ✅ Simplifies debugging (all test data belongs to known user)
- ✅ Makes Swagger UI testing seamless

**❌ Don't use random UUIDs:**
```python
# ❌ Bad: Different UUID on every request
async def get_current_user() -> UUID:
    return uuid4()  # Creates tasks you can't retrieve!
```

### Overriding Dependencies in Tests

FastAPI's dependency override system allows replacing dependencies during testing:

```python
# tests/conftest.py

import pytest
from uuid import UUID
from fastapi import FastAPI

@pytest.fixture
def test_user_id():
    """Fixed user ID for test isolation."""
    return UUID("test-user-0000-0000-0000-000000000001")

@pytest.fixture
def app_with_test_user(app: FastAPI, test_user_id: UUID):
    """Override authentication to use test user."""
    async def mock_current_user():
        return test_user_id

    # Override the dependency
    app.dependency_overrides[get_current_user] = mock_current_user
    yield app

    # Clean up after test
    app.dependency_overrides.clear()

# Usage in tests
async def test_create_task(client: AsyncClient, app_with_test_user, test_user_id):
    """Test uses overridden authentication."""
    response = await client.post("/tasks", json={"title": "Test"})
    assert response.status_code == 201
    assert response.json()["user_id"] == str(test_user_id)
```

### Development vs Production Auth

Use environment-based configuration to switch between mock and real authentication:

```python
# src/api/dependencies.py

from src.config import settings

if settings.ENVIRONMENT == "development":
    # Mock authentication for local development
    async def get_current_user() -> UUID:
        return UUID("00000000-0000-0000-0000-000000000001")
else:
    # Real authentication for production
    async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db)
    ) -> UUID:
        # Validate token, query database, return user_id
        return await auth_service.validate_token(token, db)
```

### Testing with Multiple Users

When testing multi-user scenarios:

```python
# tests/test_user_isolation.py

async def test_user_cannot_access_other_user_tasks(
    client: AsyncClient,
    app: FastAPI
):
    """Test user isolation - users can only see their own tasks."""

    # Create task as user 1
    user1_id = UUID("11111111-1111-1111-1111-111111111111")
    app.dependency_overrides[get_current_user] = lambda: user1_id

    response = await client.post("/tasks", json={"title": "User 1 task"})
    task_id = response.json()["id"]

    # Try to access as user 2
    user2_id = UUID("22222222-2222-2222-2222-222222222222")
    app.dependency_overrides[get_current_user] = lambda: user2_id

    response = await client.get(f"/tasks/{task_id}")
    assert response.status_code == 404  # Not found for user 2

    app.dependency_overrides.clear()
```

### Common Development Patterns

#### 1. Health Check Endpoint

Always include a health check for monitoring:

```python
@router.get("/health", tags=["system"])
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Health check endpoint for monitoring and deployment validation.

    Returns:
        dict: Health status and database connectivity
    """
    try:
        # Test database connectivity
        await db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    return {
        "status": "healthy",
        "database": db_status,
        "timestamp": datetime.utcnow().isoformat()
    }
```

#### 2. Request ID Middleware for Debugging

Add correlation IDs to track requests across logs:

```python
import uuid
from starlette.middleware.base import BaseHTTPMiddleware

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

# Add to app
app.add_middleware(RequestIDMiddleware)
```

#### 3. Development-Only Endpoints

Conditional endpoints for debugging:

```python
if settings.ENVIRONMENT == "development":
    @router.get("/debug/db-info", tags=["debug"])
    async def debug_db_info(db: AsyncSession = Depends(get_db)):
        """Development-only endpoint to inspect database state."""
        # Return database stats, pool info, etc.
        return {"environment": "development", "debug": True}
```

### Best Practices for Development

✅ **DO:**
- Use consistent mock IDs during development
- Override dependencies in tests
- Include health check endpoints
- Add request correlation IDs
- Use environment variables for feature flags

❌ **DON'T:**
- Generate random UUIDs in mock authentication
- Hardcode authentication in endpoints
- Skip authentication during development (use mocks instead)
- Leave debug endpoints enabled in production

## Reference

For complete examples and templates, see:
- [API-DESIGN.md](API-DESIGN.md) - Comprehensive API design guide
- [EXAMPLES.md](EXAMPLES.md) - Full working examples
- [templates/endpoint-template.py](templates/endpoint-template.py) - Reusable endpoint template

## Quick Checklist

When creating a new endpoint:
- [ ] Follow RESTful naming conventions
- [ ] Use appropriate HTTP method
- [ ] Define Pydantic request/response models
- [ ] Use correct HTTP status codes
- [ ] Implement in service layer (not router)
- [ ] Add error handling
- [ ] Add authentication/authorization if needed
- [ ] Add docstring and OpenAPI metadata
- [ ] Write tests
- [ ] Update API documentation
