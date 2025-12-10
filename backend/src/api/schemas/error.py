"""Pydantic schemas for error responses."""

from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Optional, Any


class ErrorResponse(BaseModel):
    """Standard error response format (RFC 7807-inspired)."""

    type: str = Field(..., description="Error type identifier")
    title: str = Field(..., description="Human-readable error category")
    status: int = Field(..., description="HTTP status code")
    detail: str = Field(..., description="Detailed error message")
    instance: Optional[str] = Field(None, description="Affected resource path")
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    request_id: Optional[str] = Field(None, description="Request correlation ID")
    errors: Optional[list[dict[str, Any]]] = Field(None, description="Validation errors")
    retry_after: Optional[int] = Field(None, description="Seconds to wait before retry (429 only)")
    rate_limit_info: Optional[dict[str, Any]] = Field(None, description="Rate limit details")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "type": "validation_error",
                    "title": "Request validation failed",
                    "status": 400,
                    "detail": "One or more validation errors occurred",
                    "instance": "/tasks",
                    "timestamp": "2025-12-10T12:34:56Z",
                    "errors": [
                        {
                            "field": "title",
                            "message": "String should have at least 1 character",
                            "code": "string_too_short"
                        }
                    ]
                },
                {
                    "type": "authentication_error",
                    "title": "Authentication failed",
                    "status": 401,
                    "detail": "Invalid or missing authentication credentials",
                    "timestamp": "2025-12-10T12:34:56Z"
                },
                {
                    "type": "rate_limit_exceeded",
                    "title": "Rate limit exceeded",
                    "status": 429,
                    "detail": "Too many requests. Retry after 45 seconds.",
                    "timestamp": "2025-12-10T12:34:56Z",
                    "retry_after": 45,
                    "rate_limit_info": {
                        "limit": 100,
                        "remaining": 0,
                        "reset": 1702226696,
                        "window_seconds": 60
                    }
                }
            ]
        }
    }
