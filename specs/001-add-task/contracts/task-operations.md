# Task Operations Contract

**Feature**: 001-add-task
**Date**: 2025-12-07
**Purpose**: Define the interface contract for task operations (CLI and service layer)

## Overview

This document specifies the contract between the CLI layer and the service layer for task operations. It defines function signatures, input/output formats, error handling, and behavioral contracts.

---

## CLI Interface Contract

### Command: `add`

**Purpose**: Add a new task with title and optional description

**Syntax**:
```bash
todo add <title> [--description <description>]
todo add <title> [-d <description>]
```

**Arguments**:

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `title` | `str` | Yes | Title of the task (1-200 characters) |
| `--description`, `-d` | `str` | No | Optional description (0-1000 characters) |

**Success Output**:
```
✓ Task created successfully (ID: {task_id})
  Title: {title}
  Description: {description or 'None'}
  Status: Incomplete
```

**Error Output Examples**:
```
✗ Error: Title cannot be empty
```

```
⚠️  Warning: Title exceeds 200 character limit.
   Current length: {actual_length} characters
   It will be truncated to 200 characters.
   Continue? (y/n):
```

```
✗ Task creation cancelled
```

**Exit Codes**:
- `0`: Success - task created
- `1`: Validation error (empty title, user cancelled truncation)
- `2`: Internal error (storage failure, unexpected exception)

---

## Service Layer Contract

### Function: `create_task`

**Signature**:
```python
def create_task(
    title: str,
    description: Optional[str] = None,
    confirm_callback: Callable[[str, int], bool] = default_confirm
) -> Task
```

**Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `title` | `str` | Task title (will be validated) |
| `description` | `Optional[str]` | Optional task description |
| `confirm_callback` | `Callable[[str, int], bool]` | Function to prompt user for truncation confirmation |

**Returns**: `Task` - The created task object with assigned ID

**Raises**:

| Exception | Condition | Message |
|-----------|-----------|---------|
| `ValidationError` | Title is empty or whitespace-only | "Title cannot be empty" |
| `ValidationError` | User declines truncation | "Task creation cancelled by user" |
| `StorageError` | Storage operation fails | "Failed to store task: {reason}" |

**Behavior**:

1. **Validate title**:
   - Strip for empty check, but preserve original for storage
   - If empty: raise `ValidationError("Title cannot be empty")`
   - If > 200 chars: call `confirm_callback("Title", 200)`
     - If user confirms: truncate to 200 characters
     - If user declines: raise `ValidationError("Task creation cancelled by user")`

2. **Validate description** (if provided):
   - If > 1000 chars: call `confirm_callback("Description", 1000)`
     - If user confirms: truncate to 1000 characters
     - If user declines: raise `ValidationError("Task creation cancelled by user")`

3. **Create task**:
   - Generate next sequential ID
   - Create Task object with validated title/description
   - Set `completed=False`, `created_at=now()`

4. **Store task**:
   - Add to storage
   - Return created Task object

**Invariants**:
- Task ID is always positive and unique
- Title is never empty after validation
- Title length ≤ 200 characters
- Description length ≤ 1000 characters (if not None)
- created_at is always set to task creation time

---

### Function: `validate_title`

**Signature**:
```python
def validate_title(
    title: str,
    confirm_callback: Callable[[str, int], bool] = default_confirm
) -> str
```

**Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `title` | `str` | Raw title input from user |
| `confirm_callback` | `Callable[[str, int], bool]` | Function to prompt user for truncation |

**Returns**: `str` - Validated (and possibly truncated) title

**Raises**:

| Exception | Condition | Message |
|-----------|-----------|---------|
| `ValidationError` | Title is empty/whitespace-only | "Title cannot be empty" |
| `ValidationError` | User declines truncation | "Task creation cancelled by user" |

**Contract**:
- **Pre-condition**: title is a string (may be empty)
- **Post-condition**: Returned title is 1-200 characters, non-empty after strip
- **Side effect**: May prompt user for input via confirm_callback

---

### Function: `validate_description`

**Signature**:
```python
def validate_description(
    description: Optional[str],
    confirm_callback: Callable[[str, int], bool] = default_confirm
) -> Optional[str]
```

**Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `description` | `Optional[str]` | Raw description input from user |
| `confirm_callback` | `Callable[[str, int], bool]` | Function to prompt user for truncation |

**Returns**: `Optional[str]` - Validated (and possibly truncated) description, or None

**Raises**:

| Exception | Condition | Message |
|-----------|-----------|---------|
| `ValidationError` | User declines truncation | "Task creation cancelled by user" |

**Contract**:
- **Pre-condition**: description is None or string
- **Post-condition**: Returned description is None or 0-1000 characters
- **Side effect**: May prompt user for input via confirm_callback

---

## Storage Layer Contract

### Function: `add_task`

**Signature**:
```python
def add_task(self, task: Task) -> int
```

**Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `task` | `Task` | Task object to store (without ID assigned) |

