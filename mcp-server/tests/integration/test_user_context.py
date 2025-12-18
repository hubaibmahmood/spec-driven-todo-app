"""Integration tests for user context propagation and data isolation (SC-001)."""

import pytest
from unittest.mock import AsyncMock, patch

from src.tools.list_tasks import list_tasks
from src.tools.create_task import create_task
from src.tools.mark_completed import mark_task_completed
from src.tools.update_task import update_task
from src.tools.delete_task import delete_task


@pytest.mark.asyncio
async def test_list_tasks_data_isolation():
    """Test that list_tasks only returns tasks for the authenticated user."""
    # User A tasks
    user_a_tasks = [
        {
            "id": 1,
            "title": "User A Task 1",
            "description": None,
            "completed": False,
            "priority": "Medium",
            "due_date": None,
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-01-01T00:00:00Z",
            "user_id": "user_a_123",
        },
        {
            "id": 2,
            "title": "User A Task 2",
            "description": None,
            "completed": False,
            "priority": "High",
            "due_date": None,
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-01-01T00:00:00Z",
            "user_id": "user_a_123",
        },
    ]

    # User B tasks
    user_b_tasks = [
        {
            "id": 3,
            "title": "User B Task 1",
            "description": None,
            "completed": False,
            "priority": "Low",
            "due_date": None,
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-01-01T00:00:00Z",
            "user_id": "user_b_456",
        },
    ]

    with patch("src.tools.list_tasks.BackendClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client

        # Test User A
        mock_client.get_tasks.return_value = user_a_tasks
        result_a = await list_tasks(_user_id="user_a_123")

        # Verify User A gets only their tasks
        assert len(result_a) == 2
        assert all(task["user_id"] == "user_a_123" for task in result_a)
        assert result_a[0]["title"] == "User A Task 1"
        assert result_a[1]["title"] == "User A Task 2"
        mock_client.get_tasks.assert_called_with("user_a_123")

        # Test User B
        mock_client.get_tasks.return_value = user_b_tasks
        result_b = await list_tasks(_user_id="user_b_456")

        # Verify User B gets only their tasks
        assert len(result_b) == 1
        assert all(task["user_id"] == "user_b_456" for task in result_b)
        assert result_b[0]["title"] == "User B Task 1"
        mock_client.get_tasks.assert_called_with("user_b_456")


@pytest.mark.asyncio
async def test_create_task_assigns_correct_user_id():
    """Test that create_task assigns tasks to the correct user."""
    created_task_a = {
        "id": 1,
        "title": "User A New Task",
        "description": None,
        "completed": False,
        "priority": "Medium",
        "due_date": None,
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-01-01T00:00:00Z",
        "user_id": "user_a_123",
    }

    created_task_b = {
        "id": 2,
        "title": "User B New Task",
        "description": None,
        "completed": False,
        "priority": "High",
        "due_date": None,
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-01-01T00:00:00Z",
        "user_id": "user_b_456",
    }

    with patch("src.tools.create_task.BackendClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client

        # Test User A creates task
        mock_client.create_task.return_value = created_task_a
        result_a = await create_task(
            title="User A New Task", _user_id="user_a_123"
        )

        assert result_a["user_id"] == "user_a_123"
        assert result_a["title"] == "User A New Task"
        mock_client.create_task.assert_called_with(
            user_id="user_a_123",
            title="User A New Task",
            description=None,
            priority="Medium",
            due_date=None,
        )

        # Test User B creates task
        mock_client.create_task.return_value = created_task_b
        result_b = await create_task(
            title="User B New Task", priority="High", _user_id="user_b_456"
        )

        assert result_b["user_id"] == "user_b_456"
        assert result_b["title"] == "User B New Task"
        mock_client.create_task.assert_called_with(
            user_id="user_b_456",
            title="User B New Task",
            description=None,
            priority="High",
            due_date=None,
        )


@pytest.mark.asyncio
async def test_mark_completed_authorization():
    """Test that users can only mark their own tasks as completed."""
    user_a_task = {
        "id": 1,
        "title": "User A Task",
        "description": None,
        "completed": True,
        "priority": "Medium",
        "due_date": None,
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-01-01T00:00:00Z",
        "user_id": "user_a_123",
    }

    with patch(
        "src.tools.mark_completed.BackendClient"
    ) as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client

        # User A marks their own task - SUCCESS
        mock_client.mark_task_completed.return_value = user_a_task
        result = await mark_task_completed(task_id=1, _user_id="user_a_123")

        assert result["completed"] is True
        assert result["user_id"] == "user_a_123"
        mock_client.mark_task_completed.assert_called_with(
            user_id="user_a_123", task_id=1
        )

        # User B tries to mark User A's task - Should get 403
        from httpx import HTTPStatusError, Request, Response

        mock_response = Response(
            status_code=403,
            json={"detail": "Not authorized to modify this task"},
        )
        mock_request = Request("PATCH", "http://test.com/tasks/1")
        mock_client.mark_task_completed.side_effect = HTTPStatusError(
            "403 Forbidden", request=mock_request, response=mock_response
        )

        result = await mark_task_completed(task_id=1, _user_id="user_b_456")

        # Verify error response
        assert "error_type" in result
        assert result["error_type"] == "authorization_error"
        assert "not authorized" in result["message"].lower()


@pytest.mark.asyncio
async def test_update_task_authorization():
    """Test that users can only update their own tasks."""
    user_a_task = {
        "id": 1,
        "title": "Updated Task",
        "description": "New description",
        "completed": False,
        "priority": "High",
        "due_date": None,
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-01-01T01:00:00Z",
        "user_id": "user_a_123",
    }

    with patch("src.tools.update_task.BackendClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client

        # User A updates their own task - SUCCESS
        mock_client.update_task.return_value = user_a_task
        result = await update_task(
            task_id=1,
            title="Updated Task",
            description="New description",
            priority="High",
            _user_id="user_a_123",
        )

        assert result["title"] == "Updated Task"
        assert result["user_id"] == "user_a_123"

        # User B tries to update User A's task - Should get 403
        from httpx import HTTPStatusError, Request, Response

        mock_response = Response(
            status_code=403,
            json={"detail": "Not authorized to modify this task"},
        )
        mock_request = Request("PUT", "http://test.com/tasks/1")
        mock_client.update_task.side_effect = HTTPStatusError(
            "403 Forbidden", request=mock_request, response=mock_response
        )

        result = await update_task(
            task_id=1, title="Hacked", _user_id="user_b_456"
        )

        # Verify error response
        assert "error_type" in result
        assert result["error_type"] == "authorization_error"


@pytest.mark.asyncio
async def test_delete_task_authorization():
    """Test that users can only delete their own tasks."""
    with patch("src.tools.delete_task.BackendClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client

        # User A deletes their own task - SUCCESS
        mock_client.delete_task.return_value = None
        result = await delete_task(task_id=1, _user_id="user_a_123")

        assert "successfully deleted" in result["message"].lower()

        # User B tries to delete User A's task - Should get 403
        from httpx import HTTPStatusError, Request, Response

        mock_response = Response(
            status_code=403,
            json={"detail": "Not authorized to delete this task"},
        )
        mock_request = Request("DELETE", "http://test.com/tasks/1")
        mock_client.delete_task.side_effect = HTTPStatusError(
            "403 Forbidden", request=mock_request, response=mock_response
        )

        result = await delete_task(task_id=1, _user_id="user_b_456")

        # Verify error response
        assert "error_type" in result
        assert result["error_type"] == "authorization_error"


@pytest.mark.asyncio
async def test_cross_user_data_isolation_complete_workflow():
    """
    End-to-end test: Two users creating, listing, and managing tasks independently.
    Verifies SC-001: User context propagation and data isolation.
    """
    with (
        patch("src.tools.create_task.BackendClient") as mock_create_client,
        patch("src.tools.list_tasks.BackendClient") as mock_list_client,
    ):
        mock_create = AsyncMock()
        mock_list = AsyncMock()
        mock_create_client.return_value = mock_create
        mock_list_client.return_value = mock_list

        # User A creates 2 tasks
        mock_create.create_task.side_effect = [
            {
                "id": 1,
                "title": "User A Task 1",
                "description": None,
                "completed": False,
                "priority": "Medium",
                "due_date": None,
                "created_at": "2025-01-01T00:00:00Z",
                "updated_at": "2025-01-01T00:00:00Z",
                "user_id": "user_a_123",
            },
            {
                "id": 2,
                "title": "User A Task 2",
                "description": None,
                "completed": False,
                "priority": "High",
                "due_date": None,
                "created_at": "2025-01-01T00:00:00Z",
                "updated_at": "2025-01-01T00:00:00Z",
                "user_id": "user_a_123",
            },
        ]

        await create_task(title="User A Task 1", _user_id="user_a_123")
        await create_task(title="User A Task 2", priority="High", _user_id="user_a_123")

        # User B creates 1 task
        mock_create.create_task.return_value = {
            "id": 3,
            "title": "User B Task 1",
            "description": None,
            "completed": False,
            "priority": "Low",
            "due_date": None,
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-01-01T00:00:00Z",
            "user_id": "user_b_456",
        }

        await create_task(title="User B Task 1", priority="Low", _user_id="user_b_456")

        # User A lists tasks - should only see their 2 tasks
        mock_list.get_tasks.return_value = [
            {
                "id": 1,
                "title": "User A Task 1",
                "description": None,
                "completed": False,
                "priority": "Medium",
                "due_date": None,
                "created_at": "2025-01-01T00:00:00Z",
                "updated_at": "2025-01-01T00:00:00Z",
                "user_id": "user_a_123",
            },
            {
                "id": 2,
                "title": "User A Task 2",
                "description": None,
                "completed": False,
                "priority": "High",
                "due_date": None,
                "created_at": "2025-01-01T00:00:00Z",
                "updated_at": "2025-01-01T00:00:00Z",
                "user_id": "user_a_123",
            },
        ]

        user_a_tasks = await list_tasks(_user_id="user_a_123")
        assert len(user_a_tasks) == 2
        assert all(task["user_id"] == "user_a_123" for task in user_a_tasks)
        assert user_a_tasks[0]["title"] == "User A Task 1"
        assert user_a_tasks[1]["title"] == "User A Task 2"

        # User B lists tasks - should only see their 1 task
        mock_list.get_tasks.return_value = [
            {
                "id": 3,
                "title": "User B Task 1",
                "description": None,
                "completed": False,
                "priority": "Low",
                "due_date": None,
                "created_at": "2025-01-01T00:00:00Z",
                "updated_at": "2025-01-01T00:00:00Z",
                "user_id": "user_b_456",
            }
        ]

        user_b_tasks = await list_tasks(_user_id="user_b_456")
        assert len(user_b_tasks) == 1
        assert all(task["user_id"] == "user_b_456" for task in user_b_tasks)
        assert user_b_tasks[0]["title"] == "User B Task 1"

        # Verify complete data isolation
        user_a_task_ids = {task["id"] for task in user_a_tasks}
        user_b_task_ids = {task["id"] for task in user_b_tasks}
        assert user_a_task_ids.isdisjoint(user_b_task_ids)

        print("✅ SC-001 Data Isolation Test PASSED")
        print(f"  - User A has {len(user_a_tasks)} tasks (IDs: {user_a_task_ids})")
        print(f"  - User B has {len(user_b_tasks)} tasks (IDs: {user_b_task_ids})")
        print("  - No overlap between user task sets")
