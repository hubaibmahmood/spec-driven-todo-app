# Tasks: Add Task Feature

**Input**: Design documents from `/specs/001-add-task/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: TDD approach - tests written BEFORE implementation per constitution

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

**Task Sizing**: All tasks are 15-30 minutes with ONE clear acceptance criterion

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths shown below use single project structure from plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Initialize UV project with `uv init --package .`, configure pyproject.toml with Python 3.12+ and dev dependencies (pytest>=7.4.0, pytest-cov>=4.1.0, ruff>=0.1.0, mypy>=1.7.0), and install with `uv pip install -e ".[dev]"`
  - **Acceptance**: `uv run pytest --version`, `uv run ruff --version`, `uv run mypy --version` all work
  - **Time**: 25-30 min

- [ ] T002 Create project directory structure: src/ with models/, services/, cli/, storage/ subdirectories; tests/ with contract/, integration/, unit/ subdirectories; all with __init__.py files
  - **Acceptance**: All directories exist, Python can import from src.models, src.services, etc.
  - **Time**: 15-20 min

- [ ] T003 [P] Configure development tools in pyproject.toml: ruff (line-length=100, target-version=py312), mypy (python_version=3.12, strict=true), pytest (testpaths=["tests"])
  - **Acceptance**: `uv run ruff check src/`, `uv run mypy src/`, `uv run pytest` all execute without config errors
  - **Time**: 20-25 min

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T004 [P] Create exception classes ValidationError and StorageError in src/cli/exceptions.py and src/storage/exceptions.py; create MemoryStore class skeleton in src/storage/memory_store.py with __init__ method initializing _tasks dict and _next_id counter
  - **Acceptance**: Can import exceptions, MemoryStore instantiates without errors
  - **Time**: 15-20 min

- [ ] T005 [P] Create pytest conftest.py in tests/ with fixtures: empty_store() returning fresh MemoryStore, sample_task() returning Task with test data, mock_confirm() returning mock confirmation function
  - **Acceptance**: Fixtures available in all test files, `uv run pytest --fixtures` shows custom fixtures
  - **Time**: 15-20 min

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Create Basic Task (Priority: P1) 🎯 MVP

**Goal**: Users can add tasks with a title and receive confirmation with unique ID

**Independent Test**: Add task with title → verify task created with ID → view task in list

### Tests for User Story 1 (TDD - Write FIRST, ensure FAIL) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T006 [P] [US1] Write contract tests for Task model in tests/contract/test_task_model.py: (1) creation with all fields, (2) creation with minimal fields (title only), (3) empty title raises ValueError, (4) whitespace-only title raises ValueError, (5) 201-char title raises ValueError, (6) invalid ID (<1) raises ValueError
  - **Acceptance**: 6 test functions written, all FAIL when run (Task model not implemented)
  - **Time**: 25-30 min

- [ ] T007 [P] [US1] Write unit tests for title validation in tests/unit/test_validators.py: (1) valid input returns unchanged, (2) empty input raises ValidationError, (3) whitespace-only raises ValidationError, (4) 200 chars returns unchanged, (5) 201 chars prompts and truncates if confirmed, (6) 201 chars raises if user declines
  - **Acceptance**: 6 test functions written, all FAIL (validators not implemented)
  - **Time**: 25-30 min

- [ ] T008 [P] [US1] Write unit tests for MemoryStore in tests/unit/test_memory_store.py: (1) add_task assigns sequential ID, (2) get_task retrieves by ID, (3) get_task returns None for nonexistent ID
  - **Acceptance**: 3 test functions written, all FAIL (MemoryStore methods not implemented)
  - **Time**: 15-20 min

- [ ] T009 [P] [US1] Write integration tests for add task CLI in tests/integration/test_add_task_flow.py: (1) add task with title only succeeds, (2) add task with empty title shows error, (3) multiple tasks receive sequential IDs
  - **Acceptance**: 3 test functions written, all FAIL (CLI not implemented)
  - **Time**: 20-25 min

**Run tests - ALL SHOULD FAIL**:
```bash
uv run pytest tests/ -v
# Expected: 18 tests fail (no implementation yet)
```

### Implementation for User Story 1

- [ ] T010 [US1] Implement Task dataclass in src/models/task.py with fields (id: int, title: str, completed: bool = False, created_at: datetime), __post_init__ validation for positive ID, non-empty title, title length ≤200
  - **Acceptance**: Contract tests (T006) pass, can create valid Task, invalid Tasks raise ValueError
  - **Time**: 25-30 min

- [ ] T011 [P] [US1] Implement confirm_truncation function in src/cli/validators.py: displays warning with field name and limit, prompts for y/n input, returns bool (accepts 'y'/'yes' case-insensitive)
  - **Acceptance**: Function callable, returns True/False, displays formatted warning message
  - **Time**: 10-15 min

- [ ] T012 [US1] Implement validate_title function in src/cli/validators.py with empty/whitespace check, length validation with confirm_truncation callback, truncation to 200 chars if confirmed
  - **Acceptance**: Unit tests (T007) pass, empty title raises ValidationError, >200 chars prompts user
  - **Time**: 15-20 min

- [ ] T013 [US1] Implement MemoryStore add and get methods in src/storage/memory_store.py: add() assigns sequential ID and stores task, get() retrieves by ID or returns None
  - **Acceptance**: Unit tests (T008) pass, sequential IDs work (1, 2, 3...), get retrieves correct task
  - **Time**: 20-25 min

- [ ] T014 [US1] Implement create_task service in src/services/task_service.py: validates title with validate_title, creates Task with next ID from store, stores task, returns created Task
  - **Acceptance**: Can create task end-to-end, task has ID, validation works, task stored in MemoryStore
  - **Time**: 20-25 min

- [ ] T015 [US1] Implement add_command CLI handler in src/cli/commands.py: setup argparse with title positional argument, call create_task service, display success message with Unicode symbols and task details
  - **Acceptance**: Integration tests (T009) pass, CLI displays "✓ Task created successfully (ID: 1)"
  - **Time**: 20-25 min

- [ ] T016 [US1] Create main CLI entry point in src/cli/main.py: setup ArgumentParser with subcommand routing, wire 'add' subcommand to add_command handler, handle errors with proper exit codes
  - **Acceptance**: Can run `uv run python -m src.cli.main add "Test"`, exit code 0 on success, 1 on error
  - **Time**: 15-20 min

- [ ] T017 [P] [US1] Configure CLI entry point in pyproject.toml under [project.scripts]: add `todo = "src.cli.main:main"` to enable `uv run todo` command
  - **Acceptance**: Can run `uv run todo add "Test"` instead of `python -m src.cli.main`
  - **Time**: 10-15 min

**Run tests - ALL SHOULD PASS**:
```bash
uv run pytest tests/ -v
# Expected: 18 tests pass
```

**Run quality checks**:
```bash
uv run ruff check src/ tests/
uv run mypy src/
```

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Add Task with Description (Priority: P2)

**Goal**: Users can add optional description field to tasks for additional context

**Independent Test**: Add task with title and description → verify both fields stored → view task details

### Tests for User Story 2 (TDD - Write FIRST, ensure FAIL) ⚠️

- [ ] T018 [P] [US2] Write contract test in tests/contract/test_task_model.py: Task with 1001-char description raises ValueError
  - **Acceptance**: 1 test function written, FAILS (description validation not implemented)
  - **Time**: 10-15 min

- [ ] T019 [P] [US2] Write unit tests for description validation in tests/unit/test_validators.py: (1) None returns None, (2) valid input returns unchanged, (3) 1000 chars returns unchanged, (4) 1001 chars prompts and truncates if confirmed, (5) 1001 chars raises if user declines
  - **Acceptance**: 5 test functions written, all FAIL (validate_description not implemented)
  - **Time**: 20-25 min

- [ ] T020 [P] [US2] Write integration tests in tests/integration/test_add_task_flow.py: (1) add task with title and description succeeds, (2) add task with title only (no description) succeeds
  - **Acceptance**: 2 test functions written, FAIL (CLI description support not implemented)
  - **Time**: 15-20 min

**Run tests - NEW TESTS SHOULD FAIL**:
```bash
uv run pytest tests/ -v
# Expected: 8 new US2 tests fail, 18 US1 tests still pass
```

### Implementation for User Story 2

- [ ] T021 [US2] Add description field to Task dataclass in src/models/task.py: description: Optional[str] = None, update __post_init__ to validate description length ≤1000 if provided
  - **Acceptance**: Contract test (T018) passes, Task accepts None or ≤1000 char description
  - **Time**: 15-20 min

- [ ] T022 [US2] Implement validate_description function in src/cli/validators.py: returns None for empty/None input, validates length with confirm_truncation callback, truncates to 1000 chars if confirmed
  - **Acceptance**: Unit tests (T019) pass, None/empty handled, >1000 chars prompts user
  - **Time**: 15-20 min

- [ ] T023 [US2] Update create_task service in src/services/task_service.py to accept description parameter, validate with validate_description, pass to Task creation
  - **Acceptance**: Can create task with description, description stored correctly
  - **Time**: 10-15 min

- [ ] T024 [US2] Add description argument to CLI in src/cli/commands.py: add --description/-d optional argument to argparse, pass to create_task, update success message to show description
  - **Acceptance**: Integration tests (T020) pass, `todo add "title" -d "desc"` works, output shows description
  - **Time**: 15-20 min

**Run tests - ALL SHOULD PASS**:
```bash
uv run pytest tests/ -v
# Expected: All 26 tests pass (18 US1 + 8 US2)
```

**Run quality checks**:
```bash
uv run ruff check src/ tests/
uv run mypy src/
```

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T025 [P] Create README.md with project overview, features list, installation instructions (`uv pip install -e .`), and basic usage section
  - **Acceptance**: README has all sections, installation steps are accurate, links work
  - **Time**: 20-25 min

- [ ] T026 [P] Add example usage with terminal output to README.md: show actual command execution with output for add task (title only), add task (with description), error cases
  - **Acceptance**: README shows formatted code blocks with actual CLI output (✓ success, ✗ error messages)
  - **Time**: 20-25 min

- [ ] T027 [P] Create CONTRIBUTING.md or DEVELOPMENT.md with TDD workflow (Red-Green-Refactor), commit message conventions (feat/fix/test), code quality requirements, and testing guidelines
  - **Acceptance**: Document explains TDD cycle, commit format, how to run tests/linters
  - **Time**: 15-20 min

- [ ] T028 [P] Add comprehensive docstrings to all public functions in src/: Task class, validators, MemoryStore, task_service, CLI functions using Google-style docstrings
  - **Acceptance**: All public functions have docstrings with Args, Returns, Raises sections
  - **Time**: 20-25 min

- [ ] T029 Run full test suite with coverage `uv run pytest --cov=src --cov-report=term-missing --cov-report=html`, verify coverage >90%, fix any gaps
  - **Acceptance**: Coverage report shows >90% for all modules, htmlcov/ directory generated
  - **Time**: 15-20 min

- [ ] T030 [P] Create .gitignore with Python standard ignores (__pycache__/, .pytest_cache/, .mypy_cache/, .coverage, htmlcov/, *.pyc, .venv/, dist/, *.egg-info/), run final quality check `uv run ruff check && uv run mypy src/`
  - **Acceptance**: .gitignore complete, all quality checks pass, ready to commit
  - **Time**: 15-20 min

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2)
- **Polish (Phase 5)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Extends US1 but is independently testable

### Within Each User Story

- Tests (TDD) MUST be written and FAIL before implementation
- Contract tests before models
- Unit tests before services/validators
- Integration tests before CLI commands
- All tests passing before moving to next priority

### Parallel Opportunities

- **Setup**: T003 can run parallel with T001-T002
- **Foundational**: T004 and T005 can run in parallel
- **US1 Tests**: T006, T007, T008, T009 can all be written in parallel (4 test files)
- **US1 Implementation**: T011 and T017 can run parallel with main implementation flow
- **US2 Tests**: T018, T019, T020 can all be written in parallel (3 test files)
- **US1 and US2**: After Foundational, entire US1 and US2 can be developed in parallel by different developers
- **Polish**: T025, T026, T027, T028, T030 can all run in parallel (5 documentation tasks)

**Total Parallelizable**: 19 of 30 tasks (63%)

---

## Parallel Execution Examples

### Setup Phase
```bash
# After T001-T002, run configuration in parallel:
Developer A: T003 (configure tools)
# Both complete, proceed to Foundation
```

### User Story 1 - Tests
```bash
# All test writing can happen simultaneously:
Developer A: T006 (contract tests)
Developer B: T007 (validator tests)
Developer C: T008 (storage tests)
Developer D: T009 (integration tests)
# Result: 18 tests written in parallel timeframe
```

### User Story 1 & 2 - Full Parallel
```bash
# After Foundation complete:
Team A: T006-T017 (complete User Story 1)
Team B: T018-T024 (complete User Story 2)
# Both teams work independently, merge at end
```

### Polish Phase
```bash
# All documentation in parallel:
Developer A: T025 (README)
Developer B: T026 (examples)
Developer C: T027 (CONTRIBUTING)
Developer D: T028 (docstrings)
Developer E: T030 (.gitignore + quality)
# Developer F: T029 (coverage - depends on T028)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T003) → ~1 hour
2. Complete Phase 2: Foundational (T004-T005) → ~30 minutes
3. Complete Phase 3: User Story 1 (T006-T017)
   - Write all tests first (T006-T009) → ~1.5 hours
   - Verify tests FAIL → checkpoint
   - Implement code (T010-T017) → ~2.5 hours
   - Verify tests PASS → checkpoint
