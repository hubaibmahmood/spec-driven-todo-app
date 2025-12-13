"""FastAPI dependencies for dependency injection."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.connection import get_db
from src.database.repository import TaskRepository
from src.services.auth_service import validate_session


# HTTPBearer security scheme for extracting Bearer tokens
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> str:
    """
    Authenticate user via session token and return user ID.

    Extracts Bearer token from Authorization header, validates it against
    the user_sessions table, and returns the authenticated user's ID.

    Args:
        credentials: HTTP Authorization credentials (Bearer token)
        db: Database session

    Returns:
        User ID string if session is valid

    Raises:
        HTTPException: 401 if token is missing, invalid, expired, or revoked
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    user_id = await validate_session(token, db)

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_id


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