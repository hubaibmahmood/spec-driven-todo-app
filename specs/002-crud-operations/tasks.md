# Implementation Tasks: Interactive Todo Menu with CRUD Operations

**Feature**: 002-crud-operations
**Branch**: `002-crud-operations`
**Status**: Ready for Implementation
**TDD Required**: Yes (per constitution)

## Task Organization

Tasks are organized by user story to enable independent implementation and testing. Each phase represents a complete, independently testable increment.

**Task Format**: `- [ ] [TaskID] [P] [Story] Description with file path`
- `[P]` = Parallelizable (different files, no dependencies)
- `[Story]` = User story label (US1, US2, US3, US4, US5)

---

## Phase 1: Foundational Infrastructure

**Goal**: Extend MemoryStore with CRUD methods needed by all user stories.

**Why Foundational**: All user stories (US1-US5) depend on MemoryStore having get_all(), update_task(), delete_task(), and task_exists() methods. Must complete before any user story implementation.

**Independent Test Criteria**: Run `uv run pytest tests/unit/test_memory_store.py -v` and verify all 4 new methods pass their tests (get_all, update_task, delete_task, task_exists).

### Storage Layer Tests

- [X] T001 [P] Write test for MemoryStore.get_all() with empty store in tests/unit/test_memory_store.py
- [X] T002 [P] Write test for MemoryStore.get_all() returning multiple tasks in tests/unit/test_memory_store.py
- [X] T003 [P] Write test for MemoryStore.update_task() success case in tests/unit/test_memory_store.py
- [X] T004 [P] Write test for MemoryStore.update_task() with non-existent ID in tests/unit/test_memory_store.py
- [X] T005 [P] Write test for MemoryStore.delete_task() success case in tests/unit/test_memory_store.py
- [X] T006 [P] Write test for MemoryStore.delete_task() with non-existent ID in tests/unit/test_memory_store.py
- [X] T007 [P] Write test for MemoryStore.task_exists() returning True in tests/unit/test_memory_store.py
- [X] T008 [P] Write test for MemoryStore.task_exists() returning False in tests/unit/test_memory_store.py

### Storage Layer Implementation

- [X] T009 Implement MemoryStore.get_all() method in src/storage/memory_store.py
- [X] T010 Implement MemoryStore.update_task() method in src/storage/memory_store.py
- [X] T011 Implement MemoryStore.delete_task() method in src/storage/memory_store.py
- [X] T012 Implement MemoryStore.task_exists() method in src/storage/memory_store.py

**Acceptance**: All tests T001-T008 pass; MemoryStore has 4 new working methods.

---

## Phase 2: User Story 1 - View All Tasks (P1)

**Story Goal**: Users can view all tasks with ID, title, status, and first 50 characters of description.

**Why P1**: Fundamental visibility - users need to see tasks before interacting with them.

**Independent Test Criteria**:
1. Add 3 tasks with different statuses
2. Select "View Tasks" option
3. Verify all 3 tasks appear with correct formatting
4. Verify empty list shows "No tasks found"

### US1: Validator Tests

- [ ] T013 [P] [US1] Write test for parse_task_ids() with single ID "5" in tests/unit/test_validators.py
- [ ] T014 [P] [US1] Write test for parse_task_ids() with comma-separated "1,2,3" in tests/unit/test_validators.py
- [ ] T015 [P] [US1] Write test for parse_task_ids() with whitespace "1, 2, 3" in tests/unit/test_validators.py
- [ ] T016 [P] [US1] Write test for parse_task_ids() with duplicates "1,1,2" in tests/unit/test_validators.py
- [ ] T017 [P] [US1] Write test for parse_task_ids() raising ValueError for "1,abc,3" in tests/unit/test_validators.py
- [ ] T018 [P] [US1] Write test for parse_task_ids() raising ValueError for empty string in tests/unit/test_validators.py

### US1: Validator Implementation

- [X] T019 [US1] Implement parse_task_ids() function in src/cli/validators.py

**Acceptance**: All validator tests T013-T018 pass.

### US1: View Command Tests

