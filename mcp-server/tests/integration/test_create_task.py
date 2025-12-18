"""Integration tests for create_task tool.

These tests verify the complete flow from tool invocation through backend API calls.
"""

from unittest.mock import AsyncMock, patch

import httpx
import pytest

from src.client import BackendClient
from src.schemas.task import CreateTaskParams, TaskResponse, PriorityLevel


class TestCreateTaskIntegration:
    """Integration tests for create_task tool."""

    @pytest.mark.asyncio
    async def test_create_with_title_only_applies_defaults(self, test_user_id):
        """Test creating task with title only applies default values."""
        task_data = {"title": "Buy milk"}

        created_task_response = {
            "id": 1,
            "title": "Buy milk",
            "description": None,
            "completed": False,
            "priority": "Medium",  # Default priority
            "due_date": None,
            "created_at": "2025-12-18T10:00:00Z",
            "updated_at": "2025-12-18T10:00:00Z",
            "user_id": test_user_id,
        }

        mock_response = AsyncMock(spec=httpx.Response)
        mock_response.status_code = 201
        mock_response.json.return_value = created_task_response

        backend_client = BackendClient()

        with patch.object(
            backend_client.client, "request", return_value=mock_response
        ):
            response = await backend_client.create_task(test_user_id, task_data)

            assert response.status_code == 201
            created_task = response.json()
            assert created_task["id"] == 1
            assert created_task["title"] == "Buy milk"
            assert created_task["priority"] == "Medium"
            assert created_task["completed"] is False

    @pytest.mark.asyncio
    async def test_create_with_all_fields(self, test_user_id):
        """Test creating task with all fields populated."""
        task_data = {
            "title": "Complete project report",
            "description": "Finish the Q4 2025 report with charts",
            "priority": "High",
            "due_date": "2025-12-31T23:59:59Z",
        }

        created_task_response = {
            "id": 2,
            "title": "Complete project report",
            "description": "Finish the Q4 2025 report with charts",
            "completed": False,
            "priority": "High",
            "due_date": "2025-12-31T23:59:59Z",
            "created_at": "2025-12-18T10:00:00Z",
            "updated_at": "2025-12-18T10:00:00Z",
            "user_id": test_user_id,
        }

        mock_response = AsyncMock(spec=httpx.Response)
        mock_response.status_code = 201
        mock_response.json.return_value = created_task_response

        backend_client = BackendClient()

        with patch.object(
            backend_client.client, "request", return_value=mock_response
        ):
            response = await backend_client.create_task(test_user_id, task_data)

            assert response.status_code == 201
            created_task = response.json()
            assert created_task["title"] == "Complete project report"
            assert created_task["description"] == "Finish the Q4 2025 report with charts"
            assert created_task["priority"] == "High"
            assert created_task["due_date"] == "2025-12-31T23:59:59Z"

    @pytest.mark.asyncio
    async def test_validation_error_empty_title(self, test_user_id):
        """Test that empty title triggers validation error."""
        # This validation happens at Pydantic level before API call
        from pydantic import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            CreateTaskParams(title="")

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("title",) for error in errors)

    @pytest.mark.asyncio
    async def test_validation_error_invalid_due_date_format(self, test_user_id):
        """Test that invalid due_date format triggers validation error."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            CreateTaskParams(title="Test Task", due_date="not-a-date")

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("due_date",) for error in errors)

    @pytest.mark.asyncio
    async def test_created_task_returned_with_id_and_timestamps(self, test_user_id):
        """Test that created task includes ID and timestamps."""
        task_data = {"title": "New Task"}

        created_task_response = {
            "id": 5,
            "title": "New Task",
            "description": None,
            "completed": False,
            "priority": "Medium",
            "due_date": None,
            "created_at": "2025-12-18T10:30:00Z",
            "updated_at": "2025-12-18T10:30:00Z",
            "user_id": test_user_id,
        }

        mock_response = AsyncMock(spec=httpx.Response)
        mock_response.status_code = 201
        mock_response.json.return_value = created_task_response

        backend_client = BackendClient()

        with patch.object(
            backend_client.client, "request", return_value=mock_response
        ):
            response = await backend_client.create_task(test_user_id, task_data)

            created_task = response.json()

            # Verify ID and timestamps are present
            assert "id" in created_task
            assert created_task["id"] == 5
            assert "created_at" in created_task
            assert "updated_at" in created_task
            assert created_task["user_id"] == test_user_id

    @pytest.mark.asyncio
    async def test_task_response_schema_validation(self, test_user_id):
        """Test that created task can be validated with TaskResponse schema."""
        task_data = {"title": "Schema Test Task", "priority": "Urgent"}

        created_task_response = {
            "id": 10,
            "title": "Schema Test Task",
            "description": None,
            "completed": False,
            "priority": "Urgent",
            "due_date": None,
            "created_at": "2025-12-18T11:00:00Z",
            "updated_at": "2025-12-18T11:00:00Z",
            "user_id": test_user_id,
        }

        mock_response = AsyncMock(spec=httpx.Response)
        mock_response.status_code = 201
        mock_response.json.return_value = created_task_response

        backend_client = BackendClient()

        with patch.object(
            backend_client.client, "request", return_value=mock_response
        ):
            response = await backend_client.create_task(test_user_id, task_data)

            task_data_returned = response.json()

            # Validate with TaskResponse schema
            task = TaskResponse(**task_data_returned)
            assert isinstance(task, TaskResponse)
            assert task.priority == PriorityLevel.URGENT
            assert task.completed is False
