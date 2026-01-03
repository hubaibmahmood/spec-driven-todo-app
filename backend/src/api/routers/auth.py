"""Authentication routes for JWT token management."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.connection import get_db
from src.services.jwt_service import jwt_service
from src.services.refresh_token_service import refresh_token_service, RefreshTokenError
from src.api.schemas.auth import TokenRefreshResponse, ErrorResponse

router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post("/refresh", response_model=TokenRefreshResponse)
async def refresh_access_token(
    refresh_token: str,  # Will be extracted from httpOnly cookie in later implementation
    db: AsyncSession = Depends(get_db)
) -> TokenRefreshResponse:
    """
    Refresh an expired access token using a valid refresh token.

    Args:
        refresh_token: The refresh token from httpOnly cookie
        db: Database session

    Returns:
        A new access token

    Raises:
        401 Unauthorized: If refresh token is invalid, expired, or revoked
    """
    try:
        # Validate refresh token and get user_id
        user_id = await refresh_token_service.validate_refresh_token(db, refresh_token)

        # Generate new access token
        access_token = jwt_service.generate_access_token(user_id)

        return TokenRefreshResponse(access_token=access_token)

    except RefreshTokenError as e:
        error_code = "refresh_token_expired" if "expired" in str(e).lower() else "invalid_refresh_token"
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ErrorResponse(
                error_code=error_code,
                message=str(e)
            ).model_dump()
        )
