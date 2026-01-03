# Tasks: Hybrid JWT Authentication

**Input**: Design documents from `/specs/013-hybrid-jwt-auth/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

**Task Sizing**: Each task is sized for 15-30 minutes of focused work.

**Version**: 2.0 (Refined task sizing based on analysis)

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/src/`, `backend/tests/`
- **Auth-server**: `auth-server/src/`
- **Frontend**: `frontend/src/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency installation

- [X] T001 Install PyJWT library in backend (add to pyproject.toml, run uv sync)
- [X] T002 [P] Install cryptography library in backend (add to pyproject.toml for token hashing)
- [X] T003 [P] Install jsonwebtoken library in auth-server (npm install jsonwebtoken @types/jsonwebtoken)
- [X] T004 Add JWT configuration to backend/src/config.py (JWT_SECRET, JWT_ALGORITHM, JWT_ACCESS_TOKEN_EXPIRE_MINUTES, JWT_REFRESH_TOKEN_EXPIRE_DAYS, JWT_AUTH_ENABLED, JWT_ROLLOUT_PERCENTAGE)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 Create JWT service module in backend/src/services/jwt_service.py with TokenExpiredError and InvalidTokenError exception classes
- [X] T006 Create refresh token service module in backend/src/services/refresh_token_service.py with RefreshTokenError exception class
- [X] T007 Create auth router module in backend/src/api/routers/auth.py with /api/auth prefix
- [X] T008 [P] Create Pydantic schemas in backend/src/api/schemas/auth.py (TokenRefreshResponse, TokenPairResponse)
- [X] T009 [P] Update UserSession SQLAlchemy model in backend/src/models/database.py to map to user_sessions table with camelCase column names
- [X] T010 Create JWT utility module in auth-server/src/lib/jwt.ts with TypeScript interfaces
- [X] T011 Verify user_sessions table exists in Neon PostgreSQL with required schema (userId, token, expiresAt, ipAddress, userAgent columns) via database query
- [X] T012 [P] Create error response schemas in backend/src/api/schemas/auth.py (ErrorResponse with error_code field, TokenExpiredError, RefreshTokenExpiredError, InvalidRefreshTokenError)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Seamless Long-Duration Sessions (Priority: P1) 🎯 MVP

**Goal**: Users stay logged in for 7 days without re-entering credentials

**Independent Test**: Log in, close browser, return after hours/days (within 7 days), confirm tasks accessible without re-authentication

### Implementation for User Story 1

- [X] T013 [P] [US1] Implement generate_access_token() method in backend/src/services/jwt_service.py (creates JWT with sub, iat, exp, type claims, 30-minute expiration)
- [X] T014 [P] [US1] Implement validate_access_token() method in backend/src/services/jwt_service.py (decodes JWT, validates signature and type claim, returns user_id)
- [X] T015 [US1] Implement generate_refresh_token() function in backend/src/services/refresh_token_service.py (32 bytes random via secrets.token_urlsafe)
- [X] T016 [US1] Implement hash_refresh_token() function in backend/src/services/refresh_token_service.py (SHA-256 hash with hashlib)
- [X] T017 [US1] Implement store_refresh_token() method in backend/src/services/refresh_token_service.py (saves hashed token to user_sessions table with 7-day expiration)
- [X] T018 [P] [US1] Add generateAccessToken() function to auth-server/src/lib/jwt.ts (signs JWT with HMAC-SHA256, 30-minute expiration)
- [X] T019 [P] [US1] Add generateRefreshToken() function to auth-server/src/lib/jwt.ts (32 bytes crypto.randomBytes base64url)
- [X] T020 [P] [US1] Add hashRefreshToken() function to auth-server/src/lib/jwt.ts (SHA-256 with crypto.createHash)
- [X] T021 [US1] Modify auth-server login handler to issue JWT access token on successful login (generate and return in response body)
- [X] T022 [US1] Generate and hash refresh token in auth-server login handler (call generateRefreshToken and hashRefreshToken)
- [X] T023 [US1] Store refresh token hash in user_sessions database from auth-server login handler (insert record with userId, token hash, expiresAt, ipAddress, userAgent)
- [X] T024 [US1] Set httpOnly cookie with refresh token in auth-server login response (HttpOnly=true, Secure=true, SameSite=Strict, Max-Age=7 days)
- [X] T025 [P] [US1] Update frontend/src/lib/auth-client.ts to store access token in localStorage on login response
- [X] T026 [P] [US1] Update frontend/src/lib/auth-client.ts to include access token in Authorization header for all API requests
- [X] T027 [US1] Implement get_current_user_jwt() dependency in backend/src/api/dependencies.py (validates JWT access token, returns user_id)
- [X] T028 [US1] Add JWT validation attempt in get_current_user() dependency with feature flag check (try JWT first if JWT_AUTH_ENABLED=true)
- [X] T029 [US1] Add fallback to session validation in get_current_user() when JWT validation fails or is disabled (catch InvalidTokenError, try session auth)
- [X] T030 [US1] Update auth-server signup handler to issue JWT tokens (same flow as login: generate access token, refresh token, hash, store, set cookie)

**Checkpoint**: At this point, User Story 1 should be fully functional - users can login and stay logged in for 7 days with access tokens validated via signature

---

## Phase 4: User Story 2 - Transparent Token Refresh (Priority: P1)

**Goal**: Authentication renews automatically in background without user interruption

**Independent Test**: Use application continuously for 60+ minutes (spanning multiple 30-minute expirations), confirm automatic refresh without interruptions

### Implementation for User Story 2

- [ ] T031 [P] [US2] Implement validate_refresh_token() method in backend/src/services/refresh_token_service.py (hashes incoming token, queries user_sessions, validates expiration, returns user_id)
- [ ] T032 [P] [US2] Implement delete_refresh_token() method in backend/src/services/refresh_token_service.py (deletes session by hashed token)
- [ ] T033 [US2] Create POST /api/auth/refresh endpoint in backend/src/api/routers/auth.py (reads refresh token from httpOnly cookie, validates, issues new access token)
- [ ] T034 [US2] Add error handling to /api/auth/refresh endpoint (401 for expired/invalid/revoked tokens with specific error codes: refresh_token_expired, invalid_refresh_token, session_revoked)
- [ ] T035 [US2] Add HTTP response interceptor infrastructure to frontend/src/lib/api-client.ts (setup axios/fetch interceptor for all API calls)
- [ ] T036 [US2] Implement 401 detection and token_expired error code checking in response interceptor (check response.status === 401 && error_code === "token_expired")
- [ ] T037 [US2] Implement automatic token refresh call in frontend/src/lib/api-client.ts (POST to /api/auth/refresh with credentials: 'include')
- [ ] T038 [US2] Implement request retry logic in frontend/src/lib/api-client.ts (retries original failed request with new access token after successful refresh)
- [ ] T039 [US2] Implement exponential backoff retry in frontend/src/lib/api-client.ts (3 attempts with 1s, 2s, 4s delays for network errors)
- [ ] T040 [US2] Add error type detection in frontend/src/lib/api-client.ts (distinguish auth errors 401/403 that skip retries vs network errors 500/503 that retry)
- [ ] T041 [US2] Create useTokenRefresh hook skeleton in frontend/src/hooks/useTokenRefresh.ts with BroadcastChannel initialization
- [ ] T042 [US2] Implement refreshToken() function in useTokenRefresh hook (fetch call to /api/auth/refresh with credentials, return new access token)
- [ ] T043 [US2] Implement cross-tab lock acquisition in useTokenRefresh hook (timestamp-based lock in localStorage with 5-second expiry, unique tabId)
- [ ] T044 [US2] Implement token refresh broadcast in useTokenRefresh hook (BroadcastChannel.postMessage with new access token on successful refresh)
- [ ] T045 [US2] Implement cross-tab token listener in useTokenRefresh hook (BroadcastChannel.onmessage updates localStorage access token when other tab refreshes)
- [ ] T046 [US2] Add localStorage fallback for cross-tab sync in useTokenRefresh hook (storage event listener for browsers without BroadcastChannel support)
- [ ] T047 [US2] Configure CORS middleware in backend/src/api/main.py to allow credentials (allow_credentials=True, allow_origins from config for refresh endpoint)
- [ ] T048 [US2] Implement token validation on app initialization in frontend (check if access token exists and valid on app load, trigger refresh if expired but refresh token cookie present)
- [ ] T049 [US2] Create SessionExpired component in frontend/src/components/SessionExpired.tsx to show user-friendly message when all refresh retries fail (with login button)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - users stay logged in for 7 days with automatic seamless token refresh every 30 minutes

---

## Phase 5: User Story 3 - Explicit Logout (Priority: P2)

**Goal**: Users can explicitly log out to secure account on shared/public computers

**Independent Test**: Log in, click logout, confirm all subsequent requests require re-authentication

### Implementation for User Story 3

- [ ] T050 [P] [US3] Create POST /api/auth/logout endpoint in backend/src/api/routers/auth.py (requires valid JWT access token in Authorization header)
- [ ] T051 [US3] Implement logout logic in backend to delete refresh token from user_sessions table by user_id (call delete_refresh_token service method)
- [ ] T052 [US3] Add response to clear refresh token httpOnly cookie in logout endpoint (Set-Cookie with Max-Age=0, same path and domain)
- [ ] T053 [US3] Implement frontend logout flow in frontend/src/lib/auth-client.ts (call backend /api/auth/logout endpoint, clear localStorage access token on success, redirect to login page)

**Checkpoint**: All core user stories (US1, US2, US3) should now be independently functional - login, auto-refresh, and logout all work

---

## Phase 6: User Story 4 - Performance and Scalability (Priority: P3)

**Goal**: Authentication imposes minimal database load to support 1000+ concurrent users

**Independent Test**: Load test with 1000+ concurrent users, confirm auth queries <5/sec (vs 167/sec baseline)

### Implementation for User Story 4

- [ ] T054 [P] [US4] Add Prometheus metrics histogram in backend/src/services/jwt_service.py (auth_validation_seconds with method='jwt' label)
- [ ] T055 [P] [US4] Add Prometheus metrics histogram in backend/src/services/auth_service.py (auth_validation_seconds with method='session' label for comparison)
- [ ] T056 [P] [US4] Add Prometheus counter in backend/src/api/routers/auth.py for token refresh calls (token_refresh_total)
- [ ] T057 [P] [US4] Add Prometheus counter in backend/src/api/routers/auth.py for failed refreshes (token_refresh_errors_total with reason label: expired/invalid/revoked)
- [ ] T058 [US4] Implement feature flag check method should_use_jwt(user_id) in backend/src/config.py (hash-based cohort assignment using MD5 for stable rollout based on JWT_ROLLOUT_PERCENTAGE)
- [ ] T059 [US4] Update hybrid auth dependency to use should_use_jwt() for rollout percentage logic in backend/src/api/dependencies.py
- [ ] T060 [P] [US4] Add structured logging for token refresh events in backend/src/api/routers/auth.py (user_id, timestamp, ip_address, success/failure status)
- [ ] T061 [P] [US4] Add structured logging for logout events in backend/src/api/routers/auth.py (user_id, timestamp, session_identifier)
- [ ] T062 [US4] Create load testing script in tests/load/jwt_auth_load_test.py using locust or k6 (simulates 1000 concurrent users making API requests, measures auth queries/sec and latency)

**Checkpoint**: All user stories complete with performance monitoring and gradual rollout capability

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

### Tests

- [ ] T063 [P] Add contract test for generate_access_token() in backend/tests/contract/test_jwt_service.py (verifies JWT contains sub, iat, exp, type claims with correct values)
- [ ] T064 [P] Add contract test for validate_access_token() in backend/tests/contract/test_jwt_service.py (verifies expired token rejection with TokenExpiredError)
- [ ] T065 [P] Add contract test for hash_refresh_token() in backend/tests/contract/test_refresh_token_service.py (verifies SHA-256 output format is 64 hex characters)
- [ ] T066 [P] Add contract test for validate_refresh_token() in backend/tests/contract/test_refresh_token_service.py (verifies hash comparison with constant-time and expiration check)
- [ ] T067 [P] Add integration test for full refresh flow in backend/tests/integration/test_token_refresh_flow.py (login → access token expires → refresh → new token works → make authenticated request)
- [ ] T068 [P] Add integration test for hybrid auth migration in backend/tests/integration/test_hybrid_auth_migration.py (both JWT and session auth work simultaneously with feature flag)
- [ ] T069 [P] Add unit test for JWT signature validation in backend/tests/unit/test_jwt_validation.py (invalid signature rejection, algorithm substitution attack prevention)
- [ ] T070 [P] Add unit test for token expiration edge cases in backend/tests/unit/test_jwt_validation.py (exactly expired timestamp, 1 second before expiration)
- [ ] T071 [P] Create Playwright test file in frontend/tests/integration/token-refresh.spec.ts with test setup and authentication flow
- [ ] T072 Implement token expiration simulation and auto-refresh verification in Playwright test (mock time advance to 30 minutes, verify refresh endpoint called, verify request succeeds)

### Documentation

- [ ] T073 Update quickstart.md Troubleshooting section with actual errors encountered, deployment results, and performance measurements from load testing
- [ ] T074 [P] Add example .env files to backend/.env.example, auth-server/.env.example, and frontend/.env.local.example with all JWT configuration variables and comments

### Quality Checks

- [ ] T075 Run all backend tests and verify 100% pass rate (uv run pytest backend/tests/ -v --cov)
- [ ] T076 [P] Run linting and type checking on backend (ruff check backend/src, mypy backend/src)
- [ ] T077 [P] Run linting and type checking on auth-server (cd auth-server && npm run lint && npm run type-check)
- [ ] T078 [P] Run linting and type checking on frontend (cd frontend && npm run lint && npm run type-check)

### Security Reviews

- [ ] T079 [P] Security review: Verify JWT_SECRET is minimum 32 characters in all environments (.env files, deployment configs)
- [ ] T080 [P] Security review: Verify httpOnly cookie attributes in auth-server response (HttpOnly=true, Secure=true in production, SameSite=Strict)
- [ ] T081 [P] Security review: Verify refresh token hashing uses constant-time comparison (hmac.compare_digest) in backend/src/services/refresh_token_service.py

### Performance Reviews

- [ ] T082 Performance review: Run load test with 1000 concurrent users and measure auth validation time (target: <1ms p95 for JWT validation)
- [ ] T083 Performance review: Measure database auth query rate during load test (target: <5 queries/sec for auth operations vs 167/sec baseline)

### Operational

- [ ] T084 [P] Create database cleanup script in backend/scripts/cleanup_expired_tokens.py (deletes user_sessions where expiresAt < now(), intended for daily cron job)
- [ ] T085 [P] Create Prometheus alert rules configuration file alerts/jwt_auth_alerts.yaml (high validation latency >1ms, refresh error rate >1%, token table growth >100MB)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P1 → P2 → P3)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - Builds on US1 (requires access token generation from T013-T014) but adds independent refresh capability
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - Requires refresh token storage from US1 (T017) but logout is independently testable
- **User Story 4 (P3)**: Can start after Foundational (Phase 2) - Performance monitoring can be added in parallel to implementation

### Within Each User Story

**User Story 1** (Login with long-lived sessions):
- T013, T014 can run in parallel (JWT generation and validation - different methods)
- T015, T016 can run in parallel (refresh token generation and hashing - different functions)
- T017 depends on T015, T016 (storage needs generation and hashing functions)
- T018, T019, T020 can run in parallel (auth-server JWT utilities - different functions)
- T021 depends on T018 (login handler needs generateAccessToken)
- T022 depends on T019, T020 (needs generateRefreshToken and hashRefreshToken)
- T023 depends on T022 (storing needs hash generation)
- T024 depends on T023 (cookie setting happens after storage)
- T025, T026 can run in parallel (frontend token storage - different concerns)
- T027, T028, T029 must be sequential (create dependency → add JWT attempt → add fallback)
- T030 independent (signup handler similar to login)

**User Story 2** (Auto-refresh):
- T031, T032 can run in parallel (refresh validation and deletion - different methods)
- T033 depends on T031 (endpoint needs validation)
- T034 depends on T033 (error handling added to endpoint)
- T035, T036 must be sequential (interceptor setup → detection logic)
- T037 depends on T036 (refresh call happens after detection)
- T038 depends on T037 (retry depends on refresh)
- T039, T040 can run in parallel (retry enhancements - orthogonal concerns)
- T041, T042 must be sequential (hook skeleton → refresh function)
- T043, T044, T045, T046 must be sequential (lock → broadcast → listen → fallback)
- T047, T048, T049 can run in parallel (CORS, app init, UI component - different files)

**User Story 3** (Logout):
- T050, T051, T052 must be sequential (endpoint → delete logic → clear cookie)
- T053 depends on T050-T052 (frontend logout calls backend endpoint)

**User Story 4** (Performance):
- T054, T055, T056, T057 can all run in parallel (different metrics in different files)
- T058, T059 must be sequential (feature flag method → use in dependency)
- T060, T061 can run in parallel (different logging events)
- T062 independent (load test script)

**Polish**:
- T063-T070 can all run in parallel (different test files)
- T071, T072 must be sequential (test file setup → test implementation)
- T073, T074 can run in parallel (different documentation)
- T075-T078 can run in parallel (different services/checks)
- T079-T081 can run in parallel (different security checks)
- T082, T083 can run in parallel (different performance metrics)
- T084, T085 can run in parallel (different operational tasks)

### Parallel Opportunities

**Setup Phase (4 parallel groups)**:
- T001, T002 (backend dependencies)
- T003 (auth-server dependency)
- T004 (config - can run after T001-T002)

**Foundational Phase (3 parallel groups)**:
- T005, T006, T007 (different service modules)
- T008, T009, T012 (different schemas/models)
- T010, T011 (auth-server setup and DB verification)

**User Story 1 (6 parallel groups)**:
- Group 1: T013, T014 (JWT methods)
- Group 2: T015, T016 (refresh token utilities)
- Group 3: T018, T019, T020 (auth-server utilities)
- Group 4: T025, T026 (frontend token handling)
- Others sequential

**User Story 2 (5 parallel groups)**:
- Group 1: T031, T032 (refresh service methods)
- Group 2: T039, T040 (retry enhancements)
- Group 3: T047, T048, T049 (CORS, init, UI)
- Others sequential

**User Story 4 (3 parallel groups)**:
- Group 1: T054, T055, T056, T057 (all metrics)
- Group 2: T060, T061 (logging events)
- Group 3: T062 (load test)

**Polish (multiple parallel groups)**:
- Tests: T063-T072 can mostly run in parallel (11 test files)
- Docs: T073, T074
- Quality: T075-T078 (4 different checks)
- Security: T079-T081
- Performance: T082, T083
- Operational: T084, T085

---

## Parallel Example: User Story 1

```bash
# Launch JWT service methods in parallel (different methods in same file):
Task T013: "Implement generate_access_token() method"
Task T014: "Implement validate_access_token() method"

