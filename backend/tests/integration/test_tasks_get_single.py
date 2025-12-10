"""Integration tests for GET /tasks/{task_id} endpoint (User Story 3)."""

import pytest
from httpx import AsyncClient
from src.api.routers.tasks import get_current_user
from src.database.repository import TaskRepository


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_task_by_id_returns_200(
    test_client: AsyncClient,
    db_session,
    sample_user_id
):
    """Test that GET /tasks/{task_id} returns 200 with task details."""
    # Create a task first
    repo = TaskRepository(db_session)
    task = await repo.create(sample_user_id, "Test Task", "Test Description")

    async def mock_get_current_user():
        return sample_user_id

    from src.api.main import app
    app.dependency_overrides[get_current_user] = mock_get_current_user

    try:
        response = await test_client.get(f"/tasks/{task.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == task.id
        assert data["title"] == "Test Task"
        assert data["description"] == "Test Description"
        assert data["completed"] is False
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_nonexistent_task_returns_404(
    test_client: AsyncClient,
    sample_user_id
):
    """Test that GET /tasks/{task_id} for non-existent task returns 404."""
    async def mock_get_current_user():
        return sample_user_id

    from src.api.main import app
    app.dependency_overrides[get_current_user] = mock_get_current_user

    try:
        response = await test_client.get("/tasks/99999")

        assert response.status_code == 404
        data = response.json()
        assert "error" in data or "detail" in data
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_other_users_task_returns_404(
    test_client: AsyncClient,
    db_session,
    sample_user_id
):
    """Test that users cannot access other users' tasks."""
    from uuid import uuid4

    # Create a task for another user
    repo = TaskRepository(db_session)
    other_user_id = uuid4()
    task = await repo.create(other_user_id, "Other User's Task", "Description")

    # Try to access with different user
    async def mock_get_current_user():
        return sample_user_id

    from src.api.main import app
    app.dependency_overrides[get_current_user] = mock_get_current_user

    try:
        response = await test_client.get(f"/tasks/{task.id}")

        assert response.status_code == 404
    finally:
        app.dependency_overrides.clear()
