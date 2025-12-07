# Quickstart: Interactive Todo Menu with CRUD Operations

**Feature**: 002-crud-operations
**Target Audience**: Developers implementing this feature
**Prerequisites**: Feature 001-add-task completed

## Implementation Overview

This feature adds an interactive menu system with CRUD operations (View, Update, Delete, Mark Complete) to the existing todo application. The implementation follows TDD principles and extends existing components.

---

## High-Level Architecture

```
┌─────────────────┐
│  User Terminal  │
└────────┬────────┘
         │ Interactive loop
         ▼
┌─────────────────────────────────┐
│  CLI Layer (src/cli/)           │
│  - main.py: menu loop           │
│  - commands.py: CRUD commands   │
│  - validators.py: ID parsing    │
└────────┬────────────────────────┘
         │ Calls
         ▼
┌─────────────────────────────────┐
│  Storage Layer (src/storage/)   │
│  - memory_store.py: CRUD ops    │
└─────────────────────────────────┘
```

**No service layer changes needed.** The existing `task_service.py` is only used for task creation (feature 001).

---

## Implementation Steps (TDD Order)

### Phase 1: Extend MemoryStore (Storage Layer)

**File**: `src/storage/memory_store.py`

**Add methods** (see `contracts/memory_store_interface.md`):
1. `get_all() -> list[dict]`
2. `update_task(id, updates) -> dict | None`
3. `delete_task(id) -> bool`
4. `task_exists(id) -> bool`

**Test first**: `tests/unit/test_memory_store.py`
- Test each method with happy path, not found, and edge cases
- Run tests: `uv run pytest tests/unit/test_memory_store.py -v`

---

### Phase 2: Add CLI Validators

**File**: `src/cli/validators.py`

**Add function**:
- `parse_task_ids(id_string: str) -> list[int]`
  - Handles comma-separated IDs with whitespace
  - Deduplicates and validates

**Test first**: `tests/unit/test_validators.py`
- Test valid inputs: "1,2,3", "1, 2, 3", "1,1,2"
- Test invalid inputs: "1,abc,3", ""
- Run tests: `uv run pytest tests/unit/test_validators.py -v`

---

### Phase 3: Implement CLI Commands

**File**: `src/cli/commands.py`

**Add functions** (see `contracts/cli_commands_interface.md`):
1. `view_tasks_command(store)`
2. `mark_complete_command(store)`
3. `delete_tasks_command(store)`
4. `update_task_command(store)`

**Test first**: `tests/unit/test_commands.py` (NEW FILE)
- Use pytest `monkeypatch` to mock `input()`
- Use `capsys` to capture output
- Test each command with valid/invalid inputs
- Run tests: `uv run pytest tests/unit/test_commands.py -v`

---

### Phase 4: Implement Interactive Menu Loop

**File**: `src/cli/main.py`

**Replace existing `main()` function** with:
- `run_interactive_menu(store: MemoryStore) -> None`
- Display menu with 6 options
- Route to appropriate command functions
- Handle invalid selections
- Exit on "6"

**Update entry point** to create MemoryStore and call menu loop.

**Test first**: `tests/integration/test_menu_loop_flow.py` (NEW FILE)
- Test single operation then quit
- Test multiple operations in sequence
- Test invalid menu selections
- Run tests: `uv run pytest tests/integration/test_menu_loop_flow.py -v`

---

### Phase 5: Integration Tests for Each User Flow

**New test files** in `tests/integration/`:
1. `test_view_tasks_flow.py` - View empty list, view populated list
2. `test_mark_complete_flow.py` - Mark task complete, already complete, not found
3. `test_delete_tasks_flow.py` - Delete single, delete multiple, partial success
4. `test_update_task_flow.py` - Update description, task not found

**Each test**:
- Simulates complete user interaction
- Verifies output and state changes
- Run all: `uv run pytest tests/integration/ -v`

---

## Testing Strategy

### Test Pyramid

