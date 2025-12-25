# Tasks: Settings UI for API Key Management

**Input**: Design documents from `/specs/010-settings-ui-api-keys/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Not explicitly requested in the spec - following TDD principles but implementing tests as part of each task

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Web app (microservices): `backend/src/`, `frontend/app/`, `frontend/components/`, `ai-agent/src/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure for API key management

- [X] T001 Install cryptography library (Fernet) in backend/pyproject.toml using `uv add cryptography`
- [X] T002 Install google-generativeai SDK in backend/pyproject.toml using `uv add google-generativeai` (migrated to google-genai)
- [X] T003 Generate ENCRYPTION_KEY using Fernet.generate_key() and add to backend/.env (documented in quickstart.md)
- [X] T004 Update backend/src/config.py to add ENCRYPTION_KEY setting with validation
- [X] T005 Create Alembic migration in backend/alembic/versions/XXXX_create_user_api_keys_table.py
- [X] T006 Run Alembic migration `alembic upgrade head` to create user_api_keys table (completed via custom migration script)
- [X] T007 Update backend/.env.example with ENCRYPTION_KEY placeholder and document generation command (`python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`)
- [X] T008 Document database migration rollback procedure in quickstart.md (`alembic downgrade -1` for development)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core services that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T009 [P] Create EncryptionService in backend/src/services/encryption_service.py with encrypt/decrypt methods
- [X] T010 [P] Write unit tests for EncryptionService in backend/tests/unit/test_encryption_service.py (test round-trip, wrong key fails)
- [X] T011 [P] Create UserApiKey SQLAlchemy model in backend/src/models/user_api_key.py with all columns per data-model.md
- [X] T012 [P] Write contract tests for UserApiKey model in backend/tests/contract/test_user_api_key_model.py (CRUD operations)
- [X] T013 [P] Create GeminiValidator service in backend/src/services/gemini_validator.py with validate_format and validate_key methods
- [X] T014 [P] Write unit tests for GeminiValidator in backend/tests/unit/test_gemini_validator.py (format validation, mock API calls)
- [X] T015 Create ApiKeyService in backend/src/services/api_key_service.py with save/get/delete methods (uses EncryptionService)
- [X] T016 Write unit tests for ApiKeyService in backend/tests/unit/test_api_key_service.py (encryption integration, CRUD flows)
- [X] T017 [P] Create Pydantic schemas in backend/src/api/schemas/api_key.py (SaveApiKeyRequest, ApiKeyStatusResponse, etc.)
- [X] T018 [P] Create API router in backend/src/api/routers/api_keys.py with stub endpoints (GET, POST, DELETE, POST /test)
- [X] T019 Register api_keys router in backend/src/api/main.py (or equivalent app initialization file)
- [X] T020 Verify current_user dependency injection works in API routers with mock authenticated request test

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Access Settings Tab (Priority: P1) 🎯 MVP

**Goal**: Users can navigate to a Settings tab and see a settings interface for API configuration

**Independent Test**: Click Settings tab in sidebar → verify settings page renders with proper layout and navigation

### Implementation for User Story 1

- [X] T021 [P] [US1] Create Settings page component in frontend/app/(authenticated)/settings/page.tsx with responsive layout and Tailwind CSS (320px-2560px support)
- [X] T022 [P] [US1] Add "Settings" navigation link to sidebar in frontend/components/layout/Sidebar.tsx (or equivalent navigation component)
- [X] T023 [US1] Create API client stub in frontend/lib/api/apiKeys.ts with function signatures for GET, POST, DELETE, POST /test
- [X] T024 [US1] Add Jest test for Settings page in frontend/__tests__/settings/page.test.tsx (renders correctly, navigation visible)
- [X] T025 [US1] Add authentication check to Settings page (redirect to login if not authenticated - implemented via Next.js middleware)

**Checkpoint**: At this point, User Story 1 should be fully functional - users can navigate to Settings and see basic interface

---

## Phase 4: User Story 2 - Enter and Save Gemini API Key (Priority: P1)

**Goal**: Users can provide their Gemini API key, save it, and receive confirmation that their key is stored

