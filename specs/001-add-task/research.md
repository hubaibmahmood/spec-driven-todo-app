# Research: Add Task Feature

**Feature**: 001-add-task
**Date**: 2025-12-07
**Purpose**: Technical research and decision documentation for task creation functionality

## Overview

This document captures technical decisions, best practices research, and architectural choices for implementing the add task feature in a Python CLI todo application.

## Technology Stack Decisions

### Python CLI Framework

**Decision**: Use built-in `argparse` module for CLI parsing

**Rationale**:
- Built-in to Python standard library (no external dependency)
- Sufficient for simple CLI operations
- Well-documented and widely understood
- Supports subcommands, argument validation, help generation
- Aligns with constitution's simplicity principle (YAGNI)

**Alternatives Considered**:
- **Click**: More features but adds external dependency; overkill for simple CRUD operations
- **Typer**: Modern with type hints but adds dependency; excessive for this scope
- **Fire**: Automatic CLI from functions but less control over interface design

**Reference**: Python argparse documentation, CLI best practices for simple applications

---

### Data Model Implementation

**Decision**: Use Python `dataclasses` with type hints for Task model

**Rationale**:
- Built-in since Python 3.7, no external dependency
- Automatic `__init__`, `__repr__`, `__eq__` generation
- Native support for type hints (required by constitution)
- Immutable option via `frozen=True` for data integrity
- Clean, readable syntax reduces boilerplate

**Alternatives Considered**:
- **Pydantic**: Powerful validation but adds dependency; overkill for in-memory model
- **attrs**: Similar to dataclasses but external dependency
- **Plain classes**: More boilerplate, no automatic methods

**Example Pattern**:
```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Task:
    id: int
    title: str
    description: Optional[str] = None
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)
```

**Reference**: PEP 557 (Data Classes), Python dataclasses documentation

---

### In-Memory Storage Strategy

**Decision**: Use a dictionary with integer keys for O(1) lookups + counter for ID generation

**Rationale**:
- Fast lookup by ID: O(1) time complexity
- Preserves insertion order (Python 3.7+)
- Simple ID generation via counter (thread-safe for single-user CLI)
- Easy to extend to persistent storage later (same interface)
- Minimal memory overhead for 1000+ tasks requirement

**Storage Pattern**:
```python
class MemoryStore:
    def __init__(self):
        self._tasks: dict[int, Task] = {}
        self._next_id: int = 1

    def add(self, task: Task) -> int:
        task_id = self._next_id
        self._tasks[task_id] = task
        self._next_id += 1
        return task_id

    def get(self, task_id: int) -> Optional[Task]:
        return self._tasks.get(task_id)
```

**Alternatives Considered**:
- **List-based storage**: O(n) lookup by ID, requires linear search
- **UUID for IDs**: Overkill for single-user; sequential integers simpler
- **SQLite in-memory**: Adds dependency, excessive for simple CRUD

**Reference**: Python dict performance characteristics, in-memory data structure patterns

---

### Input Validation Strategy

**Decision**: Multi-layer validation (CLI → Service → Model)

**Rationale**:
- **CLI layer**: Basic type checking, empty string detection
- **Service layer**: Business logic validation (length limits, confirmation prompts)
- **Model layer**: Data integrity constraints (type hints, required fields)
- Separation of concerns per constitution Principle III
- Each layer handles appropriate validation level

**Validation Flow**:
1. CLI validates basic input presence (empty checks)
2. Service validates business rules (character limits, prompts user)
3. Model ensures data integrity via dataclass validation

**Error Handling Pattern**:
```python
class ValidationError(Exception):
    """Custom exception for validation failures"""
    pass

def validate_title(title: str) -> str:
    if not title or not title.strip():
        raise ValidationError("Title cannot be empty")

    if len(title) > 200:
        # Prompt user for confirmation
        if not confirm_truncation("Title", 200):
            raise ValidationError("Task creation cancelled")
        return title[:200]

    return title
```

**Reference**: Python validation patterns, CLI error handling best practices

---

### Testing Strategy

**Decision**: Three-tier testing approach (contract, integration, unit)

**Rationale**:
- **Contract tests**: Verify Task model behavior (dataclass contracts)
- **Integration tests**: End-to-end CLI workflows (add → view confirmation)
- **Unit tests**: Individual function behavior (validators, service methods)
- Aligns with constitution's TDD requirements
- Comprehensive coverage without redundancy

**Test Structure**:
```
tests/
├── contract/
│   └── test_task_model.py      # Task creation, field validation, immutability
├── integration/
│   └── test_add_task_flow.py   # Full CLI command execution, user prompts
└── unit/
    ├── test_validators.py       # Input validation functions
    └── test_task_service.py     # Service layer methods
```

**Reference**: Python testing best practices, pytest documentation, TDD patterns

---

### User Confirmation for Truncation

**Decision**: Use `input()` with yes/no prompt for character limit confirmations

**Rationale**:
- Built-in Python function, no dependency
- Synchronous blocking appropriate for CLI (user must respond)
- Clear y/n pattern familiar to CLI users
- Aligns with spec requirement for user confirmation

**Confirmation Pattern**:
```python
def confirm_truncation(field_name: str, limit: int) -> bool:
    """Prompt user to confirm truncation of field exceeding limit."""
    message = (
        f"\n⚠️  Warning: {field_name} exceeds {limit} character limit.\n"
        f"   It will be truncated. Continue? (y/n): "
    )
    response = input(message).strip().lower()
    return response in ('y', 'yes')
```

**Reference**: CLI UX patterns, Python input handling

---

### CLI Output Formatting

**Decision**: Use formatted strings with Unicode symbols for clarity

**Rationale**:
- Clear visual feedback (✓ for success, ⚠️ for warnings, ✗ for errors)
- Structured output with consistent formatting
- Human-readable per constitution Principle V
- No external dependencies (built-in string formatting)

**Output Patterns**:
```python
# Success message
print(f"✓ Task created successfully (ID: {task_id})")

# Warning message
print(f"⚠️  Warning: Title exceeds 200 character limit")

# Error message
print(f"✗ Error: Title cannot be empty")
```

**Reference**: CLI design patterns, terminal output best practices

---

### Performance Considerations

**Decision**: No special optimization needed for MVP

**Rationale**:
- Target: 1000 tasks, <1 second response time
- Dictionary lookup: O(1), well within performance budget
- Task creation overhead: minimal (dataclass instantiation)
- No I/O operations (in-memory only)
- Premature optimization violates constitution Principle II

**Measured Expectations**:
- Task creation: <10ms for validation + storage
- List retrieval (1000 tasks): <50ms
- Well within <1 second requirement

**Reference**: Python performance characteristics, profiling guidelines

---

## Best Practices Applied

### Type Safety
- All functions use type hints per constitution
- mypy for static type checking
- Runtime type validation via dataclasses

### Error Handling
- Custom ValidationError exception for business logic violations
- Clear error messages with actionable guidance
- No silent failures

### Code Organization
- Single Responsibility Principle: each module has one purpose
- Dependency direction: CLI → Service → Storage → Model
- No circular dependencies

### Testing
- Write tests first (TDD per constitution)
- Test file names mirror source file names
- One test file per source module

---

## Open Questions

None - all technical decisions resolved for add task feature scope.

---

## References

- Python 3.12 documentation
- PEP 8 (Style Guide)
- PEP 557 (Data Classes)
- pytest documentation
- CLI design patterns and best practices
- Constitution v1.0.0
