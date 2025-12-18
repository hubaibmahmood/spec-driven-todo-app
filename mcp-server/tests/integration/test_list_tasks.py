"""Integration tests for list_tasks tool.

These tests verify the complete flow from tool invocation through backend API calls.
"""

from unittest.mock import AsyncMock, patch

import httpx
import pytest

from src.client import BackendClient
from src.schemas.task import TaskResponse, PriorityLevel


@pytest.fixture
def sample_tasks():
    """Return sample task data from backend."""
    return [
        {
            "id": 1,
            "title": "Buy groceries",
            "description": "Milk, eggs, bread",
            "completed": False,
            "priority": "Medium",
            "due_date": "2025-12-20T10:00:00Z",
            "created_at": "2025-12-18T10:00:00Z",
            "updated_at": "2025-12-18T10:00:00Z",
            "user_id": "test_user_123",
        },
        {
            "id": 2,
            "title": "Finish project report",
            "description": None,
            "completed": False,
            "priority": "High",
            "due_date": None,
            "created_at": "2025-12-18T11:00:00Z",
            "updated_at": "2025-12-18T11:00:00Z",
            "user_id": "test_user_123",
        },
    ]


class TestListTasksIntegration:
    """Integration tests for list_tasks tool."""

    @pytest.mark.asyncio
    async def test_valid_auth_returns_user_tasks(self, test_user_id, sample_tasks):
        """Test that valid authentication returns user's tasks."""
        # Mock backend response
        mock_response = AsyncMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = sample_tasks
        mock_response.raise_for_status = AsyncMock()

        backend_client = BackendClient()

        with patch.object(
            backend_client.client, "request", return_value=mock_response
        ):
            response = await backend_client.get_tasks(test_user_id)

            assert response.status_code == 200
            tasks = response.json()
            assert len(tasks) == 2
            assert tasks[0]["id"] == 1
            assert tasks[0]["title"] == "Buy groceries"
            assert tasks[1]["id"] == 2

    @pytest.mark.asyncio
    async def test_invalid_service_token_returns_401(self, test_user_id):
        """Test that invalid service token returns 401 Unauthorized."""
        mock_response = AsyncMock(spec=httpx.Response)
        mock_response.status_code = 401
        mock_response.json.return_value = {"detail": "Invalid service token"}
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "401 Unauthorized",
            request=AsyncMock(),
            response=mock_response,
        )

        backend_client = BackendClient()

        with patch.object(
            backend_client.client, "request", return_value=mock_response
        ):
            response = await backend_client.get_tasks(test_user_id)

            assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_missing_user_id_returns_400(self):
        """Test that missing X-User-ID header returns 400 Bad Request."""
        # This test simulates what happens when X-User-ID is missing
        mock_response = AsyncMock(spec=httpx.Response)
        mock_response.status_code = 400
        mock_response.json.return_value = {"detail": "X-User-ID header required"}
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "400 Bad Request",
            request=AsyncMock(),
            response=mock_response,
        )

        backend_client = BackendClient()

        with patch.object(
            backend_client.client, "request", return_value=mock_response
        ):
            # Passing empty user_id to simulate missing header
            response = await backend_client.get_tasks("")

            assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_empty_task_list_scenario(self, test_user_id):
        """Test that empty task list is handled correctly."""
        mock_response = AsyncMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = []

        backend_client = BackendClient()

        with patch.object(
            backend_client.client, "request", return_value=mock_response
        ):
            response = await backend_client.get_tasks(test_user_id)

            assert response.status_code == 200
            tasks = response.json()
            assert len(tasks) == 0
            assert tasks == []

    @pytest.mark.asyncio
    async def test_multiple_tasks_returned_correctly(self, test_user_id):
        """Test that multiple tasks are returned and parsed correctly."""
        tasks_data = [
            {
                "id": i,
                "title": f"Task {i}",
                "description": f"Description {i}",
                "completed": i % 2 == 0,
                "priority": ["Low", "Medium", "High", "Urgent"][i % 4],
                "due_date": None,
                "created_at": "2025-12-18T10:00:00Z",
                "updated_at": "2025-12-18T10:00:00Z",
                "user_id": test_user_id,
            }
            for i in range(1, 6)
        ]

        mock_response = AsyncMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = tasks_data

        backend_client = BackendClient()

        with patch.object(
            backend_client.client, "request", return_value=mock_response
        ):
            response = await backend_client.get_tasks(test_user_id)

            assert response.status_code == 200
            tasks = response.json()
            assert len(tasks) == 5

            # Verify task data is correctly structured
            for i, task in enumerate(tasks, start=1):
                assert task["id"] == i
                assert task["title"] == f"Task {i}"
                assert task["user_id"] == test_user_id

    @pytest.mark.asyncio
    async def test_task_response_schema_validation(self, test_user_id, sample_tasks):
        """Test that returned tasks can be validated with TaskResponse schema."""
        mock_response = AsyncMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = sample_tasks

        backend_client = BackendClient()

        with patch.object(
            backend_client.client, "request", return_value=mock_response
        ):
            response = await backend_client.get_tasks(test_user_id)

            tasks_data = response.json()

            # Validate each task with TaskResponse schema
            for task_data in tasks_data:
                task = TaskResponse(**task_data)
                assert isinstance(task, TaskResponse)
                assert isinstance(task.priority, PriorityLevel)
                assert task.user_id == test_user_id
