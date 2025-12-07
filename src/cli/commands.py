"""CLI command handlers."""
from typing import Optional

from src.cli.exceptions import ValidationError
from src.cli.validators import parse_task_ids, validate_description
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


def view_tasks_command(store: MemoryStore) -> None:
    """Display all tasks with ID, status, title, and truncated description.

    Args:
        store: MemoryStore instance
    """
    tasks = store.get_all()

    if not tasks:
        print("\nNo tasks found.")
        return

    print("\nTasks:")
    print("-" * 80)
    for task in tasks:
        status = "[✓]" if task.get("completed", False) else "[ ]"
        title = task.get("title", "")
        description = task.get("description", "")

        # Truncate description at 50 chars
        if description and len(description) > 50:
            desc_display = description[:50] + "..."
        else:
            desc_display = description if description else ""

        print(f"{task['id']:>3} {status} {title:<30} {desc_display}")
    print("-" * 80)


def mark_complete_command(store: MemoryStore) -> None:
    """Mark a task as complete by ID.

    Args:
        store: MemoryStore instance
    """
    try:
        task_id_str = input("Enter task ID to mark complete: ").strip()
        task_id = int(task_id_str)
    except ValueError:
        print("✗ Error: Task ID must be a number")
        return

    task = store.get_task(task_id)
    if not task:
        print(f"✗ Error: Task {task_id} not found")
        return

    if task.get("completed", False):
        print(f"Task {task_id} is already complete")
        return

    store.update_task(task_id, {"completed": True})
    print(f"✓ Task {task_id} marked complete")


def delete_tasks_command(store: MemoryStore) -> None:
    """Delete one or more tasks by ID.

    Args:
        store: MemoryStore instance
    """
    try:
        id_string = input("Enter task ID(s) to delete (comma-separated): ").strip()
        task_ids = parse_task_ids(id_string)
    except ValidationError as e:
        print(f"✗ Error: {str(e)}")
        return

    deleted = []
    not_found = []

    for task_id in task_ids:
        if store.delete_task(task_id):
            deleted.append(task_id)
        else:
            not_found.append(task_id)

    # Report results
    if deleted:
        print(f"✓ Deleted task(s): {', '.join(map(str, deleted))}")
    if not_found:
        print(f"✗ Task(s) not found: {', '.join(map(str, not_found))}")


def update_task_command(store: MemoryStore) -> None:
    """Update a task's description by ID.

    Args:
        store: MemoryStore instance
    """
    try:
        task_id_str = input("Enter task ID to update: ").strip()
        task_id = int(task_id_str)
    except ValueError:
        print("✗ Error: Task ID must be a number")
        return

    task = store.get_task(task_id)
    if not task:
        print(f"✗ Error: Task {task_id} not found")
        return

    # Show current description
    current_desc = task.get("description", "")
    print(f"\nCurrent description: {current_desc if current_desc else '(empty)'}")

    # Get new description
    new_desc_input = input("Enter new description (or press Enter to clear): ").strip()

    try:
        validated_desc = validate_description(new_desc_input if new_desc_input else None)
        store.update_task(task_id, {"description": validated_desc})
        print(f"✓ Task {task_id} description updated")
    except ValidationError as e:
        print(f"✗ Error: {str(e)}")