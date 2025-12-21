"""Unit tests for task context metadata storage and resolution."""

import pytest
from datetime import datetime, timedelta
from ai_agent.agent.context_manager import ContextManager


def test_store_task_list_context():
    """Unit: Should store task list metadata for ordinal reference resolution."""
    manager = ContextManager()

    task_list = [
        {"id": 1, "title": "First task"},
        {"id": 2, "title": "Second task"},
        {"id": 3, "title": "Third task"},
    ]

    # Store task list context
    context_metadata = manager.store_task_list_context(task_list)

    # Assert: Metadata contains position-to-ID mapping
    assert "task_context" in context_metadata
    assert "positions" in context_metadata["task_context"]
    assert "timestamp" in context_metadata["task_context"]
    assert context_metadata["task_context"]["positions"] == {
        "1": 1,  # First position -> task ID 1
        "2": 2,  # Second position -> task ID 2
        "3": 3,  # Third position -> task ID 3
    }


def test_get_task_list_context_valid():
    """Unit: Should retrieve valid task context within expiration window."""
    manager = ContextManager()

    # Create recent context (within 5 minutes)
    metadata = {
        "task_context": {
            "positions": {"1": 1, "2": 2, "3": 3},
            "timestamp": datetime.now().isoformat(),
        }
    }

    context = manager.get_task_list_context(metadata)

    assert context is not None
    assert context["positions"] == {"1": 1, "2": 2, "3": 3}


def test_get_task_list_context_expired():
    """Unit: Should return None for expired task context (>5 minutes old)."""
    manager = ContextManager()

    # Create expired context (6 minutes ago)
    expired_time = datetime.now() - timedelta(minutes=6)
    metadata = {
        "task_context": {
            "positions": {"1": 1, "2": 2, "3": 3},
            "timestamp": expired_time.isoformat(),
        }
    }

    context = manager.get_task_list_context(metadata)

    assert context is None


def test_get_task_list_context_missing():
    """Unit: Should return None when no task context exists."""
    manager = ContextManager()

    # No task context in metadata
    metadata = {"some_other_key": "value"}

    context = manager.get_task_list_context(metadata)

    assert context is None


def test_resolve_ordinal_reference_first():
    """Unit: Should resolve 'first' to task ID at position 1."""
    manager = ContextManager()

    context = {
        "positions": {"1": 10, "2": 20, "3": 30},
        "timestamp": datetime.now().isoformat(),
    }

    task_id = manager.resolve_ordinal_reference("first", context)

    assert task_id == 10


def test_resolve_ordinal_reference_second():
    """Unit: Should resolve 'second' to task ID at position 2."""
    manager = ContextManager()

    context = {
        "positions": {"1": 10, "2": 20, "3": 30},
        "timestamp": datetime.now().isoformat(),
    }

    task_id = manager.resolve_ordinal_reference("second", context)

    assert task_id == 20


def test_resolve_ordinal_reference_last():
    """Unit: Should resolve 'last' to task ID at highest position."""
    manager = ContextManager()

    context = {
        "positions": {"1": 10, "2": 20, "3": 30},
        "timestamp": datetime.now().isoformat(),
    }

    task_id = manager.resolve_ordinal_reference("last", context)

    assert task_id == 30


def test_resolve_ordinal_reference_third():
    """Unit: Should resolve 'third' to task ID at position 3."""
    manager = ContextManager()

    context = {
        "positions": {"1": 10, "2": 20, "3": 30},
        "timestamp": datetime.now().isoformat(),
    }

    task_id = manager.resolve_ordinal_reference("third", context)

    assert task_id == 30


def test_resolve_ordinal_reference_invalid():
    """Unit: Should return None for invalid ordinal reference."""
    manager = ContextManager()

    context = {
        "positions": {"1": 10, "2": 20, "3": 30},
        "timestamp": datetime.now().isoformat(),
    }

    # Reference out of bounds
    task_id = manager.resolve_ordinal_reference("tenth", context)

    assert task_id is None


def test_resolve_ordinal_reference_numeric():
    """Unit: Should resolve numeric position to task ID."""
    manager = ContextManager()

    context = {
        "positions": {"1": 10, "2": 20, "3": 30},
        "timestamp": datetime.now().isoformat(),
    }

    task_id = manager.resolve_ordinal_reference("2", context)

    assert task_id == 20