```
┌─────────────────────────────────────┐
│  Integration Tests (5 new files)   │  ← User flows, multi-step
│  - Menu loop, CRUD workflows       │
└─────────────────────────────────────┘
           ▲
┌─────────────────────────────────────┐
│  Unit Tests (extend 2, add 1)      │  ← Individual functions
│  - MemoryStore methods             │
│  - Validators                       │
│  - Command functions                │
└─────────────────────────────────────┘
           ▲
┌─────────────────────────────────────┐
│  Contract Tests (no changes)       │  ← Task model validation
│  - Task model (existing from 001)  │
└─────────────────────────────────────┘
```

### Running Tests

**All tests**:
```bash
uv run pytest
```

**Specific layer**:
```bash
uv run pytest tests/unit/
uv run pytest tests/integration/
```

**Watch mode** (re-run on file changes):
```bash
uv run pytest --watch
```

---

## Key Design Decisions (From research.md)

1. **Menu loop**: Simple `while True` with `break` on quit (no dependencies)
2. **ID parsing**: `str.split(',')` + `strip()` + dedup (no regex)
3. **Display format**: Fixed-width columns with UTF-8 symbols (no tabulate/rich)
4. **Error handling**: Try-except in commands; never crash menu loop
5. **Storage**: Extend MemoryStore with 4 methods (minimal API)
6. **Testing**: pytest with monkeypatch for input() mocking

---

## Example Usage (After Implementation)

```bash
# Run the app
uv run python -m src.cli.main

# Example session
=== Todo App Menu ===
1. Add Task
2. View Tasks
3. Update Task
4. Delete Tasks
5. Mark Complete
6. Quit

Select option (1-6): 1
Enter task title: Buy groceries
Enter task description (optional): Need milk, eggs, and bread
✓ Task created successfully with ID: 1

Select option (1-6): 2
  1 [ ] Buy groceries               Need milk, eggs, and bread

Select option (1-6): 5
Enter task ID to mark complete: 1
✓ Task 1 marked complete

Select option (1-6): 2
  1 [✓] Buy groceries               Need milk, eggs, and bread

Select option (1-6): 6
Goodbye!
```

---

## Files Modified/Created Summary

### Modified (3 files)
- `src/storage/memory_store.py` - Add 4 CRUD methods
- `src/cli/validators.py` - Add parse_task_ids()
- `src/cli/main.py` - Replace main() with interactive menu loop

### Extended (2 test files)
- `tests/unit/test_memory_store.py` - Add tests for new methods
- `tests/unit/test_validators.py` - Add tests for parse_task_ids()

### Created (6 files)
- `src/cli/commands.py` - May need to be created if doesn't exist; add 4 command functions
- `tests/unit/test_commands.py` - New test file
- `tests/integration/test_view_tasks_flow.py` - New test file
- `tests/integration/test_mark_complete_flow.py` - New test file
- `tests/integration/test_delete_tasks_flow.py` - New test file
- `tests/integration/test_update_task_flow.py` - New test file
- `tests/integration/test_menu_loop_flow.py` - New test file

**Total**: 3 modified, 2 extended, 7 created (if commands.py doesn't exist)

---

## Common Pitfalls to Avoid

1. **Don't mutate task data outside MemoryStore** - Always use store methods
2. **Don't skip tests** - TDD is mandatory per constitution
3. **Don't add abstractions** - Keep it simple; no repository pattern, no ORM-like features
4. **Don't hardcode IDs in tests** - Use store.add_task() and get the returned ID
5. **Don't forget to test error paths** - Invalid IDs, empty lists, etc.
6. **Don't crash on invalid input** - Always handle ValueError, return to menu

---

## Next Steps After This Feature

This feature completes the basic CRUD functionality. Future features might add:
- Persistence (save/load tasks to file)
- Filtering (show only complete/incomplete tasks)
- Search (find tasks by keyword)
- Priority levels
- Due dates

**But**: Only implement when explicitly requested. Keep it simple for now.

---

## References

- **Spec**: `specs/002-crud-operations/spec.md` - User requirements
- **Research**: `specs/002-crud-operations/research.md` - Technical decisions
- **Data Model**: `specs/002-crud-operations/data-model.md` - Entity definitions
- **Contracts**: `specs/002-crud-operations/contracts/` - Method signatures
- **Constitution**: `.specify/memory/constitution.md` - Development principles
