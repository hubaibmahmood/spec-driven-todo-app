# Quickstart Guide: Add Task Feature

**Feature**: 001-add-task
**Date**: 2025-12-07
**Purpose**: Quick reference for implementing and testing the add task feature

## Prerequisites

- Python 3.12+ installed
- UV package manager installed
- Git repository initialized
- Constitution and feature spec reviewed

---

## Project Setup (First Time)

### 1. Initialize UV Project

```bash
# Initialize UV project with package structure
uv init --package .

# Configure project metadata
cat > pyproject.toml << 'EOF'
[project]
name = "todo-app"
version = "0.1.0"
description = "Command-line todo application"
requires-python = ">=3.12"
dependencies = []

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "ruff>=0.1.0",
    "mypy>=1.7.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.mypy]
python_version = "3.12"
strict = true
warn_return_any = true
warn_unused_configs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_functions = "test_*"
EOF
```

### 2. Create Project Structure

```bash
# Create source directories
mkdir -p src/models
mkdir -p src/services
mkdir -p src/cli
mkdir -p src/storage

# Create test directories
mkdir -p tests/contract
mkdir -p tests/integration
mkdir -p tests/unit

# Create __init__.py files
touch src/__init__.py
touch src/models/__init__.py
touch src/services/__init__.py
touch src/cli/__init__.py
touch src/storage/__init__.py
touch tests/__init__.py
touch tests/contract/__init__.py
touch tests/integration/__init__.py
touch tests/unit/__init__.py
```

### 3. Install Dependencies

```bash
# Install development dependencies
uv pip install -e ".[dev]"

# Verify installation
uv run pytest --version
uv run ruff --version
uv run mypy --version
```

---

## Implementation Workflow (TDD)

### Phase 1: Contract Tests (Red)

**File**: `tests/contract/test_task_model.py`

```python
"""Contract tests for Task model."""
from datetime import datetime
import pytest
from src.models.task import Task


def test_task_creation_with_all_fields():
    """Task can be created with all fields specified."""
    task = Task(
        id=1,
        title="Buy groceries",
        description="Milk, eggs, bread",
        completed=False,
        created_at=datetime(2025, 12, 7, 10, 0, 0)
    )

    assert task.id == 1
    assert task.title == "Buy groceries"
    assert task.description == "Milk, eggs, bread"
    assert task.completed is False
    assert task.created_at == datetime(2025, 12, 7, 10, 0, 0)


def test_task_creation_minimal_fields():
    """Task can be created with only required fields."""
    task = Task(id=1, title="Simple task")

    assert task.id == 1
    assert task.title == "Simple task"
    assert task.description is None
    assert task.completed is False
    assert isinstance(task.created_at, datetime)


def test_task_empty_title_raises_error():
    """Creating task with empty title raises ValueError."""
    with pytest.raises(ValueError, match="Title cannot be empty"):
        Task(id=1, title="")


def test_task_whitespace_title_raises_error():
    """Creating task with whitespace-only title raises ValueError."""
    with pytest.raises(ValueError, match="Title cannot be empty"):
        Task(id=1, title="   ")


def test_task_title_too_long_raises_error():
    """Creating task with >200 char title raises ValueError."""
    long_title = "x" * 201
    with pytest.raises(ValueError, match="Title exceeds 200 character limit"):
        Task(id=1, title=long_title)


def test_task_description_too_long_raises_error():
    """Creating task with >1000 char description raises ValueError."""
    long_desc = "x" * 1001
    with pytest.raises(ValueError, match="Description exceeds 1000 character limit"):
        Task(id=1, title="Valid title", description=long_desc)


def test_task_invalid_id_raises_error():
    """Creating task with invalid ID raises ValueError."""
    with pytest.raises(ValueError, match="Task ID must be positive"):
        Task(id=0, title="Valid title")
```

**Run tests (should FAIL)**:
```bash
uv run pytest tests/contract/ -v
# Expected: All tests fail (Task model not implemented)
```

### Phase 2: Implement Task Model (Green)

**File**: `src/models/task.py`

```python
"""Task model definition."""
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
        if self.id < 1:
            raise ValueError("Task ID must be positive")

        if not self.title or not self.title.strip():
            raise ValueError("Title cannot be empty")

        if len(self.title) > 200:
            raise ValueError("Title exceeds 200 character limit")

        if self.description is not None and len(self.description) > 1000:
            raise ValueError("Description exceeds 1000 character limit")
```

**Run tests (should PASS)**:
```bash
uv run pytest tests/contract/ -v
# Expected: All contract tests pass
```

### Phase 3: Storage Layer Tests (Red)

**File**: `tests/unit/test_memory_store.py`

```python
"""Unit tests for in-memory storage."""
import pytest
from src.models.task import Task
from src.storage.memory_store import MemoryStore


def test_add_task_assigns_id():
    """Adding task assigns sequential ID."""
    store = MemoryStore()
    task = Task(id=0, title="Placeholder")  # ID will be assigned

    task_id = store.add(task)

    assert task_id == 1


def test_add_multiple_tasks_sequential_ids():
    """Multiple tasks receive sequential IDs."""
    store = MemoryStore()

    id1 = store.add(Task(id=0, title="First"))
    id2 = store.add(Task(id=0, title="Second"))
    id3 = store.add(Task(id=0, title="Third"))

    assert id1 == 1
    assert id2 == 2
    assert id3 == 3


def test_get_task_by_id():
    """Can retrieve task by ID."""
    store = MemoryStore()
    task = Task(id=0, title="Test task")
    task_id = store.add(task)

    retrieved = store.get(task_id)

    assert retrieved is not None
    assert retrieved.title == "Test task"


def test_get_nonexistent_task_returns_none():
    """Getting nonexistent task returns None."""
    store = MemoryStore()

    result = store.get(999)

    assert result is None
```

