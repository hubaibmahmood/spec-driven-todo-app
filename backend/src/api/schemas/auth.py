"""Pydantic schemas for authentication endpoints."""

from pydantic import BaseModel, Field


class TokenRefreshResponse(BaseModel):
    """Response schema for token refresh endpoint."""

    access_token: str = Field(..., description="New JWT access token")


class TokenPairResponse(BaseModel):
    """Response schema when both access and refresh tokens are issued."""

    access_token: str = Field(..., description="JWT access token (30 minutes)")
    refresh_token: str = Field(..., description="Refresh token (7 days, httpOnly cookie)")
    user: dict = Field(..., description="User information")


class ErrorResponse(BaseModel):
    """Standard error response schema."""

    error_code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error message")


class TokenExpiredError(ErrorResponse):
    """Error response for expired access tokens."""

    error_code: str = "token_expired"
    message: str = "Access token has expired"


class RefreshTokenExpiredError(ErrorResponse):
    """Error response for expired refresh tokens."""

    error_code: str = "refresh_token_expired"
    message: str = "Refresh token has expired. Please log in again."


class InvalidRefreshTokenError(ErrorResponse):
    """Error response for invalid refresh tokens."""

    error_code: str = "invalid_refresh_token"
    message: str = "Invalid refresh token. Please log in again."