# Launch refresh token utilities in parallel (different functions):
Task T015: "Implement generate_refresh_token() function"
Task T016: "Implement hash_refresh_token() function"

# Launch auth-server JWT utilities in parallel (different functions):
Task T018: "Add generateAccessToken() function"
Task T019: "Add generateRefreshToken() function"
Task T020: "Add hashRefreshToken() function"

# Launch frontend token storage in parallel (different concerns):
Task T025: "Update auth-client.ts to store access token"
Task T026: "Update auth-client.ts to include token in headers"
```

---

## Parallel Example: User Story 4 (Performance Metrics)

```bash
# Launch all Prometheus metrics in parallel (different services/files):
Task T054: "Add JWT validation histogram in jwt_service.py"
Task T055: "Add session validation histogram in auth_service.py"
Task T056: "Add refresh counter in auth.py"
Task T057: "Add refresh errors counter in auth.py"

# Launch logging tasks in parallel (different events):
Task T060: "Add token refresh event logging"
Task T061: "Add logout event logging"
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only)

1. Complete Phase 1: Setup (T001-T004) - ~20 minutes
2. Complete Phase 2: Foundational (T005-T012) - ~2 hours
3. Complete Phase 3: User Story 1 (T013-T030) - ~5 hours
4. Complete Phase 4: User Story 2 (T031-T049) - ~6 hours
5. **STOP and VALIDATE**: Test login, auto-refresh, and 7-day sessions
6. Deploy/demo if ready

