"""Main CLI entry point."""
import sys
from typing import Optional

from src.cli.commands import add_command
from src.storage.memory_store import MemoryStore


def main() -> int:
    """Main interactive CLI entry point."""
    store = MemoryStore()  # Single store instance for the session

    print("Welcome to the Todo App!")
    print("Available commands:")
    print("1. add <title> [description] - Add a new task")
    print("2. view - View all tasks")
    print("3. complete <id> - Mark task as complete")
    print("4. delete <id> - Delete a task")
    print("5. quit - Exit the application")
    print()

    while True:
        try:
            command_input = input("Enter command: ").strip()
            if not command_input:
                continue

            # Initialize variables to avoid UnboundLocalError
            command = ""
            title = None
            description = None

            # Parse command: first word is command, rest is arguments
            # For add command, we want to support "add <title>" or "add <title> -d <description>"
            if command_input.startswith("add "):
                # Extract everything after "add "
                command = "add"
                args_str = command_input[4:].strip()  # Remove "add " prefix

                # Support "add title -d description" format
                if " -d " in args_str:
                    parts = args_str.split(" -d ", 1)  # Split only on first occurrence
                    title = parts[0].strip()
                    description = parts[1].strip() if len(parts) > 1 else None
                else:
                    # If no -d flag, treat entire remainder as title
                    title = args_str
                    description = None
            else:
                # For other commands, split by whitespace
                parts = command_input.split()
                if not parts:
                    continue
                command = parts[0].lower()
                # Other commands will be handled below if we add them

            if command == "quit":
                print("Goodbye!")
                return 0
            elif command == "add":
                if not title:
                    print("✗ Error: Please provide a title for the task")
                    continue

                # For interactive mode, we'll call add_command with store parameter
                result = add_command(title, description, store)
                if result != 0:
                    return result  # Exit if there was an error
            else:
                print(f"✗ Error: Unknown command '{command}'. Use 'quit' to exit.")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            return 0
        except EOFError:
            print("\nGoodbye!")
            return 0


if __name__ == "__main__":
    sys.exit(main())