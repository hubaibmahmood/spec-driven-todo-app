"""Task data model."""
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Task:
    """Represents a task in the todo application."""

    id: int
    title: str
    description: str | None = None
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """Validate task attributes after initialization."""
        if self.id < 1:
            raise ValueError("Task ID must be positive")

        if not self.title or not self.title.strip():
            raise ValueError("Title cannot be empty")

        if len(self.title.strip()) > 200:
            raise ValueError("Title exceeds 200 character limit")

        if self.description and len(self.description) > 1000:
            raise ValueError("Description exceeds 1000 character limit")

        # Clean up the title by stripping whitespace
        self.title = self.title.strip()