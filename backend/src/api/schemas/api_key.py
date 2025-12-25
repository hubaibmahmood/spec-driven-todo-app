"""Pydantic schemas for API key management endpoints."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class SaveApiKeyRequest(BaseModel):
    """Request schema for saving an API key."""

    api_key: str = Field(..., min_length=20, description="Gemini API key (starts with 'AIza')")
    provider: str = Field(default="gemini", description="Provider name")

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "api_key": "AIzaSyDPjJjPjVq_yqBN6OdqY5Hk3gV4ZfmULeo",
                "provider": "gemini"
            }
        }


class TestApiKeyRequest(BaseModel):
    """Request schema for testing an API key."""

    api_key: str = Field(..., min_length=20, description="Gemini API key to test")

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "api_key": "AIzaSyDPjJjPjVq_yqBN6OdqY5Hk3gV4ZfmULeo"
            }
        }


class ApiKeyStatusResponse(BaseModel):
    """Response schema for API key status."""

    configured: bool = Field(..., description="Whether user has an API key configured")
    provider: Optional[str] = Field(None, description="Provider name")
    masked_key: Optional[str] = Field(None, description="Masked API key (e.g., 'AIza...xyz')")
    plaintext_key: Optional[str] = Field(None, description="Decrypted API key (only for service-to-service requests)")
    validation_status: Optional[str] = Field(None, description="Last validation status: 'success', 'failure', or null")
    last_validated_at: Optional[datetime] = Field(None, description="Timestamp of last validation")
    created_at: Optional[datetime] = Field(None, description="Timestamp of key creation")
    updated_at: Optional[datetime] = Field(None, description="Timestamp of last key update")

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "configured": True,
                "provider": "gemini",
                "masked_key": "AIza...Ueo",
                "validation_status": "success",
                "last_validated_at": "2025-12-24T10:30:00Z",
                "created_at": "2025-12-24T10:25:00Z",
                "updated_at": "2025-12-24T10:30:00Z"
            }
        }


class SaveApiKeyResponse(BaseModel):
    """Response schema for saving an API key."""

    success: bool = Field(..., description="Whether the operation succeeded")
    message: str = Field(..., description="Human-readable success message")
    masked_key: str = Field(..., description="Masked API key (e.g., 'AIza...xyz')")

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "API key saved successfully",
                "masked_key": "AIza...Ueo"
            }
        }


class TestApiKeyResponse(BaseModel):
    """Response schema for testing an API key."""

    success: bool = Field(..., description="Whether the test succeeded")
    message: str = Field(..., description="Human-readable test result message")
    validation_status: str = Field(..., description="Validation result: 'success' or 'failure'")

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "API key is valid and working",
                "validation_status": "success"
            }
        }


class DeleteApiKeyResponse(BaseModel):
    """Response schema for deleting an API key."""

    success: bool = Field(..., description="Whether the operation succeeded")
    message: str = Field(..., description="Human-readable success message")

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "API key removed successfully"
            }
        }


class ErrorResponse(BaseModel):
    """Generic error response schema."""

    detail: str = Field(..., description="Error message")

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "detail": "API key is invalid or expired"
            }
        }


def mask_api_key(api_key: str) -> str:
    """
    Mask an API key for display.

    Shows first 4 and last 3 characters with '...' in between.

    Args:
        api_key: Full API key

    Returns:
        Masked key (e.g., 'AIza...Ueo')
    """
    if not api_key or len(api_key) < 10:
        return "****"

    return f"{api_key[:4]}...{api_key[-3:]}"
