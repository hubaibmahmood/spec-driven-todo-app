"""Contract tests for Task model."""
from datetime import datetime

import pytest

from src.models.task import Task


def test_task_creation_with_all_fields() -> None:
    """Task can be created with all fields specified."""
    task = Task(
        id=1,
        title="Buy groceries",
        description="Milk, eggs, bread",
        completed=False,
        created_at=datetime(2025, 12, 7, 10, 0, 0),
    )

    assert task.id == 1
    assert task.title == "Buy groceries"
    assert task.description == "Milk, eggs, bread"
    assert task.completed is False
    assert task.created_at == datetime(2025, 12, 7, 10, 0, 0)


def test_task_creation_minimal_fields() -> None:
    """Task can be created with only required fields."""
    task = Task(id=1, title="Simple task")

    assert task.id == 1
    assert task.title == "Simple task"
    assert task.description is None
    assert task.completed is False
    assert isinstance(task.created_at, datetime)


def test_task_empty_title_raises_error() -> None:
    """Creating task with empty title raises ValueError."""
    with pytest.raises(ValueError, match="Title cannot be empty"):
        Task(id=1, title="")


def test_task_whitespace_title_raises_error() -> None:
    """Creating task with whitespace-only title raises ValueError."""
    with pytest.raises(ValueError, match="Title cannot be empty"):
        Task(id=1, title="   ")


def test_task_title_too_long_raises_error() -> None:
    """Creating task with >200 char title raises ValueError."""
    long_title = "x" * 201
    with pytest.raises(ValueError, match="Title exceeds 200 character limit"):
        Task(id=1, title=long_title)


def test_task_description_too_long_raises_error() -> None:
    """Creating task with >1000 char description raises ValueError."""
    long_desc = "x" * 1001
    with pytest.raises(ValueError, match="Description exceeds 1000 character limit"):
        Task(id=1, title="Valid title", description=long_desc)


def test_task_invalid_id_raises_error() -> None:
    """Creating task with invalid ID raises ValueError."""
    with pytest.raises(ValueError, match="Task ID must be positive"):
        Task(id=0, title="Valid title")
