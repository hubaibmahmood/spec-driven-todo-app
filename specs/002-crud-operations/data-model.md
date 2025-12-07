# Data Model: Interactive Todo Menu with CRUD Operations

**Feature**: 002-crud-operations
**Date**: 2025-12-07
**Phase**: 1 - Design

## Overview

This feature extends the existing Task model and MemoryStore with CRUD operations. No new entities are required per user guidance to keep things simple.

## Entities

### Task (Existing - No Changes)

The Task model from feature 001-add-task remains unchanged.

**Source**: `src/models/task.py`

**Attributes**:
- `id: int` - Unique identifier (positive integer)
- `title: str` - Task title (1-200 characters, required)
- `description: str | None` - Optional description (0-1000 characters)
- `completed: bool` - Completion status (default: False)
- `created_at: datetime` - Creation timestamp (auto-generated)

**Validation Rules** (existing):
- ID must be >= 1
- Title cannot be empty or whitespace-only
- Title max 200 characters
- Description max 1000 characters
- Title is stripped of leading/trailing whitespace on creation

**State Transitions**:
```
┌─────────────┐
│  incomplete │ ──────────────────────────┐
│ (default)   │                           │
└─────────────┘                           │
                                          │
                                    mark_complete()
                                          │
                                          ▼
                                   ┌──────────┐
                                   │ complete │
                                   └──────────┘
```

**Notes**:
- Title is immutable after creation (per spec clarification)
- Description can be updated via update operation
- Marking an already-completed task is idempotent (no error)

---

## Storage Layer Extensions

### MemoryStore (Extended)

**Source**: `src/storage/memory_store.py`

**Existing Methods**:
- `add_task(task_data: dict) -> dict` - Add task with auto-generated ID
- `get_task(task_id: int) -> dict | None` - Retrieve single task

**New Methods**:

#### `get_all() -> list[dict[str, Any]]`
Returns all tasks as a list ordered by ID (insertion order).

**Returns**: List of task dictionaries with all fields
**Use Case**: View tasks operation

---

#### `update_task(task_id: int, updates: dict[str, Any]) -> dict[str, Any] | None`
Updates specified fields of a task.

**Parameters**:
- `task_id`: ID of task to update
- `updates`: Dictionary of fields to update (e.g., `{"description": "New desc"}`)

**Returns**: Updated task dict if found, None if task doesn't exist
**Validation**: Caller responsible for validating update values
**Use Case**: Update task description operation

---

#### `delete_task(task_id: int) -> bool`
Deletes a task by ID.

**Parameters**:
- `task_id`: ID of task to delete

**Returns**: True if task was deleted, False if task didn't exist
**Use Case**: Delete tasks operation (called once per ID)

---

#### `task_exists(task_id: int) -> bool`
Checks if a task exists.

**Parameters**:
- `task_id`: ID to check

**Returns**: True if task exists, False otherwise
**Use Case**: Service layer validation before operations

---

## Data Flow

### View Tasks Flow
```
User → CLI (view command) → MemoryStore.get_all()
                         → Format list → Display to user
```

### Mark Complete Flow
```
User → CLI (mark complete) → Validate ID
                          → MemoryStore.get_task(id)
                          → Check if already complete
                          → MemoryStore.update_task(id, {"completed": True})
                          → Confirmation message
```

### Delete Tasks Flow
```
User → CLI (delete) → Parse comma-separated IDs
                   → Validate each ID as integer
                   → For each ID:
                       → MemoryStore.delete_task(id)
                       → Track success/failure
                   → Report results
```

### Update Task Flow
```
User → CLI (update) → Get task ID
                   → MemoryStore.get_task(id)
                   → Display current description
                   → Get new description
                   → Validate (max 1000 chars)
                   → MemoryStore.update_task(id, {"description": new_desc})
                   → Confirmation message
```

---

## Validation Rules Summary

| Field | Validation | Where Enforced |
|-------|------------|----------------|
| Task ID (input) | Must be integer > 0 | CLI validators |
| Task ID (existence) | Must exist in store | Service layer via task_exists() |
| Description (update) | Max 1000 chars | CLI validators (reuse from 001) |
| Menu selection | Must be 1-6 | CLI main loop |
| Comma-separated IDs | Each part must be valid integer | CLI validators |

---

## Error Conditions

| Condition | Detection | Handling |
|-----------|-----------|----------|
| Task ID not found | `get_task()` returns None | Display "Task {id} not found" |
| Invalid ID format (non-numeric) | `int()` raises ValueError | Display "Task ID must be a number" |
| Empty task list | `get_all()` returns [] | Display "No tasks found" |
| Already completed | `task["completed"]` is True | Display "Task is already complete" (idempotent) |
| Description too long | Length check in validator | Warn and truncate (same as add) |
| Invalid menu choice | Not in range 1-6 | Display "Invalid option. Please select 1-6." |

---

## Relationships

No relationships between entities (single entity: Task).

Tasks are stored independently in a flat dictionary keyed by ID.

---

## Invariants

1. **Unique IDs**: Every task has a unique, sequential ID (enforced by MemoryStore)
2. **ID Immutability**: Task IDs never change after creation
3. **Title Immutability**: Task title cannot be updated (per spec clarification)
4. **Title Required**: Every task must have a non-empty title (enforced by Task model)
5. **Boolean Status**: Completed field is always boolean (never null/missing)
6. **Sequential IDs**: IDs are assigned sequentially starting from 1 (MemoryStore._next_id)

---

## Design Notes

**Simplicity Decisions**:
- No new models/entities (reuse existing Task)
- No relationship tracking (single entity)
- No soft deletes (hard delete from dict)
- No update history/audit trail
- No filtering or search (get all or get by ID only)
- No pagination (acceptable for in-memory tool)

**Extension Points** (if future features needed):
- Filtering: Add `get_by_status(completed: bool)` to MemoryStore
- Search: Add `search_by_title(query: str)` to MemoryStore
- Soft delete: Add `deleted: bool` field to Task and filter in `get_all()`
- Update history: Add `updated_at: datetime` field to Task

All extension points deferred until explicitly requested to maintain simplicity.
