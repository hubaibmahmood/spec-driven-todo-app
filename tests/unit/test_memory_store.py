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


def test_memory_store_get_all_returns_empty_list_when_no_tasks() -> None:
    """MemoryStore.get_all returns empty list when store is empty."""
    store = MemoryStore()
    tasks = store.get_all()
    assert tasks == []


def test_memory_store_get_all_returns_all_tasks() -> None:
    """MemoryStore.get_all returns all tasks."""
    store = MemoryStore()

    # Add multiple tasks
    store.add_task({"title": "Task 1", "completed": False})
    store.add_task({"title": "Task 2", "completed": True})
    store.add_task({"title": "Task 3", "completed": False})

    tasks = store.get_all()
    assert len(tasks) == 3
    assert tasks[0]["title"] == "Task 1"
    assert tasks[1]["title"] == "Task 2"
    assert tasks[2]["title"] == "Task 3"


def test_memory_store_update_task_success() -> None:
    """MemoryStore.update_task successfully updates task."""
    store = MemoryStore()
    task = store.add_task({"title": "Original", "description": "Old desc", "completed": False})
    task_id = task["id"]

    # Update the task
    updated = store.update_task(task_id, {"description": "New desc", "completed": True})

    assert updated is not None
    assert updated["description"] == "New desc"
    assert updated["completed"] is True
    assert updated["title"] == "Original"  # Unchanged


def test_memory_store_update_task_nonexistent_id() -> None:
    """MemoryStore.update_task returns None for nonexistent ID."""
    store = MemoryStore()
    result = store.update_task(999, {"completed": True})
    assert result is None


def test_memory_store_delete_task_success() -> None:
    """MemoryStore.delete_task successfully deletes task."""
    store = MemoryStore()
    task = store.add_task({"title": "To delete", "completed": False})
    task_id = task["id"]

    # Delete the task
    result = store.delete_task(task_id)
    assert result is True

    # Verify it's gone
    assert store.get_task(task_id) is None


def test_memory_store_delete_task_nonexistent_id() -> None:
    """MemoryStore.delete_task returns False for nonexistent ID."""
    store = MemoryStore()
    result = store.delete_task(999)
    assert result is False


def test_memory_store_task_exists_returns_true() -> None:
    """MemoryStore.task_exists returns True for existing task."""
    store = MemoryStore()
    task = store.add_task({"title": "Exists", "completed": False})
    task_id = task["id"]

    assert store.task_exists(task_id) is True


def test_memory_store_task_exists_returns_false() -> None:
    """MemoryStore.task_exists returns False for nonexistent task."""
    store = MemoryStore()
    assert store.task_exists(999) is False