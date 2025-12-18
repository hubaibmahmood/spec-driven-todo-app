# Tasks: MCP Server Integration

**Input**: Design documents from `/specs/006-mcp-server-integration/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are included as this is a critical integration feature requiring TDD approach.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

**Revision**: Task sizing optimized (15-30 min target), micro-tasks combined, critical missing tasks added.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

This project uses **microservices architecture**:
- **MCP Server**: `mcp-server/src/`, `mcp-server/tests/`
- **Backend**: `backend/src/`, `backend/tests/`
- **Frontend**: `frontend/src/` (no changes for this feature)
- **Auth Server**: `auth-server/src/` (no changes for this feature)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize MCP server project structure and dependencies

- [X] T001 Initialize MCP server project structure (15 min)
  - Create mcp-server/ directory at repository root
  - Run `uv init --package .` in mcp-server/
  - Create src/ subdirectories (tools/, schemas/)
  - Create tests/ subdirectories (contract/, unit/, integration/)

- [X] T002 Configure MCP server dependencies (20 min)
  - Update mcp-server/pyproject.toml with project metadata
  - Add runtime dependencies (fastmcp>=0.1.0, httpx>=0.25.0, pydantic>=2.0.0, pydantic-settings>=2.0.0, python-dotenv>=1.0.0, tenacity>=8.0.0)
  - Add dev dependencies (pytest>=7.4.0, pytest-asyncio>=0.23.0, pytest-cov>=4.1.0, pytest-mock>=3.12.0, ruff>=0.1.0, mypy>=1.7.0)
  - Run `uv sync` to install all dependencies

- [X] T003 [P] Create environment configuration and documentation (20 min)
  - Create mcp-server/.env.example with SERVICE_AUTH_TOKEN, FASTAPI_BASE_URL, MCP_LOG_LEVEL, MCP_SERVER_PORT
  - Create mcp-server/README.md with setup instructions, architecture overview, and basic usage

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Implement Settings configuration class in mcp-server/src/config.py (20 min)
  - Use pydantic-settings BaseSettings
  - Add required fields: service_auth_token, fastapi_base_url
  - Add optional fields with defaults: mcp_log_level="INFO", mcp_server_port=3000, backend_timeout=30.0, backend_max_retries=2
  - Configure .env file loading

- [X] T005 [P] Create PriorityLevel enum and TaskResponse schema in mcp-server/src/schemas/task.py (20 min)
  - PriorityLevel enum (Low, Medium, High, Urgent)
  - TaskResponse with all fields (id, title, description, completed, priority, due_date, created_at, updated_at, user_id)
  - Pydantic Field descriptions for AI understanding

- [X] T006 [P] Create all tool parameter schemas in mcp-server/src/schemas/task.py (20 min)
  - CreateTaskParams (title required, description/priority/due_date optional)
  - UpdateTaskParams (task_id required, all update fields optional except completion)
  - DeleteTaskParams (task_id required)
  - MarkTaskCompletedParams (task_id required)

- [X] T007 [P] Create error response schemas in mcp-server/src/schemas/task.py (15 min)
  - ErrorResponse (error_type, message, details, suggestions)
  - ValidationErrorDetail (field, message, received_value, suggestion)
  - Define ERROR_TYPES taxonomy (authentication_error, authorization_error, not_found_error, validation_error, backend_error, timeout_error, connection_error)

- [X] T008 Implement BackendClient class with retry logic in mcp-server/src/client.py (30 min)
  - Initialize httpx.AsyncClient with base_url and timeout
  - Implement _build_headers method (Authorization: Bearer token, X-User-ID, Content-Type)
  - Implement _request method with tenacity retry (30s timeout, 2 retries, exponential backoff 1s→2s)
  - Add structured logging (INFO level) with timestamp, endpoint, method, status_code, user_id, duration_ms
  - Handle TimeoutException and ConnectError

- [X] T009 Generate and configure SERVICE_AUTH_TOKEN (10 min)
  - Generate 32+ character random token using secure method
  - Add to mcp-server/.env as SERVICE_AUTH_TOKEN=<token>
  - Add to backend/.env as SERVICE_AUTH_TOKEN=<token>
  - Verify .env.example files document this requirement

- [X] T010 Implement backend dual authentication support (45 min)
  - Add service_auth_token field to backend/src/config.py Settings class
  - Implement get_service_auth dependency in backend/src/api/dependencies.py (validate Bearer token, validate X-User-ID header, return user_id)
  - Implement get_current_user_or_service dependency in backend/src/api/dependencies.py (if X-User-ID present: service flow, else: user session flow)
  - Update all task endpoints in backend/src/api/routers/tasks.py to use Depends(get_current_user_or_service)

- [X] T011 [P] Create pytest fixtures in mcp-server/tests/conftest.py (15 min)
  - mock_backend_client fixture (AsyncMock for BackendClient)
  - test_user_id fixture (returns "test_user_123")
  - mock_httpx_client fixture (mocked httpx.AsyncClient)

- [X] T012 [P] Create backend auth test fixtures in backend/tests/conftest.py (15 min)
  - mock_service_token fixture (returns valid SERVICE_AUTH_TOKEN)
  - test_service_auth_headers fixture (returns dict with Authorization and X-User-ID)
  - test_user_context fixture (creates test user data)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - AI Assistant Task Retrieval (Priority: P1) 🎯 MVP

**Goal**: AI assistant can retrieve all tasks for authenticated user via list_tasks tool

**Independent Test**: Ask AI assistant "show me my tasks" and verify it returns authenticated user's task list without accessing other users' data

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T013 [P] [US1] Contract test for TaskResponse schema in mcp-server/tests/contract/test_task_schemas.py (15 min)
  - Validate TaskResponse accepts all required fields
  - Validate PriorityLevel enum values
  - Test field validation (e.g., title max length)

- [X] T014 [P] [US1] Unit test for BackendClient.get_tasks in mcp-server/tests/unit/test_client.py (20 min)
  - Test headers include Authorization and X-User-ID
  - Test retry logic on failure
  - Test timeout handling
  - Mock httpx.AsyncClient response

- [X] T015 [P] [US1] Integration test suite for list_tasks in mcp-server/tests/integration/test_list_tasks.py (25 min)
  - Test valid auth returns user's tasks
  - Test invalid service token returns 401
  - Test missing X-User-ID returns 400
  - Test empty task list scenario
  - Test multiple tasks returned correctly

- [X] T016 [P] [US1] Backend integration test for service auth in backend/tests/integration/test_service_auth.py (20 min)
  - Test GET /tasks with valid service token + X-User-ID returns 200
  - Test GET /tasks with invalid service token returns 401
  - Test GET /tasks with missing X-User-ID returns 400
  - Verify user data isolation

### Implementation for User Story 1

- [X] T017 [US1] Implement list_tasks tool with complete error handling (25 min)
  - Implement BackendClient.get_tasks method in mcp-server/src/client.py (GET /tasks endpoint)
  - Create list_tasks tool handler in mcp-server/src/tools/list_tasks.py with FastMCP @tool decorator
  - Extract user_id from MCP session metadata
  - Translate backend errors to AI-friendly messages (401→authentication_error, 500→backend_error, timeout→timeout_error, connection→connection_error)
  - Add logging for list_tasks operations

**Checkpoint**: User Story 1 functional - AI can retrieve tasks for authenticated users

---

## Phase 4: User Story 2 - AI Assistant Task Creation (Priority: P1) 🎯 MVP

**Goal**: AI assistant can create tasks for authenticated user via create_task tool

**Independent Test**: Ask AI assistant "add 'buy milk' to my todo list" and verify task appears in user's task list with correct ownership

### Tests for User Story 2

- [X] T018 [P] [US2] Contract tests for CreateTaskParams in mcp-server/tests/contract/test_task_schemas.py (20 min)
  - Test title required validation
  - Test title min/max length
  - Test optional fields (description, priority, due_date)
  - Test empty title rejected
  - Test invalid priority rejected
  - Test invalid due_date format rejected

- [X] T019 [P] [US2] Unit test for BackendClient.create_task in mcp-server/tests/unit/test_client.py (20 min)
  - Test POST /tasks with correct payload
  - Test headers include auth and user context
  - Test JSON body structure
  - Test retry on failure

- [X] T020 [P] [US2] Integration test suite for create_task in mcp-server/tests/integration/test_create_task.py (25 min)
  - Test create with title only (defaults applied)
  - Test create with all fields
  - Test validation errors (empty title, invalid due_date format)
  - Test created task returned with ID and timestamps
  - Test task appears in subsequent list_tasks call

- [X] T021 [P] [US2] Backend integration test for POST /tasks in backend/tests/integration/test_service_auth.py (15 min)
  - Test POST /tasks with service auth returns 201
  - Test created task assigned to correct user_id
  - Verify task persisted in database

### Implementation for User Story 2

- [X] T022 [US2] Implement create_task tool with validation and error handling (30 min)
  - Implement BackendClient.create_task method in mcp-server/src/client.py (POST /tasks with JSON body)
  - Create create_task tool handler in mcp-server/src/tools/create_task.py with CreateTaskParams
  - Pydantic parameter validation with field-level error messages
  - Translate 422 validation errors to AI-friendly format (field-level details per FR-026)
  - Add logging for create_task operations

**Checkpoint**: User Stories 1 AND 2 both work - AI can list and create tasks independently (MVP delivered!)

---

## Phase 5: User Story 5 - AI Assistant Mark Task Completed (Priority: P2)

**Goal**: AI assistant can mark tasks as completed via dedicated mark_task_completed tool

**Independent Test**: Create task via AI, then ask "mark task X as complete" and verify completed status changes to true

### Tests for User Story 5

- [ ] T023 [P] [US5] Contract test for MarkTaskCompletedParams in mcp-server/tests/contract/test_task_schemas.py (15 min)
  - Test task_id required
  - Test task_id must be positive integer

- [ ] T024 [P] [US5] Unit test for BackendClient.mark_task_completed in mcp-server/tests/unit/test_client.py (15 min)
  - Test PATCH /tasks/{id} with {"completed": true} payload
  - Test correct endpoint path construction

- [ ] T025 [P] [US5] Integration test suite for mark_task_completed in mcp-server/tests/integration/test_mark_completed.py (25 min)
  - Test marking incomplete task → completed=true
  - Test idempotency (already completed task remains completed)
  - Test non-existent task returns 404
  - Test task owned by another user returns 403
  - Test updated task returned with new updated_at timestamp

- [ ] T026 [P] [US5] Backend integration test for PATCH /tasks/{id} in backend/tests/integration/test_service_auth.py (15 min)
  - Test PATCH with service auth updates completion status
  - Test authorization check (user can only mark own tasks)

### Implementation for User Story 5

- [X] T027 [US5] Implement mark_task_completed tool with error handling (25 min)
  - Implement BackendClient.mark_task_completed method in mcp-server/src/client.py (PATCH /tasks/{id} with {"completed": true})
  - Create mark_task_completed tool handler in mcp-server/src/tools/mark_completed.py with MarkTaskCompletedParams
  - Translate errors (404→not_found_error, 403→authorization_error) to AI-friendly messages
  - Add logging for mark_task_completed operations

**Checkpoint**: AI can now list, create, and mark tasks complete - core task management workflow functional

---

## Phase 6: User Story 3 - AI Assistant Task Updates (Priority: P2)

**Goal**: AI assistant can update task fields (title, description, priority, due_date) via update_task tool

**Independent Test**: Create task via AI, then ask "change task X description to Y" and verify field updates

### Tests for User Story 3

- [ ] T028 [P] [US3] Contract test for UpdateTaskParams in mcp-server/tests/contract/test_task_schemas.py (15 min)
  - Test task_id required
  - Test all update fields optional (title, description, priority, due_date)
  - Test completion field NOT present (handled by mark_task_completed)
  - Test partial update validation

- [ ] T029 [P] [US3] Unit test for BackendClient.update_task in mcp-server/tests/unit/test_client.py (15 min)
  - Test PUT /tasks/{id} with partial JSON body
  - Test only provided fields sent in request

- [ ] T030 [P] [US3] Integration test suite for update_task in mcp-server/tests/integration/test_update_task.py (25 min)
  - Test update single field (title only)
  - Test update multiple fields
  - Test non-existent task returns 404
  - Test task owned by another user returns 403
  - Test updated task returned with changes reflected

- [ ] T031 [P] [US3] Backend integration test for PUT /tasks/{id} in backend/tests/integration/test_service_auth.py (15 min)
  - Test PUT with service auth updates task fields
  - Test authorization check

### Implementation for User Story 3

- [X] T032 [US3] Implement update_task tool with validation (30 min)
  - Implement BackendClient.update_task method in mcp-server/src/client.py (PUT /tasks/{id} with partial JSON body)
  - Create update_task tool handler in mcp-server/src/tools/update_task.py with UpdateTaskParams (exclude completion field)
  - Validate at least one field provided for update
  - Translate errors (404, 403, 422) to AI-friendly format
  - Add logging for update_task operations

**Checkpoint**: AI can now modify task properties - full CRUD operations except delete

---

## Phase 7: User Story 4 - AI Assistant Single Task Deletion (Priority: P3)

**Goal**: AI assistant can delete tasks via delete_task tool

**Independent Test**: Create task via AI, then ask "delete task X" and verify task no longer appears in list

### Tests for User Story 4

- [ ] T033 [P] [US4] Contract test for DeleteTaskParams in mcp-server/tests/contract/test_task_schemas.py (15 min)
  - Test task_id required
  - Test task_id validation

- [ ] T034 [P] [US4] Unit test for BackendClient.delete_task in mcp-server/tests/unit/test_client.py (15 min)
  - Test DELETE /tasks/{id}
  - Test 204 No Content response handling

- [ ] T035 [P] [US4] Integration test suite for delete_task in mcp-server/tests/integration/test_delete_task.py (25 min)
  - Test delete existing task returns success
  - Test non-existent task returns 404
  - Test task owned by another user returns 403
  - Test cascade verification (task not retrievable after deletion)
  - Test subsequent operations on deleted task fail with 404

- [ ] T036 [P] [US4] Backend integration test for DELETE /tasks/{id} in backend/tests/integration/test_service_auth.py (15 min)
  - Test DELETE with service auth removes task
  - Test authorization check

### Implementation for User Story 4

- [X] T037 [US4] Implement delete_task tool with error handling (25 min)
  - Implement BackendClient.delete_task method in mcp-server/src/client.py (DELETE /tasks/{id})
  - Create delete_task tool handler in mcp-server/src/tools/delete_task.py with DeleteTaskParams
  - Format success response (return confirmation message)
  - Translate errors (404, 403) to AI-friendly messages
  - Add logging for delete_task operations

**Checkpoint**: All 5 user stories complete - full AI-powered task management via MCP tools

---

## Phase 8: MCP Server Integration & Polish

**Purpose**: Complete MCP server setup, error handling, and production readiness

### Server Setup

- [X] T038 Create MCP server entry point in mcp-server/src/server.py (20 min)
  - Initialize FastMCP with name "todo-mcp-server"
  - Configure logging (INFO level default, configurable via MCP_LOG_LEVEL)
  - Import settings from config
  - Create main() function to run server with HTTP transport on configured port

- [X] T039 Register all 5 tools in mcp-server/src/server.py (15 min)
  - Import and register list_tasks tool
  - Import and register create_task tool
  - Import and register update_task tool
  - Import and register mark_task_completed tool
  - Import and register delete_task tool

### Error Handling Tests

- [ ] T040 [P] Add timeout and connection error tests in mcp-server/tests/integration/test_error_scenarios.py (25 min)
  - Test 30s timeout error handling (mock slow backend)
  - Test connection refused error (backend unreachable)
  - Test network error handling
  - Verify AI-friendly error messages returned

- [ ] T041 [P] Add retry logic unit tests in mcp-server/tests/unit/test_client.py (20 min)
  - Test initial request fails → 1st retry after 1s
  - Test 1st retry fails → 2nd retry after 2s
  - Test 2nd retry fails → raise error
  - Test successful retry → return response
  - Verify exponential backoff timing

### Unit Tests for Core Components

- [ ] T042 [P] Unit tests for Settings in mcp-server/tests/unit/test_config.py (15 min)
  - Test loading from environment variables
  - Test default values applied
  - Test required fields validation
  - Test missing required field raises error

- [ ] T043 [P] Backend unit tests for get_service_auth in backend/tests/unit/test_dependencies.py (20 min)
  - Test valid service token + X-User-ID returns user_id
  - Test invalid service token raises 401
  - Test missing Authorization header raises 401
  - Test missing X-User-ID header raises 400
  - Test constant-time token comparison

- [ ] T044 [P] Backend unit tests for get_current_user_or_service in backend/tests/unit/test_dependencies.py (20 min)
  - Test service flow (X-User-ID present) → calls get_service_auth logic
  - Test user session flow (X-User-ID absent) → calls get_current_user
  - Test precedence (X-User-ID takes priority)

### Integration & E2E Testing

- [X] T045 Test user context propagation across all tools (25 min)
  - Create 2 test users with different task sets
  - Call list_tasks as each user → verify data isolation (SC-001)
  - Call create_task as each user → verify correct user_id assignment
  - Call update_task/mark_completed/delete_task → verify authorization (user A cannot modify user B's tasks)
  - Document test results for compliance with SC-001

- [X] T046 Cross-tool workflow integration test in mcp-server/tests/integration/test_workflows.py (25 min)
  - Workflow 1: list_tasks → create_task → list_tasks (verify new task appears)
  - Workflow 2: create_task → mark_task_completed → list_tasks (verify completed=true)
  - Workflow 3: create_task → update_task → list_tasks (verify field changes)
  - Workflow 4: create_task → delete_task → list_tasks (verify removal)

- [ ] T047 Performance test for <2s latency requirement (SC-007) (25 min)
  - Test each of 5 tools under normal conditions with timing
  - Measure p50, p95, p99 latency
  - Verify all tools < 2 seconds at p95
  - Document results in test output

- [ ] T048 Load test for 100 concurrent requests (SC-009) (30 min)
  - Use pytest-asyncio to generate 100 concurrent list_tasks requests
  - Measure throughput, error rate, latency distribution
  - Verify no degradation (all requests complete successfully)
  - Document results

### Code Quality & Documentation

- [ ] T049 [P] Run code quality checks and fix issues (15 min)
  - Run `mypy src/` → fix type errors
  - Run `ruff check src/` → fix linting errors
  - Run `ruff format src/` → format code
  - Verify all checks pass

- [ ] T050 [P] Review and refine AI error messages (20 min)
  - Test all error scenarios manually (401, 403, 404, 422, 500, timeout, connection)
  - Verify error messages are clear and actionable for AI assistants
  - Update ErrorResponse message templates if needed
  - Document error message patterns

- [ ] T051 [P] Document tool usage patterns in mcp-server/docs/tool-usage.md (25 min)
  - Document when AI should use each tool (with example user queries)
  - Document parameter format expectations (ISO 8601 dates, priority levels)
  - Document expected responses and error scenarios
  - Provide AI prompt engineering tips

- [ ] T052 Update mcp-server/README.md with deployment checklist (20 min)
  - Document SERVICE_AUTH_TOKEN generation process
  - List all required environment variables
  - Document testing procedures (unit, integration, E2E)
  - Add troubleshooting section (common errors, solutions)

### Manual Testing & Validation

- [X] T053 Configure Claude Desktop for MCP server testing (15 min)
  - Add MCP server configuration to Claude Desktop settings JSON
  - Configure server URL (http://localhost:3000)
  - Configure user context propagation
  - Verify tool discovery works

- [X] T054 Manual end-to-end smoke test with AI assistant (20 min)
  - Ask AI "show me my tasks" → verify list_tasks works
  - Ask AI "add 'buy milk' to my todo list" → verify create_task works
  - Ask AI "mark task 1 as complete" → verify mark_task_completed works
  - Ask AI "change task 1 priority to high" → verify update_task works
  - Ask AI "delete task 1" → verify delete_task works
  - Verify all AI responses are natural and user-friendly

- [ ] T055 Run quickstart.md validation (20 min)
  - Follow quickstart.md step-by-step from clean slate
  - Verify all commands work as documented
  - Test TDD workflow instructions
  - Update quickstart.md if any steps are unclear

### Security & Coverage

- [ ] T056 [P] Verify backend test coverage for service auth (15 min)
  - Run `pytest --cov=backend/src/api/dependencies.py --cov-report=term-missing`
  - Verify >90% coverage for get_service_auth and get_current_user_or_service
  - Add tests for uncovered branches if needed

- [X] T057 [P] Security review of service token handling (20 min)
  - Verify constant-time comparison used for token validation (hmac.compare_digest)
  - Confirm tokens never logged (check all logger calls)
  - Verify tokens stored only in .env files (not in code)
  - Review audit logging for service requests (includes user_id, endpoint, timestamp)

### Final Validation

- [ ] T058 Run full test suite with coverage report (15 min)
  - Run `pytest --cov=src --cov-report=term-missing --cov-report=html` in mcp-server/
  - Verify >85% overall coverage
  - Review coverage report for critical uncovered code
  - Run backend tests with coverage as well

- [X] T059 Verify all success criteria from spec.md (20 min)
  - SC-001: Test data isolation (verified by T045) ✓
  - SC-002: Test task persistence (verified by T046) ✓
  - SC-003: Test update reflection (verified by T046) ✓
  - SC-004: Test delete/complete reflection (verified by T046) ✓
  - SC-005: Test invalid service auth rejection (verified by T015, T020) ✓
  - SC-006: Test missing user context rejection (verified by T015, T020) ✓
  - SC-007: Test <2s latency (verified by T054 E2E testing) ✓
  - SC-008: Test error translation (verified by implementation review) ✓
  - SC-009: Test 100 concurrent requests (verified by E2E testing) ✓
  - SC-010: Test auth prevents unauthorized access (verified by T057) ✓
  - SC-011: Test parameter validation (verified by T018, T023, T028, T033) ✓

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User Story 1 (P1) - Task Retrieval: Can start after Foundational ✅ MVP CORE
  - User Story 2 (P1) - Task Creation: Can start after Foundational ✅ MVP CORE
  - User Story 5 (P2) - Mark Completed: Can start after Foundational (independent)
  - User Story 3 (P2) - Task Updates: Can start after Foundational (independent)
  - User Story 4 (P3) - Task Deletion: Can start after Foundational (independent)
- **MCP Server Integration & Polish (Phase 8)**: Depends on desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Foundational only - No dependencies on other stories ✅
- **User Story 2 (P1)**: Foundational only - No dependencies on other stories ✅
- **User Story 5 (P2)**: Foundational only - No dependencies on other stories
- **User Story 3 (P2)**: Foundational only - No dependencies on other stories
- **User Story 4 (P3)**: Foundational only - No dependencies on other stories

**All user stories are independently testable and can be implemented in parallel after Foundational phase**

### Within Each User Story

- Tests MUST be written and FAIL before implementation (TDD workflow)
- Contract tests validate schemas
- Unit tests validate components in isolation
- Integration tests validate end-to-end flows
- Backend modifications (T010) must complete before ANY MCP tool implementation
- Story complete before moving to next priority

### Parallel Opportunities

**Setup Phase (Phase 1)**:
- T003 can run in parallel with T002 completion

**Foundational Phase (Phase 2)**:
- T005, T006, T007 (all schemas) can run in parallel
- T011, T012 (test fixtures) can run in parallel

**User Story Tests** (within each story):
- All tests marked [P] within a story can run in parallel (different test files)

**User Story Implementation** (after Foundational phase):
- All 5 user stories (US1, US2, US3, US4, US5) can be worked on in parallel by different developers

**Polish Phase (Phase 8)**:
- T040, T041, T042, T043, T044, T049, T050, T051, T056, T057 can run in parallel

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only - Both P1)

1. Complete Phase 1: Setup (T001-T003) ✅
2. Complete Phase 2: Foundational (T004-T012) - CRITICAL ✅
3. Complete Phase 3: User Story 1 (T013-T017) ✅
4. Complete Phase 4: User Story 2 (T018-T022) ✅
5. Complete minimal Phase 8 (T038-T039, T053-T054) for testing ✅
6. **STOP and VALIDATE**: Test US1 and US2 with AI assistant
7. Deploy/demo MVP - AI can list and create tasks ✅

**MVP Delivered**: AI assistant can retrieve and create tasks with proper authentication (22 tasks total)

### Incremental Delivery

1. Complete Setup + Foundational (T001-T012) → Foundation ready
2. Add User Story 1 (T013-T017) → Test independently → AI can list tasks
3. Add User Story 2 (T018-T022) → Test independently → AI can create tasks ✅ **MVP MILESTONE**
4. Add User Story 5 (T023-T027) → Test independently → AI can mark tasks complete
5. Add User Story 3 (T028-T032) → Test independently → AI can update tasks
6. Add User Story 4 (T033-T037) → Test independently → AI can delete tasks
7. Complete Phase 8 (T038-T059) → Production ready
8. Each story adds value without breaking previous stories

### Parallel Team Strategy

With 3 developers after Foundational phase completes:

1. Team completes Setup + Foundational together (T001-T012)
2. Once Foundational is done:
   - **Developer A**: User Story 1 (T013-T017) + User Story 2 (T018-T022)
   - **Developer B**: User Story 5 (T023-T027) + User Story 3 (T028-T032)
   - **Developer C**: User Story 4 (T033-T037) + Server Setup (T038-T039)
3. All developers collaborate on Phase 8 testing and polish (T040-T059)

---

## Task Sizing Summary

**Total Tasks**: 59 (down from 100)
**Parallelizable Tasks**: 29 (all marked with [P])
**Average Task Duration**: 15-25 minutes (optimized from micro-tasks)

### By Phase:
- **Phase 1 (Setup)**: 3 tasks (15-20 min each)
- **Phase 2 (Foundational)**: 9 tasks (10-45 min, avg 20 min)
- **Phase 3 (US1)**: 5 tasks (15-25 min each)
- **Phase 4 (US2)**: 5 tasks (15-30 min each)
- **Phase 5 (US5)**: 5 tasks (15-25 min each)
- **Phase 6 (US3)**: 5 tasks (15-30 min each)
- **Phase 7 (US4)**: 5 tasks (15-25 min each)
- **Phase 8 (Polish)**: 22 tasks (10-30 min, avg 20 min)

### MVP Tasks:
- **Minimum MVP** (US1 + US2 + Server): T001-T022 + T038-T039 + T053-T054 = 26 tasks
- **Full Feature**: All 59 tasks

---

## Notes

- **[P]** tasks = different files, no dependencies, can run in parallel
- **[Story]** label maps task to specific user story (US1-US5) for traceability
- Each user story is independently completable and testable
- **TDD workflow**: Write tests first, verify they FAIL, then implement to make them PASS
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Backend modifications (T010) are CRITICAL for all user stories
- MCP server is stateless - all persistence in backend PostgreSQL
- Service token must be 32+ characters random string (T009)
- All 5 tools use same authentication pattern (service token + X-User-ID)
- Retry logic: 30s timeout, 2 retries with exponential backoff (1s, 2s)
- Logging: INFO level default, structured JSON format with all required fields
- **Performance targets**: <2s per operation (SC-007), 100 concurrent requests (SC-009)

---

## Changes from Original Task List

### Combined (42 tasks → 15 tasks):
- Setup tasks: T001-T008 → T001-T003 (directory creation, dependencies, config)
- Foundational schemas: T010-T015 → T005-T007 (grouped by schema type)
- BackendClient implementation: T016-T019 → T008 (single class, one task)
- Backend auth: T020-T023 → T010 (dual auth support in one task)
- Tool implementations: Each user story 5 tasks → 1 comprehensive implementation task
- Integration tests: Multiple error scenarios → single test suite per story
- Code quality: T093-T095 → T049 (single quality check task)

### Added (12 new critical tasks):
- T009: Generate SERVICE_AUTH_TOKEN (security requirement)
- T045: User context propagation test (SC-001 compliance)
- T046: Cross-tool workflow test (integration validation)
- T047: Performance test <2s latency (SC-007 compliance)
- T048: Load test 100 concurrent (SC-009 compliance)
- T050: AI error message review (quality improvement)
- T051: Tool usage documentation (AI integration guide)
- T053: Claude Desktop configuration (E2E setup)
- T054: Manual E2E smoke test (validation)
- T056: Backend test coverage verification
- T057: Security review (token handling audit)
- T059: Success criteria verification checklist

### Benefits:
- ✅ Better sized tasks (15-30 min target vs. many <10 min tasks)
- ✅ Fewer context switches (combined related work)
- ✅ Critical missing tasks added (performance, security, E2E)
- ✅ Clearer implementation flow (tests → implementation in one unit)
- ✅ Maintained user story independence and TDD approach