**Returns**: `int` - The assigned task ID

**Raises**:

| Exception | Condition | Message |
|-----------|-----------|---------|
| `StorageError` | Task already has an ID | "Task already has an ID assigned" |
| `StorageError` | Storage is full | "Storage capacity exceeded" (unlikely in practice) |

**Contract**:
- **Pre-condition**: Task object is valid (per data model constraints)
- **Post-condition**: Task is stored with unique sequential ID
- **Side effect**: Increments internal ID counter
- **Thread safety**: Single-threaded CLI application (no locking required)

**Invariants**:
- IDs are sequential integers starting from 1
- IDs are never reused
- Storage maintains insertion order

---

### Function: `get_task`

**Signature**:
```python
def get_task(self, task_id: int) -> Optional[Task]
```

**Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `task_id` | `int` | ID of task to retrieve |

**Returns**: `Optional[Task]` - Task object if found, None otherwise

**Contract**:
- **Pre-condition**: task_id is a positive integer
- **Post-condition**: Returns task if exists, None otherwise
- **Complexity**: O(1) lookup

---

## Confirmation Callback Contract

### Function: `confirm_truncation`

**Signature**:
```python
def confirm_truncation(field_name: str, limit: int) -> bool
```

**Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `field_name` | `str` | Name of field being truncated ("Title" or "Description") |
| `limit` | `int` | Character limit (200 or 1000) |

**Returns**: `bool` - True if user confirms, False if user declines

**Behavior**:
1. Display warning message with field name and limit
2. Prompt for y/n input
3. Accept 'y', 'yes' (case-insensitive) as confirmation
4. Accept 'n', 'no', or any other input as decline
5. Return boolean result

**Output Format**:
```
⚠️  Warning: {field_name} exceeds {limit} character limit.
   Current length: {actual_length} characters
   It will be truncated to {limit} characters.
   Continue? (y/n):
```

**Contract**:
- **Pre-condition**: field_name is non-empty, limit is positive
- **Post-condition**: Returns True or False based on user input
- **Side effect**: Prompts user for input via stdin
- **Blocking**: Waits for user response

---

## Error Handling Contract

### Exception Hierarchy

```
Exception
└── TodoError (base exception for todo app)
    ├── ValidationError (input validation failures)
    ├── StorageError (storage operation failures)
    └── UserCancelledError (user explicitly cancelled operation)
```

### ValidationError

**When raised**: Input validation fails (empty title, user declines truncation)

**Attributes**:
- `message: str` - Human-readable error description
- `field: Optional[str]` - Field that failed validation (if applicable)

**Example**:
```python
raise ValidationError("Title cannot be empty", field="title")
```

### StorageError

**When raised**: Storage operation fails (ID conflict, capacity exceeded)

**Attributes**:
- `message: str` - Human-readable error description
- `operation: str` - Operation that failed ("add", "get", "update", etc.)

**Example**:
```python
raise StorageError("Task already has an ID assigned", operation="add")
```

---

## Test Contract

### Contract Tests (Test the Model)

**File**: `tests/contract/test_task_model.py`

**Required Tests**:
- Task creation with all fields validates correctly
- Task creation with minimal fields uses defaults
- Task with invalid ID raises ValueError
- Task with empty title raises ValueError
- Task with 201-char title raises ValueError
- Task with 1001-char description raises ValueError
- Task dataclass equality works correctly

### Integration Tests (Test CLI → Service → Storage)

**File**: `tests/integration/test_add_task_flow.py`

**Required Tests**:
- Add task with title only succeeds
- Add task with title and description succeeds
- Add task with empty title shows error and exits
- Add task with 201-char title prompts for confirmation
- Confirming truncation creates task with truncated title
- Declining truncation cancels task creation
- Add task with 1001-char description prompts for confirmation
- Multiple tasks receive sequential IDs

### Unit Tests (Test Individual Functions)

**File**: `tests/unit/test_validators.py`

**Required Tests**:
- validate_title with valid input returns unchanged
- validate_title with empty input raises ValidationError
- validate_title with whitespace-only raises ValidationError
- validate_title with 200 chars returns unchanged
- validate_title with 201 chars prompts and truncates if confirmed
- validate_title with 201 chars raises if declined
- validate_description with None returns None
- validate_description with valid input returns unchanged
- validate_description with 1001 chars prompts and truncates if confirmed

---

## Contract Verification Checklist

Before implementation, verify:

- [ ] All function signatures match specification
- [ ] All error conditions raise specified exceptions
- [ ] All return types match specification
- [ ] All pre-conditions and post-conditions documented
- [ ] All invariants are maintained
- [ ] All side effects are documented
- [ ] Test coverage includes all contract requirements

---

## References

- Data model: `specs/001-add-task/data-model.md`
- Feature specification: `specs/001-add-task/spec.md`
- Python type hints: PEP 484, PEP 526
- Contract design: Design by Contract principles
