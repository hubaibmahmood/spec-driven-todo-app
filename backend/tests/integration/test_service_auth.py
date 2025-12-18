"""Integration tests for service authentication.

These tests verify that the backend correctly handles service authentication
from the MCP server using SERVICE_AUTH_TOKEN and X-User-ID headers.
"""

import pytest
from httpx import AsyncClient

from src.config import settings


@pytest.mark.asyncio
class TestServiceAuthenticationGetTasks:
    """Integration tests for GET /tasks with service authentication."""

    async def test_get_tasks_with_valid_service_token_and_user_id(
        self, test_client: AsyncClient, test_service_auth_headers, sample_user_id
    ):
        """Test GET /tasks with valid service token and X-User-ID returns 200."""
        # First, create a task for the user
        task_data = {
            "title": "Test Task",
            "description": "A test task for service auth testing",
        }

        # Create task using service auth
        create_response = await test_client.post(
            "/tasks/",
            json=task_data,
            headers=test_service_auth_headers,
        )
        assert create_response.status_code == 201

        # Now retrieve tasks using service auth
        response = await test_client.get(
            "/tasks/",
            headers=test_service_auth_headers,
        )

        assert response.status_code == 200
        tasks = response.json()
        assert isinstance(tasks, list)
        assert len(tasks) >= 1

        # Verify the task belongs to the correct user
        task = tasks[0]
        assert task["user_id"] == sample_user_id
        assert task["title"] == "Test Task"

    async def test_get_tasks_with_invalid_service_token(
        self, test_client: AsyncClient, sample_user_id
    ):
        """Test GET /tasks with invalid service token returns 401."""
        headers = {
            "Authorization": "Bearer invalid-token-12345",
            "X-User-ID": sample_user_id,
        }

        response = await test_client.get("/tasks/", headers=headers)

        assert response.status_code == 401
        error_data = response.json()
        assert "detail" in error_data

    async def test_get_tasks_with_missing_user_id_header(
        self, test_client: AsyncClient, mock_service_token
    ):
        """Test GET /tasks with missing X-User-ID header returns 400."""
        headers = {
            "Authorization": f"Bearer {mock_service_token}",
            # X-User-ID is missing
        }

        response = await test_client.get("/tasks/", headers=headers)

        assert response.status_code == 400
        error_data = response.json()
        assert "detail" in error_data

    async def test_user_data_isolation(
        self, test_client: AsyncClient, mock_service_token
    ):
        """Test that service auth correctly isolates user data."""
        # Create tasks for two different users
        user_1_id = "user_1_test"
        user_2_id = "user_2_test"

        # Create task for user 1
        headers_1 = {
            "Authorization": f"Bearer {mock_service_token}",
            "X-User-ID": user_1_id,
        }
        await test_client.post(
            "/tasks/",
            json={"title": "User 1 Task"},
            headers=headers_1,
        )

        # Create task for user 2
        headers_2 = {
            "Authorization": f"Bearer {mock_service_token}",
            "X-User-ID": user_2_id,
        }
        await test_client.post(
            "/tasks/",
            json={"title": "User 2 Task"},
            headers=headers_2,
        )

        # Retrieve tasks for user 1
        response_1 = await test_client.get("/tasks/", headers=headers_1)
        assert response_1.status_code == 200
        tasks_1 = response_1.json()

        # Retrieve tasks for user 2
        response_2 = await test_client.get("/tasks/", headers=headers_2)
        assert response_2.status_code == 200
        tasks_2 = response_2.json()

        # Verify data isolation
        assert all(task["user_id"] == user_1_id for task in tasks_1)
        assert all(task["user_id"] == user_2_id for task in tasks_2)
        assert len(tasks_1) >= 1
        assert len(tasks_2) >= 1

        # Verify no cross-contamination
        user_1_titles = {task["title"] for task in tasks_1}
        user_2_titles = {task["title"] for task in tasks_2}
        assert "User 1 Task" in user_1_titles
        assert "User 1 Task" not in user_2_titles
        assert "User 2 Task" in user_2_titles
        assert "User 2 Task" not in user_1_titles


@pytest.mark.asyncio
class TestServiceAuthenticationPostTasks:
    """Integration tests for POST /tasks with service authentication."""

    async def test_post_tasks_with_service_auth_returns_201(
        self, test_client: AsyncClient, test_service_auth_headers, sample_user_id
    ):
        """Test POST /tasks with service auth creates task and returns 201."""
        task_data = {
            "title": "New Task via Service Auth",
            "description": "Created through MCP server",
            "priority": "High",
        }

        response = await test_client.post(
            "/tasks/",
            json=task_data,
            headers=test_service_auth_headers,
        )

        assert response.status_code == 201
        created_task = response.json()

        assert created_task["title"] == task_data["title"]
        assert created_task["description"] == task_data["description"]
        assert created_task["priority"] == task_data["priority"]
        assert created_task["user_id"] == sample_user_id
        assert "id" in created_task

    async def test_created_task_assigned_to_correct_user(
        self, test_client: AsyncClient, mock_service_token
    ):
        """Test that created task is assigned to user from X-User-ID header."""
        user_id = "specific_user_123"
        headers = {
            "Authorization": f"Bearer {mock_service_token}",
            "X-User-ID": user_id,
        }

        task_data = {"title": "Task for specific user"}

        response = await test_client.post(
            "/tasks/",
            json=task_data,
            headers=headers,
        )

        assert response.status_code == 201
        created_task = response.json()
        assert created_task["user_id"] == user_id

    async def test_created_task_persisted_in_database(
        self, test_client: AsyncClient, test_service_auth_headers, sample_user_id
    ):
        """Test that task created via service auth is persisted in database."""
        task_data = {"title": "Persistent Task"}

        # Create task
        create_response = await test_client.post(
            "/tasks/",
            json=task_data,
            headers=test_service_auth_headers,
        )
        assert create_response.status_code == 201
        created_task = create_response.json()
        task_id = created_task["id"]

        # Retrieve task to verify persistence
        get_response = await test_client.get(
            f"/tasks/{task_id}/",
            headers=test_service_auth_headers,
        )
        assert get_response.status_code == 200
        retrieved_task = get_response.json()

        assert retrieved_task["id"] == task_id
        assert retrieved_task["title"] == task_data["title"]
        assert retrieved_task["user_id"] == sample_user_id
