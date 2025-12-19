---

description: "Task list for Chat Persistence Service implementation (REVISED)"
---

# Tasks: Chat Persistence Service

**Input**: Design documents from `/specs/007-chat-persistence/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: Not explicitly requested - focusing on implementation

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

**Revision Notes**: Tasks have been refined to:
- Combine over-granular endpoint implementation tasks
- Add missing critical steps (health check, auth testing, router creation, migration execution)
- Split complex auth service task for realistic sizing
- Remove vague verification tasks

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure (15-20 minutes total)

- [X] T001 Create ai-agent/ directory structure with src/ai_agent/ and tests/ subdirectories
- [X] T002 [P] Initialize pyproject.toml with FastAPI, SQLModel, SQLAlchemy, Alembic, httpx dependencies using uv
- [X] T003 [P] Create ai-agent/.env.example with DATABASE_URL and SERVICE_AUTH_TOKEN placeholders

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Create database connection module in ai-agent/src/ai_agent/database/connection.py with async engine and session factory
- [X] T005 Create UserSession SQLModel in ai-agent/src/ai_agent/database/models.py (read-only model for user_sessions table with camelCase mapping)
- [X] T006 [P] Create auth service in ai-agent/src/ai_agent/services/auth.py with Bearer token parsing from Authorization header
- [X] T007 Add session validation to auth service: query user_sessions table, verify expiresAt is in future, return user_id
- [X] T008 Create FastAPI dependency for authentication in ai-agent/src/ai_agent/api/deps.py using auth service
- [X] T009 Create FastAPI dependency for database session in ai-agent/src/ai_agent/api/deps.py with async context manager
- [X] T010 Create main.py in ai-agent/src/ai_agent/main.py with FastAPI app initialization and CORS middleware
- [X] T011 Initialize Alembic in ai-agent/ directory for database migrations
- [X] T012 [P] Create health check endpoint GET /health in ai-agent/src/ai_agent/api/health.py to verify app runs
- [X] T013 Test auth flow manually: query sample session token from database and verify auth dependency works

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Start New Conversation (Priority: P1) 🎯 MVP

**Goal**: Allow authenticated users to send a message and create a new conversation with persistence

**Independent Test**: POST to /api/chat with auth token should create conversation and return conversation_id with echo response

### Implementation for User Story 1

- [X] T014 [P] [US1] Create Conversation SQLModel in ai-agent/src/ai_agent/database/models.py with id, user_id, title, created_at, updated_at fields
- [X] T015 [P] [US1] Create Message SQLModel in ai-agent/src/ai_agent/database/models.py with id, conversation_id, role, content, metadata (JSONB), created_at fields
- [X] T016 [US1] Create Alembic migration for conversations table in ai-agent/alembic/versions/ with all fields, indexes on user_id and created_at
- [X] T017 [US1] Create Alembic migration for messages table in ai-agent/alembic/versions/ with all fields, foreign key to conversations, indexes on conversation_id
- [X] T018 [US1] Run Alembic migrations to create conversations and messages tables in database: alembic upgrade head
- [X] T019 [US1] Create APIRouter in ai-agent/src/ai_agent/api/chat.py for chat endpoints
- [X] T020 [US1] Create Pydantic schemas in ai-agent/src/ai_agent/api/chat.py: ChatRequest (message, optional conversation_id) and ChatResponse (conversation_id, user_message, assistant_message)
- [X] T021 [US1] Implement POST /api/chat endpoint in ai-agent/src/ai_agent/api/chat.py with conversation creation (title: "Chat - [YYYY-MM-DD HH:MM]"), user message persistence (role='user'), and echo response (role='assistant')
- [X] T022 [US1] Add error handling and input validation to POST /api/chat endpoint for database errors, invalid tokens, and missing message field
- [X] T023 [US1] Add Conversation.updated_at auto-update logic in chat endpoint when new messages are added to existing conversations
- [X] T024 [US1] Register chat router in ai-agent/src/ai_agent/main.py with /api prefix

**Checkpoint**: At this point, User Story 1 should be fully functional - users can create conversations and send messages

---

## Phase 4: User Story 2 - View Conversation History (Priority: P2)

**Goal**: Allow authenticated users to retrieve their conversation list and message history

**Independent Test**: GET /api/conversations should return user's conversations; GET /api/conversations/{id} should return message history

### Implementation for User Story 2

- [X] T025 [US2] Create APIRouter in ai-agent/src/ai_agent/api/history.py for conversation history endpoints
- [X] T026 [US2] Create Pydantic schemas in ai-agent/src/ai_agent/api/history.py: ConversationListResponse (id, title, created_at, updated_at), MessageResponse (id, role, content, metadata, created_at), ConversationDetailResponse (conversation fields + messages list)
- [X] T027 [P] [US2] Implement GET /api/conversations endpoint in ai-agent/src/ai_agent/api/history.py to list user's conversations filtered by user_id and ordered by updated_at DESC
- [X] T028 [P] [US2] Implement GET /api/conversations/{id} endpoint in ai-agent/src/ai_agent/api/history.py with ownership validation (404 if not user's conversation), message ordering (created_at ASC), and error handling
- [X] T029 [US2] Register history router in ai-agent/src/ai_agent/main.py with /api prefix

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - users can create chats and view history

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T030 [P] Add logging for all API endpoints in ai-agent/src/ai_agent/api/ using Python logging module with INFO level for requests and ERROR for failures
- [X] T031 [P] Update quickstart.md with actual curl commands and response examples for all endpoints (/api/chat, /api/conversations, /api/conversations/{id})
- [X] T032 Validate end-to-end flow: create conversation → send message → list conversations → retrieve history
- [X] T033 Add API documentation strings (docstrings) to all endpoints for automatic OpenAPI schema generation
- [X] T034 Add database connection pooling configuration in connection.py (pool_size=5, max_overflow=10) for production readiness

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately (15-20 min total)
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories (90-120 min total)
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2)
- **Polish (Phase 5)**: Depends on all desired user stories being complete (60-75 min total)

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories (90-120 min total)
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Reads data created by US1 but independently testable (45-60 min total)

### Within Each User Story

- Models (T014, T015) before migrations (T016, T017)
- Migrations created before migrations executed (T018)
- Migrations executed before endpoint implementation
- APIRouter created before endpoint handlers
- Schemas before endpoint implementation
- Core implementation before error handling
- Core implementation before router registration

### Parallel Opportunities

- **Phase 1**: T002 and T003 can run in parallel (different files)
- **Phase 2**: T006 and T012 can run in parallel (different files)
- **Phase 3 (US1)**: T014 and T015 can run in parallel (both adding to models.py but separate model classes)
- **Phase 4 (US2)**: T027 and T028 can run in parallel (different endpoint handlers in same file)
- **Phase 5**: T030 and T031 can run in parallel (different files)

---

## Parallel Example: User Story 1 Models

```bash
# Launch both model definitions together:
Task: "Create Conversation SQLModel in ai-agent/src/ai_agent/database/models.py"
Task: "Create Message SQLModel in ai-agent/src/ai_agent/database/models.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (15-20 min)
2. Complete Phase 2: Foundational (90-120 min) - CRITICAL - blocks all stories
3. Complete Phase 3: User Story 1 (90-120 min)
4. **STOP and VALIDATE**: Test User Story 1 independently using quickstart.md
5. Deploy/demo if ready

