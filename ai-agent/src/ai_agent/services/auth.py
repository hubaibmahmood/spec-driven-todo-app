"""Authentication service for AI Agent."""

from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from ai_agent.database.models import UserSession


class AuthService:
    """Handles authentication by validating session tokens."""

    @staticmethod
    def parse_bearer_token(authorization: Optional[str]) -> str:
        """
        Extract token from Authorization header.

        Args:
            authorization: Authorization header value (e.g., "Bearer <token>")

        Returns:
            The extracted token

        Raises:
            HTTPException: If authorization header is missing or malformed
        """
        if not authorization:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing Authorization header",
                headers={"WWW-Authenticate": "Bearer"},
            )

        parts = authorization.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Authorization header format. Expected: Bearer <token>",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return parts[1]

    @staticmethod
    async def validate_session(db: AsyncSession, token: str) -> str:
        """
        Validate session token and return user_id.

        Args:
            db: Database session
            token: Session token to validate

        Returns:
            user_id if session is valid

        Raises:
            HTTPException: If session is invalid or expired
        """
        # Query user_sessions table
        statement = select(UserSession).where(UserSession.token == token)
        result = await db.execute(statement)
        session = result.scalar_one_or_none()

        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid session token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Check if session has expired
        now = datetime.now(timezone.utc)
        # Make expires_at timezone-aware if it isn't already
        expires_at = session.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        if expires_at < now:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return session.user_id
