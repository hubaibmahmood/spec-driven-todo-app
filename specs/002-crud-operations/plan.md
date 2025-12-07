# Implementation Plan: Interactive Todo Menu with CRUD Operations

**Branch**: `002-crud-operations` | **Date**: 2025-12-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-crud-operations/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build an interactive CLI menu system that enables users to perform CRUD operations on tasks (view all tasks, mark complete, delete single/multiple tasks, update task descriptions) in a continuous loop until quit. The system extends the existing add-task functionality (feature 001) with menu-driven interaction using numbered options (1-6) and maintains all tasks in memory during the session.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: dataclasses (models), pytest (testing), ruff (linting), mypy (type checking)
**Storage**: In-memory (MemoryStore with dict-based storage, no persistence)
**Testing**: pytest with contract/integration/unit test structure
**Target Platform**: Cross-platform CLI (Linux, macOS, Windows)
**Project Type**: Single project (CLI application)
**Performance Goals**: <2s for view operations, <5s for CRUD operations on lists up to 100 tasks
**Constraints**: In-memory only (no persistence), session-based (data lost on quit), single-user CLI, interactive menu (no CLI arguments)
**Scale/Scope**: Small personal tool, ~5 core operations, ~10 source files expected

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| **I. Test-First Development** | ✅ PASS | All CRUD operations will follow TDD with tests before implementation |
| **II. Clean Code & Simplicity** | ✅ PASS | User guidance: "Keep things as simple as possible"; no unnecessary models/abstractions |
| **III. Proper Project Structure** | ✅ PASS | Extending existing src/ structure (models, services, cli, storage) |
| **IV. In-Memory Data Storage** | ✅ PASS | Using existing MemoryStore; extending with get_all, delete, update methods |
| **V. CLI Excellence** | ✅ PASS | Interactive menu with numbered options, clear error messages, status indicators |
| **VI. UV Package Manager** | ✅ PASS | Project already initialized with uv; no new dependencies needed |

**Gate Result**: ✅ ALL GATES PASS - Proceed to Phase 0

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
src/
├── models/
│   └── task.py              # Existing: Task dataclass (no changes needed)
├── services/
│   └── task_service.py      # Extend: add view, update, delete, mark_complete
├── storage/
│   ├── memory_store.py      # Extend: add get_all, update, delete methods
│   └── exceptions.py        # Existing storage exceptions
└── cli/
    ├── main.py              # Replace: interactive menu loop (entry point)
    ├── commands.py          # Extend: add view, update, delete, mark_complete commands
    ├── validators.py        # Extend: add ID validation, comma-separated ID parsing
    └── exceptions.py        # Existing CLI exceptions

tests/
├── contract/
│   └── test_task_model.py   # Existing: Task model validation (no changes)
├── integration/
│   ├── test_add_task_flow.py      # Existing: add task flow
│   ├── test_view_tasks_flow.py    # New: view tasks flow
│   ├── test_mark_complete_flow.py # New: mark complete flow
│   ├── test_delete_tasks_flow.py  # New: delete tasks flow (single & multiple)
│   ├── test_update_task_flow.py   # New: update task flow
│   └── test_menu_loop_flow.py     # New: interactive menu loop flow
└── unit/
    ├── test_memory_store.py       # Extend: test get_all, update, delete
    ├── test_validators.py         # Extend: test ID validators
    └── test_commands.py           # New: test individual command functions
```

**Structure Decision**: Single project structure (Option 1). Extending existing codebase from feature 001-add-task. No new directories needed. Focus on extending MemoryStore, task_service, and cli modules with CRUD operations while maintaining simple, focused functions.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations detected. All design decisions align with constitution principles and user guidance to keep things simple.

---

## Post-Phase 1 Constitution Re-Evaluation

*Re-checking after design artifacts complete*

| Principle | Status | Design Review Notes |
|-----------|--------|---------------------|
| **I. Test-First Development** | ✅ PASS | Quickstart defines clear TDD workflow; test files identified for each component |
| **II. Clean Code & Simplicity** | ✅ PASS | No abstractions added; extending existing classes with minimal methods (4 on MemoryStore, 1 validator, 4 commands) |
| **III. Proper Project Structure** | ✅ PASS | All new code fits existing structure; no new directories |
| **IV. In-Memory Data Storage** | ✅ PASS | No persistence; pure dict operations; data lost on quit per spec |
| **V. CLI Excellence** | ✅ PASS | Clear menu, numbered options, error messages defined in contracts |
| **VI. UV Package Manager** | ✅ PASS | No new dependencies; uses standard library only |

**Final Gate Result**: ✅ ALL GATES PASS - Design approved for implementation

**Complexity Score**: **Low** - Minimal changes to existing codebase; no new patterns or abstractions; straightforward CRUD operations.

---

## Design Artifacts Summary

All Phase 0 and Phase 1 artifacts completed:

- ✅ **research.md** - 7 research questions resolved with implementation patterns
- ✅ **data-model.md** - Entity definitions, validation rules, data flows documented
- ✅ **contracts/memory_store_interface.md** - Storage layer method contracts
- ✅ **contracts/cli_commands_interface.md** - CLI command function contracts
- ✅ **quickstart.md** - Implementation guide with TDD workflow and file-by-file breakdown

**Next Command**: `/sp.tasks` to generate testable implementation tasks from these artifacts.
