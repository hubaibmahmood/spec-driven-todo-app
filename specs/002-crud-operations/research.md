# Research: Interactive Todo Menu with CRUD Operations

**Feature**: 002-crud-operations
**Date**: 2025-12-07
**Phase**: 0 - Research

## Research Questions & Findings

### 1. Interactive Menu Loop Pattern in Python CLI

**Question**: What is the best practice for implementing an interactive menu loop in a Python CLI application that returns to the menu after each operation?

**Decision**: Use a simple while-True loop with numbered menu options and input() for user selection.

**Rationale**:
- Simplest approach that meets requirements (no external dependencies)
- Clear control flow that's easy to test
- Allows graceful exit via break on "quit" selection
- Standard pattern for educational/small CLI tools

**Alternatives Considered**:
- `cmd.Cmd` module: Overkill for numbered menu; designed for command-based interfaces
- Third-party libraries (prompt_toolkit, click): Violates simplicity principle; adds dependencies
- Recursive function calls: Risk of stack overflow on long sessions; harder to test

**Implementation Pattern**:
```python
def run_interactive_menu(store: MemoryStore) -> None:
    while True:
        display_menu()
        choice = input("Select option (1-6): ").strip()

        if choice == "6":  # Quit
            break
        elif choice == "1":  # Add
            add_task_command(store)
        # ... other options
        else:
            print("Invalid option. Please select 1-6.")
```

---

### 2. Task Listing Display Format

**Question**: What is the optimal way to display task lists in a CLI with ID, title, status, and truncated description?

**Decision**: Use simple formatted strings with fixed-width columns and UTF-8 status symbols.

**Rationale**:
- No external dependencies (no tabulate, rich, etc.)
- Clear visual hierarchy with status symbols [✓] and [ ]
- Description truncation at 50 chars prevents line wrapping on standard terminals
- Easy to test output format

**Alternatives Considered**:
- `tabulate` library: Adds dependency; overkill for simple list
- `rich` library: Beautiful but violates simplicity; adds complexity
- CSV-style output: Poor readability for users

**Implementation Pattern**:
```python
def format_task_list(tasks: list[dict]) -> str:
    if not tasks:
        return "No tasks found."

    output = []
    for task in tasks:
        status = "[✓]" if task["completed"] else "[ ]"
        desc = task["description"][:50] + "..." if len(task.get("description", "")) > 50 else task.get("description", "")
        output.append(f"{task['id']:>3} {status} {task['title']:<30} {desc}")
    return "\n".join(output)
```

---

### 3. Comma-Separated ID Parsing and Validation

**Question**: How should the system parse and validate comma-separated task IDs for deletion with whitespace handling?

**Decision**: Use `str.split(',')` with `strip()` on each element, filter out empties, validate as integers, remove duplicates.

**Rationale**:
- Handles "1, 2, 3" and "1,2,3" uniformly
- Clear error messages for invalid IDs (non-numeric)
- Deduplication prevents accidental double-delete attempts
- No regex needed (KISS principle)

**Alternatives Considered**:
- Regex-based parsing: Overcomplicated for simple comma-separated integers
- Accept only strict "1,2,3" format: Poor UX; users naturally add spaces
- Custom parser class: Violates simplicity for this simple task

**Implementation Pattern**:
```python
def parse_task_ids(id_string: str) -> list[int]:
    """Parse comma-separated task IDs with whitespace tolerance."""
    parts = [p.strip() for p in id_string.split(",") if p.strip()]

    try:
        ids = [int(p) for p in parts]
    except ValueError:
        raise ValueError("Task IDs must be numeric")

    return list(set(ids))  # Remove duplicates
```

---

### 4. MemoryStore Extension Strategy

**Question**: What methods should be added to MemoryStore to support CRUD operations while maintaining simplicity?

**Decision**: Add four methods: `get_all()`, `update_task(id, updates)`, `delete_task(id)`, `task_exists(id)`.

**Rationale**:
- Minimal surface area for CRUD operations
- `get_all()` returns list of all tasks for view operation
- `update_task()` accepts partial dict for flexibility
- `delete_task()` returns bool for success/failure feedback
- `task_exists()` helper for validation in service layer
- No need for filtering/querying beyond basic ID lookup

**Alternatives Considered**:
- Separate methods for each field update: Too granular; violates simplicity
- Query builder pattern: Massive overkill for in-memory dict
- Repository pattern: Unnecessary abstraction layer

