# API Design Comprehensive Guide

## API Versioning

### URL-based Versioning (Recommended)

```python
# app/main.py
from fastapi import FastAPI
from app.api.v1.router import api_router as v1_router
from app.api.v2.router import api_router as v2_router

app = FastAPI()

app.include_router(v1_router, prefix="/api/v1")
app.include_router(v2_router, prefix="/api/v2")
```

**URLs:**
```
https://api.example.com/api/v1/users
https://api.example.com/api/v2/users
```

### Benefits
- Clear and explicit
- Easy to cache and route
- Simple to understand
- Works with all HTTP clients

## Pagination Patterns

### Limit-Offset Pagination

```python
from fastapi import APIRouter, Query
from typing import List

router = APIRouter()

@router.get("/users", response_model=List[UserResponse])
async def list_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Number of records to return")
):
    users = await service.list_users(skip=skip, limit=limit)
    return users
```

**Request:**
```
GET /api/v1/users?skip=0&limit=20
```

### Cursor-based Pagination

```python
from pydantic import BaseModel
from typing import List, Optional

class PaginatedResponse(BaseModel):
    items: List[UserResponse]
    next_cursor: Optional[str] = None
    has_more: bool

@router.get("/users", response_model=PaginatedResponse)
async def list_users(
    cursor: Optional[str] = Query(None, description="Pagination cursor"),
    limit: int = Query(20, ge=1, le=100)
):
    result = await service.list_users_paginated(cursor=cursor, limit=limit)
    return result
```

**Request:**
```
GET /api/v1/users?limit=20
GET /api/v1/users?cursor=eyJpZCI6MTAwfQ&limit=20
```

## Filtering and Sorting

### Query Parameters for Filtering

```python
from typing import Optional
from datetime import datetime

@router.get("/users", response_model=List[UserResponse])
async def list_users(
    email: Optional[str] = Query(None, description="Filter by email"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    created_after: Optional[datetime] = Query(None, description="Filter by creation date"),
    sort_by: str = Query("created_at", regex="^(created_at|email|username)$"),
    order: str = Query("desc", regex="^(asc|desc)$")
):
    filters = {
        "email": email,
        "is_active": is_active,
        "created_after": created_after
    }
    return await service.list_users(
        filters=filters,
        sort_by=sort_by,
        order=order
    )
```

**Request:**
```
GET /api/v1/users?is_active=true&sort_by=created_at&order=desc
GET /api/v1/users?email=john@example.com
```

## Bulk Operations

### Bulk Create

```python
from typing import List

@router.post("/users/bulk", response_model=List[UserResponse], status_code=201)
async def bulk_create_users(
    users_data: List[UserCreate],
    service: UserService = Depends(get_user_service)
):
    """Create multiple users at once."""
    return await service.bulk_create(users_data)
```

### Bulk Update

```python
class BulkUpdateRequest(BaseModel):
    ids: List[int]
    updates: UserUpdate

@router.patch("/users/bulk", response_model=List[UserResponse])
async def bulk_update_users(
    request: BulkUpdateRequest,
    service: UserService = Depends(get_user_service)
):
    """Update multiple users with the same changes."""
    return await service.bulk_update(request.ids, request.updates)
```

## Partial Responses (Field Selection)

```python
from typing import Optional, Set

@router.get("/users/{user_id}")
async def get_user(
    user_id: int,
    fields: Optional[str] = Query(None, description="Comma-separated fields to include"),
    service: UserService = Depends(get_user_service)
):
    """Get user with optional field selection."""
    field_set = set(fields.split(",")) if fields else None
    user = await service.get_user(user_id, fields=field_set)
    return user
```

**Request:**
```
GET /api/v1/users/1?fields=id,email,username
```

## API Rate Limiting

### Response Headers

Include rate limit information in headers:

```python
from fastapi import Response

@router.get("/users")
async def list_users(response: Response):
    users = await service.list_users()

    # Add rate limit headers
    response.headers["X-RateLimit-Limit"] = "100"
    response.headers["X-RateLimit-Remaining"] = "95"
    response.headers["X-RateLimit-Reset"] = "1640000000"

    return users
```

