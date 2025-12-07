"""CLI command handlers."""
from typing import Optional

from src.services.task_service import create_task
from src.storage.memory_store import MemoryStore


def add_command(title: str, description: Optional[str] = None, store: Optional[MemoryStore] = None) -> int:
    """Handle the 'add' command to create a new task.

    Args:
        title: The title of the task to create
        description: Optional description for the task
        store: MemoryStore instance to use (creates new one if not provided)

    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    try:
        if store is None:
            store = MemoryStore()

        task = create_task(title, description, store)
        print(f"✓ Task created successfully (ID: {task.id})")
        if task.description:
            print(f"Description: {task.description}")
        return 0

    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return 1