- [ ] T020 [P] [US1] Write test for view_tasks_command() with empty store in tests/unit/test_commands.py
- [ ] T021 [P] [US1] Write test for view_tasks_command() with 3 tasks showing correct format in tests/unit/test_commands.py
- [ ] T022 [P] [US1] Write test for view_tasks_command() with completed and incomplete tasks in tests/unit/test_commands.py
- [ ] T023 [P] [US1] Write test for view_tasks_command() with description > 50 chars showing truncation in tests/unit/test_commands.py

### US1: View Command Implementation

- [X] T024 [US1] Implement view_tasks_command() function in src/cli/commands.py

**Acceptance**: All view command tests T020-T023 pass.

### US1: Integration Test

- [ ] T025 [US1] Write integration test for view tasks flow in tests/integration/test_view_tasks_flow.py
- [ ] T026 [US1] Run integration test and verify end-to-end view functionality

**Story 1 Complete**: Users can view tasks; empty list handled; truncation works.

---

## Phase 3: User Story 2 - Mark Task as Complete (P1)

**Story Goal**: Users can mark tasks as complete by ID and see status change.

**Why P1**: Core functionality - provides progress tracking and sense of accomplishment.

**Independent Test Criteria**:
1. Add incomplete task
2. Mark it complete by ID
3. View task list and verify [✓] status indicator
4. Attempt to mark already-complete task (idempotent)

### US2: Mark Complete Command Tests

- [ ] T027 [P] [US2] Write test for mark_complete_command() successfully marking task in tests/unit/test_commands.py
- [ ] T028 [P] [US2] Write test for mark_complete_command() with non-existent ID in tests/unit/test_commands.py
- [ ] T029 [P] [US2] Write test for mark_complete_command() with non-numeric input in tests/unit/test_commands.py
- [ ] T030 [P] [US2] Write test for mark_complete_command() with already-complete task (idempotent) in tests/unit/test_commands.py

### US2: Mark Complete Implementation

- [X] T031 [US2] Implement mark_complete_command() function in src/cli/commands.py

**Acceptance**: All mark complete tests T027-T030 pass.

### US2: Integration Test

- [ ] T032 [US2] Write integration test for mark complete flow in tests/integration/test_mark_complete_flow.py
- [ ] T033 [US2] Run integration test and verify status change is visible in view

**Story 2 Complete**: Users can mark tasks complete; idempotent behavior works.

---

## Phase 4: User Story 5 - Interactive Menu Loop (P1)

**Story Goal**: Users see menu after each operation and can perform multiple actions in one session.

**Why P1**: Core interface paradigm - without it, app is impractical.

**Why After US1 & US2**: Menu needs at least 2 operations to test (view and mark complete). Implementing menu now enables testing remaining stories through interactive workflow.

**Independent Test Criteria**:
1. Launch app and see menu
2. Perform action (view or mark complete)
3. Verify menu reappears
4. Perform another action
5. Select quit and verify graceful exit

### US5: Menu Loop Tests

- [ ] T034 [P] [US5] Write test for run_interactive_menu() displaying menu on start in tests/integration/test_menu_loop_flow.py
- [ ] T035 [P] [US5] Write test for run_interactive_menu() with view then quit in tests/integration/test_menu_loop_flow.py
- [ ] T036 [P] [US5] Write test for run_interactive_menu() with multiple operations then quit in tests/integration/test_menu_loop_flow.py
- [ ] T037 [P] [US5] Write test for run_interactive_menu() with invalid option showing error in tests/integration/test_menu_loop_flow.py

### US5: Menu Loop Implementation

- [X] T038 [US5] Implement run_interactive_menu() function in src/cli/main.py
- [X] T039 [US5] Update main() entry point to call run_interactive_menu() in src/cli/main.py

**Acceptance**: All menu tests T034-T037 pass; menu loops until quit.

**Story 5 Complete**: Menu works; operations loop; invalid selections handled; quit exits.

---

## Phase 5: User Story 3 - Delete Single or Multiple Tasks (P2)

**Story Goal**: Users can delete tasks by single ID or comma-separated IDs.

**Why P2**: Important but not MVP - users can work around by ignoring tasks.

**Independent Test Criteria**:
1. Add 5 tasks
2. Delete single task by ID
3. Verify only that task removed
4. Delete multiple tasks "1,3,5"
5. Verify all 3 removed and confirmation shown

