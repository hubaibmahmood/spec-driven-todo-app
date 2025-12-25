"""Service for retrieving user-specific API keys from the backend."""

import logging
from typing import Optional

import httpx
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ApiKeyResponse(BaseModel):
    """Response from backend GET /api/user-api-keys/current endpoint."""

    configured: bool
    provider: Optional[str] = None
    plaintext_key: Optional[str] = None  # Decrypted key for ai-agent use
    validation_status: Optional[str] = None
    last_validated_at: Optional[str] = None


class ApiKeyRetrievalService:
    """Service for fetching user-specific API keys from the backend."""

    def __init__(self, backend_url: str = "http://localhost:8000"):
        """
        Initialize ApiKeyRetrievalService.

        Args:
            backend_url: Base URL of the FastAPI backend
        """
        self.backend_url = backend_url.rstrip("/")
        self.client = httpx.AsyncClient(timeout=10.0)

    async def get_user_api_key(
        self, user_id: str, service_auth_token: str
    ) -> Optional[str]:
        """
        Fetch user's API key from the backend.

        Args:
            user_id: User ID to fetch API key for
            service_auth_token: Service-to-service authentication token

        Returns:
            Decrypted API key if configured, None otherwise

        Raises:
            ValueError: If service authentication fails (configuration issue)
            httpx.HTTPError: If backend request fails (network errors)

        Examples:
            >>> service = ApiKeyRetrievalService()
            >>> key = await service.get_user_api_key("user123", "service_token")
            >>> assert key is not None or key is None
        """
        endpoint = f"{self.backend_url}/api/user-api-keys/current"

        try:
            response = await self.client.get(
                endpoint,
                headers={
                    "X-User-ID": user_id,
                    "X-Service-Auth": service_auth_token,
                },
            )

            # User has no API key configured - this is OK, return None
            if response.status_code == 404:
                logger.info(f"User {user_id[:8]}... has no API key configured")
                return None

            # Service auth token is wrong - configuration error
            if response.status_code == 401:
                error_detail = response.json().get("detail", "Unknown error")
                logger.error(
                    f"Service authentication failed: {error_detail}. "
                    f"Check SERVICE_AUTH_TOKEN in ai-agent and backend .env files"
                )
                raise ValueError(
                    f"Service authentication failed: {error_detail}. "
                    f"This is a configuration issue - check SERVICE_AUTH_TOKEN."
                )

            # Other errors
            if response.status_code != 200:
                logger.error(
                    f"Failed to fetch API key: {response.status_code} {response.text}"
                )
                raise httpx.HTTPError(
                    f"Backend returned {response.status_code}: {response.text}"
                )

            data = response.json()
            api_key_response = ApiKeyResponse(**data)

            # User has no API key configured - this is OK, return None
            if not api_key_response.configured or not api_key_response.plaintext_key:
                logger.info(f"User {user_id[:8]}... has no API key configured")
                return None

            logger.info(f"Successfully retrieved API key for user {user_id[:8]}...")
            return api_key_response.plaintext_key

        except httpx.RequestError as e:
            logger.error(f"Network error fetching API key: {e}")
            raise httpx.HTTPError(f"Network error: {e}")

    async def close(self):
        """Close HTTP client connections."""
        await self.client.aclose()