4. **STOP and VALIDATE**: Test User Story 1 independently
   ```bash
   uv run pytest tests/ -v  # 18 tests pass
   uv run todo add "Buy groceries"  # Works!
   ```
5. Deploy/demo if ready (MVP complete!)

**Total MVP time**: ~5.5 hours (single developer, sequential)

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready (~1.5 hours)
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!) (~4 hours)
   - Users can add tasks with title
   - Tasks get unique IDs
   - Validation works (empty title rejected)
   - Truncation prompts for >200 char titles
3. Add User Story 2 → Test independently → Deploy/Demo (~1.5 hours)
   - Users can now add descriptions
   - Truncation prompts for >1000 char descriptions
4. Polish → Final release (~2 hours)

**Total feature time**: ~9 hours (single developer, sequential)

### Parallel Team Strategy (Fastest)

With 2 developers:

1. Team completes Setup + Foundational together (T001-T005) → ~1.5 hours
2. Once Foundational is done:
   - **Developer A**: User Story 1 (T006-T017) → ~4 hours
   - **Developer B**: User Story 2 (T018-T024) → ~1.5 hours
     - Dev B helps Dev A after completing US2
3. Team completes Polish together (T025-T030) → ~1.5 hours

**Total parallel time**: ~5.5 hours (with 2 developers)

