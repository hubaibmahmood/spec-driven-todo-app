# Tasks: FastAPI REST API Conversion

**Input**: Design documents from `/specs/003-fastapi-rest-api/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/openapi.yaml, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing. Following user guidance: implement all endpoints and Neon storage first, then authentication. One test per endpoint unless multiple tests are necessary.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Single project structure: `src/`, `tests/` at repository root
- FastAPI app in `src/api/`, database layer in `src/database/`, business logic in `src/services/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Add FastAPI dependencies to pyproject.toml (fastapi>=0.104.0, uvicorn>=0.24.0, sqlalchemy>=2.0.0, asyncpg>=0.29.0, alembic>=1.13.0, pydantic>=2.0.0, pydantic-settings>=2.0.0, python-dotenv>=1.0.0)
- [ ] T002 [P] Add development dependencies to pyproject.toml (pytest>=7.4.0, pytest-asyncio>=0.23.0, pytest-cov>=4.1.0, httpx>=0.25.0, factory-boy>=3.3.0, faker>=20.0.0, pytest-mock>=3.12.0)
- [ ] T003 [P] Create .env.example file with DATABASE_URL, SESSION_HASH_SECRET, ENVIRONMENT, CORS_ORIGINS, SQLALCHEMY_POOL_SIZE, SQLALCHEMY_POOL_OVERFLOW, SQLALCHEMY_POOL_TIMEOUT, SQLALCHEMY_POOL_RECYCLE, SQLALCHEMY_ECHO
- [ ] T004 [P] Create project directory structure (src/api/, src/api/routers/, src/api/schemas/, src/api/middleware/, src/database/, src/models/, tests/unit/, tests/contract/, tests/integration/)
- [ ] T005 [P] Update pytest.ini with asyncio_mode=auto and test markers (asyncio, integration, unit, contract)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T006 Create SQLAlchemy Task model in src/models/database.py (id: Integer PK, user_id: UUID, title: String(200), description: Text, completed: Boolean, created_at: DateTime, updated_at: DateTime)
- [ ] T007 [P] Create UserSession reference model in src/models/database.py (id: UUID PK, user_id: UUID, token_hash: String(255), expires_at: DateTime, revoked: Boolean) - read-only, no migrations
- [ ] T008 Create async database engine and session factory in src/database/connection.py (asyncpg driver, pool_size=10, max_overflow=20, pool_pre_ping=True, pool_recycle=3600)
- [ ] T009 [P] Initialize Alembic configuration with alembic.ini and alembic/env.py (async-to-sync URL conversion, exclude users and user_sessions tables)
- [ ] T010 Create initial Alembic migration for tasks table in alembic/versions/001_create_tasks_table.py
- [ ] T011 [P] Create TaskRepository with async methods in src/database/repository.py (get_all_by_user, get_by_id, create, update, delete)
- [ ] T012 [P] Create Pydantic schemas in src/api/schemas/task.py (TaskCreate, TaskUpdate, TaskResponse with validation)
- [ ] T013 [P] Create ErrorResponse schema in src/api/schemas/error.py (type, title, status, detail, instance, timestamp, request_id, errors, retry_after, rate_limit_info)
- [ ] T014 Create FastAPI app initialization in src/api/main.py (app instance, CORS middleware, exception handlers, lifespan for database connection)
- [ ] T015 [P] Create health check router in src/api/routers/health.py (GET /health endpoint returning status and timestamp)
- [ ] T016 [P] Create database session dependency in src/api/dependencies.py (get_db function yielding AsyncSession)
- [ ] T017 [P] Create test fixtures in tests/conftest.py (async_engine, db_session with transaction rollback, test_client with httpx AsyncClient)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - View All Tasks via API (Priority: P1) 🎯 MVP

**Goal**: Enable web applications to fetch all tasks for a user via HTTP GET request

**Independent Test**: Can be fully tested by making GET request to /tasks endpoint and verifying response contains all tasks in JSON format

### Test for User Story 1

- [ ] T018 [US1] Integration test for GET /tasks endpoint in tests/integration/test_tasks_list.py (test_get_all_tasks_returns_200_with_task_list, test_get_all_tasks_empty_returns_200_with_empty_array, test_get_all_tasks_includes_completed_and_incomplete)

