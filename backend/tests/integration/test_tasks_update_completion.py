"""Integration tests for PATCH /tasks/{task_id} endpoint (User Story 4)."""

import pytest
from httpx import AsyncClient
from src.api.routers.tasks import get_current_user
from src.database.repository import TaskRepository


@pytest.mark.asyncio
@pytest.mark.integration
async def test_patch_task_completion_returns_200(
    test_client: AsyncClient,
    db_session,
    sample_user_id
):
    """Test that PATCH /tasks/{task_id} updates completion status."""
    # Create a task
    repo = TaskRepository(db_session)
    task = await repo.create(sample_user_id, "Test Task", "Description")

    async def mock_get_current_user():
        return sample_user_id

    from src.api.main import app
    app.dependency_overrides[get_current_user] = mock_get_current_user

    try:
        # Mark as completed
        response = await test_client.patch(
            f"/tasks/{task.id}",
            json={"completed": True}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == task.id
        assert data["completed"] is True
        assert data["title"] == "Test Task"

        # Mark as incomplete again
        response = await test_client.patch(
            f"/tasks/{task.id}",
            json={"completed": False}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["completed"] is False
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_patch_nonexistent_task_returns_404(
    test_client: AsyncClient,
    sample_user_id
):
    """Test that PATCH on non-existent task returns 404."""
    async def mock_get_current_user():
        return sample_user_id

    from src.api.main import app
    app.dependency_overrides[get_current_user] = mock_get_current_user

    try:
        response = await test_client.patch(
            "/tasks/99999",
            json={"completed": True}
        )

        assert response.status_code == 404
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_patch_other_users_task_returns_404(
    test_client: AsyncClient,
    db_session,
    sample_user_id
):
    """Test that users cannot update other users' tasks."""
    from uuid import uuid4

    # Create a task for another user
    repo = TaskRepository(db_session)
    other_user_id = uuid4()
    task = await repo.create(other_user_id, "Other User's Task", "Description")

    # Try to update with different user
    async def mock_get_current_user():
        return sample_user_id

    from src.api.main import app
    app.dependency_overrides[get_current_user] = mock_get_current_user

    try:
        response = await test_client.patch(
            f"/tasks/{task.id}",
            json={"completed": True}
        )

        assert response.status_code == 404
    finally:
        app.dependency_overrides.clear()