**Implementation Pattern**:
```python
class MemoryStore:
    # ... existing methods ...

    def get_all(self) -> list[dict[str, Any]]:
        """Return all tasks as a list."""
        return list(self._tasks.values())

    def update_task(self, task_id: int, updates: dict[str, Any]) -> dict[str, Any] | None:
        """Update task fields. Returns updated task or None if not found."""
        if task_id not in self._tasks:
            return None
        self._tasks[task_id].update(updates)
        return self._tasks[task_id]

    def delete_task(self, task_id: int) -> bool:
        """Delete task by ID. Returns True if deleted, False if not found."""
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False

    def task_exists(self, task_id: int) -> bool:
        """Check if task exists."""
        return task_id in self._tasks
```

---

### 5. Update Task UX Flow

**Question**: Should the update operation show the current description before accepting new input?

**Decision**: Yes - display full current description before prompting for new description.

**Rationale**:
- Spec clarifies: "full description visible only during update" (FR-010a)
- Users need context to make informed edits
- Prevents accidental overwrites of content they can't see
- Simple to implement with print() before input()

**Alternatives Considered**:
- Pre-populate input with current description: Not supported by basic input(); would need readline library
- Show description in view, edit blind: Poor UX per spec requirements

**Implementation Pattern**:
```python
def update_task_command(store: MemoryStore) -> None:
    task_id = int(input("Enter task ID: "))
    task = store.get_task(task_id)

    if not task:
        print(f"Error: Task {task_id} not found")
        return

    print(f"\nCurrent description: {task.get('description', '(empty)')}")
    new_desc = input("Enter new description (or press Enter to clear): ").strip()

    # ... validation and update ...
```

---

### 6. Error Handling Strategy for CRUD Operations

**Question**: How should the system handle errors (non-existent IDs, invalid input) without crashing?

**Decision**: Use try-except blocks in command functions; return to menu on all errors with clear messages.

**Rationale**:
- Spec requires: "clear error messages for invalid operations" (FR-014)
- Never crash the interactive loop (bad UX)
- Print error immediately; return to menu (FR-002)
- Distinguish between validation errors (bad input) and not-found errors (bad ID)

**Alternatives Considered**:
- Raise exceptions to top level: Would crash the menu loop
- Return error codes: Less Pythonic; unclear to developers
- Silent failures: Terrible UX; violates spec requirements

**Implementation Pattern**:
```python
def mark_complete_command(store: MemoryStore) -> None:
    try:
        task_id_str = input("Enter task ID to mark complete: ").strip()
        task_id = int(task_id_str)
    except ValueError:
        print("Error: Task ID must be a number")
        return

    task = store.get_task(task_id)
    if not task:
        print(f"Error: Task {task_id} not found")
        return

    if task["completed"]:
        print(f"Task {task_id} is already complete")  # Idempotent, not error
        return

    store.update_task(task_id, {"completed": True})
    print(f"✓ Task {task_id} marked complete")
```

---

### 7. Testing Strategy for Interactive Menu

**Question**: How to test an interactive menu loop that uses input() without manual user interaction?

**Decision**: Use pytest with `monkeypatch.setattr` to mock input() and capsys to capture output.

**Rationale**:
- Standard pytest pattern for testing CLI interactions
- No additional dependencies
- Tests are reproducible and automated
- Can simulate multi-step user workflows

**Alternatives Considered**:
- Manual testing only: Not TDD compliant; regressions likely
- `unittest.mock.patch`: Works but monkeypatch is more pytest-idiomatic
- Click's testing utilities: Would require rewriting to use Click framework

**Implementation Pattern**:
```python
def test_menu_view_then_quit(monkeypatch, capsys):
    """Test user selects view, then quit."""
    # Simulate: view (2), then quit (6)
    inputs = iter(["2", "6"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    store = MemoryStore()
    store.add_task({"title": "Test", "description": "Desc", "completed": False})

    run_interactive_menu(store)

    captured = capsys.readouterr()
    assert "No tasks found" not in captured.out
    assert "Test" in captured.out
```

---

## Summary of Technical Decisions

| Area | Decision | Key Rationale |
|------|----------|---------------|
| Menu Loop | while-True with break on quit | Simplest; no dependencies; easy to test |
| Display Format | Fixed-width columns with UTF-8 symbols | No dependencies; clear; testable |
| ID Parsing | split() + strip() + dedup | Handles whitespace; simple; no regex |
| Storage Methods | 4 new methods on MemoryStore | Minimal API; supports all CRUD |
| Update UX | Show current before edit | Required by spec; better UX |
| Error Handling | Try-except in commands; never crash | Spec requirement; graceful failures |
| Testing | monkeypatch + capsys | Standard pytest; no new deps |

All decisions prioritize simplicity per user guidance and constitution principles.