### Implementation for User Story 1

- [ ] T019 [US1] Implement GET /tasks endpoint in src/api/routers/tasks.py (list all tasks for user, return TaskResponse array, HTTP 200)
- [ ] T020 [US1] Register tasks router in src/api/main.py with /tasks prefix

**Checkpoint**: User Story 1 complete - GET /tasks endpoint functional and tested

---

## Phase 4: User Story 2 - Create Task via API (Priority: P1)

**Goal**: Enable web applications to create new tasks via HTTP POST request

**Independent Test**: Can be fully tested by sending POST requests with task data and verifying tasks are created with auto-generated IDs

### Test for User Story 2

- [ ] T021 [US2] Integration test for POST /tasks endpoint in tests/integration/test_tasks_create.py (test_create_task_with_valid_data_returns_201, test_create_task_title_only_returns_201, test_create_task_empty_title_returns_400, test_create_task_title_too_long_returns_400, test_create_task_description_too_long_returns_400)

### Implementation for User Story 2

- [ ] T022 [US2] Implement POST /tasks endpoint in src/api/routers/tasks.py (create task with TaskCreate schema, return TaskResponse, HTTP 201)
- [ ] T023 [US2] Add Pydantic validators for title (non-empty after strip, 1-200 chars) and description (max 1000 chars) in src/api/schemas/task.py

**Checkpoint**: User Story 2 complete - POST /tasks endpoint functional and tested

---

## Phase 5: User Story 3 - Retrieve Single Task via API (Priority: P2)

**Goal**: Enable web applications to fetch specific task details by ID via HTTP GET request

**Independent Test**: Can be fully tested by requesting specific task IDs and verifying correct task details returned or 404 for non-existent IDs

### Test for User Story 3

- [ ] T024 [US3] Integration test for GET /tasks/{task_id} endpoint in tests/integration/test_tasks_get_single.py (test_get_task_by_id_returns_200, test_get_task_nonexistent_id_returns_404, test_get_task_invalid_id_format_returns_400)

### Implementation for User Story 3

- [ ] T025 [US3] Implement GET /tasks/{task_id} endpoint in src/api/routers/tasks.py (retrieve task by ID, return TaskResponse, HTTP 200 or 404)
- [ ] T026 [US3] Add custom HTTPException handler for 404 Not Found in src/api/main.py with ErrorResponse format

**Checkpoint**: User Story 3 complete - GET /tasks/{task_id} endpoint functional and tested

---

## Phase 6: User Story 4 - Update Task Completion Status via API (Priority: P2)

**Goal**: Enable web applications to toggle task completion status via HTTP PATCH request

**Independent Test**: Can be fully tested by sending PATCH requests to update completion status and verifying changes persist

### Test for User Story 4

- [ ] T027 [US4] Integration test for PATCH /tasks/{task_id} endpoint in tests/integration/test_tasks_update_completion.py (test_patch_task_mark_complete_returns_200, test_patch_task_mark_incomplete_returns_200, test_patch_task_nonexistent_returns_404)

### Implementation for User Story 4

- [ ] T028 [US4] Implement PATCH /tasks/{task_id} endpoint in src/api/routers/tasks.py (partial update for completion status, return TaskResponse, HTTP 200 or 404)
- [ ] T029 [US4] Update TaskRepository.update method to handle partial updates in src/database/repository.py

**Checkpoint**: User Story 4 complete - PATCH /tasks/{task_id} endpoint functional and tested

---

## Phase 7: User Story 5 - Update Task Details via API (Priority: P3)

**Goal**: Enable web applications to update task title and description via HTTP PUT request

**Independent Test**: Can be fully tested by sending PUT requests with updated data and verifying changes persist with proper validation

### Test for User Story 5

- [ ] T030 [US5] Integration test for PUT /tasks/{task_id} endpoint in tests/integration/test_tasks_update_full.py (test_put_task_update_title_and_description_returns_200, test_put_task_invalid_title_returns_400, test_put_task_nonexistent_returns_404)

### Implementation for User Story 5

- [ ] T031 [US5] Implement PUT /tasks/{task_id} endpoint in src/api/routers/tasks.py (full update with title/description/completion, return TaskResponse, HTTP 200 or 400/404)