**Run tests (should FAIL)**:
```bash
uv run pytest tests/unit/test_memory_store.py -v
```

### Phase 4: Implement Storage Layer (Green)

**File**: `src/storage/memory_store.py`

```python
"""In-memory task storage."""
from typing import Optional
from src.models.task import Task


class MemoryStore:
    """In-memory storage for tasks."""

    def __init__(self):
        """Initialize empty storage."""
        self._tasks: dict[int, Task] = {}
        self._next_id: int = 1

    def add(self, task: Task) -> int:
        """Add task to storage and assign ID."""
        task_id = self._next_id
        # Create new task with assigned ID
        stored_task = Task(
            id=task_id,
            title=task.title,
            description=task.description,
            completed=task.completed,
            created_at=task.created_at
        )
        self._tasks[task_id] = stored_task
        self._next_id += 1
        return task_id

    def get(self, task_id: int) -> Optional[Task]:
        """Retrieve task by ID."""
        return self._tasks.get(task_id)
```

**Run tests (should PASS)**:
```bash
uv run pytest tests/unit/test_memory_store.py -v
```

### Phase 5: Integration Tests (Red → Green → Refactor)

Continue TDD cycle for:
1. Validators (`tests/unit/test_validators.py` → `src/cli/validators.py`)
2. Task service (`tests/unit/test_task_service.py` → `src/services/task_service.py`)
3. CLI commands (`tests/integration/test_add_task_flow.py` → `src/cli/commands.py`)

---

## Running Tests

### Run All Tests
```bash
uv run pytest
```

### Run Specific Test Suite
```bash
# Contract tests only
uv run pytest tests/contract/

# Integration tests only
uv run pytest tests/integration/

# Unit tests only
uv run pytest tests/unit/
```

### Run with Coverage
```bash
uv run pytest --cov=src --cov-report=term-missing
```

### Run Specific Test
```bash
uv run pytest tests/contract/test_task_model.py::test_task_creation_with_all_fields -v
```

---

## Code Quality Checks

### Linting
```bash
# Check for style issues
uv run ruff check src/ tests/

# Auto-fix issues
uv run ruff check --fix src/ tests/
```

### Type Checking
```bash
uv run mypy src/
```

### Run All Quality Checks
```bash
# Combined command
uv run pytest && uv run ruff check src/ tests/ && uv run mypy src/
```

---

## Manual Testing

### Test Add Task (Title Only)
```bash
uv run python -m src.cli.main add "Buy groceries"
# Expected: ✓ Task created successfully (ID: 1)
```

### Test Add Task (With Description)
```bash
uv run python -m src.cli.main add "Buy groceries" -d "Milk, eggs, bread"
# Expected: ✓ Task created successfully (ID: 2)
```

### Test Empty Title
```bash
uv run python -m src.cli.main add ""
# Expected: ✗ Error: Title cannot be empty
```

### Test Title Truncation
```bash
# Generate 201-character title
uv run python -m src.cli.main add "$(python -c 'print("x" * 201)')"
# Expected: Warning prompt, truncation on confirmation
```

---

## Common Commands Reference

### Development Workflow
```bash
# 1. Write failing test
uv run pytest tests/contract/test_task_model.py -v

# 2. Implement feature
# (edit src/models/task.py)

# 3. Run tests until pass
uv run pytest tests/contract/test_task_model.py -v

# 4. Refactor
# (improve code while keeping tests green)

# 5. Check quality
uv run ruff check src/
uv run mypy src/

# 6. Commit
git add .
git commit -m "feat: implement Task model with validation"
```

### Debugging
```bash
# Run with verbose output
uv run pytest -vv

# Run with print statements visible
uv run pytest -s

# Drop into debugger on failure
uv run pytest --pdb

# Run last failed tests
uv run pytest --lf
```

---

## Troubleshooting

### Issue: Import errors
**Solution**: Ensure `__init__.py` exists in all directories and you're running from repo root

### Issue: Tests not discovered
**Solution**: Check test file names start with `test_` and functions start with `test_`

### Issue: Type checking failures
**Solution**: Add type hints to all functions; use `Optional[T]` for nullable types

### Issue: Linting errors
**Solution**: Run `uv run ruff check --fix` to auto-fix, or adjust code manually

---

## Commit Messages

Follow conventional commits:

```bash
# Feature implementation
git commit -m "feat: implement Task model with validation"

# Test addition
git commit -m "test: add contract tests for Task model"

# Bug fix
git commit -m "fix: handle whitespace-only titles correctly"

# Documentation
git commit -m "docs: add quickstart guide for add task feature"

# Refactoring
git commit -m "refactor: extract validation logic to validators module"
```

---

## Next Steps After Implementation

1. Run full test suite: `uv run pytest`
2. Check coverage: `uv run pytest --cov=src --cov-report=html`
3. Review coverage report: `open htmlcov/index.html`
4. Run quality checks: `uv run ruff check src/ && uv run mypy src/`
5. Generate tasks.md: `/sp.tasks`
6. Implement remaining features (view, update, delete, mark complete)

---

## References

- Constitution: `.specify/memory/constitution.md`
- Feature spec: `specs/001-add-task/spec.md`
- Data model: `specs/001-add-task/data-model.md`
- Contracts: `specs/001-add-task/contracts/task-operations.md`
- Research: `specs/001-add-task/research.md`
- pytest docs: https://docs.pytest.org/
- UV docs: https://github.com/astral-sh/uv