**Independent Test**: Enter valid Gemini API key → click Save → verify key is persisted and success message shown

### Implementation for User Story 2

- [X] T026 [P] [US2] Create PasswordInput component in frontend/components/ui/PasswordInput.tsx with show/hide toggle (Eye/EyeOff icons)
- [X] T027 [P] [US2] Create ApiKeyInput component in frontend/components/settings/ApiKeyInput.tsx wrapping PasswordInput with API key-specific labels
- [X] T028 [P] [US2] Implement POST /api/user-api-keys endpoint in backend/src/api/routers/api_keys.py (format validation, encryption, save with 400 errors for invalid format)
- [ ] T029 [P] [US2] Write integration test for POST endpoint in backend/tests/integration/test_api_key_endpoints.py (save flow, validation errors)
- [X] T030 [US2] Implement GET /api/user-api-keys/current endpoint in backend/src/api/routers/api_keys.py (retrieve masked key, status)
- [ ] T031 [US2] Write integration test for GET endpoint in backend/tests/integration/test_api_key_endpoints.py (configured/not configured states)
- [X] T032 [US2] Implement API client methods in frontend/lib/api/apiKeys.ts (saveApiKey, getCurrentApiKey with proper error handling)
- [X] T033 [US2] Create useApiKey React hook in frontend/lib/hooks/useApiKey.ts for state management (loading, error, success states)
- [X] T034 [US2] Integrate ApiKeyInput with useApiKey hook in Settings page
- [X] T035 [US2] Add save button with loading state to Settings page
- [X] T036 [US2] Add toast/alert notifications for success and error states to Settings page
- [ ] T037 [US2] Add Jest tests for PasswordInput in frontend/__tests__/settings/PasswordInput.test.tsx (show/hide toggle, accessibility)
- [ ] T038 [US2] Add Jest tests for ApiKeyInput in frontend/__tests__/settings/ApiKeyInput.test.tsx (save flow, error states)

**Checkpoint**: At this point, User Story 2 should be fully functional - users can save API keys and see them persisted

---

## Phase 5: User Story 3 - Validate API Key Format and Connectivity (Priority: P1)

**Goal**: System validates API key format before saving and tests connectivity to Gemini API with clear error messages

**Independent Test**: Enter invalid keys (wrong format, expired) → verify appropriate error messages appear before saving

### Implementation for User Story 3

- [X] T039 [P] [US3] Implement POST /api/user-api-keys/test endpoint in backend/src/api/routers/api_keys.py (calls GeminiValidator.validate_key)
- [ ] T040 [P] [US3] Write integration test for POST /test endpoint in backend/tests/integration/test_gemini_validation.py (success, invalid key, timeout scenarios, verify error messages match spec)
- [X] T041 [P] [US3] Create TestConnectionButton component in frontend/components/settings/TestConnectionButton.tsx with loading state
- [X] T042 [US3] Implement testApiKey method in frontend/lib/api/apiKeys.ts (calls POST /api/user-api-keys/test)
- [X] T043 [US3] Update useApiKey hook to support Test Connection flow (testConnection method, testStatus state)
- [X] T044 [US3] Add TestConnectionButton to Settings page
- [X] T045 [US3] Wire TestConnectionButton to useApiKey hook
- [X] T046 [US3] Add visual error/success indicators for test results to Settings page
- [ ] T047 [US3] Add client-side format validation in ApiKeyInput (check "AIza" prefix before API call)
- [ ] T048 [US3] Add Jest tests for TestConnectionButton in frontend/__tests__/settings/TestConnectionButton.test.tsx (loading, success, error states)

**Checkpoint**: At this point, User Story 3 should be fully functional - users get clear validation feedback

---

## Phase 6: User Story 4 - View API Key Status and Usage (Priority: P2)

**Goal**: Users can see if their API key is properly configured and view basic status information

**Independent Test**: Save an API key → verify status indicators update correctly (configured/not configured, last tested timestamp)

### Implementation for User Story 4