**Checkpoint**: User Story 5 complete - PUT /tasks/{task_id} endpoint functional and tested

---

## Phase 8: User Story 6 - Delete Task via API (Priority: P3)

**Goal**: Enable web applications to delete tasks via HTTP DELETE request

**Independent Test**: Can be fully tested by sending DELETE requests and verifying tasks are removed and subsequent requests return 404

### Test for User Story 6

- [ ] T032 [US6] Integration test for DELETE /tasks/{task_id} endpoint in tests/integration/test_tasks_delete.py (test_delete_task_returns_204, test_delete_task_verify_404_on_subsequent_get, test_delete_nonexistent_task_returns_404, test_delete_task_idempotent_returns_404)

### Implementation for User Story 6

- [ ] T033 [US6] Implement DELETE /tasks/{task_id} endpoint in src/api/routers/tasks.py (delete task by ID, return HTTP 204 on success, 404 if not found)

**Checkpoint**: User Story 6 complete - DELETE /tasks/{task_id} endpoint functional and tested

---

## Phase 9: User Story 7 - Bulk Delete Tasks via API (Priority: P3)

**Goal**: Enable web applications to delete multiple tasks in a single request via HTTP POST

**Independent Test**: Can be fully tested by sending requests with multiple IDs and verifying all are deleted with proper reporting

### Test for User Story 7

- [ ] T034 [US7] Integration test for POST /tasks/bulk-delete endpoint in tests/integration/test_tasks_bulk_delete.py (test_bulk_delete_all_exist_returns_200, test_bulk_delete_some_not_found_returns_200_with_partial_results, test_bulk_delete_empty_list_returns_400)

### Implementation for User Story 7

- [ ] T035 [US7] Implement POST /tasks/bulk-delete endpoint in src/api/routers/tasks.py (accept array of task IDs, return deleted and not_found arrays, HTTP 200)
- [ ] T036 [US7] Create BulkDeleteRequest and BulkDeleteResponse schemas in src/api/schemas/task.py (task_ids array, deleted/not_found arrays)
- [ ] T037 [US7] Add TaskRepository.bulk_delete method in src/database/repository.py (delete multiple by IDs, return success/failure lists)

**Checkpoint**: User Story 7 complete - POST /tasks/bulk-delete endpoint functional and tested

---

## Phase 10: User Story 8 - Protected Endpoints with Session Authentication (Priority: P1)

**Goal**: Secure all task endpoints with session-based authentication via database lookup in shared Neon PostgreSQL

**Independent Test**: Can be fully tested by sending requests with valid/invalid/expired tokens and verifying proper authorization

### Test for User Story 8

- [ ] T038 [US8] Integration test for session authentication in tests/integration/test_auth.py (test_valid_session_token_allows_access, test_missing_token_returns_401, test_invalid_token_returns_401, test_expired_token_returns_401, test_user_cannot_access_other_user_tasks_returns_403)

### Implementation for User Story 8

- [ ] T039 [US8] Create SessionTokenHasher class in src/services/auth_service.py (hash_token with HMAC-SHA256, verify_token_against_hash with hmac.compare_digest)
- [ ] T040 [US8] Create validate_session function in src/services/auth_service.py (query user_sessions table WHERE token_hash AND expires_at > now AND revoked=false, return user_id or None)
- [ ] T041 [US8] Create get_current_user dependency in src/api/dependencies.py (extract bearer token, hash with SESSION_HASH_SECRET, validate session, return user_id UUID or raise HTTPException 401)
- [ ] T042 [US8] Create authentication middleware in src/api/middleware/auth.py (HTTPBearer security scheme, attach user_id to request.state)
- [ ] T043 [US8] Add authentication dependency to all task endpoints in src/api/routers/tasks.py (inject current_user: UUID = Depends(get_current_user))
- [ ] T044 [US8] Update TaskRepository methods to filter by user_id in src/database/repository.py (enforce user isolation on all queries)
- [ ] T045 [US8] Add custom HTTPException handler for 401 Unauthorized and 403 Forbidden in src/api/main.py with ErrorResponse format

**Checkpoint**: User Story 8 complete - All endpoints secured with session authentication and user isolation

---

## Phase 11: User Story 9 - Rate Limiting for API Protection (Priority: P2)

