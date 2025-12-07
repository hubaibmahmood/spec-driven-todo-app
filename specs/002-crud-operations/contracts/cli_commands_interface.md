# CLI Commands Interface Contract

**Feature**: 002-crud-operations
**Component**: CLI Layer
**File**: `src/cli/commands.py`

## Overview

This document defines the contracts for CLI command functions that handle user interactions for CRUD operations. Each command function is called from the interactive menu loop.

---

## Command Function Contracts

### Existing Command (No Changes)

#### `add_task_command(store: MemoryStore) -> None`

Prompts user for task title and description, validates, and creates task.

**Already implemented in feature 001-add-task.**

---

### New Commands (To Be Implemented)

#### `view_tasks_command(store: MemoryStore) -> None`

Displays all tasks with ID, status, title, and truncated description.

**Input**: `store: MemoryStore` (current task store)

**Output**: None (prints to stdout)

**Behavior**:
1. Call `store.get_all()` to retrieve all tasks
2. If empty, print "No tasks found" and return
3. For each task, format as: `{id:>3} {status} {title:<30} {description[:50]...}`
4. Status symbols: `[✓]` for complete, `[ ]` for incomplete
5. Truncate description at 50 chars with "..." if longer

**Output Format Example**:
```
  1 [ ] Buy groceries               Need milk, eggs, and bread
  2 [✓] Review pull request         Check PR #123 for security issues...
  3 [ ] Call dentist
```

**Edge Cases**:
- Empty store → "No tasks found"
- Task with no description → empty description column
- Task with description exactly 50 chars → no "..."
- Task with description > 50 chars → show first 50 + "..."

---

#### `mark_complete_command(store: MemoryStore) -> None`

Marks a task as complete by ID.

**Input**: `store: MemoryStore`

**Output**: None (prints to stdout)

**Behavior**:
1. Prompt: "Enter task ID to mark complete: "
2. Read input and strip whitespace
3. Try to convert to integer:
   - On ValueError → print "Error: Task ID must be a number" and return
4. Call `store.get_task(task_id)`:
   - If None → print "Error: Task {id} not found" and return
5. Check if `task["completed"]` is True:
   - If already complete → print "Task {id} is already complete" and return (idempotent)
6. Call `store.update_task(task_id, {"completed": True})`
7. Print "✓ Task {id} marked complete"

**Success Output**: `✓ Task 5 marked complete`