**Total MVP Time Estimate**: ~3.5-4.5 hours

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready (~2-2.5 hours)
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!) (+1.5-2 hours)
3. Add User Story 2 → Test independently → Deploy/Demo (+45-60 min)
4. Complete Polish → Production ready (+60-75 min)

**Total Complete Feature Time Estimate**: ~5.5-7 hours

### Parallel Team Strategy

With two developers:

1. Team completes Setup + Foundational together (~2-2.5 hours)
2. Once Foundational is done:
   - Developer A: User Story 1 (~1.5-2 hours)
   - Developer B: User Story 2 (~45-60 min, then helps with US1 or starts Polish)
3. Team completes Polish together (~60-75 min)

**Total Team Time**: ~4-5 hours (wall clock time with parallelization)

---

## Revision Summary

**Changes from v1**:
- **Combined**: Endpoint implementation tasks (US1: 5→2, US2: 5→2) and schema tasks (US1: 2→1, US2: 3→1) for realistic 20-30 min sizing
- **Added**: Health check endpoint (T012), auth testing (T013), APIRouter creation (T019, T025), migration execution (T018), updated_at auto-update logic (T023)
- **Split**: Auth service (T006→T006+T007) from 35-40 min to two 20 min tasks
- **Removed**: Vague verification task (old T037)

**Task Count**: 34 tasks (was 37)
- Phase 1: 3 tasks (unchanged)
- Phase 2: 10 tasks (was 7, +3 for split auth + health check + testing)
- Phase 3: 11 tasks (was 12, -1 net: combined schemas/endpoints, added router/migrations/updated_at)
- Phase 4: 5 tasks (was 9, -4 from combining schemas and endpoints)
- Phase 5: 5 tasks (was 6, -1 from removing vague task)

---

## Notes

- [P] tasks = different files or independent sections, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Tasks sized for 15-30 minute completion time
- **CRITICAL**: T013 (auth testing) must pass before starting User Story work - catch auth bugs early
- **CRITICAL**: T018 (run migrations) must complete before testing endpoints - database tables must exist
- Commit after each task or logical group (e.g., after migrations, after endpoint)
- Stop at any checkpoint to validate story independently
- Echo response in US1 will be replaced with OpenAI Agents SDK in spec 008
- Metadata field in Message model is reserved for future tool call storage (spec 008)
