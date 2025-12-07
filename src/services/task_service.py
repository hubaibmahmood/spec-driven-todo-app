"""Task creation service."""
from typing import Any, Dict

from src.cli.validators import validate_description, validate_title
from src.models.task import Task
from src.storage.memory_store import MemoryStore


def create_task(title: str, description: str | None = None, store: MemoryStore | None = None) -> Task:
    """Create a new task with validation and storage.

    Args:
        title: The title of the task
        description: Optional description of the task
        store: MemoryStore instance to use (creates new one if not provided)

    Returns:
        Task: The created Task instance with assigned ID
    """
    if store is None:
        store = MemoryStore()

    # Validate title and description with user confirmation for truncation if needed
    validated_title = validate_title(title)
    validated_description = validate_description(description)

    # Create task data for storage
    task_data = {
        "title": validated_title,
        "description": validated_description,
        "completed": False
    }

    # Add task to store and get the stored version with ID
    stored_task = store.add_task(task_data)

    # Create and return Task instance
    return Task(
        id=stored_task["id"],
        title=stored_task["title"],
        description=stored_task["description"],
        completed=stored_task["completed"]
    )