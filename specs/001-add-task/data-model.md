# Data Model: Add Task Feature

**Feature**: 001-add-task
**Date**: 2025-12-07
**Purpose**: Define data structures, relationships, and validation rules for task entities

## Entities

### Task

Represents a single todo item with title, optional description, completion status, and metadata.

**Attributes**:

| Attribute | Type | Required | Default | Constraints | Description |
|-----------|------|----------|---------|-------------|-------------|
| `id` | `int` | Yes | Auto-assigned | Positive integer, unique, sequential | Unique identifier for the task |
| `title` | `str` | Yes | None | 1-200 characters, non-empty after strip | Brief description of the task |
| `description` | `Optional[str]` | No | `None` | 0-1000 characters if provided | Detailed context about the task |
| `completed` | `bool` | Yes | `False` | Boolean | Whether the task is marked complete |
| `created_at` | `datetime` | Yes | Auto-generated | Valid datetime | Timestamp when task was created |

**Uniqueness Rules**:
- `id` field is the primary unique identifier
- IDs are sequential integers starting from 1
- IDs never reused, even after task deletion

**Immutability Rules**:
- `id` is immutable after creation (never changes)
- `created_at` is immutable after creation
- `title`, `description`, `completed` are mutable

**State Transitions**:
```
[New Task]
    ↓
[Created: completed=False]
    ↓
[Marked Complete: completed=True]
    ↓
[Marked Incomplete: completed=False]  (can toggle)
```

**Lifecycle**:
1. **Creation**: Task created with auto-assigned ID, provided title/description, `completed=False`, `created_at=now()`
2. **Updates**: Title, description, or completion status can be modified
3. **Deletion**: Task removed from storage (ID not reused)

---

## Validation Rules

### Title Validation

**Rules**:
1. **Non-empty**: Title must contain at least one non-whitespace character
2. **Length limit**: Maximum 200 characters
3. **Whitespace handling**: Leading/trailing whitespace preserved (user may want it)
4. **Character preservation**: All special characters, Unicode, newlines preserved

**Validation Flow**:
```python
def validate_title(title: str) -> str:
    # Check for empty or whitespace-only
    if not title or not title.strip():
        raise ValidationError("Title cannot be empty")

    # Check length and prompt for confirmation if needed
    if len(title) > 200:
        if not confirm_truncation("Title", 200):
            raise ValidationError("Task creation cancelled by user")
        return title[:200]

    return title
```

**Error Messages**:
- Empty title: `"Title cannot be empty"`
- Exceeds 200 chars: `"⚠️  Warning: Title exceeds 200 character limit. It will be truncated. Continue? (y/n):"`
- User cancels: `"Task creation cancelled"`

---

### Description Validation

**Rules**:
1. **Optional**: Description can be `None` or empty string
2. **Length limit**: Maximum 1000 characters if provided
3. **Character preservation**: All special characters, Unicode, newlines preserved

**Validation Flow**:
```python
def validate_description(description: Optional[str]) -> Optional[str]:
    # None or empty string is valid
    if not description:
        return None

    # Check length and prompt for confirmation if needed
    if len(description) > 1000:
        if not confirm_truncation("Description", 1000):
            raise ValidationError("Task creation cancelled by user")
        return description[:1000]

    return description
```

**Error Messages**:
- Exceeds 1000 chars: `"⚠️  Warning: Description exceeds 1000 character limit. It will be truncated. Continue? (y/n):"`
- User cancels: `"Task creation cancelled"`

---

## Relationships

### Current Scope (Add Task Feature)

No relationships in current scope - Task entity is standalone.

### Future Scope

Potential relationships for future features:
- **Tags**: Many-to-many relationship (Task ↔ Tag)
- **Categories**: Many-to-one relationship (Task → Category)
- **Subtasks**: One-to-many relationship (Task → Subtask)
- **User**: Many-to-one relationship (Task → User) for multi-user support

*Note: These are not implemented in the add task feature.*

---

## Data Volume & Scale Assumptions

**Expected Volume**:
- Typical usage: 10-100 tasks
- Maximum tested: 1000 tasks
- Performance target: <1 second response time for all operations

**Memory Estimates**:
- Single Task object: ~500 bytes (including Python overhead)
- 1000 tasks: ~500 KB
- Well within memory constraints for CLI application

**Storage Strategy**:
- In-memory dictionary: `dict[int, Task]`
- O(1) lookup by ID
- O(1) insertion
- O(n) iteration (for list operations)

---

## Data Integrity Constraints