### US3: Delete Command Tests

- [ ] T040 [P] [US3] Write test for delete_tasks_command() deleting single task in tests/unit/test_commands.py
- [ ] T041 [P] [US3] Write test for delete_tasks_command() deleting multiple tasks "1,3,5" in tests/unit/test_commands.py
- [ ] T042 [P] [US3] Write test for delete_tasks_command() with partial success (some IDs invalid) in tests/unit/test_commands.py
- [ ] T043 [P] [US3] Write test for delete_tasks_command() with all IDs non-existent in tests/unit/test_commands.py
- [ ] T044 [P] [US3] Write test for delete_tasks_command() with non-numeric input in tests/unit/test_commands.py

### US3: Delete Implementation

- [X] T045 [US3] Implement delete_tasks_command() function in src/cli/commands.py

**Acceptance**: All delete tests T040-T044 pass.

### US3: Integration Test

- [ ] T046 [US3] Write integration test for delete tasks flow (single and multiple) in tests/integration/test_delete_tasks_flow.py
- [ ] T047 [US3] Run integration test and verify deletions work correctly

**Story 3 Complete**: Users can delete single/multiple tasks; partial success handled.

---

## Phase 6: User Story 4 - Update Task Description (P3)

**Story Goal**: Users can update task descriptions by ID.

**Why P3**: Convenience feature - users can work around by delete/recreate.

**Independent Test Criteria**:
1. Add task with description
2. Update description by ID
3. Verify new description shows in view (first 50 chars)
4. Verify title and ID unchanged

### US4: Update Command Tests

- [ ] T048 [P] [US4] Write test for update_task_command() updating description successfully in tests/unit/test_commands.py
- [ ] T049 [P] [US4] Write test for update_task_command() with non-existent ID in tests/unit/test_commands.py
- [ ] T050 [P] [US4] Write test for update_task_command() with non-numeric input in tests/unit/test_commands.py
- [ ] T051 [P] [US4] Write test for update_task_command() clearing description (empty input) in tests/unit/test_commands.py
- [ ] T052 [P] [US4] Write test for update_task_command() with description > 1000 chars (truncation) in tests/unit/test_commands.py

### US4: Update Implementation

- [X] T053 [US4] Implement update_task_command() function in src/cli/commands.py

**Acceptance**: All update tests T048-T052 pass.

### US4: Integration Test

- [ ] T054 [US4] Write integration test for update task flow in tests/integration/test_update_task_flow.py
- [ ] T055 [US4] Run integration test and verify description updates correctly

**Story 4 Complete**: Users can update descriptions; validation works; title immutable.

---

## Phase 7: Polish & Verification

**Goal**: Ensure all user stories work together and quality gates pass.

### Cross-Story Integration

- [ ] T056 Write end-to-end test exercising all 5 operations in sequence in tests/integration/test_menu_loop_flow.py
- [ ] T057 Run all tests with `uv run pytest` and verify 100% pass rate

### Code Quality

- [ ] T058 Run ruff linter with `uv run ruff check src/ tests/` and fix any issues
- [ ] T059 Run mypy type checker with `uv run mypy src/` and fix any type errors
- [ ] T060 Verify all functions have type hints per constitution

**Acceptance**: All tests pass; no linter errors; no type errors; constitution compliance verified.

---

## Task Summary

**Total Tasks**: 60
**Parallelizable**: 43 tasks marked with [P]

**Tasks by User Story**:
- Foundational: 12 tasks (T001-T012)
- US1 (View Tasks): 14 tasks (T013-T026)
- US2 (Mark Complete): 7 tasks (T027-T033)
- US5 (Menu Loop): 6 tasks (T034-T039)
- US3 (Delete Tasks): 8 tasks (T040-T047)
- US4 (Update Tasks): 8 tasks (T048-T055)
- Polish: 5 tasks (T056-T060)

**Estimated Time**: 60 tasks × 15-30 min = 15-30 hours total

---

## Dependencies & Execution Order

### Story Dependencies

