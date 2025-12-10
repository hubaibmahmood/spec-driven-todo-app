"""Integration tests for DELETE /tasks/{task_id} endpoint (User Story 6)."""

import pytest
from httpx import AsyncClient
from src.api.routers.tasks import get_current_user
from src.database.repository import TaskRepository


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_task_returns_204(
    test_client: AsyncClient,
    db_session,
    sample_user_id
):
    """Test that DELETE /tasks/{task_id} deletes task and returns 204."""
    repo = TaskRepository(db_session)
    task = await repo.create(sample_user_id, "Test Task", "Description")

    async def mock_get_current_user():
        return sample_user_id

    from src.api.main import app
    app.dependency_overrides[get_current_user] = mock_get_current_user

    try:
        response = await test_client.delete(f"/tasks/{task.id}")

        assert response.status_code == 204
        assert response.content == b''  # No content

        # Verify task is actually deleted
        deleted_task = await repo.get_by_id(task.id, sample_user_id)
        assert deleted_task is None
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_nonexistent_task_returns_404(
    test_client: AsyncClient,
    sample_user_id
):
    """Test that DELETE on non-existent task returns 404."""
    async def mock_get_current_user():
        return sample_user_id

    from src.api.main import app
    app.dependency_overrides[get_current_user] = mock_get_current_user

    try:
        response = await test_client.delete("/tasks/99999")

        assert response.status_code == 404
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_other_users_task_returns_404(
    test_client: AsyncClient,
    db_session,
    sample_user_id
):
    """Test that users cannot delete other users' tasks."""
    from uuid import uuid4

    repo = TaskRepository(db_session)
    other_user_id = uuid4()
    task = await repo.create(other_user_id, "Other User's Task", "Description")

    async def mock_get_current_user():
        return sample_user_id

    from src.api.main import app
    app.dependency_overrides[get_current_user] = mock_get_current_user

    try:
        response = await test_client.delete(f"/tasks/{task.id}")

        assert response.status_code == 404

        # Verify task was NOT deleted
        still_exists = await repo.get_by_id(task.id, other_user_id)
        assert still_exists is not None
    finally:
        app.dependency_overrides.clear()
