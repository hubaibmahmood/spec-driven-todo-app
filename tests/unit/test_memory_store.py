"""Unit tests for MemoryStore."""
import pytest

from src.storage.memory_store import MemoryStore


def test_memory_store_add_task_assigns_sequential_id() -> None:
    """MemoryStore.add_task assigns sequential IDs."""
    store = MemoryStore()

    # Add first task - should get ID 1
    task1 = {"title": "First task", "completed": False}
    added_task1 = store.add_task(task1)
    assert added_task1["id"] == 1

    # Add second task - should get ID 2
    task2 = {"title": "Second task", "completed": False}
    added_task2 = store.add_task(task2)
    assert added_task2["id"] == 2

    # Add third task - should get ID 3
    task3 = {"title": "Third task", "completed": False}
    added_task3 = store.add_task(task3)
    assert added_task3["id"] == 3


def test_memory_store_get_task_retrieves_by_id() -> None:
    """MemoryStore.get_task retrieves task by ID."""
    store = MemoryStore()

    # Add a task
    task_data = {"title": "Test task", "completed": False}
    added_task = store.add_task(task_data)
    task_id = added_task["id"]

    # Retrieve the task by ID
    retrieved_task = store.get_task(task_id)
    assert retrieved_task is not None
    assert retrieved_task["id"] == task_id
    assert retrieved_task["title"] == "Test task"
    assert retrieved_task["completed"] is False


def test_memory_store_get_task_returns_none_for_nonexistent_id() -> None:
    """MemoryStore.get_task returns None for nonexistent ID."""
    store = MemoryStore()

    # Try to get a task with ID that doesn't exist
    nonexistent_task = store.get_task(999)
    assert nonexistent_task is None