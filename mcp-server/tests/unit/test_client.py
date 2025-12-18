"""Unit tests for BackendClient."""

from datetime import datetime
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from src.client import BackendClient
from src.config import settings


@pytest.fixture
def backend_client():
    """Create a BackendClient instance for testing."""
    return BackendClient()


class TestBackendClientGetTasks:
    """Unit tests for BackendClient.get_tasks method."""

    @pytest.mark.asyncio
    async def test_headers_include_authorization_and_user_id(
        self, backend_client, test_user_id
    ):
        """Test that get_tasks includes Authorization and X-User-ID headers."""
        # Mock the httpx client response
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []

        with patch.object(
            backend_client.client, "request", return_value=mock_response
        ) as mock_request:
            await backend_client.get_tasks(test_user_id)

            # Verify request was called with correct headers
            mock_request.assert_called_once()
            call_kwargs = mock_request.call_args.kwargs

            assert "headers" in call_kwargs
            headers = call_kwargs["headers"]
            assert headers["Authorization"] == f"Bearer {settings.service_auth_token}"
            assert headers["X-User-ID"] == test_user_id
            assert headers["Content-Type"] == "application/json"

    @pytest.mark.asyncio
    async def test_get_tasks_makes_get_request_to_tasks_endpoint(
        self, backend_client, test_user_id
    ):
        """Test that get_tasks makes GET request to /tasks endpoint."""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []

        with patch.object(
            backend_client.client, "request", return_value=mock_response
        ) as mock_request:
            await backend_client.get_tasks(test_user_id)

            # Verify GET request to /tasks
            mock_request.assert_called_once()
            call_args = mock_request.call_args

            assert call_args.kwargs["method"] == "GET"
            assert call_args.kwargs["url"] == "/tasks"

    @pytest.mark.asyncio
    async def test_retry_logic_on_timeout(self, backend_client, test_user_id):
        """Test that get_tasks retries on timeout errors."""
        # First two calls timeout, third succeeds
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []

        with patch.object(
            backend_client.client,
            "request",
            side_effect=[
                httpx.TimeoutException("Request timeout"),
                httpx.TimeoutException("Request timeout"),
                mock_response,
            ],
        ) as mock_request:
            response = await backend_client.get_tasks(test_user_id)

            # Should have retried twice (3 total attempts)
            assert mock_request.call_count == 3
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_retry_logic_on_connection_error(self, backend_client, test_user_id):
        """Test that get_tasks retries on connection errors."""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []

        with patch.object(
            backend_client.client,
            "request",
            side_effect=[
                httpx.ConnectError("Connection refused"),
                httpx.ConnectError("Connection refused"),
                mock_response,
            ],
        ) as mock_request:
            response = await backend_client.get_tasks(test_user_id)

            # Should have retried twice (3 total attempts)
            assert mock_request.call_count == 3
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_raises_timeout_after_max_retries(self, backend_client, test_user_id):
        """Test that get_tasks raises TimeoutException after max retries."""
        with patch.object(
            backend_client.client,
            "request",
            side_effect=httpx.TimeoutException("Request timeout"),
        ) as mock_request:
            with pytest.raises(httpx.TimeoutException):
                await backend_client.get_tasks(test_user_id)

            # Should have attempted 3 times (initial + 2 retries)
            assert mock_request.call_count == 3

    @pytest.mark.asyncio
    async def test_raises_connection_error_after_max_retries(
        self, backend_client, test_user_id
    ):
        """Test that get_tasks raises ConnectError after max retries."""
        with patch.object(
            backend_client.client,
            "request",
            side_effect=httpx.ConnectError("Connection refused"),
        ) as mock_request:
            with pytest.raises(httpx.ConnectError):
                await backend_client.get_tasks(test_user_id)

            # Should have attempted 3 times (initial + 2 retries)
            assert mock_request.call_count == 3

    @pytest.mark.asyncio
    async def test_timeout_handling(self, backend_client, test_user_id):
        """Test that get_tasks handles timeout exceptions correctly."""
        with patch.object(
            backend_client.client,
            "request",
            side_effect=httpx.TimeoutException("Request timeout"),
        ):
            with pytest.raises(httpx.TimeoutException) as exc_info:
                await backend_client.get_tasks(test_user_id)

            assert "timeout" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_successful_response_returned(self, backend_client, test_user_id):
        """Test that successful response is returned correctly."""
        expected_tasks = [
            {
                "id": 1,
                "title": "Test Task",
                "completed": False,
                "priority": "Medium",
                "created_at": "2025-12-18T10:00:00Z",
                "updated_at": "2025-12-18T10:00:00Z",
                "user_id": test_user_id,
            }
        ]

        mock_response = AsyncMock()
        mock_response.status_code = 200

        with patch.object(
            backend_client.client, "request", return_value=mock_response
        ):
            response = await backend_client.get_tasks(test_user_id)

            assert response.status_code == 200
            # Just verify we got a response object back
            assert response is not None