## Async Request Processing

### Background Tasks

```python
from fastapi import BackgroundTasks

def send_welcome_email(email: str):
    # Send email logic
    pass

@router.post("/users", status_code=201)
async def create_user(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    service: UserService = Depends(get_user_service)
):
    user = await service.create_user(user_data)

    # Queue background task
    background_tasks.add_task(send_welcome_email, user.email)

    return user
```

### Long-running Jobs

```python
from uuid import uuid4

@router.post("/reports/generate", status_code=202)
async def generate_report(
    report_params: ReportParams,
    background_tasks: BackgroundTasks
):
    """Start report generation job."""
    job_id = str(uuid4())

    background_tasks.add_task(generate_report_task, job_id, report_params)

    return {
        "job_id": job_id,
        "status": "processing",
        "status_url": f"/api/v1/reports/status/{job_id}"
    }

@router.get("/reports/status/{job_id}")
async def get_report_status(job_id: str):
    """Check report generation status."""
    status = await get_job_status(job_id)
    return status
```

## Webhooks

### Webhook Registration

```python
class WebhookCreate(BaseModel):
    url: str = Field(..., regex="^https://")
    events: List[str]
    secret: Optional[str] = None

@router.post("/webhooks", status_code=201)
async def register_webhook(
    webhook_data: WebhookCreate,
    service: WebhookService = Depends(get_webhook_service)
):
    """Register a webhook endpoint."""
    webhook = await service.create_webhook(webhook_data)
    return webhook
```

## File Uploads

### Single File Upload

```python
from fastapi import File, UploadFile

@router.post("/users/{user_id}/avatar")
async def upload_avatar(
    user_id: int,
    file: UploadFile = File(...),
    service: UserService = Depends(get_user_service)
):
    """Upload user avatar image."""
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "File must be an image")

    if file.size > 5 * 1024 * 1024:  # 5MB
        raise HTTPException(400, "File too large")

    avatar_url = await service.upload_avatar(user_id, file)
    return {"avatar_url": avatar_url}
```

### Multiple File Uploads

```python
from typing import List

@router.post("/posts/{post_id}/attachments")
async def upload_attachments(
    post_id: int,
    files: List[UploadFile] = File(...),
    service: PostService = Depends(get_post_service)
):
    """Upload multiple attachments to a post."""
    if len(files) > 10:
        raise HTTPException(400, "Maximum 10 files allowed")

    attachment_urls = await service.upload_attachments(post_id, files)
    return {"attachments": attachment_urls}
```

## Request/Response Examples

### Detailed OpenAPI Examples

```python
from pydantic import BaseModel, Field

class UserCreate(BaseModel):
    email: str = Field(..., example="john@example.com")
    username: str = Field(..., example="johndoe")
    password: str = Field(..., example="SecurePass123!")
    full_name: str = Field(..., example="John Doe")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "john@example.com",
                "username": "johndoe",
                "password": "SecurePass123!",
                "full_name": "John Doe"
            }
        }

@router.post(
    "/users",
    response_model=UserResponse,
    responses={
        201: {
            "description": "User created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "email": "john@example.com",
                        "username": "johndoe",
                        "full_name": "John Doe",
                        "created_at": "2024-01-01T00:00:00"
                    }
                }
            }
        },
        409: {
            "description": "User already exists",
            "content": {
                "application/json": {
                    "example": {
                        "error": "User with this email already exists"
                    }
                }
            }
        }
    }
)
async def create_user(user_data: UserCreate):
    ...
```

## Error Response Format

### Standardized Error Structure

```python
from pydantic import BaseModel
from typing import Optional, Dict, Any

class ErrorResponse(BaseModel):
    error: str
    message: str
    code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "error": "Validation Error",
                "message": "Invalid input provided",
                "code": "VALIDATION_ERROR",
                "details": {
                    "field": "email",
                    "reason": "Invalid email format"
                }
            }
        }
```

