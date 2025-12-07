"""Pytest fixtures for testing."""
from datetime import datetime
from unittest.mock import Mock

import pytest

from src.storage.memory_store import MemoryStore


@pytest.fixture
def empty_store() -> MemoryStore:
    """Return a fresh, empty MemoryStore instance."""
    return MemoryStore()


@pytest.fixture
def sample_task() -> dict[str, object]:
    """Return sample task data for testing."""
    return {
        "id": 1,
        "title": "Test task",
        "description": "Test description",
        "completed": False,
        "created_at": datetime(2025, 12, 7, 10, 0, 0),
    }


@pytest.fixture
def mock_confirm() -> Mock:
    """Return a mock confirmation function."""
    return Mock(return_value=True)
