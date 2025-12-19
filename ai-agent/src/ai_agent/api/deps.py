"""FastAPI dependencies for authentication and database access."""

from typing import Annotated, AsyncGenerator

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from ai_agent.database.connection import async_session_maker
from ai_agent.services.auth import AuthService


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Database session dependency.

    Provides an async database session and ensures proper cleanup.
    """
    async with async_session_maker() as session:
        yield session


async def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
    db: AsyncSession = Depends(get_db),
) -> str:
    """
    Authentication dependency.

    Validates the Bearer token from Authorization header and returns user_id.

    Args:
        authorization: Authorization header (Bearer <token>)
        db: Database session

    Returns:
        user_id of the authenticated user

    Raises:
        HTTPException: If authentication fails
    """
    auth_service = AuthService()
    token = auth_service.parse_bearer_token(authorization)
    user_id = await auth_service.validate_session(db, token)
    return user_id


# Type aliases for dependency injection
DbSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[str, Depends(get_current_user)]