---

## Task Breakdown by Type

### Test Tasks (TDD)
- **Total**: 8 tasks (T006-T009, T018-T020, T029)
- **Coverage**: Contract (2), Unit (3), Integration (2), Coverage verification (1)
- **Time**: ~2.5 hours total

### Implementation Tasks
- **Total**: 14 tasks (T010-T017, T021-T024)
- **Coverage**: Models (2), Validators (3), Storage (1), Services (2), CLI (3), Config (1), Entry point (1), Description support (1)
- **Time**: ~4 hours total

### Setup/Infrastructure Tasks
- **Total**: 8 tasks (T001-T005, T025-T027, T030)
- **Coverage**: Project init (3), Foundation (2), Documentation (4)
- **Time**: ~2.5 hours total

### Grand Total: 30 tasks (~9 hours single developer, ~5.5 hours with team)

---

## Testing Commands Reference

```bash
# Run all tests
uv run pytest

# Run specific test suite
uv run pytest tests/contract/         # Contract tests only
uv run pytest tests/integration/      # Integration tests only
uv run pytest tests/unit/             # Unit tests only

# Run with coverage
uv run pytest --cov=src --cov-report=term-missing --cov-report=html

# Run specific test file
uv run pytest tests/contract/test_task_model.py -v

# Run specific test
uv run pytest tests/contract/test_task_model.py::test_task_creation_with_all_fields -v

# Run with verbose output
uv run pytest -vv

# Run with print statements visible
uv run pytest -s

# Code quality checks
uv run ruff check src/ tests/        # Linting
uv run ruff check --fix src/ tests/  # Auto-fix
uv run mypy src/                     # Type checking

# Combined quality check
uv run ruff check src/ tests/ && uv run mypy src/
```

