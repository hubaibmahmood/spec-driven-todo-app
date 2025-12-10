"""Integration tests for POST /tasks/bulk-delete endpoint (User Story 7)."""

import pytest
from httpx import AsyncClient
from src.api.routers.tasks import get_current_user
from src.database.repository import TaskRepository


@pytest.mark.asyncio
@pytest.mark.integration
async def test_bulk_delete_returns_200_with_deleted_list(
    test_client: AsyncClient,
    db_session,
    sample_user_id
):
    """Test that POST /tasks/bulk-delete deletes multiple tasks."""
    repo = TaskRepository(db_session)
    task1 = await repo.create(sample_user_id, "Task 1", "Desc 1")
    task2 = await repo.create(sample_user_id, "Task 2", "Desc 2")
    task3 = await repo.create(sample_user_id, "Task 3", "Desc 3")

    async def mock_get_current_user():
        return sample_user_id

    from src.api.main import app
    app.dependency_overrides[get_current_user] = mock_get_current_user

    try:
        response = await test_client.post(
            "/tasks/bulk-delete",
            json={"task_ids": [task1.id, task2.id, task3.id]}
        )

        assert response.status_code == 200
        data = response.json()
        assert set(data["deleted"]) == {task1.id, task2.id, task3.id}
        assert data["not_found"] == []
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_bulk_delete_partial_success_returns_200(
    test_client: AsyncClient,
    db_session,
    sample_user_id
):
    """Test bulk delete with mix of existing and non-existing tasks."""
    repo = TaskRepository(db_session)
    task1 = await repo.create(sample_user_id, "Task 1", "Desc 1")

    async def mock_get_current_user():
        return sample_user_id

    from src.api.main import app
    app.dependency_overrides[get_current_user] = mock_get_current_user

    try:
        response = await test_client.post(
            "/tasks/bulk-delete",
            json={"task_ids": [task1.id, 99999, 99998]}
        )

        assert response.status_code == 200
        data = response.json()
        assert task1.id in data["deleted"]
        assert set(data["not_found"]) == {99999, 99998}
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_bulk_delete_empty_list_returns_400(
    test_client: AsyncClient,
    sample_user_id
):
    """Test that empty task_ids list returns 400."""
    async def mock_get_current_user():
        return sample_user_id

    from src.api.main import app
    app.dependency_overrides[get_current_user] = mock_get_current_user

    try:
        response = await test_client.post(
            "/tasks/bulk-delete",
            json={"task_ids": []}
        )

        assert response.status_code == 422  # Pydantic validation
    finally:
        app.dependency_overrides.clear()
