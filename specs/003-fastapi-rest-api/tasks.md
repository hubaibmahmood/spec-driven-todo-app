# Tasks: FastAPI REST API Conversion

**Input**: Design documents from `/specs/003-fastapi-rest-api/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/openapi.yaml, quickstart.md

**Status**: **Phases 1-10 Complete ✅** | **Phases 11-12 Blocked ⏸️**

**Completion Summary**:
- ✅ **Phases 1-10**: Setup, Foundation, CRUD endpoints (US1-7), Session Authentication (US8)
- ⏸️ **Phase 11**: Rate Limiting - Blocked pending better-auth integration (Feature 004)
- ⏸️ **Phase 12**: Polish - Blocked pending Phase 11 completion
- 📋 **Next**: Implement better-auth in Feature 004, then return to complete Phase 11-12 in Feature 005

**Organization**: Tasks are grouped by user story to enable independent implementation and testing. Following user guidance: implement all endpoints and Neon storage first, then authentication. One test per endpoint unless multiple tests are necessary.

**Task Sizing**: All tasks sized for 15-30 minutes of focused work

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

- [ ] T001 Add all project dependencies to pyproject.toml (fastapi>=0.104.0, uvicorn>=0.24.0, sqlalchemy>=2.0.0, asyncpg>=0.29.0, alembic>=1.13.0, pydantic>=2.0.0, pydantic-settings>=2.0.0, python-dotenv>=1.0.0, pytest>=7.4.0, pytest-asyncio>=0.23.0, pytest-cov>=4.1.0, httpx>=0.25.0, factory-boy>=3.3.0, faker>=20.0.0, pytest-mock>=3.12.0)
- [ ] T002 Initialize project structure and configuration (create directories: src/api/, src/api/routers/, src/api/schemas/, src/api/middleware/, src/database/, src/models/, tests/unit/, tests/contract/, tests/integration/; create .env.example with DATABASE_URL, SESSION_HASH_SECRET, ENVIRONMENT, CORS_ORIGINS, pool settings with comments; update pytest.ini with asyncio_mode=auto and test markers)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T003 Create environment configuration class in src/config.py using Pydantic Settings (DATABASE_URL, SESSION_HASH_SECRET, ENVIRONMENT, CORS_ORIGINS, SQLALCHEMY_POOL_SIZE, SQLALCHEMY_POOL_OVERFLOW, SQLALCHEMY_POOL_TIMEOUT, SQLALCHEMY_POOL_RECYCLE, SQLALCHEMY_ECHO with validation)
- [ ] T004 Create SQLAlchemy models in src/models/database.py (Task model: id Integer PK, user_id UUID, title String(200), description Text, completed Boolean, created_at DateTime, updated_at DateTime; UserSession reference model: id UUID PK, user_id UUID, token_hash String(255), expires_at DateTime, revoked Boolean - read-only, no migrations)
- [ ] T005 Create async database engine and session factory in src/database/connection.py (asyncpg driver, load config from Settings, pool_size=10, max_overflow=20, pool_pre_ping=True, pool_recycle=3600)
- [ ] T006 [P] Initialize Alembic configuration (alembic.ini and alembic/env.py with async-to-sync URL conversion, exclude users and user_sessions tables from autogeneration)
- [ ] T007 Create and run initial Alembic migration for tasks table (alembic/versions/001_create_tasks_table.py with all columns, indexes on user_id and created_at; run migration and verify schema creation)
- [ ] T008 [P] Create Pydantic schemas in src/api/schemas/ (task.py: TaskCreate, TaskUpdate, TaskResponse with field validators for title 1-200 chars, description max 1000 chars; error.py: ErrorResponse with type, title, status, detail, instance, timestamp, request_id, errors, retry_after, rate_limit_info)
- [ ] T009 [P] Create TaskRepository with async methods in src/database/repository.py (get_all_by_user, get_by_id, create, update with partial support, delete - all methods accept session as parameter)
- [ ] T010 Create centralized error handling in src/api/main.py (custom HTTPException handlers for 400, 401, 403, 404, 422, 429, 500 returning ErrorResponse format with request_id and timestamp)
- [ ] T011 Create FastAPI app initialization with core middleware in src/api/main.py (app instance, CORS middleware with config from Settings, register centralized error handlers from T010, lifespan context manager for database connection pool)
- [ ] T012 Create database session dependency in src/api/dependencies.py (get_db function yielding AsyncSession with proper cleanup)
- [ ] T013 [P] Create health check endpoint in src/api/routers/health.py (GET /health returning status "healthy", timestamp, database connectivity check; register in main.py)
- [ ] T014 [P] Create test infrastructure in tests/conftest.py (async_engine fixture, db_session fixture with transaction rollback, test_client fixture with httpx AsyncClient, test database setup/teardown)
- [ ] T015 [P] Integration test for health check endpoint in tests/integration/test_health.py (test_health_check_returns_200, test_health_check_includes_database_status)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - View All Tasks via API (Priority: P1) 🎯 MVP

**Goal**: Enable web applications to fetch all tasks for a user via HTTP GET request

**Independent Test**: Can be fully tested by making GET request to /tasks endpoint and verifying response contains all tasks in JSON format

### Test for User Story 1

- [ ] T016 [US1] Integration test for GET /tasks endpoint in tests/integration/test_tasks_list.py (test_get_all_tasks_returns_200_with_task_list, test_get_all_tasks_empty_returns_200_with_empty_array, test_get_all_tasks_includes_completed_and_incomplete)

### Implementation for User Story 1

- [ ] T017 [US1] Implement and register GET /tasks endpoint (create src/api/routers/tasks.py with GET /tasks endpoint using TaskRepository.get_all_by_user, return list of TaskResponse, HTTP 200; register router in src/api/main.py with /tasks prefix and appropriate tags)

**Checkpoint**: User Story 1 complete - GET /tasks endpoint functional and tested

---

## Phase 4: User Story 2 - Create Task via API (Priority: P1)

**Goal**: Enable web applications to create new tasks via HTTP POST request

**Independent Test**: Can be fully tested by sending POST requests with task data and verifying tasks are created with auto-generated IDs

### Test for User Story 2

- [ ] T018 [US2] Integration test for POST /tasks endpoint in tests/integration/test_tasks_create.py (test_create_task_with_valid_data_returns_201, test_create_task_title_only_returns_201, test_create_task_empty_title_returns_400, test_create_task_title_too_long_returns_400, test_create_task_description_too_long_returns_400)

### Implementation for User Story 2

- [ ] T019 [US2] Implement POST /tasks endpoint in src/api/routers/tasks.py (create task using TaskCreate schema with Pydantic validators, use TaskRepository.create, return TaskResponse, HTTP 201 with Location header)

**Checkpoint**: User Story 2 complete - POST /tasks endpoint functional and tested

---

## Phase 5: User Story 3 - Retrieve Single Task via API (Priority: P2)

**Goal**: Enable web applications to fetch specific task details by ID via HTTP GET request

**Independent Test**: Can be fully tested by requesting specific task IDs and verifying correct task details returned or 404 for non-existent IDs

### Test for User Story 3

- [ ] T020 [US3] Integration test for GET /tasks/{task_id} endpoint in tests/integration/test_tasks_get_single.py (test_get_task_by_id_returns_200, test_get_task_nonexistent_id_returns_404, test_get_task_invalid_id_format_returns_400)

### Implementation for User Story 3

- [ ] T021 [US3] Implement GET /tasks/{task_id} endpoint in src/api/routers/tasks.py (retrieve task by ID using TaskRepository.get_by_id, return TaskResponse with HTTP 200, raise 404 HTTPException if not found - handled by centralized error handler)

**Checkpoint**: User Story 3 complete - GET /tasks/{task_id} endpoint functional and tested

---

## Phase 6: User Story 4 - Update Task Completion Status via API (Priority: P2)

**Goal**: Enable web applications to toggle task completion status via HTTP PATCH request

**Independent Test**: Can be fully tested by sending PATCH requests to update completion status and verifying changes persist

### Test for User Story 4

- [ ] T022 [US4] Integration test for PATCH /tasks/{task_id} endpoint in tests/integration/test_tasks_update_completion.py (test_patch_task_mark_complete_returns_200, test_patch_task_mark_incomplete_returns_200, test_patch_task_nonexistent_returns_404)

### Implementation for User Story 4

- [ ] T023 [US4] Implement PATCH /tasks/{task_id} endpoint in src/api/routers/tasks.py (partial update for completion status using TaskUpdate schema with Optional fields, use TaskRepository.update with exclude_unset=True, return TaskResponse, HTTP 200 or 404)

**Checkpoint**: User Story 4 complete - PATCH /tasks/{task_id} endpoint functional and tested

---

## Phase 7: User Story 5 - Update Task Details via API (Priority: P3)

**Goal**: Enable web applications to update task title and description via HTTP PUT request

**Independent Test**: Can be fully tested by sending PUT requests with updated data and verifying changes persist with proper validation

### Test for User Story 5

- [ ] T024 [US5] Integration test for PUT /tasks/{task_id} endpoint in tests/integration/test_tasks_update_full.py (test_put_task_update_title_and_description_returns_200, test_put_task_invalid_title_returns_400, test_put_task_nonexistent_returns_404)

### Implementation for User Story 5

- [ ] T025 [US5] Implement PUT /tasks/{task_id} endpoint in src/api/routers/tasks.py (full update with title/description/completion using TaskUpdate schema, use TaskRepository.update, return TaskResponse, HTTP 200 or 400/404)

**Checkpoint**: User Story 5 complete - PUT /tasks/{task_id} endpoint functional and tested

---

## Phase 8: User Story 6 - Delete Task via API (Priority: P3)

**Goal**: Enable web applications to delete tasks via HTTP DELETE request

**Independent Test**: Can be fully tested by sending DELETE requests and verifying tasks are removed and subsequent requests return 404

### Test for User Story 6

- [ ] T026 [US6] Integration test for DELETE /tasks/{task_id} endpoint in tests/integration/test_tasks_delete.py (test_delete_task_returns_204, test_delete_task_verify_404_on_subsequent_get, test_delete_nonexistent_task_returns_404, test_delete_task_idempotent_returns_404)

### Implementation for User Story 6

- [ ] T027 [US6] Implement DELETE /tasks/{task_id} endpoint in src/api/routers/tasks.py (delete task by ID using TaskRepository.delete, return HTTP 204 on success, raise 404 if not found)

**Checkpoint**: User Story 6 complete - DELETE /tasks/{task_id} endpoint functional and tested

---

## Phase 9: User Story 7 - Bulk Delete Tasks via API (Priority: P3)

**Goal**: Enable web applications to delete multiple tasks in a single request via HTTP POST

**Independent Test**: Can be fully tested by sending requests with multiple IDs and verifying all are deleted with proper reporting

### Test for User Story 7

- [ ] T028 [US7] Integration test for POST /tasks/bulk-delete endpoint in tests/integration/test_tasks_bulk_delete.py (test_bulk_delete_all_exist_returns_200, test_bulk_delete_some_not_found_returns_200_with_partial_results, test_bulk_delete_empty_list_returns_400)

### Implementation for User Story 7

- [ ] T029 [US7] Create bulk delete schemas and repository method (BulkDeleteRequest and BulkDeleteResponse in src/api/schemas/task.py with task_ids array, deleted/not_found arrays; add TaskRepository.bulk_delete method in src/database/repository.py that returns success/failure lists)
- [ ] T030 [US7] Implement POST /tasks/bulk-delete endpoint in src/api/routers/tasks.py (accept BulkDeleteRequest, use TaskRepository.bulk_delete, return BulkDeleteResponse with deleted and not_found arrays, HTTP 200)

**Checkpoint**: User Story 7 complete - POST /tasks/bulk-delete endpoint functional and tested

---

## Phase 10: User Story 8 - Protected Endpoints with Session Authentication (Priority: P1)

**Goal**: Secure all task endpoints with session-based authentication via database lookup in shared Neon PostgreSQL

**Independent Test**: Can be fully tested by sending requests with valid/invalid/expired tokens and verifying proper authorization

### Test for User Story 8

- [x] T031 [US8] Integration test for session authentication - valid/invalid/missing tokens in tests/integration/test_auth.py (test_valid_session_token_allows_access, test_missing_token_returns_401, test_invalid_token_returns_401)
- [x] T032 [US8] Integration test for session authentication - expiration and user isolation in tests/integration/test_auth.py (test_expired_token_returns_401, test_revoked_token_returns_401, test_user_cannot_access_other_user_tasks_returns_403)

### Implementation for User Story 8

- [x] T033 [US8] Create session authentication service in src/services/auth_service.py (SessionTokenHasher class with hash_token using HMAC-SHA256, verify_token_against_hash with hmac.compare_digest; validate_session async function querying user_sessions table WHERE token_hash AND expires_at > now AND revoked=false, return user_id UUID or None)
- [x] T034 [US8] Create authentication dependency and middleware (get_current_user dependency in src/api/dependencies.py extracting bearer token, hashing with SESSION_HASH_SECRET from Settings, validating session, returning user_id or raising 401; HTTPBearer security scheme integrated)
- [x] T035 [US8] Add authentication to all task endpoints in src/api/routers/tasks.py (inject current_user: UUID = Depends(get_current_user) to all endpoints; update all endpoint calls to pass user_id to repository methods)
- [x] T036 [US8] Update TaskRepository for user isolation (modify get_all_by_user, get_by_id, create, update, delete, bulk_delete in src/database/repository.py to filter by user_id on all queries; get_by_id verifies ownership)

**Checkpoint**: User Story 8 complete - All endpoints secured with session authentication and user isolation

---

## Phase 11: User Story 9 - Rate Limiting for API Protection (Priority: P2)

**Status**: ⏸️ **BLOCKED - Pending better-auth integration (Feature 004)**

**Reason**: Rate limiting requires real user_id from authenticated sessions. Phase 10 implemented authentication with placeholder compatibility for better-auth. Once better-auth Node.js server is integrated, rate limiting will use actual user_id for user-based tracking (with IP fallback for unauthenticated requests).

**Goal**: Implement rate limiting to prevent abuse and ensure fair resource usage

**Independent Test**: Can be fully tested by sending rapid successive requests and verifying rate limit enforcement

### Test for User Story 9

- [ ] T037 [US9] Integration test for rate limiting in tests/integration/test_rate_limit.py (test_within_rate_limit_allows_requests, test_exceeds_rate_limit_returns_429, test_rate_limit_reset_after_window, test_read_and_write_endpoints_have_different_limits)

### Implementation for User Story 9

- [ ] T038 [US9] Implement rate limiting infrastructure (add slowapi>=0.1.9 and redis>=5.0.0 to pyproject.toml; create src/api/middleware/rate_limit.py with slowapi Limiter using custom key function for user-based tracking with IP fallback and Redis storage; initialize and configure Limiter in src/api/main.py with Redis backend URL from Settings)
- [ ] T039 [US9] Apply rate limit decorators to all task endpoints in src/api/routers/tasks.py (100/minute for GET endpoints, 30/minute for POST/PUT/PATCH/DELETE endpoints using @limiter.limit() decorator)

**Checkpoint**: User Story 9 complete - Rate limiting implemented and tested

---

## Phase 12: Polish & Cross-Cutting Concerns

**Status**: ⏸️ **BLOCKED - Pending better-auth integration and Phase 11 completion**

**Reason**: Polish tasks will be completed after better-auth integration and rate limiting implementation to ensure all production features work together cohesively.

**Purpose**: Improvements that affect multiple user stories and production readiness

- [ ] T040 [P] Add structured logging middleware in src/api/middleware/logging.py (request/response logging with correlation IDs, timing, status codes; error logging in exception handlers)
- [ ] T041 [P] Add request correlation ID middleware in src/api/middleware/request_id.py (generate unique request_id for each request, attach to request.state, include in all log messages and ErrorResponse)
- [ ] T042 [P] Enhance validation error handling in src/api/main.py (custom RequestValidationError handler converting Pydantic validation errors to ErrorResponse format with field-level error details)
- [ ] T043 [P] Add database error handling in src/api/main.py (catch SQLAlchemyError, OperationalError, IntegrityError exceptions, return appropriate ErrorResponse with 500 or 409 status)
- [ ] T044 [P] Add unit tests for TaskRepository in tests/unit/test_repository.py (test all CRUD methods: get_all_by_user, get_by_id, create, update, delete, bulk_delete with mocked AsyncSession)
- [ ] T045 [P] Add unit tests for auth service in tests/unit/test_auth_service.py (test SessionTokenHasher.hash_token, verify_token_against_hash, validate_session with mocked database queries)
- [ ] T046 [P] Add contract tests for Pydantic schemas in tests/contract/test_api_schemas.py (test validation rules for TaskCreate, TaskUpdate, TaskResponse, ErrorResponse, BulkDeleteRequest with valid and invalid inputs)
- [ ] T047 [P] Configure comprehensive OpenAPI documentation (add title, description, version, contact, license to FastAPI app; add tags, summaries, and descriptions to all endpoints in src/api/routers/tasks.py; configure response_model for automatic validation on all endpoints)
- [ ] T048 [P] Add database connection health check to startup (modify lifespan in src/api/main.py to test database connectivity on startup, fail fast with clear error message if database is unreachable)
- [ ] T049 Run end-to-end validation using quickstart.md (verify all steps work: dependencies install with pip, alembic migrations run, uvicorn server starts, /health endpoint responds, /docs accessible, pytest runs all tests successfully)
- [ ] T050 [P] Create production deployment configuration (Dockerfile with multi-stage build using Python 3.12+ slim image; docker-compose.yml for local development with FastAPI app, PostgreSQL, and Redis; .dockerignore)
- [ ] T051 [P] Document API usage and deployment in README.md (authentication flow with session tokens, rate limiting rules, error response format, local development setup, running migrations, environment variables, Docker deployment instructions)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-9)**: All depend on Foundational phase completion
  - US1 (View All Tasks) → US2 (Create Task) → US3 (Get Single Task) can proceed sequentially for basic CRUD
  - US4 (Update Completion) → US5 (Update Details) → US6 (Delete) → US7 (Bulk Delete) can proceed sequentially after US1-3
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

- **Phase 1 (Setup)**: Both tasks can run in parallel if done by different developers
- **Phase 2 (Foundational)**: T006, T008, T009, T013, T014, T015 can run in parallel after T003, T004, T005 complete
- **Phase 12 (Polish)**: T040, T041, T042, T043, T044, T045, T046, T047, T048, T050, T051 can all run in parallel (different files, no dependencies)

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
- **Task Sizing**: All tasks are sized for 15-30 minutes of focused work
- Verify tests fail before implementing (TDD workflow)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- One test per endpoint (unless multiple test scenarios are necessary for comprehensive coverage)
- Follow the user's guidance: endpoints + Neon storage first, then authentication last

---

## Summary

- **Total Tasks**: 51 (reduced from 62)
- **Tasks per Phase**:
  - Phase 1 (Setup): 2 tasks (reduced from 5 by combining)
  - Phase 2 (Foundational): 13 tasks (increased from 12 by adding critical tasks)
  - Phase 3 (US1 - View All): 2 tasks (reduced from 3 by combining router registration)
  - Phase 4 (US2 - Create): 2 tasks (reduced from 3 by combining validation)
  - Phase 5 (US3 - Get Single): 2 tasks (reduced from 3 by using centralized error handling)
  - Phase 6 (US4 - Update Completion): 2 tasks
  - Phase 7 (US5 - Update Details): 2 tasks
  - Phase 8 (US6 - Delete): 2 tasks
  - Phase 9 (US7 - Bulk Delete): 3 tasks (reduced from 4 by combining schema and repository)
  - Phase 10 (US8 - Authentication): 6 tasks (reduced from 8 by splitting large tasks appropriately and combining small ones)
  - Phase 11 (US9 - Rate Limiting): 3 tasks (reduced from 6 by combining setup tasks)
  - Phase 12 (Polish): 12 tasks (increased from 11 by adding production-critical tasks)

- **Improvements**:
  - ✅ All tasks sized for 15-30 minutes of focused work
  - ✅ Eliminated tasks < 15 minutes by combining related work
  - ✅ Split tasks > 30 minutes into manageable chunks
  - ✅ Added missing critical tasks (config, migration execution, test infrastructure, production deployment)
  - ✅ Centralized error handling early in foundational phase
  - ✅ Router registration combined with endpoint implementation
  - ✅ Better test organization with appropriate test groupings

- **Parallel Opportunities**: 18 tasks marked [P] can run in parallel
- **Independent Test Criteria**: Each user story has clear acceptance criteria and can be tested independently
- **Suggested MVP Scope**: Phase 1 (Setup) + Phase 2 (Foundational) + Phase 3 (US1) + Phase 4 (US2) = Basic task viewing and creation via API

---

**Format Validation**: ✅ All tasks follow checklist format: `- [ ] [ID] [P?] [Story?] Description with file path`
**Sizing Validation**: ✅ All tasks are 15-30 minutes of focused work
