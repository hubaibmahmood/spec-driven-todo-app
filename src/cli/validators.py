"""Input validation utilities."""
from typing import Callable

from src.cli.exceptions import ValidationError


def confirm_truncation(field_name: str, limit: int) -> bool:
    """Display warning and prompt user for confirmation to truncate field.

    Args:
        field_name: Name of the field being validated (e.g., "title", "description")
        limit: Maximum allowed length for the field

    Returns:
        bool: True if user confirms truncation, False if user declines
    """
    print(f"⚠️  Warning: {field_name.capitalize()} exceeds {limit} character limit.")
    response = input(f"Continue? (y/n): ").strip().lower()
    return response in ('y', 'yes')


def validate_title(title: str, confirm_func: Callable[[str, int], bool] = confirm_truncation) -> str:
    """Validate task title with length check and user confirmation for truncation.

    Args:
        title: The title to validate
        confirm_func: Function to call for confirmation when truncation is needed

    Returns:
        str: Validated title (potentially truncated if user confirms)

    Raises:
        ValidationError: If title is invalid (empty/whitespace) or user declines truncation
    """
    if not title or not title.strip():
        raise ValidationError("Title cannot be empty")

    if len(title) <= 200:
        return title.strip()

    # Title is too long, ask user if they want to truncate
    if confirm_func("title", 200):
        return title[:200]
    else:
        raise ValidationError("Title too long and user declined truncation")


def validate_description(description: str | None, confirm_func: Callable[[str, int], bool] = confirm_truncation) -> str | None:
    """Validate task description with length check and user confirmation for truncation.

    Args:
        description: The description to validate (can be None)
        confirm_func: Function to call for confirmation when truncation is needed

    Returns:
        str | None: Validated description (potentially truncated if user confirms), or None if input is None/empty

    Raises:
        ValidationError: If user declines truncation of long description
    """
    if description is None or not description.strip():
        return None

    if len(description) <= 1000:
        return description

    # Description is too long, ask user if they want to truncate
    if confirm_func("description", 1000):
        return description[:1000]
    else:
        raise ValidationError("Description too long and user declined truncation")


def parse_task_ids(id_string: str) -> list[int]:
    """Parse comma-separated task IDs with whitespace tolerance.

    Args:
        id_string: Comma-separated task IDs (e.g., "1, 2, 3" or "1,2,3")

    Returns:
        list[int]: List of unique task IDs

    Raises:
        ValidationError: If any ID is non-numeric or if input is empty
    """
    if not id_string or not id_string.strip():
        raise ValidationError("Task IDs cannot be empty")

    # Split by comma and strip whitespace from each part
    parts = [p.strip() for p in id_string.split(",") if p.strip()]

    if not parts:
        raise ValidationError("Task IDs cannot be empty")

    try:
        ids = [int(p) for p in parts]
    except ValueError:
        raise ValidationError("Task IDs must be numeric")

    # Remove duplicates while preserving order
    return list(dict.fromkeys(ids))