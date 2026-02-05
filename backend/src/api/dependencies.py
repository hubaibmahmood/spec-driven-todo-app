"""FastAPI dependencies for dependency injection."""

import hmac
from typing import Optional

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.database.connection import get_db
from src.database.repository import TaskRepository
from src.services.jwt_service import jwt_service, TokenExpiredError, InvalidTokenError


# HTTPBearer security scheme for extracting Bearer tokens
security = HTTPBearer()


async def get_current_user_jwt(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """
    Authenticate user via JWT access token and return user ID.

    Extracts Bearer token from Authorization header, validates the JWT
    signature and expiration, and returns the authenticated user's ID.

    This validation is stateless (no database query) - only signature verification.

    Args:
        credentials: HTTP Authorization credentials (Bearer token)

    Returns:
        User ID string if JWT is valid

    Raises:
        HTTPException: 401 if token is missing, invalid, expired, or wrong type
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    try:
        user_id = jwt_service.validate_access_token(token)
        return user_id
    except TokenExpiredError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error_code": "token_expired", "message": "Access token has expired"},
            headers={"WWW-Authenticate": "Bearer"},
        )
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error_code": "invalid_token", "message": str(e)},
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """
    Authenticate user via JWT access token and return user ID.

    This dependency validates JWT access tokens issued by the auth-server.
    Session-based authentication has been fully migrated to JWT.

    Args:
        credentials: HTTP Authorization credentials (Bearer token)

    Returns:
        User ID string if JWT is valid

    Raises:
        HTTPException: 401 if token is missing, invalid, or expired
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    try:
        user_id = jwt_service.validate_access_token(token)
        return user_id
    except TokenExpiredError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error_code": "token_expired", "message": "Access token has expired"},
            headers={"WWW-Authenticate": "Bearer"},
        )
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error_code": "invalid_token", "message": str(e)},
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_service_auth(
    authorization: str = Header(...),
    x_user_id: str = Header(..., alias="X-User-ID"),
) -> str:
    """
    Validate service authentication token and return user ID from header.

    This dependency is used for service-to-service authentication (e.g., MCP server).
    It validates the SERVICE_AUTH_TOKEN and extracts user context from X-User-ID header.

    Args:
        authorization: Authorization header (Bearer {SERVICE_AUTH_TOKEN})
        x_user_id: User ID from X-User-ID header

    Returns:
        User ID string from X-User-ID header

    Raises:
        HTTPException: 401 if service token is invalid
        HTTPException: 400 if X-User-ID header is missing
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization.split(" ", 1)[1]

    # Use constant-time comparison to prevent timing attacks
    if not settings.SERVICE_AUTH_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Service authentication not configured",
        )

    if not hmac.compare_digest(token, settings.SERVICE_AUTH_TOKEN):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid service authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing X-User-ID header",
        )

    return x_user_id


async def get_current_user_or_service(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    x_user_id: Optional[str] = Header(None, alias="X-User-ID"),
) -> str:
    """
    Authenticate user via service token or JWT access token.

    This dependency supports dual authentication:
    - If X-User-ID header is present: use service authentication flow (MCP server)
    - Otherwise: use JWT authentication flow

    Args:
        credentials: HTTP Authorization credentials (Bearer token)
        x_user_id: Optional X-User-ID header for service authentication

    Returns:
        User ID string

    Raises:
        HTTPException: 401 if authentication fails
        HTTPException: 400 if X-User-ID is present but service auth fails
    """
    # Service authentication flow (MCP server)
    if x_user_id is not None:
        if credentials is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authorization header for service authentication",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = credentials.credentials

        # Validate service token
        if not settings.SERVICE_AUTH_TOKEN:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Service authentication not configured",
            )

        if not hmac.compare_digest(token, settings.SERVICE_AUTH_TOKEN):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid service authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return x_user_id

    # JWT authentication flow
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    try:
        user_id = jwt_service.validate_access_token(token)
        return user_id
    except TokenExpiredError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error_code": "token_expired", "message": "Access token has expired"},
            headers={"WWW-Authenticate": "Bearer"},
        )
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error_code": "invalid_token", "message": str(e)},
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_task_repository(
    db: AsyncSession = Depends(get_db)
) -> TaskRepository:
    """
    Dependency to get TaskRepository instance.

    Args:
        db: Database session from get_db dependency

    Returns:
        TaskRepository instance
    """
    return TaskRepository(db)