**MVP Total**: 46 tasks (~13-14 hours of focused implementation)

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready (~2.5 hours)
2. Add User Story 1 → Test independently → Deploy/Demo (~5 hours, 7-day sessions working)
3. Add User Story 2 → Test independently → Deploy/Demo (~6 hours, MVP complete with auto-refresh!)
4. Add User Story 3 → Test independently → Deploy/Demo (~1 hour, logout capability)
5. Add User Story 4 → Test independently → Deploy/Demo (~2.5 hours, performance monitoring)
6. Add Polish → Final validation → Production ready (~6 hours, comprehensive testing)
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. **Team completes Setup + Foundational together** (~2.5 hours)
2. **Once Foundational is done, split work**:
   - **Developer A**: User Story 1 backend (T013-T017, T027-T029)
   - **Developer B**: User Story 1 auth-server + frontend (T018-T026, T030)
   - **Developer C**: User Story 2 backend (T031-T034)
   - **Developer D**: User Story 2 frontend (T035-T049)
   - **Developer E**: User Story 3 + User Story 4 (T050-T062)
3. Stories complete and integrate independently
4. **Polish phase**: Divide test writing, reviews, and operational tasks

---

## Notes

- **Task Sizing**: All tasks sized for 15-30 minutes of focused implementation
  - Small, concrete tasks (e.g., "add one function", "update one handler")
  - No task spans multiple files unless they're tightly coupled (e.g., T053 logout flow)
  - Tests are separate tasks from implementation
