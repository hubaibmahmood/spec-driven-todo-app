"""JWT token validation service for AI Agent.

This module provides JWT validation utilities that mirror the backend's JWT service.
The AI Agent validates JWT access tokens using the same shared secret.
"""

import os
from typing import Any, Dict

import jwt


class TokenExpiredError(Exception):
    """Raised when a JWT token has expired."""

    pass


class InvalidTokenError(Exception):
    """Raised when a JWT token is invalid."""

    pass


class JWTValidationService:
    """Service for validating JWT access tokens.

    This service validates tokens issued by the auth-server and ensures
    they are correctly signed and not expired.
    """

    def __init__(self):
        """Initialize JWT validation service with configuration from environment."""
        self.secret = os.getenv(
            "JWT_SECRET", "dev-jwt-secret-min-32-chars-change-in-production-please"
        )
        self.algorithm = os.getenv("JWT_ALGORITHM", "HS256")

    def validate_access_token(self, token: str) -> str:
        """
        Validate a JWT access token and extract the user ID.

        This method validates:
        - JWT signature using the shared secret
        - Token expiration
        - Token type (must be "access")
        - Presence of subject claim (user_id)

        Args:
            token: The JWT access token string to validate

        Returns:
            The user_id extracted from the token's "sub" claim

        Raises:
            TokenExpiredError: If the token has expired
            InvalidTokenError: If the token is invalid (bad signature, malformed, wrong type)
        """
        try:
            payload: Dict[str, Any] = jwt.decode(
                token, self.secret, algorithms=[self.algorithm]
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
jwt_validation_service = JWTValidationService()
