"""Authentication routes for JWT token management."""

import logging
from typing import Optional
from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from prometheus_client import Counter
from src.database.connection import get_db
from src.services.jwt_service import jwt_service
from src.services.refresh_token_service import refresh_token_service, RefreshTokenError
from src.api.schemas.auth import TokenRefreshResponse, LogoutResponse, ErrorResponse
from src.api.dependencies import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["authentication"])

# Prometheus metrics
token_refresh_total = Counter(
    'token_refresh_total',
    'Total number of token refresh attempts'
)

token_refresh_errors_total = Counter(
    'token_refresh_errors_total',
    'Total number of failed token refresh attempts',
    ['reason']
)


@router.post("/refresh", response_model=TokenRefreshResponse)
async def refresh_access_token(
    request: Request,
    db: AsyncSession = Depends(get_db),
    refresh_token: Optional[str] = Cookie(None, alias="refreshToken")
) -> TokenRefreshResponse:
    """
    Refresh an expired access token using a valid refresh token.

    Args:
        request: FastAPI request object for extracting client IP
        db: Database session
        refresh_token: The refresh token from httpOnly cookie

    Returns:
        A new access token

    Raises:
        401 Unauthorized: If refresh token is missing, invalid, expired, or revoked
    """
    # Increment total refresh attempts counter
    token_refresh_total.inc()

    # Extract client IP address
    client_ip = request.client.host if request.client else "unknown"

    # Check if refresh token cookie is present
    if not refresh_token:
        token_refresh_errors_total.labels(reason='missing').inc()
        logger.warning(
            "Token refresh failed: missing refresh token",
            extra={
                "event": "token_refresh_failed",
                "reason": "missing_token",
                "ip_address": client_ip,
                "timestamp": logging.Formatter().formatTime(logging.LogRecord(
                    "", 0, "", 0, "", (), None
                ))
            }
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ErrorResponse(
                error_code="missing_refresh_token",
                message="Refresh token not found. Please log in again."
            ).model_dump()
        )

    try:
        # Validate refresh token and get user_id
        user_id = await refresh_token_service.validate_refresh_token(db, refresh_token)

        # Generate new access token
        access_token = jwt_service.generate_access_token(user_id)

        # Log successful refresh
        logger.info(
            "Token refresh successful",
            extra={
                "event": "token_refresh_success",
                "user_id": user_id[:8] + "..." if len(user_id) > 8 else user_id,
                "ip_address": client_ip,
                "status": "success"
            }
        )

        return TokenRefreshResponse(access_token=access_token)

    except RefreshTokenError as e:
        # Determine specific error code based on exception message
        error_message = str(e).lower()
        if "expired" in error_message:
            error_code = "refresh_token_expired"
            reason = "expired"
        elif "invalid" in error_message or "not found" in error_message:
            error_code = "invalid_refresh_token"
            reason = "invalid"
        else:
            error_code = "session_revoked"
            reason = "revoked"

        # Increment error counter with specific reason
        token_refresh_errors_total.labels(reason=reason).inc()

        # Log refresh failure with details
        logger.warning(
            f"Token refresh failed: {reason}",
            extra={
                "event": "token_refresh_failed",
                "reason": reason,
                "ip_address": client_ip,
                "status": "failure",
                "error_message": str(e)
            }
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ErrorResponse(
                error_code=error_code,
                message=str(e)
            ).model_dump()
        )


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    request: Request,
    response: Response,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    refresh_token: Optional[str] = Cookie(None, alias="refreshToken")
) -> LogoutResponse:
    """
    Logout user by invalidating refresh token and clearing cookie.

    This endpoint:
    1. Requires a valid JWT access token (user must be authenticated)
    2. Deletes the refresh token from the database
    3. Clears the httpOnly refresh token cookie

    Args:
        request: FastAPI request object for extracting client IP
        response: FastAPI response object for setting cookies
        user_id: User ID from JWT token (injected by get_current_user)
        db: Database session
        refresh_token: Optional refresh token from httpOnly cookie

    Returns:
        LogoutResponse with success status and message

    Raises:
        401 Unauthorized: If JWT access token is invalid or expired
    """
    # Extract client IP address
    client_ip = request.client.host if request.client else "unknown"

    # Generate session identifier from refresh token (first 8 chars)
    session_id = refresh_token[:8] if refresh_token else "none"

    # Log logout initiation with structured fields
    logger.info(
        "Logout initiated",
        extra={
            "event": "logout_initiated",
            "user_id": user_id[:8] + "..." if len(user_id) > 8 else user_id,
            "session_identifier": session_id,
            "ip_address": client_ip,
            "has_refresh_token": refresh_token is not None
        }
    )

    # Delete refresh token from database if present
    if refresh_token:
        try:
            await refresh_token_service.delete_refresh_token(db, refresh_token)
            logger.info(
                "Refresh token deleted",
                extra={
                    "event": "refresh_token_deleted",
                    "user_id": user_id[:8] + "..." if len(user_id) > 8 else user_id,
                    "session_identifier": session_id,
                    "status": "success"
                }
            )
        except Exception as e:
            # Log error but don't fail logout if token deletion fails
            logger.warning(
                "Failed to delete refresh token",
                extra={
                    "event": "refresh_token_deletion_failed",
                    "user_id": user_id[:8] + "..." if len(user_id) > 8 else user_id,
                    "session_identifier": session_id,
                    "error": str(e),
                    "status": "warning"
                }
            )

    # Clear refresh token httpOnly cookie
    # Set Max-Age=0 to expire the cookie immediately
    response.set_cookie(
        key="refreshToken",
        value="",
        max_age=0,
        httponly=True,
        secure=True,  # Only send over HTTPS in production
        samesite="strict",
        path="/"
    )

    # Log successful logout with structured fields
    logger.info(
        "Logout successful",
        extra={
            "event": "logout_success",
            "user_id": user_id[:8] + "..." if len(user_id) > 8 else user_id,
            "session_identifier": session_id,
            "ip_address": client_ip,
            "status": "success"
        }
    )

    return LogoutResponse(
        success=True,
        message="Logged out successfully"
    )