**Goal**: Implement rate limiting to prevent abuse and ensure fair resource usage

**Independent Test**: Can be fully tested by sending rapid successive requests and verifying rate limit enforcement

### Test for User Story 9

- [ ] T046 [US9] Integration test for rate limiting in tests/integration/test_rate_limit.py (test_within_rate_limit_allows_requests, test_exceeds_rate_limit_returns_429, test_rate_limit_reset_after_window, test_read_and_write_endpoints_have_different_limits)

### Implementation for User Story 9

- [ ] T047 [US9] Add slowapi and redis dependencies to pyproject.toml (slowapi>=0.1.9, redis>=5.0.0)
- [ ] T048 [US9] Create rate limiting middleware in src/api/middleware/rate_limit.py (slowapi Limiter with custom key function for user-based tracking with IP fallback, Redis storage)
- [ ] T049 [US9] Configure rate limiter in src/api/main.py (initialize Limiter with Redis backend, add middleware to app)
- [ ] T050 [US9] Apply rate limit decorators to endpoints in src/api/routers/tasks.py (100/minute for GET endpoints, 30/minute for POST/PUT/PATCH/DELETE endpoints)
- [ ] T051 [US9] Add custom HTTPException handler for 429 Too Many Requests in src/api/main.py (return ErrorResponse with retry_after and rate_limit_info)

**Checkpoint**: User Story 9 complete - Rate limiting implemented and tested

---

## Phase 12: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and production readiness

- [ ] T052 [P] Add comprehensive logging to all endpoints in src/api/routers/tasks.py (request/response logging, error logging)
- [ ] T053 [P] Add request_id generation middleware in src/api/middleware/ for request correlation
- [ ] T054 [P] Create custom validation exception handler in src/api/main.py to convert Pydantic validation errors to ErrorResponse format
- [ ] T055 [P] Add database connection error handling in src/api/main.py (catch SQLAlchemy exceptions, return ErrorResponse)
- [ ] T056 [P] Add unit tests for TaskRepository in tests/unit/test_repository.py (test all CRUD methods with mocked database)
- [ ] T057 [P] Add unit tests for auth_service in tests/unit/test_auth_service.py (test token hashing, session validation logic)
- [ ] T058 [P] Add contract tests for Pydantic schemas in tests/contract/test_api_schemas.py (test validation rules for TaskCreate, TaskUpdate, TaskResponse)
- [ ] T059 [P] Update .env.example with comprehensive comments and production-ready defaults
- [ ] T060 Run quickstart.md validation (verify all steps work: dependencies install, migrations run, server starts, health endpoint responds, tests pass)
- [ ] T061 [P] Add OpenAPI tags and descriptions to all endpoints in src/api/routers/tasks.py for better documentation
- [ ] T062 [P] Configure response models for all endpoints in src/api/routers/tasks.py (response_model parameter for automatic validation)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-9)**: All depend on Foundational phase completion
  - US1 (View All Tasks) → US2 (Create Task) → US3 (Get Single Task) can proceed sequentially for basic CRUD
  - US4 (Update Completion) → US5 (Update Details) → US6 (Delete) → US7 (Bulk Delete) can proceed in parallel after US1-3
  - US8 (Authentication) depends on all endpoint implementations (US1-7) being complete
  - US9 (Rate Limiting) depends on US8 (Authentication) being complete
- **Polish (Phase 12)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - No dependencies
- **User Story 2 (P1)**: Can start after US1 - Depends on router setup from US1
- **User Story 3 (P2)**: Can start after US2 - Depends on router and error handling from US1-2
- **User Story 4 (P2)**: Can start after US3 - Independently testable PATCH endpoint
- **User Story 5 (P3)**: Can start after US4 - Independently testable PUT endpoint
- **User Story 6 (P3)**: Can start after US5 - Independently testable DELETE endpoint
- **User Story 7 (P3)**: Can start after US6 - Adds bulk delete on top of single delete
- **User Story 8 (P1)**: **MUST wait for US1-7 to complete** - Adds authentication to all existing endpoints
- **User Story 9 (P2)**: **MUST wait for US8 to complete** - Rate limiting needs user tracking from authentication

### Within Each User Story