### At Model Level (Dataclass)

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class Task:
    """Represents a single todo item."""

    id: int
    title: str
    description: Optional[str] = None
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validate task data after initialization."""
        # ID must be positive
        if self.id < 1:
            raise ValueError("Task ID must be positive")

        # Title cannot be empty
        if not self.title or not self.title.strip():
            raise ValueError("Title cannot be empty")

        # Title length constraint
        if len(self.title) > 200:
            raise ValueError("Title exceeds 200 character limit")

        # Description length constraint (if provided)
        if self.description is not None and len(self.description) > 1000:
            raise ValueError("Description exceeds 1000 character limit")
```

### At Service Level

- Validation before Task creation
- User confirmation for truncation
- Business logic enforcement (unique IDs, sequential generation)

### At Storage Level

- Atomic ID generation (thread-safe counter)
- Prevent ID conflicts
- Maintain referential integrity

---

## Sample Data

### Minimal Task (Title Only)

```python
Task(
    id=1,
    title="Buy groceries",
    description=None,
    completed=False,
    created_at=datetime(2025, 12, 7, 10, 30, 0)
)
```

### Full Task (With Description)

```python
Task(
    id=2,
    title="Prepare quarterly report",
    description="Include sales data, expense analysis, and forecasts for Q1 2026",
    completed=False,
    created_at=datetime(2025, 12, 7, 11, 15, 0)
)
```

### Completed Task

```python
Task(
    id=3,
    title="Review pull request #42",
    description="Check code quality, test coverage, and documentation",
    completed=True,
    created_at=datetime(2025, 12, 6, 14, 45, 0)
)
```

---

## Design Decisions

### Why Sequential Integer IDs?

**Decision**: Use auto-incrementing integers starting from 1

**Rationale**:
- Simplest approach for single-user CLI application
- Easy for users to reference (short IDs)
- Deterministic ordering
- Aligns with constitution's simplicity principle

**Alternatives Rejected**:
- **UUIDs**: Overkill for single-user; long IDs harder for users
- **Timestamps**: Not guaranteed unique; harder to reference
- **Hash-based**: Unnecessary complexity

### Why Mutable Title/Description?

**Decision**: Allow title and description updates

**Rationale**:
- Users make mistakes and need corrections
- Requirements may change after task creation
- Supports future "update task" feature
- Only ID and created_at are immutable (identity preservation)

### Why Preserve Special Characters?

**Decision**: Store title/description exactly as provided (after validation)

**Rationale**:
- Users may need special formatting (e.g., "TODO: fix bug #123")
- Unicode support for international users
- Newlines may be intentional for multi-line descriptions
- Sanitization can cause data loss

---

## Validation Error Catalog

| Error Code | Condition | Message | Action |
|------------|-----------|---------|--------|
| EMPTY_TITLE | Title is None, empty, or whitespace-only | "Title cannot be empty" | Reject task creation |
| TITLE_TOO_LONG | Title length > 200 | "⚠️  Warning: Title exceeds 200 character limit..." | Prompt user confirmation |
| DESC_TOO_LONG | Description length > 1000 | "⚠️  Warning: Description exceeds 1000 character limit..." | Prompt user confirmation |
| USER_CANCELLED | User declines truncation | "Task creation cancelled" | Abort task creation |
| INVALID_ID | ID < 1 (internal error) | "Invalid task ID" | Raise exception |

---

## Testing Checklist

### Contract Tests (test_task_model.py)

- [ ] Task creation with all fields
- [ ] Task creation with minimal fields (title only)
- [ ] Task with exactly 200 character title
- [ ] Task with exactly 1000 character description
- [ ] Title validation (empty string raises error)
- [ ] Title validation (whitespace-only raises error)
- [ ] Title validation (201 characters raises error)
- [ ] Description validation (1001 characters raises error)
- [ ] ID must be positive integer
- [ ] created_at is auto-generated
- [ ] Default completed is False

### Integration Tests (test_add_task_flow.py)

- [ ] Add task with title only via CLI
- [ ] Add task with title and description via CLI
- [ ] Add task with 201-char title (confirm truncation)
- [ ] Add task with 201-char title (decline truncation)
- [ ] Add task with 1001-char description (confirm truncation)
- [ ] Add task with 1001-char description (decline truncation)
- [ ] Add task with empty title (error displayed)
- [ ] Task receives unique sequential ID
- [ ] Confirmation message includes task ID

---

## References

- Feature specification: `specs/001-add-task/spec.md`
- Research document: `specs/001-add-task/research.md`
- Python dataclasses: PEP 557
- Constitution: `.specify/memory/constitution.md` v1.0.0
