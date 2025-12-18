"""HTTP client for FastAPI backend communication."""

import logging
from datetime import datetime
from typing import Any, Optional

import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from .config import settings

logger = logging.getLogger(__name__)


class BackendClient:
    """HTTP client for communicating with FastAPI backend."""

    def __init__(self):
        """Initialize backend client with configuration."""
        self.base_url = settings.fastapi_base_url
        self.timeout = settings.backend_timeout
        self.max_retries = settings.backend_max_retries
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
        )

    def _build_headers(self, user_id: str) -> dict[str, str]:
        """Build headers for authenticated backend requests.

        Args:
            user_id: User ID from MCP session context

        Returns:
            Dictionary of HTTP headers
        """
        return {
            "Authorization": f"Bearer {settings.service_auth_token}",
            "X-User-ID": user_id,
            "Content-Type": "application/json",
        }

    @retry(
        stop=stop_after_attempt(3),  # Initial + 2 retries
        wait=wait_exponential(multiplier=1, min=1, max=2),  # 1s, 2s backoff
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError)),
        reraise=True,
    )
    async def _request(
        self,
        method: str,
        endpoint: str,
        user_id: str,
        json: Optional[dict[str, Any]] = None,
    ) -> httpx.Response:
        """Make HTTP request to backend with retry logic.

        Args:
            method: HTTP method (GET, POST, PUT, PATCH, DELETE)
            endpoint: API endpoint path
            user_id: User ID for context propagation
            json: Optional JSON body

        Returns:
            HTTP response

        Raises:
            httpx.TimeoutException: Request timed out after retries
            httpx.ConnectError: Connection failed after retries
        """
        start_time = datetime.now()
        headers = self._build_headers(user_id)

        try:
            response = await self.client.request(
                method=method,
                url=endpoint,
                headers=headers,
                json=json,
            )

            duration_ms = (datetime.now() - start_time).total_seconds() * 1000

            # Log successful request
            logger.info(
                "Backend API call completed",
                extra={
                    "timestamp": datetime.now().isoformat(),
                    "endpoint": endpoint,
                    "method": method,
                    "status_code": response.status_code,
                    "user_id": user_id,
                    "duration_ms": duration_ms,
                },
            )

            return response

        except (httpx.TimeoutException, httpx.ConnectError) as e:
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000

            # Log failed request
            logger.error(
                "Backend API call failed",
                extra={
                    "timestamp": datetime.now().isoformat(),
                    "endpoint": endpoint,
                    "method": method,
                    "user_id": user_id,
                    "duration_ms": duration_ms,
                    "error": str(e),
                },
            )
            raise

    async def get_tasks(self, user_id: str) -> httpx.Response:
        """Retrieve all tasks for the user.

        Args:
            user_id: User ID from MCP session context

        Returns:
            HTTP response from backend
        """
        return await self._request("GET", "/tasks/", user_id)

    async def create_task(
        self, user_id: str, task_data: dict[str, Any]
    ) -> httpx.Response:
        """Create a new task.

        Args:
            user_id: User ID from MCP session context
            task_data: Task creation data

        Returns:
            HTTP response from backend
        """
        return await self._request("POST", "/tasks/", user_id, json=task_data)

    async def update_task(
        self, user_id: str, task_id: int, task_data: dict[str, Any]
    ) -> httpx.Response:
        """Update an existing task.

        Args:
            user_id: User ID from MCP session context
            task_id: ID of task to update
            task_data: Task update data

        Returns:
            HTTP response from backend
        """
        return await self._request("PUT", f"/tasks/{task_id}", user_id, json=task_data)

    async def mark_task_completed(
        self, user_id: str, task_id: int
    ) -> httpx.Response:
        """Mark a task as completed.

        Args:
            user_id: User ID from MCP session context
            task_id: ID of task to mark as completed

        Returns:
            HTTP response from backend
        """
        return await self._request(
            "PATCH", f"/tasks/{task_id}", user_id, json={"completed": True}
        )

    async def delete_task(self, user_id: str, task_id: int) -> httpx.Response:
        """Delete a task.

        Args:
            user_id: User ID from MCP session context
            task_id: ID of task to delete

        Returns:
            HTTP response from backend
        """
        return await self._request("DELETE", f"/tasks/{task_id}", user_id)

    async def close(self):
        """Close the HTTP client connection."""
        await self.client.aclose()
