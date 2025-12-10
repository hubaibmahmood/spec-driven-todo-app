"""Integration tests for PUT /tasks/{task_id} endpoint (User Story 5)."""

import pytest
from httpx import AsyncClient
from src.api.routers.tasks import get_current_user
from src.database.repository import TaskRepository


@pytest.mark.asyncio
@pytest.mark.integration
async def test_put_task_updates_title_and_description(
    test_client: AsyncClient,
    db_session,
    sample_user_id
):
    """Test that PUT /tasks/{task_id} updates title and description."""
    repo = TaskRepository(db_session)
    task = await repo.create(sample_user_id, "Old Title", "Old Description")

    async def mock_get_current_user():
        return sample_user_id

    from src.api.main import app
    app.dependency_overrides[get_current_user] = mock_get_current_user

    try:
        response = await test_client.put(
            f"/tasks/{task.id}",
            json={"title": "New Title", "description": "New Description"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == task.id
        assert data["title"] == "New Title"
        assert data["description"] == "New Description"
        assert data["completed"] is False
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_put_task_can_clear_description(
    test_client: AsyncClient,
    db_session,
    sample_user_id
):
    """Test that PUT can clear description by setting to null."""
    repo = TaskRepository(db_session)
    task = await repo.create(sample_user_id, "Test", "Some description")

    async def mock_get_current_user():
        return sample_user_id

    from src.api.main import app
    app.dependency_overrides[get_current_user] = mock_get_current_user

    try:
        response = await test_client.put(
            f"/tasks/{task.id}",
            json={"title": "Test", "description": None}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["description"] is None
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_put_nonexistent_task_returns_404(
    test_client: AsyncClient,
    sample_user_id
):
    """Test that PUT on non-existent task returns 404."""
    async def mock_get_current_user():
        return sample_user_id

    from src.api.main import app
    app.dependency_overrides[get_current_user] = mock_get_current_user

    try:
        response = await test_client.put(
            "/tasks/99999",
            json={"title": "New Title"}
        )

        assert response.status_code == 404
    finally:
        app.dependency_overrides.clear()