**Error Outputs**:
- `Error: Task ID must be a number` (non-numeric input)
- `Error: Task 999 not found` (task doesn't exist)
- `Task 5 is already complete` (idempotent case)

---

#### `delete_tasks_command(store: MemoryStore) -> None`

Deletes one or more tasks by comma-separated IDs.

**Input**: `store: MemoryStore`

**Output**: None (prints to stdout)

**Behavior**:
1. Prompt: "Enter task ID(s) to delete (comma-separated): "
2. Read input and parse comma-separated IDs (call `parse_task_ids()` helper)
   - On ValueError → print error message and return
3. For each parsed ID:
   - Call `store.delete_task(id)`
   - Track success (True) or failure (False)
4. Print summary:
   - Success: "✓ Deleted task(s): 1, 3, 5"
   - Partial: "✓ Deleted: 1, 3 | Not found: 99"
   - All failed: "Error: No tasks found with IDs: 99, 100"

**Success Output**: `✓ Deleted task(s): 1, 3, 5`

**Partial Success Output**: `✓ Deleted: 1, 3 | Not found: 99, 100`

**All Failed Output**: `Error: No tasks found with IDs: 99, 100`

**Error Outputs**:
- `Error: Task IDs must be numeric` (invalid input like "1,abc,3")
- `Error: No task IDs provided` (empty input)

---

#### `update_task_command(store: MemoryStore) -> None`

Updates a task's description by ID.

**Input**: `store: MemoryStore`

**Output**: None (prints to stdout)

**Behavior**:
1. Prompt: "Enter task ID to update: "
2. Read input and strip whitespace
3. Try to convert to integer:
   - On ValueError → print "Error: Task ID must be a number" and return
4. Call `store.get_task(task_id)`:
   - If None → print "Error: Task {id} not found" and return
5. Print current description: `\nCurrent description: {description or '(empty)'}`
6. Prompt: "Enter new description (or press Enter to clear): "
7. Read new description and strip
8. Validate description length (max 1000 chars):
   - If > 1000 → warn and truncate (same as add task behavior)
9. Call `store.update_task(task_id, {"description": new_description or None})`
10. Print "✓ Task {id} description updated"

**Success Output**: `✓ Task 3 description updated`

**Error Outputs**:
- `Error: Task ID must be a number`
- `Error: Task 999 not found`
- `Warning: Description exceeds 1000 characters. Truncating...` (then success)

---

## Helper Functions

### `parse_task_ids(id_string: str) -> list[int]`

Parses comma-separated task IDs with whitespace tolerance.

**Input**: String like "1, 2, 3" or "1,2,3"

**Output**: List of unique integers `[1, 2, 3]`

**Behavior**:
1. Split by comma: `id_string.split(",")`
2. Strip whitespace from each part
3. Filter out empty strings
4. Convert each to integer (raise ValueError if any fail)
5. Remove duplicates (convert to set, back to list)
6. Return sorted list

**Raises**: `ValueError` if any part is not a valid integer

**Examples**:
- `"1, 2, 3"` → `[1, 2, 3]`
- `"1,2,3"` → `[1, 2, 3]`
- `"1,1,2"` → `[1, 2]` (deduplicated)
- `" 5 , 10 , 15 "` → `[5, 10, 15]`
- `"1,abc,3"` → raises ValueError
- `""` → raises ValueError ("No task IDs provided")

---

## Menu Loop Contract

### `run_interactive_menu(store: MemoryStore) -> None`

Main interactive menu loop.

**Input**: `store: MemoryStore` (shared across all operations)

**Output**: None (prints to stdout, loops until quit)

**Behavior**:
1. Display menu:
   ```
   === Todo App Menu ===
   1. Add Task
   2. View Tasks
   3. Update Task
   4. Delete Tasks
   5. Mark Complete
   6. Quit
   ```
2. Prompt: "Select option (1-6): "
3. Read input and strip whitespace
4. Match choice:
   - "1" → call `add_task_command(store)`
   - "2" → call `view_tasks_command(store)`
   - "3" → call `update_task_command(store)`
   - "4" → call `delete_tasks_command(store)`
   - "5" → call `mark_complete_command(store)`
   - "6" → break loop (quit)
   - Other → print "Invalid option. Please select 1-6."
5. Repeat from step 1 (unless quit)
6. On quit, print "Goodbye!" and exit

**Loop Invariant**: Menu always redisplays after any operation completes

**Exit Condition**: User selects option "6"

---

## Error Handling Strategy

**All command functions must:**
1. Never raise exceptions to the menu loop
2. Handle errors locally with try-except
3. Print clear error messages
4. Return to allow menu loop to continue

**Command functions never crash the application.**

---

## Testing Contracts

### Command Function Tests

Each command function must be tested with:
- Happy path (valid input, task exists)
- Error cases (invalid input, task not found)
- Edge cases (empty store, already complete, etc.)

**Testing Pattern** (using pytest monkeypatch and capsys):
```python
def test_mark_complete_success(monkeypatch, capsys):
    """Test marking a task complete successfully."""
    store = MemoryStore()
    task = store.add_task({"title": "Test", "description": None, "completed": False})

    # Simulate user input
    monkeypatch.setattr("builtins.input", lambda _: str(task["id"]))

    mark_complete_command(store)

    # Verify output
    captured = capsys.readouterr()
    assert f"✓ Task {task['id']} marked complete" in captured.out

    # Verify state change
    updated = store.get_task(task["id"])
    assert updated["completed"] is True
```

### Menu Loop Tests

Must test:
- Single operation then quit
- Multiple operations in sequence
- Invalid menu selections (error + redisplay)
- Each menu option routes to correct command

**Testing Pattern**:
```python
def test_menu_multiple_operations(monkeypatch, capsys):
    """Test view, mark complete, view, quit sequence."""
    store = MemoryStore()
    task = store.add_task({"title": "Test", "description": "Desc", "completed": False})

    # Simulate: view (2), mark complete (5) with ID, view (2), quit (6)
    inputs = iter(["2", "5", str(task["id"]), "2", "6"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    run_interactive_menu(store)

    captured = capsys.readouterr()
    # Verify both view operations show task, second shows as complete
    assert "Test" in captured.out
    assert "[✓]" in captured.out
    assert "Goodbye!" in captured.out
```

---

## Integration with Existing Code

**From feature 001-add-task:**
- Reuse `add_task_command()` for menu option 1
- Reuse `validate_description()` from `src/cli/validators.py` for update command
- Reuse `validate_title()` (not needed for this feature, but available)

**New validators needed:**
- `parse_task_ids()` for delete command

---

## CLI Output Standards

**Success messages**: Start with "✓ " (checkmark)
**Error messages**: Start with "Error: "
**Info messages**: Start with "Task {id} is already complete" (no prefix for idempotent)
**Warnings**: Start with "Warning: "

**Consistency**: All messages are complete sentences with proper capitalization.