- **[P] tasks** = different files, methods, or orthogonal concerns - no dependencies
- **[Story] label** maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group (2-3 related tasks)
- Stop at any checkpoint to validate story independently
- **Total tasks**: 85 (avg 17 minutes each = ~24 hours of implementation time)
- **Critical path**: Phase 1 → Phase 2 → US1 → US2 (minimum viable product = 46 tasks)
- **Feature flags**: JWT_AUTH_ENABLED and JWT_ROLLOUT_PERCENTAGE enable gradual rollout (0% → 10% → 25% → 50% → 100%)

---

## Summary

- **Total Tasks**: 85 (revised from 72)
- **Setup**: 4 tasks (T001-T004)
- **Foundational**: 8 tasks (T005-T012) - added schema verification and error schemas
- **User Story 1** (7-day sessions): 18 tasks (T013-T030) - split login handler and hybrid auth logic
- **User Story 2** (Auto-refresh): 19 tasks (T031-T049) - split interceptor setup, added CORS, app init, session expired UI
- **User Story 3** (Logout): 4 tasks (T050-T053) - combined frontend logout flow
- **User Story 4** (Performance): 9 tasks (T054-T062) - added load testing script
- **Polish**: 23 tasks (T063-T085) - split E2E test, added cleanup script and alert rules

**MVP Scope** (Phase 1+2+US1+US2): 4 + 8 + 18 + 19 = **49 tasks** (~14-15 hours)

**Full Feature**: All phases = 85 tasks (~24-25 hours)

**Key Improvements**:
- Split oversized tasks (T020, T024, T029, T034, T061) into 15-30 minute units
- Combined undersized tasks (T042-T044 → single logout flow)
- Added missing infrastructure (CORS, error schemas, app init, cleanup, alerts)
- Added missing tests and operational tasks
- Clarified dependencies and parallel opportunities
