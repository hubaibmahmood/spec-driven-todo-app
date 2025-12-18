"""Pytest fixtures for MCP server tests."""

from unittest.mock import AsyncMock, MagicMock
import pytest


@pytest.fixture
def test_user_id() -> str:
    """Return test user ID."""
    return "test_user_123"


@pytest.fixture
def mock_httpx_client():
    """Create mocked httpx.AsyncClient."""
    mock_client = AsyncMock()
    return mock_client


@pytest.fixture
def mock_backend_client():
    """Create mocked BackendClient."""
    mock_client = AsyncMock()
    return mock_client


@pytest.fixture
def test_service_token() -> str:
    """Return test service authentication token."""
    return "test-service-token-for-testing-purposes"