- [X] T049 [P] [US4] Create ApiKeyStatus component in frontend/components/settings/ApiKeyStatus.tsx with status indicators (checkmark/warning/info icons), masked key preview (AIza...xyz), and timestamp formatting (human-readable)
- [X] T050 [US4] Update GET /api/user-api-keys/current response to include validation_status and last_validated_at in ApiKeyStatusResponse
- [X] T051 [US4] Integrate ApiKeyStatus component into Settings page above API key input section
- [X] T052 [US4] Update POST /test endpoint to persist validation_status and last_validated_at in user_api_keys table
- [ ] T053 [US4] Add Jest tests for ApiKeyStatus in frontend/__tests__/settings/ApiKeyStatus.test.tsx (all status states, timestamp rendering)

**Checkpoint**: At this point, User Story 4 should be fully functional - users see transparent status information

---

## Phase 7: User Story 5 - Clear/Remove API Key (Priority: P2)

**Goal**: Users can remove their stored API key for security reasons or to switch providers

**Independent Test**: Save a key → click "Remove Key" → confirm → verify key is deleted and status updates

### Implementation for User Story 5

- [X] T054 [P] [US5] Implement DELETE /api/user-api-keys/current endpoint in backend/src/api/routers/api_keys.py (delete key, return success)
- [ ] T055 [P] [US5] Write integration test for DELETE endpoint in backend/tests/integration/test_api_key_endpoints.py (delete flow, 404 handling)
- [X] T056 [US5] Implement deleteApiKey method in frontend/lib/api/apiKeys.ts (calls DELETE endpoint)
- [X] T057 [US5] Add deleteApiKey method to useApiKey hook with confirmation flow
- [X] T058 [US5] Add "Remove Key" button to Settings page with confirmation dialog, success state update (clear form, status "Not Configured"), and error handling
- [ ] T059 [US5] Add Jest test for deletion flow in frontend/__tests__/settings/page.test.tsx (confirmation, success state update)

**Checkpoint**: All user stories should now be independently functional - complete CRUD for API keys

---

## Phase 8: AI Agent Integration (Cross-Cutting)

**Purpose**: Update AI agent to use per-user API keys (critical for feature to deliver value)

