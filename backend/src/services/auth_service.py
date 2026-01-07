"""Session authentication service."""

import hashlib
import hmac
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from prometheus_client import Histogram

from src.models.database import UserSession
from src.config import settings

# Prometheus metrics - shared with jwt_service.py
from prometheus_client import REGISTRY

# Get or create the histogram metric (shared with jwt_service)
try:
    auth_validation_duration = REGISTRY._names_to_collectors['auth_validation_seconds']
except KeyError:
    auth_validation_duration = Histogram(
        'auth_validation_seconds',
        'Time spent validating authentication tokens',
        ['method']
    )


class SessionTokenHasher:
    """Hash and verify session tokens using HMAC-SHA256.

    Note: This is kept for potential future use or if better-auth token
    storage requirements change. Currently, FastAPI validates tokens directly
    against the plain token stored by better-auth.
    """

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


async def validate_session(token: str, db: AsyncSession) -> Optional[str]:
    """
    Validate a session token and return the user ID.

    Queries user_sessions table for:
    - token matches the provided token (better-auth stores plain tokens)
    - expires_at > now (not expired)

    Note: better-auth uses a token format of {tokenId}.{signature}, but only
    stores the tokenId part in the database.

    Args:
        token: Session token from Authorization header (format: tokenId.signature)
        db: Database session

    Returns:
        User ID string if session is valid, None otherwise
    """
    with auth_validation_duration.labels(method='session').time():
        # Extract token ID from the full token (before the first dot)
        # better-auth format: {tokenId}.{signature}
        token_id = token.split('.')[0] if '.' in token else token

        # Query for valid session - better-auth stores only the token ID
        # Note: Database stores timestamps without timezone, but they are in UTC
        # So we use datetime.now(timezone.utc).replace(tzinfo=None) to get naive UTC time
        current_time_utc = datetime.now(timezone.utc).replace(tzinfo=None)

        stmt = select(UserSession).where(
            UserSession.token == token_id,
            UserSession.expires_at > current_time_utc
        )

        result = await db.execute(stmt)
        session = result.scalar_one_or_none()

        if session is None:
            return None

        return session.user_id