---

## Manual Testing Examples

```bash
# Test basic task creation
uv run todo add "Buy groceries"
# Expected: ✓ Task created successfully (ID: 1)

# Test with description
uv run todo add "Plan meeting" -d "Prepare agenda and invite team"
# Expected: ✓ Task created successfully (ID: 2)
#           Description: Prepare agenda and invite team

# Test empty title (should fail)
uv run todo add ""
# Expected: ✗ Error: Title cannot be empty

# Test title truncation (201 chars)
uv run todo add "$(python -c 'print("x" * 201)')"
# Expected: ⚠️  Warning: Title exceeds 200 character limit...
#           Continue? (y/n):
```

---

## Success Metrics

### MVP (User Story 1) Complete When:
- [ ] All US1 tests passing (18 tests: 6 contract + 9 unit + 3 integration)
- [ ] Can add task with title via `uv run todo add "Task"`
- [ ] Task receives unique sequential ID (1, 2, 3...)
- [ ] Empty title rejected with error: "✗ Error: Title cannot be empty"
- [ ] >200 char title prompts for confirmation with truncation
- [ ] All code passes ruff and mypy checks (strict mode)
- [ ] Test coverage >90% for all modules
- [ ] CLI entry point configured (`todo` command works)

### Full Feature (User Story 1 + 2) Complete When:
- [ ] All tests passing (26 tests: 18 US1 + 8 US2)
- [ ] Can add task with title and description via `todo add "title" -d "desc"`
- [ ] Can add task with title only (description optional)
- [ ] >1000 char description prompts for confirmation with truncation
- [ ] All acceptance scenarios from spec.md verified manually
- [ ] All code passes quality checks (ruff, mypy strict)
- [ ] README with installation, usage, and examples complete
- [ ] CONTRIBUTING/DEVELOPMENT docs explain TDD workflow
- [ ] All public functions have comprehensive docstrings
- [ ] Test coverage >90% confirmed with HTML report

