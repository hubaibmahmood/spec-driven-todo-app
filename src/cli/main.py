"""Main CLI entry point."""
import sys

from src.cli.commands import (
    add_command,
    delete_tasks_command,
    mark_complete_command,
    update_task_command,
    view_tasks_command,
)
from src.cli.exceptions import ValidationError
from src.cli.validators import validate_description, validate_title
from src.storage.memory_store import MemoryStore


def display_menu() -> None:
    """Display the interactive menu options."""
    print("\n" + "=" * 50)
    print("TODO APP - Main Menu")
    print("=" * 50)
    print("1. Add Task")
    print("2. View Tasks")
    print("3. Mark Task Complete")
    print("4. Delete Task(s)")
    print("5. Update Task Description")
    print("6. Quit")
    print("=" * 50)


def add_task_interactive(store: MemoryStore) -> None:
    """Interactive add task flow.

    Args:
        store: MemoryStore instance
    """
    try:
        title_input = input("Enter task title: ").strip()
        title = validate_title(title_input)

        desc_input = input("Enter task description (optional, press Enter to skip): ").strip()
        description = validate_description(desc_input if desc_input else None)

        # Use the existing add_command which handles the task creation
        add_command(title, description, store)

    except ValidationError as e:
        print(f"✗ Error: {str(e)}")
    except Exception as e:
        print(f"✗ Error: {str(e)}")


def run_interactive_menu(store: MemoryStore) -> None:
    """Run the interactive menu loop.

    Args:
        store: MemoryStore instance
    """
    print("\nWelcome to the Todo App!")

    while True:
        display_menu()

        choice = input("\nSelect option (1-6): ").strip()

        if choice == "1":
            add_task_interactive(store)
        elif choice == "2":
            view_tasks_command(store)
        elif choice == "3":
            mark_complete_command(store)
        elif choice == "4":
            delete_tasks_command(store)
        elif choice == "5":
            update_task_command(store)
        elif choice == "6":
            print("\nGoodbye!")
            break
        else:
            print("✗ Invalid option. Please select 1-6.")


def main() -> int:
    """Main entry point.

    Returns:
        int: Exit code (0 for success)
    """
    try:
        store = MemoryStore()
        run_interactive_menu(store)
        return 0
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
        return 0
    except EOFError:
        print("\n\nGoodbye!")
        return 0


if __name__ == "__main__":
    sys.exit(main())