### Validation Error Format

```python
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(x) for x in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "message": "Invalid input provided",
            "details": errors
        }
    )
```

## Health Checks and Status Endpoints

### Health Check Endpoint

```python
from fastapi import status

@router.get("/health", status_code=status.HTTP_200_OK, tags=["health"])
async def health_check():
    """Basic health check endpoint."""
    return {"status": "healthy"}

@router.get("/health/detailed", tags=["health"])
async def detailed_health_check(
    db: AsyncSession = Depends(get_db)
):
    """Detailed health check with dependency status."""
    checks = {
        "api": "healthy",
        "database": "unknown",
        "redis": "unknown"
    }

    # Check database
    try:
        await db.execute("SELECT 1")
        checks["database"] = "healthy"
    except Exception:
        checks["database"] = "unhealthy"

    # Check Redis
    try:
        await redis.ping()
        checks["redis"] = "healthy"
    except Exception:
        checks["redis"] = "unhealthy"

    overall_status = "healthy" if all(
        v == "healthy" for v in checks.values()
    ) else "degraded"

    return {
        "status": overall_status,
        "checks": checks
    }
```

## API Deprecation

### Marking Endpoints as Deprecated

```python
@router.get(
    "/old-endpoint",
    deprecated=True,
    summary="Old endpoint (deprecated)",
    description="This endpoint is deprecated. Use /api/v2/new-endpoint instead."
)
async def old_endpoint():
    """Deprecated endpoint."""
    return {"message": "This endpoint is deprecated"}
```

### Deprecation Headers

```python
from fastapi import Response

@router.get("/users")
async def list_users_old(response: Response):
    """Legacy users endpoint."""
    response.headers["Deprecation"] = "true"
    response.headers["Sunset"] = "2024-12-31"
    response.headers["Link"] = '</api/v2/users>; rel="successor-version"'

    return await service.list_users()
```

## Content Negotiation

### Multiple Response Formats

```python
from fastapi import Response
from fastapi.responses import JSONResponse, PlainTextResponse

@router.get("/users/{user_id}")
async def get_user(
    user_id: int,
    format: str = Query("json", regex="^(json|xml|csv)$")
):
    user = await service.get_user(user_id)

    if format == "xml":
        # Return XML format
        return Response(
            content=to_xml(user),
            media_type="application/xml"
        )
    elif format == "csv":
        # Return CSV format
        return PlainTextResponse(
            content=to_csv(user),
            media_type="text/csv"
        )

    # Default JSON format
    return user
```

## HATEOAS (Hypermedia)

### Including Links in Responses

```python
from pydantic import BaseModel
from typing import Dict, Optional

class UserResponseWithLinks(BaseModel):
    id: int
    email: str
    username: str
    _links: Dict[str, Dict[str, str]]

@router.get("/users/{user_id}", response_model=UserResponseWithLinks)
async def get_user(user_id: int, request: Request):
    user = await service.get_user(user_id)

    base_url = str(request.url_for("get_user", user_id=user_id))

    return {
        **user.dict(),
        "_links": {
            "self": {"href": base_url},
            "posts": {"href": f"{base_url}/posts"},
            "update": {"href": base_url, "method": "PUT"},
            "delete": {"href": base_url, "method": "DELETE"}
        }
    }
```

## Best Practices Summary

### API Design Checklist

- [ ] Use RESTful resource naming (plural nouns)
- [ ] Implement proper HTTP methods and status codes
- [ ] Version your API (URL-based recommended)
- [ ] Provide pagination for list endpoints
- [ ] Support filtering and sorting
- [ ] Include rate limiting headers
- [ ] Implement health check endpoints
- [ ] Use consistent error response format
- [ ] Add OpenAPI documentation and examples
- [ ] Support content negotiation if needed
- [ ] Mark deprecated endpoints clearly
- [ ] Use proper authentication and authorization
- [ ] Implement request validation
- [ ] Add response models to all endpoints
- [ ] Follow consistent naming conventions
- [ ] Provide detailed API documentation