```
Foundational (T001-T012)
    ↓
US1: View Tasks (T013-T026) ────┐
    ↓                           │
US2: Mark Complete (T027-T033)  │
    ↓                           │
US5: Menu Loop (T034-T039) ─────┘
    ↓
US3: Delete Tasks (T040-T047) [Independent]
    ↓
US4: Update Tasks (T048-T055) [Independent]
    ↓
Polish (T056-T060)
```

**Critical Path**: Foundational → US1 → US2 → US5 → Polish

**Independent Stories**: US3 and US4 can be implemented in any order after US5.

### Parallel Execution Opportunities

**Within Foundational Phase**:
- All 8 test tasks (T001-T008) can run in parallel (different test methods)
- Implementation tasks (T009-T012) must run sequentially (modifying same file)

**Within US1**:
- All 6 validator tests (T013-T018) can run in parallel
- All 4 view command tests (T020-T023) can run in parallel

**Within US2**:
- All 4 mark complete tests (T027-T030) can run in parallel

**Within US5**:
- All 4 menu loop tests (T034-T037) can run in parallel

**Within US3**:
- All 5 delete tests (T040-T044) can run in parallel

**Within US4**:
- All 5 update tests (T048-T052) can run in parallel

**Example Parallel Batch**:
- Batch 1: T001, T002, T003, T004, T005, T006, T007, T008 (8 storage tests)
- Batch 2: T013, T014, T015, T016, T017, T018 (6 validator tests)
- Batch 3: T020, T021, T022, T023 (4 view tests)

---

## Implementation Strategy

### MVP Scope (Minimum Viable Product)

**Phase 1 + Phase 2 + Phase 3 + Phase 4 = MVP**
- Foundational infrastructure (T001-T012)
- View tasks (T013-T026)
- Mark complete (T027-T033)
- Interactive menu (T034-T039)

**MVP Delivers**: Users can view tasks, mark them complete, and use interactive menu loop. This satisfies all P1 user stories.

**Time Estimate**: ~12 hours (40 tasks × 15-30 min average)

### Incremental Delivery

1. **Week 1**: Foundational + US1 (View) → Users can see tasks
2. **Week 2**: US2 (Mark Complete) + US5 (Menu) → Full interactive experience with 2 operations
3. **Week 3**: US3 (Delete) → Task cleanup capability
4. **Week 4**: US4 (Update) + Polish → Full CRUD + quality verification

### Testing Strategy

**TDD Workflow** (per constitution):
1. Write test (Red)
2. Implement minimal code to pass (Green)
3. Refactor while keeping tests green
4. Commit only when tests pass

**Test Execution**:
- Run unit tests after each implementation task
- Run integration tests after completing each story phase
- Run full test suite before story completion sign-off

---

## File Modification Summary

### Files to Modify (3):
- `src/storage/memory_store.py` - Add 4 methods (T009-T012)
- `src/cli/validators.py` - Add 1 function (T019)
- `src/cli/main.py` - Replace main loop (T038-T039)

### Files to Create (7):
- `src/cli/commands.py` - Add 4 command functions (T024, T031, T045, T053)
- `tests/unit/test_commands.py` - New test file (T020-T023, T027-T030, T040-T044, T048-T052)
- `tests/integration/test_view_tasks_flow.py` - New test file (T025-T026)
- `tests/integration/test_mark_complete_flow.py` - New test file (T032-T033)
- `tests/integration/test_menu_loop_flow.py` - New test file (T034-T037, T056)
- `tests/integration/test_delete_tasks_flow.py` - New test file (T046-T047)
- `tests/integration/test_update_task_flow.py` - New test file (T054-T055)

### Files to Extend (2):
- `tests/unit/test_memory_store.py` - Add tests for 4 new methods (T001-T008)
- `tests/unit/test_validators.py` - Add tests for parse_task_ids (T013-T018)

**Total**: 3 modified, 7 created, 2 extended = 12 files touched

---

## Quality Gates

Before marking each phase complete, verify:

✅ All tests in phase pass
✅ No ruff linting errors
✅ No mypy type errors
✅ All functions have type hints
✅ Story's independent test criteria met
✅ Code follows PEP 8 style guidelines

---

## Notes

- Each task is atomic (one acceptance criterion)
- Each task is sized for 15-30 minutes
- Tasks can be reviewed independently
- TDD is mandatory (tests before implementation)
- Constitution compliance verified throughout
