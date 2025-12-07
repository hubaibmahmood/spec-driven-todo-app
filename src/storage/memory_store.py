"""In-memory task storage."""
from typing import Any, Dict


class MemoryStore:
    """In-memory storage for tasks."""

    def __init__(self) -> None:
        """Initialize empty storage."""
        self._tasks: Dict[int, Any] = {}
        self._next_id: int = 1

    def add_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a task to storage with the next available ID.

        Args:
            task_data: Dictionary containing task information (without ID)

        Returns:
            Dict[str, Any]: The task with assigned ID
        """
        task_with_id = task_data.copy()
        task_with_id["id"] = self._next_id
        self._tasks[self._next_id] = task_with_id
        assigned_id = self._next_id
        self._next_id += 1
        return self._tasks[assigned_id]

    def get_task(self, task_id: int) -> Dict[str, Any] | None:
        """Retrieve a task by ID.

        Args:
            task_id: The ID of the task to retrieve

        Returns:
            Dict[str, Any] | None: The task if found, None otherwise
        """
        return self._tasks.get(task_id)

    def get_all(self) -> list[Dict[str, Any]]:
        """Return all tasks as a list ordered by ID.

        Returns:
            list[Dict[str, Any]]: List of all tasks
        """
        return list(self._tasks.values())

    def update_task(self, task_id: int, updates: Dict[str, Any]) -> Dict[str, Any] | None:
        """Update task fields.

        Args:
            task_id: ID of task to update
            updates: Dictionary of fields to update

        Returns:
            Dict[str, Any] | None: Updated task if found, None otherwise
        """
        if task_id not in self._tasks:
            return None
        self._tasks[task_id].update(updates)
        return self._tasks[task_id]

    def delete_task(self, task_id: int) -> bool:
        """Delete task by ID.

        Args:
            task_id: ID of task to delete

        Returns:
            bool: True if deleted, False if not found
        """
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False

    def task_exists(self, task_id: int) -> bool:
        """Check if task exists.

        Args:
            task_id: ID to check

        Returns:
            bool: True if task exists, False otherwise
        """
        return task_id in self._tasks