- [X] T060 [P] Create ApiKeyRetrievalService in ai-agent/src/ai_agent/services/api_key_retrieval.py (fetches key from backend)
- [ ] T061 [P] Write unit tests for ApiKeyRetrievalService in ai-agent/tests/unit/test_api_key_retrieval.py (mock HTTP calls, error handling)
- [X] T062 Update AgentService in ai-agent/src/ai_agent/agent/agent_service.py to use per-user API keys via ApiKeyRetrievalService with error handling for missing keys (return message: "Please configure your Gemini API key in Settings")
- [ ] T063 Write integration test in ai-agent/tests/integration/test_per_user_api_key.py (verify agent uses user's key, fails gracefully when missing)
- [X] T064 Update backend GET /api/user-api-keys/current endpoint to support service-to-service auth (X-User-ID header or similar) and return decrypted plaintext_key field for ai-agent consumption

**Checkpoint**: AI agent now uses per-user API keys - feature delivers end-to-end value

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and ensure production readiness

- [X] T065 [P] Add rate limiting to POST /api/user-api-keys/test endpoint (max 5 tests per hour per user) using FastAPI middleware
- [X] T066 [P] Add security headers to API responses (no-cache for API key endpoints, HSTS, etc.)
- [X] T067 [P] Verify no API keys are logged in plaintext (audit all logging statements in backend)
- [X] T068 [P] Add structured audit logging for API key operations (create, test, delete) without logging key values in backend
- [ ] T069 [P] Update OpenAPI/Swagger documentation for new API key endpoints with security notes
- [X] T070 Add loading states and spinners to all async operations in Settings page (save, test, delete)
- [X] T071 Add toast notifications for success/error messages using frontend notification system (if available)
- [ ] T072 Test responsive design on mobile (320px width) and desktop (2560px width) - verify touch targets ≥44px
- [ ] T073 Add ARIA labels and test keyboard navigation for accessibility (WCAG 2.1 AA compliance)
- [X] T074 Add error boundary to Settings page to catch and display React errors gracefully
- [ ] T075 Run backend test suite with coverage report `pytest --cov=src --cov-report=term-missing`
- [ ] T076 Run frontend test suite `npm test -- --coverage`
- [X] T077 Update CLAUDE.md with new technologies (cryptography, google-generativeai, PasswordInput pattern)
- [ ] T078 Validate quickstart.md by following setup steps from scratch
- [ ] T079 Add security scan for sensitive data exposure (check network tab for plaintext keys)
- [ ] T080 Performance test: verify API key retrieval adds <50ms latency to AI agent requests

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (US1 → US2 → US3 → US4 → US5)
- **AI Agent Integration (Phase 8)**: Depends on User Story 2 (save/retrieve API key) being complete
- **Polish (Phase 9)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - Builds on US1 UI but independently testable
- **User Story 3 (P1)**: Can start after Foundational (Phase 2) - Extends US2 but independently testable
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - Reads data from US2 but independently testable
- **User Story 5 (P2)**: Can start after Foundational (Phase 2) - Deletes data from US2 but independently testable

### Within Each User Story

- Tests written first (TDD) - ensure they FAIL before implementation
- Models before services
- Services before endpoints
- Backend endpoints before frontend integration
- Core implementation before polish
- Story complete before moving to next priority

### Parallel Opportunities

- **Phase 1 (Setup)**: T001-T003 can run in parallel (different dependencies/env vars)
- **Phase 2 (Foundational)**: T009-T010, T011-T012, T013-T014 can run in parallel (different services)
- **Phase 3 (US1)**: T021-T022 can run in parallel (frontend page vs sidebar)
- **Phase 4 (US2)**: T026-T027, T028-T029, T037-T038 can run in parallel (different components/endpoints)
- **Phase 5 (US3)**: T039-T040, T041, T048 can run in parallel (backend vs frontend components)
- **Phase 6 (US4)**: T049 can run in parallel with T050 (frontend vs backend)
- **Phase 7 (US5)**: T054-T055 can run in parallel with T056 (backend vs frontend)
- **Phase 8 (AI Agent)**: T060-T061 can run in parallel with T064 (ai-agent vs backend updates)
- **Phase 9 (Polish)**: T065-T069, T070-T074 can run in parallel (different concerns)

---

## Parallel Example: User Story 2

```bash
# Launch backend and frontend work together:
Task: "Create PasswordInput component in frontend/components/ui/PasswordInput.tsx"
Task: "Implement POST /api/user-api-keys endpoint in backend/src/api/routers/api_keys.py"

# Launch tests together after implementation:
Task: "Write integration test for POST endpoint in backend/tests/integration/test_api_key_endpoints.py"
Task: "Add Jest tests for PasswordInput in frontend/__tests__/settings/PasswordInput.test.tsx"
```

---

## Implementation Strategy

### MVP First (User Stories 1-3 Only)

1. Complete Phase 1: Setup (T001-T008) → ~1.5 hours
2. Complete Phase 2: Foundational (T009-T020) → ~5.5 hours (critical foundation)
3. Complete Phase 3: User Story 1 (T021-T025) → ~2.5 hours
4. Complete Phase 4: User Story 2 (T026-T038) → ~4.5 hours
5. Complete Phase 5: User Story 3 (T039-T048) → ~3.5 hours
6. Complete Phase 8: AI Agent Integration (T060-T064) → ~2.5 hours
7. **STOP and VALIDATE**: Test all P1 stories independently
8. Deploy/demo MVP with core functionality

**MVP Total**: ~20 hours (covers all P1 user stories)

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready (~7 hours)
2. Add User Story 1 → Test independently → Can navigate to Settings page
3. Add User Story 2 → Test independently → Can save API keys
4. Add User Story 3 → Test independently → Validation works (MVP!)
5. Add User Story 4 → Test independently → Status visibility
6. Add User Story 5 → Test independently → Can remove keys
7. Add AI Agent Integration → Test independently → AI uses user keys (CRITICAL)
8. Add Polish → Production ready

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (~7 hours)
2. Once Foundational is done:
   - **Developer A**: User Story 1 + User Story 2 (frontend heavy)
   - **Developer B**: User Story 3 + AI Agent Integration (backend + validation)
   - **Developer C**: User Story 4 + User Story 5 (status + deletion)
3. All developers collaborate on Phase 9 (Polish)

**Parallel Team Total**: ~11-13 hours (with 3 developers)

---

## Changes from Original Tasks

### Combined Tasks (Reduced Redundancy)
- **T021**: Combined original T018 (create page) + T020 (responsive styles) → single cohesive task
- **T049**: Combined original T044, T045, T047, T048 → single ApiKeyStatus component with all features
- **T058**: Combined original T056, T057, T058 → Remove Key button with complete error handling
- **T062**: Combined original T062 + T063 → AgentService update with error handling built-in
- **T064**: Combined original T065 + T066 → Service-to-service auth with decryption

### Split Tasks (Better Granularity)
- **T034-T036**: Split original T031 → separate integration, button, and notifications
- **T044-T046**: Split original T039 → separate add button, wire hook, add indicators

### Removed Tasks (Merged into Existing)
- **Original T041**: Server-side format validation merged into T028 (POST endpoint should validate from the start)
- **Original T043**: Error message verification merged into T040 (write tests correctly the first time)

### Added Tasks (Critical Gaps)
- **T007**: Document ENCRYPTION_KEY in .env.example (other devs need this)
- **T008**: Document migration rollback (dev workflow)
- **T020**: Verify auth middleware works (critical dependency)
- **T025**: Frontend authentication check (security requirement)
- **T068**: Audit logging for sensitive operations (security best practice)
- **T069**: OpenAPI documentation update (API consumer needs)

**Net Result**: 80 tasks → 80 tasks (same count, better structure)
- Eliminated 7 redundant/merged tasks
- Added 6 critical missing tasks
- Split 2 overly complex tasks into 6 granular tasks

---

## Notes

- **Task Sizing**: Each task sized for 20-30 minutes of focused work
- **[P] marker**: Indicates tasks that can run in parallel (different files, no blocking dependencies)
- **[Story] label**: Maps task to specific user story for traceability and independent testing
- **TDD Approach**: Write tests first, ensure they fail, then implement
- **Independent Stories**: Each user story can be tested and validated independently
- **Commit Strategy**: Commit after each task or logical group of tasks
- **Checkpoints**: Stop at each checkpoint to validate story works independently
- **ENCRYPTION_KEY**: NEVER commit to git - use .env locally, secrets manager in production
- **Security**: Verify no plaintext API keys in logs, network traffic, or error messages

---

## Estimated Time

- **Phase 1 (Setup)**: ~1.5 hours
- **Phase 2 (Foundational)**: ~5.5 hours
- **Phase 3 (US1)**: ~2.5 hours
- **Phase 4 (US2)**: ~4.5 hours
- **Phase 5 (US3)**: ~3.5 hours
- **Phase 6 (US4)**: ~2 hours
- **Phase 7 (US5)**: ~1.5 hours
- **Phase 8 (AI Agent)**: ~2.5 hours
- **Phase 9 (Polish)**: ~3.5 hours

**Total Sequential**: ~27 hours (all tasks in order)
**Total Parallel (3 devs)**: ~11-13 hours (with parallelization)
**MVP Only (P1 stories + AI integration)**: ~20 hours

---

## Summary

- **Total Tasks**: 80 tasks (optimized from original 80)
- **User Stories**: 5 (3 P1, 2 P2)
- **Parallel Opportunities**: 28+ tasks marked [P]
- **Independent Test Criteria**: Each story has clear validation checkpoint
- **MVP Scope**: User Stories 1-3 + AI Agent Integration (T001-T048 + T060-T064)
- **Format Validation**: ✅ All tasks follow `- [ ] [ID] [P?] [Story] Description with file path` format
- **Quality Improvements**: Eliminated redundancy, added critical security/auth tasks, improved granularity