class TestBackendClientCreateTask:
    """Unit tests for BackendClient.create_task method."""

    @pytest.mark.asyncio
    async def test_post_request_to_tasks_endpoint(
        self, backend_client, test_user_id
    ):
        """Test that create_task makes POST request to /tasks endpoint."""
        task_data = {
            "title": "Buy milk",
            "description": "Get 2% milk",
            "priority": "Medium",
        }

        mock_response = AsyncMock()
        mock_response.status_code = 201

        with patch.object(
            backend_client.client, "request", return_value=mock_response
        ) as mock_request:
            await backend_client.create_task(test_user_id, task_data)

            # Verify POST request to /tasks
            mock_request.assert_called_once()
            call_args = mock_request.call_args

            assert call_args.kwargs["method"] == "POST"
            assert call_args.kwargs["url"] == "/tasks"

    @pytest.mark.asyncio
    async def test_headers_include_auth_and_user_context(
        self, backend_client, test_user_id
    ):
        """Test that create_task includes Authorization and X-User-ID headers."""
        task_data = {"title": "Test Task"}

        mock_response = AsyncMock()
        mock_response.status_code = 201

        with patch.object(
            backend_client.client, "request", return_value=mock_response
        ) as mock_request:
            await backend_client.create_task(test_user_id, task_data)

            # Verify headers
            call_kwargs = mock_request.call_args.kwargs
            headers = call_kwargs["headers"]

            assert headers["Authorization"] == f"Bearer {settings.service_auth_token}"
            assert headers["X-User-ID"] == test_user_id
            assert headers["Content-Type"] == "application/json"

    @pytest.mark.asyncio
    async def test_json_body_structure(self, backend_client, test_user_id):
        """Test that create_task sends correct JSON body."""
        task_data = {
            "title": "Buy milk",
            "description": "Get 2% milk",
            "priority": "High",
            "due_date": "2025-12-20T10:00:00Z",
        }

        mock_response = AsyncMock()
        mock_response.status_code = 201

        with patch.object(
            backend_client.client, "request", return_value=mock_response
        ) as mock_request:
            await backend_client.create_task(test_user_id, task_data)

            # Verify JSON body
            call_kwargs = mock_request.call_args.kwargs
            assert call_kwargs["json"] == task_data

    @pytest.mark.asyncio
    async def test_retry_on_failure(self, backend_client, test_user_id):
        """Test that create_task retries on timeout or connection errors."""
        task_data = {"title": "Test Task"}

        mock_response = AsyncMock()
        mock_response.status_code = 201

        with patch.object(
            backend_client.client,
            "request",
            side_effect=[
                httpx.TimeoutException("Request timeout"),
                httpx.TimeoutException("Request timeout"),
                mock_response,
            ],
        ) as mock_request:
            response = await backend_client.create_task(test_user_id, task_data)

            # Should have retried twice (3 total attempts)
            assert mock_request.call_count == 3
            assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_successful_response_returned(self, backend_client, test_user_id):
        """Test that successful 201 response is returned correctly."""
        task_data = {"title": "Buy milk"}

        expected_task = {
            "id": 1,
            "title": "Buy milk",
            "description": None,
            "completed": False,
            "priority": "Medium",
            "due_date": None,
            "created_at": "2025-12-18T10:00:00Z",
            "updated_at": "2025-12-18T10:00:00Z",
            "user_id": test_user_id,
        }

        mock_response = AsyncMock()
        mock_response.status_code = 201

        with patch.object(
            backend_client.client, "request", return_value=mock_response
        ):
            response = await backend_client.create_task(test_user_id, task_data)

            assert response.status_code == 201
            assert response is not None
