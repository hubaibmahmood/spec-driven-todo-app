"""Integration tests for GET /tasks endpoint (User Story 1)."""

import pytest
from httpx import AsyncClient
from uuid import uuid4
from src.database.repository import TaskRepository
from src.api.routers.tasks import get_current_user


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_all_tasks_returns_200_with_task_list(
    test_client: AsyncClient,
    db_session,
    sample_user_id
):
    """Test that GET /tasks returns 200 with list of tasks."""
    # Create some tasks for the user
    repo = TaskRepository(db_session)
    await repo.create(sample_user_id, "Task 1", "Description 1")
    await repo.create(sample_user_id, "Task 2", None)

    # Mock authentication dependency
    async def mock_get_current_user():
        return sample_user_id

    from src.api.main import app
    app.dependency_overrides[get_current_user] = mock_get_current_user

    try:
        response = await test_client.get("/tasks/")  # Note: trailing slash

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_all_tasks_empty_returns_200_with_empty_array(
    test_client: AsyncClient,
    sample_user_id
):
    """Test that GET /tasks returns 200 with empty array when no tasks exist."""
    # Mock authentication
    async def mock_get_current_user():
        return sample_user_id

    from src.api.main import app
    app.dependency_overrides[get_current_user] = mock_get_current_user

    try:
        response = await test_client.get("/tasks/")  # Note: trailing slash

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_all_tasks_includes_completed_and_incomplete(
    test_client: AsyncClient,
    db_session,
    sample_user_id
):
    """Test that GET /tasks includes both completed and incomplete tasks."""
    # Create tasks with different completion statuses
    repo = TaskRepository(db_session)
    task1 = await repo.create(sample_user_id, "Incomplete Task", "Not done")
    task2 = await repo.create(sample_user_id, "Complete Task", "Done")
    await repo.update(task2.id, sample_user_id, completed=True)

    # Mock authentication
    async def mock_get_current_user():
        return sample_user_id

    from src.api.main import app
    app.dependency_overrides[get_current_user] = mock_get_current_user

    try:
        response = await test_client.get("/tasks/")  # Note: trailing slash

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

        # Check that we have both completed and incomplete
        completed_statuses = [task["completed"] for task in data]
        assert True in completed_statuses
        assert False in completed_statuses
    finally:
        app.dependency_overrides.clear()