- Tests MUST be written FIRST and should FAIL before implementation
- Models and schemas before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- **Phase 1 (Setup)**: T001, T002, T003, T004, T005 can all run in parallel (different files)
- **Phase 2 (Foundational)**: T007, T009, T011, T012, T013, T015, T016, T017 can run in parallel (after T006, T008 complete)
- **Phase 12 (Polish)**: T052, T053, T054, T055, T056, T057, T058, T059, T061, T062 can all run in parallel (different files, no dependencies)

---

## Parallel Example: Foundational Phase

```bash
# After T006 (Task model) and T008 (database engine) are complete:
Task: "Create UserSession reference model in src/models/database.py" (T007)
Task: "Initialize Alembic configuration" (T009)
Task: "Create TaskRepository" (T011)
Task: "Create Pydantic schemas in src/api/schemas/task.py" (T012)
Task: "Create ErrorResponse schema in src/api/schemas/error.py" (T013)
Task: "Create health check router" (T015)
Task: "Create database session dependency" (T016)
Task: "Create test fixtures in tests/conftest.py" (T017)
```

---

## Implementation Strategy

### MVP First (User Stories 1-2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (View All Tasks)
4. Complete Phase 4: User Story 2 (Create Task)
5. **STOP and VALIDATE**: Test US1 and US2 independently (basic read/write functional)
6. Deploy/demo if ready - users can view and create tasks via API

### Incremental Delivery

1. **Foundation** (Phase 1-2) → Database and FastAPI structure ready
2. **US1-2** → MVP: List and create tasks (basic CRUD) → Deploy/Demo
3. **US3-7** → Full CRUD operations (get, update, delete, bulk delete) → Deploy/Demo
4. **US8** → Secure all endpoints with authentication → Deploy/Demo (production-ready security)
5. **US9** → Add rate limiting → Deploy/Demo (production-ready protection)
6. **Phase 12** → Polish and optimize → Final production deployment

### Parallel Team Strategy

With multiple developers:

1. **Team completes Phase 1-2 together** (foundation is critical)
2. **Sequential endpoint implementation** (US1 → US2 → US3 → US4 → US5 → US6 → US7)
   - Developer A: Writes test for USX
   - Developer B: Implements endpoint for USX after test is written
   - This ensures TDD workflow and clean integration
3. **US8 (Authentication)**: Single developer adds auth to all endpoints after US1-7 complete
4. **US9 (Rate Limiting)**: Single developer adds rate limiting after US8 complete
5. **Phase 12 (Polish)**: All tasks marked [P] can be divided among team members

---

## Notes

- [P] tasks = different files, no dependencies, can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- **CRITICAL**: US8 (Authentication) must wait until ALL endpoints (US1-7) are implemented
- **CRITICAL**: US9 (Rate Limiting) must wait until US8 (Authentication) is complete
- Verify tests fail before implementing (TDD workflow)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- One test per endpoint (unless multiple test scenarios are necessary for comprehensive coverage)
- Follow the user's guidance: endpoints + Neon storage first, then authentication last

---

## Summary

- **Total Tasks**: 62
- **Tasks per Phase**:
  - Phase 1 (Setup): 5 tasks
  - Phase 2 (Foundational): 12 tasks
  - Phase 3 (US1 - View All): 3 tasks
  - Phase 4 (US2 - Create): 3 tasks
  - Phase 5 (US3 - Get Single): 3 tasks
  - Phase 6 (US4 - Update Completion): 3 tasks
  - Phase 7 (US5 - Update Details): 2 tasks
  - Phase 8 (US6 - Delete): 2 tasks
  - Phase 9 (US7 - Bulk Delete): 4 tasks
  - Phase 10 (US8 - Authentication): 8 tasks
  - Phase 11 (US9 - Rate Limiting): 6 tasks
  - Phase 12 (Polish): 11 tasks

- **Parallel Opportunities**: 23 tasks marked [P] can run in parallel
- **Independent Test Criteria**: Each user story has clear acceptance criteria and can be tested independently
- **Suggested MVP Scope**: Phase 1 (Setup) + Phase 2 (Foundational) + Phase 3 (US1) + Phase 4 (US2) = Basic task viewing and creation via API

---

**Format Validation**: ✅ All tasks follow checklist format: `- [ ] [ID] [P?] [Story?] Description with file path`
