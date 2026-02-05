"""JWT token generation and validation service."""

from datetime import UTC, datetime, timedelta
from typing import Dict, Any
import jwt
from prometheus_client import Histogram
from ..config import settings

# Prometheus metrics
auth_validation_duration = Histogram(
    'auth_validation_seconds',
    'Time spent validating authentication tokens',
    ['method']
)


class TokenExpiredError(Exception):
    """Raised when a JWT token has expired."""
    pass


class InvalidTokenError(Exception):
    """Raised when a JWT token is invalid."""
    pass


class JWTService:
    """Service for generating and validating JWT access tokens."""

    def __init__(self):
        """Initialize JWT service with configuration from settings."""
        self.secret = settings.JWT_SECRET
        self.algorithm = settings.JWT_ALGORITHM
        self.access_token_expire_minutes = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES

    def generate_access_token(self, user_id: str) -> str:
        """
        Generate a new JWT access token for the given user.

        Args:
            user_id: The user's unique identifier

        Returns:
            A signed JWT access token string

        The token contains:
            - sub: user ID (subject)
            - iat: issued at timestamp
            - exp: expiration timestamp (30 minutes from now)
            - type: "access" (to distinguish from other token types)
        """
        now = datetime.now(UTC)
        expires_at = now + timedelta(minutes=self.access_token_expire_minutes)

        payload: Dict[str, Any] = {
            "sub": user_id,
            "iat": now,
            "exp": expires_at,
            "type": "access"
        }

        token = jwt.encode(payload, self.secret, algorithm=self.algorithm)
        return token

    def validate_access_token(self, token: str) -> str:
        """
        Validate a JWT access token and extract the user ID.

        Args:
            token: The JWT access token string to validate

        Returns:
            The user_id extracted from the token's "sub" claim

        Raises:
            TokenExpiredError: If the token has expired
            InvalidTokenError: If the token is invalid (bad signature, malformed, wrong type)
        """
        with auth_validation_duration.labels(method='jwt').time():
            try:
                payload = jwt.decode(
                    token,
                    self.secret,
                    algorithms=[self.algorithm]
                )

                # Verify token type
                if payload.get("type") != "access":
                    raise InvalidTokenError("Invalid token type")

                user_id = payload.get("sub")
                if not user_id:
                    raise InvalidTokenError("Missing subject claim")

                return user_id

            except jwt.ExpiredSignatureError as e:
                raise TokenExpiredError("Access token has expired") from e
            except jwt.InvalidTokenError as e:
                raise InvalidTokenError(f"Invalid access token: {e}") from e
            except Exception as e:
                raise InvalidTokenError(f"Token validation failed: {e}") from e


# Global service instance
jwt_service = JWTService()
