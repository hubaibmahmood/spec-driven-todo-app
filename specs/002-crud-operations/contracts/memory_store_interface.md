# MemoryStore Interface Contract

**Feature**: 002-crud-operations
**Component**: Storage Layer
**File**: `src/storage/memory_store.py`

## Overview

This document defines the contract for MemoryStore CRUD operations. These are Python method signatures that must be implemented to support the interactive menu feature.

---

## Method Contracts

### Existing Methods (No Changes)

#### `add_task(task_data: dict[str, Any]) -> dict[str, Any]`

Adds a new task with auto-generated ID.

**Input Contract**:
```python
{
    "title": str,          # Required, validated by caller
    "description": str | None,  # Optional
    "completed": bool      # Required, default False
}
```

**Output Contract**:
```python
{
    "id": int,             # Auto-generated, sequential
    "title": str,
    "description": str | None,
    "completed": bool
}
```

**Guarantees**:
- ID is unique and sequential (1, 2, 3, ...)
- Returned dict includes assigned ID
- Input dict is not mutated

---

#### `get_task(task_id: int) -> dict[str, Any] | None`

Retrieves a single task by ID.

**Input**: `task_id: int` (any integer)

**Output**: Task dict (same structure as add_task output) or `None` if not found

**Guarantees**:
- Returns None if task doesn't exist (not an error)
- Returned dict is a reference to stored data (mutations affect storage)

---

### New Methods (To Be Implemented)

#### `get_all() -> list[dict[str, Any]]`

Retrieves all tasks.

**Input**: None

**Output Contract**:
```python
[
    {
        "id": int,
        "title": str,
        "description": str | None,
        "completed": bool
    },
    # ... more tasks
]
```

**Guarantees**:
- Returns empty list if no tasks exist (not None)
- Tasks ordered by ID (insertion order)
- Each task dict matches add_task output structure
- List is a new list (safe to modify); dicts are references to stored data

**Edge Cases**:
- Empty store → returns `[]`

---

#### `update_task(task_id: int, updates: dict[str, Any]) -> dict[str, Any] | None`

Updates specified fields of a task.

**Input Contract**:
```python
task_id: int  # ID of task to update
updates: dict[str, Any]  # Fields to update, e.g.:
{
    "description": str | None,  # Update description
    "completed": bool,          # Update status
    # Other fields as needed
}
```

**Output Contract**: Updated task dict or `None` if task not found

**Guarantees**:
- Only updates fields present in `updates` dict
- Other fields remain unchanged
- Returns None if task doesn't exist (not an error)
- ID field cannot be changed (should not be in updates)
- Returns updated task immediately after update

**Edge Cases**:
- Task not found → returns `None`
- Empty updates dict → no change, returns task
- Invalid field names in updates → stored but ignored (caller's responsibility to validate)

**Validation**:
- Caller must validate update values (e.g., description length)
- Store does not re-validate; trusts caller

---

#### `delete_task(task_id: int) -> bool`

Deletes a task by ID.

**Input**: `task_id: int`

**Output**: `True` if deleted, `False` if task didn't exist

**Guarantees**:
- Removes task from storage permanently
- Returns False if task doesn't exist (not an error)
- ID is not reused for future tasks

**Edge Cases**:
- Task not found → returns `False`
- Already deleted ID → returns `False`

---

#### `task_exists(task_id: int) -> bool`

Checks if a task exists.

**Input**: `task_id: int`

**Output**: `True` if task exists, `False` otherwise

**Guarantees**:
- Read-only operation (no side effects)
- Fast O(1) lookup

---

## Error Handling

**MemoryStore does NOT raise exceptions for:**
- Task not found (returns None or False)
- Invalid task IDs (negative, zero, etc.)

**Caller Responsibilities:**
- Validate task IDs before calling (positive integers)
- Validate update values before calling update_task
- Handle None/False returns appropriately

---

## Thread Safety

**Not thread-safe**. This is a single-user CLI application. No concurrency expected.

---

## Performance Characteristics

| Operation | Complexity | Notes |
|-----------|------------|-------|
| `add_task` | O(1) | Dict insert + counter increment |
| `get_task` | O(1) | Dict lookup by key |
| `get_all` | O(n) | Returns all n tasks |
| `update_task` | O(1) | Dict lookup + update |
| `delete_task` | O(1) | Dict delete |
| `task_exists` | O(1) | Dict key check |

---

## Testing Contract

All methods must be tested with:
- Happy path (valid inputs, task exists)
- Not found (task doesn't exist)
- Edge cases (empty store, boundary values)

Example test structure:
```python
def test_get_all_empty_store():
    store = MemoryStore()
    assert store.get_all() == []

def test_update_task_not_found():
    store = MemoryStore()
    result = store.update_task(999, {"completed": True})
    assert result is None

def test_delete_task_success():
    store = MemoryStore()
    task = store.add_task({"title": "Test", "description": None, "completed": False})
    assert store.delete_task(task["id"]) is True
    assert store.get_task(task["id"]) is None
```
