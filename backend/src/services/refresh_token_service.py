"""Refresh token generation, hashing, and validation service."""

import hashlib
import hmac
import secrets
from datetime import UTC, datetime, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from ..models.database import UserSession
from ..config import settings


class RefreshTokenError(Exception):
    """Base exception for refresh token operations."""
    pass


class RefreshTokenService:
    """Service for managing refresh tokens."""

    def __init__(self):
        """Initialize refresh token service with configuration."""
        self.refresh_token_expire_days = settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS

    def generate_refresh_token(self) -> str:
        """
        Generate a cryptographically secure refresh token.

        Returns:
            A URL-safe base64-encoded random string (32 bytes)
        """
        return secrets.token_urlsafe(32)

    def hash_refresh_token(self, token: str) -> str:
        """
        Hash a refresh token using SHA-256.

        Args:
            token: The refresh token to hash

        Returns:
            Hexadecimal string of the SHA-256 hash
        """
        return hashlib.sha256(token.encode()).hexdigest()

    async def store_refresh_token(
        self,
        db: AsyncSession,
        user_id: str,
        token: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> None:
        """
        Store a hashed refresh token in the database.

        Args:
            db: Database session
            user_id: The user's unique identifier
            token: The plaintext refresh token (will be hashed before storage)
            ip_address: Optional IP address of the client
            user_agent: Optional user agent string

        Note: Only the hashed token is stored in the database for security.
        """
        hashed_token = self.hash_refresh_token(token)
        expires_at = datetime.now(UTC) + timedelta(days=self.refresh_token_expire_days)

        session = UserSession(
            user_id=user_id,
            token=hashed_token,
            expires_at=expires_at,
            ip_address=ip_address or "",
            user_agent=user_agent or ""
        )

        db.add(session)
        await db.commit()

    async def validate_refresh_token(
        self,
        db: AsyncSession,
        token: str
    ) -> str:
        """
        Validate a refresh token and return the associated user ID.

        Args:
            db: Database session
            token: The plaintext refresh token to validate

        Returns:
            The user_id associated with this refresh token

        Raises:
            RefreshTokenError: If the token is invalid, expired, or not found
        """
        hashed_token = self.hash_refresh_token(token)

        # Query for session with this token hash
        result = await db.execute(
            select(UserSession).where(UserSession.token == hashed_token)
        )
        session = result.scalar_one_or_none()

        if not session:
            raise RefreshTokenError("Invalid refresh token")

        # Check if token has expired
        if session.expires_at < datetime.now(UTC):
            # Clean up expired token
            await db.delete(session)
            await db.commit()
            raise RefreshTokenError("Refresh token has expired")

        # Use constant-time comparison for security (prevent timing attacks)
        if not hmac.compare_digest(session.token, hashed_token):
            raise RefreshTokenError("Invalid refresh token")

        return session.user_id

    async def delete_refresh_token(
        self,
        db: AsyncSession,
        token: str
    ) -> None:
        """
        Delete a refresh token from the database (for logout).

        Args:
            db: Database session
            token: The plaintext refresh token to delete
        """
        hashed_token = self.hash_refresh_token(token)

        await db.execute(
            delete(UserSession).where(UserSession.token == hashed_token)
        )
        await db.commit()


# Global service instance
refresh_token_service = RefreshTokenService()
