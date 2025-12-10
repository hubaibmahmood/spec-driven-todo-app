"""Integration tests for POST /tasks endpoint (User Story 2)."""

import pytest
from httpx import AsyncClient
from src.api.routers.tasks import get_current_user


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_task_with_valid_data_returns_201(
    test_client: AsyncClient,
    sample_user_id,
    sample_task_data
):
    """Test that POST /tasks with valid data returns 201."""
    async def mock_get_current_user():
        return sample_user_id

    from src.api.main import app
    app.dependency_overrides[get_current_user] = mock_get_current_user

    try:
        response = await test_client.post("/tasks/", json=sample_task_data)

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == sample_task_data["title"]
        assert data["description"] == sample_task_data["description"]
        assert data["completed"] is False
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_task_title_only_returns_201(
    test_client: AsyncClient,
    sample_user_id
):
    """Test that POST /tasks with title only (no description) returns 201."""
    task_data = {"title": "Task without description"}

    async def mock_get_current_user():
        return sample_user_id

    from src.api.main import app
    app.dependency_overrides[get_current_user] = mock_get_current_user

    try:
        response = await test_client.post("/tasks/", json=task_data)

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == task_data["title"]
        assert data["description"] is None
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_task_empty_title_returns_422(
    test_client: AsyncClient,
    sample_user_id
):
    """Test that POST /tasks with empty title returns 422."""
    task_data = {"title": "", "description": "Valid description"}

    async def mock_get_current_user():
        return sample_user_id

    from src.api.main import app
    app.dependency_overrides[get_current_user] = mock_get_current_user

    try:
        response = await test_client.post("/tasks/", json=task_data)

        assert response.status_code == 422
        data = response.json()
        assert "errors" in data or "detail" in data
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_task_title_too_long_returns_422(
    test_client: AsyncClient,
    sample_user_id
):
    """Test that POST /tasks with title > 200 chars returns 422."""
    task_data = {
        "title": "x" * 201,  # 201 characters
        "description": "Valid description"
    }

    async def mock_get_current_user():
        return sample_user_id

    from src.api.main import app
    app.dependency_overrides[get_current_user] = mock_get_current_user

    try:
        response = await test_client.post("/tasks/", json=task_data)

        assert response.status_code == 422
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_task_description_too_long_returns_422(
    test_client: AsyncClient,
    sample_user_id
):
    """Test that POST /tasks with description > 1000 chars returns 422."""
    task_data = {
        "title": "Valid title",
        "description": "x" * 1001  # 1001 characters
    }

    async def mock_get_current_user():
        return sample_user_id

    from src.api.main import app
    app.dependency_overrides[get_current_user] = mock_get_current_user

    try:
        response = await test_client.post("/tasks/", json=task_data)

        assert response.status_code == 422
    finally:
        app.dependency_overrides.clear()
