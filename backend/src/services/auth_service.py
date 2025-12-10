"""Session authentication service."""

import hashlib
import hmac
from datetime import datetime, timezone
from uuid import UUID
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.database import UserSession
from src.config import settings


class SessionTokenHasher:
    """Hash and verify session tokens using HMAC-SHA256."""

    def __init__(self, secret: str):
        """
        Initialize token hasher with secret key.

        Args:
            secret: Secret key for HMAC hashing
        """
        self.secret = secret.encode()

    def hash_token(self, token: str) -> str:
        """
        Hash a session token using HMAC-SHA256.

        Args:
            token: Plain session token

        Returns:
            Hex-encoded hash of the token
        """
        return hmac.new(
            self.secret,
            token.encode(),
            hashlib.sha256
        ).hexdigest()

    def verify_token_against_hash(self, token: str, token_hash: str) -> bool:
        """
        Verify a token matches its hash using constant-time comparison.

        Args:
            token: Plain session token
            token_hash: Expected hash to verify against

        Returns:
            True if token matches hash, False otherwise
        """
        computed_hash = self.hash_token(token)
        return hmac.compare_digest(computed_hash, token_hash)


async def validate_session(token: str, db: AsyncSession) -> Optional[UUID]:
    """
    Validate a session token and return the user ID.

    Queries user_sessions table for:
    - token_hash matches the hashed token
    - expires_at > now (not expired)
    - revoked = False (not revoked)

    Args:
        token: Plain session token from Authorization header
        db: Database session

    Returns:
        User UUID if session is valid, None otherwise
    """
    # Hash the token
    hasher = SessionTokenHasher(settings.SESSION_HASH_SECRET)
    token_hash = hasher.hash_token(token)

    # Query for valid session
    stmt = select(UserSession).where(
        UserSession.token_hash == token_hash,
        UserSession.expires_at > datetime.now(timezone.utc),
        UserSession.revoked == False  # noqa: E712
    )

    result = await db.execute(stmt)
    session = result.scalar_one_or_none()

    if session is None:
        return None

    return session.user_id