---

## Notes

- **[P] tasks** = Different files, no dependencies - can run in parallel
- **[Story] label** = Maps task to specific user story for traceability
- **Each task is atomic** = Does ONE thing with ONE clear acceptance criterion
- **Each task is 15-30 minutes** = Right-sized for tracking and review
- **TDD CRITICAL**: Verify tests fail before implementing (Red), then make them pass (Green), then refactor
- **Commit frequently**: After each task or logical group (e.g., after all tests for a component pass)
- **Stop at checkpoints**: Validate story independently before moving to next
- **Run quality checks**: `uv run ruff check && uv run mypy src/` after each implementation task
- **Avoid**: Vague tasks, same-file conflicts, cross-story dependencies that break independence

---

## Review Checklist (Before Starting Implementation)

- [ ] Each task has clear acceptance criterion
- [ ] Each task is 15-30 minutes (verified by time estimates)
- [ ] Each task can be reviewed independently
- [ ] Test tasks explicitly state "write FIRST, ensure FAIL"
- [ ] Implementation tasks reference which tests they satisfy
- [ ] Parallel opportunities clearly marked with [P]
- [ ] Story labels correctly map tasks to user stories
- [ ] File paths included in all implementation tasks
- [ ] Dependencies between tasks are clear
- [ ] Success metrics are measurable and specific
