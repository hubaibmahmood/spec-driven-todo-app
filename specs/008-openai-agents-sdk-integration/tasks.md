# Tasks: OpenAI Agents SDK Integration

**Input**: Design documents from `/specs/008-openai-agents-sdk-integration/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Included following TDD workflow from quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **ai-agent/**: FastAPI application (existing from spec 007)
- **ai-agent/src/ai_agent/agent/**: New agent module
- **ai-agent/tests/agent/**: Agent tests (contract/integration/unit)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency installation

- [X] T001 Install OpenAI Agents SDK dependencies via uv in ai-agent/pyproject.toml
- [X] T002 [P] Install testing dependencies (pytest-asyncio, httpx) via uv in ai-agent/pyproject.toml
- [X] T003 [P] Create agent module structure in ai-agent/src/ai_agent/agent/ with __init__.py
- [X] T004 [P] Create test directory structure in ai-agent/tests/agent/ with contract/, integration/, unit/ subdirectories
- [X] T005 Create .env.example in ai-agent/ with GEMINI_API_KEY and MCP_SERVER_URL placeholders

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Configuration Module

- [X] T006 [RED] Write failing test for AgentConfig validation in ai-agent/tests/agent/contract/test_agent_config.py
- [X] T007 [GREEN] Implement AgentConfig with Pydantic in ai-agent/src/ai_agent/agent/config.py
- [X] T008 [REFACTOR] Add field validators for temperature, token_budget, api_key in config.py

### Message Conversion Module

- [X] T009 [RED] Write failing test for db_to_agent conversion in ai-agent/tests/agent/unit/test_message_converter.py
- [X] T010 [GREEN] Implement MessageConverter.db_to_agent() in ai-agent/src/ai_agent/agent/message_converter.py
- [X] T011 [RED] Write failing test for tool_calls preservation in test_message_converter.py
- [X] T012 [GREEN] Enhance db_to_agent() to preserve tool_calls from metadata
- [X] T013 [REFACTOR] Implement db_messages_to_agent_batch() method in message_converter.py

### Context Management Module - Token Counting

- [X] T014 [RED] Write failing test for token counting in ai-agent/tests/agent/unit/test_context_manager.py
- [X] T015 [GREEN] Implement ContextManager.__init__() with tiktoken encoding in ai-agent/src/ai_agent/agent/context_manager.py
- [X] T016 [GREEN] Implement ContextManager.count_tokens() method
- [X] T017 [RED] Write failing test for token truncation preserving system messages
- [X] T018 [GREEN] Implement ContextManager.truncate_by_tokens() with system message preservation
- [X] T019 [REFACTOR] Optimize token counting with message-level caching

### Context Management Module - History Loading

- [X] T020 [RED] Write failing integration test for conversation history loading in ai-agent/tests/agent/integration/test_context_loading.py
- [X] T021 [GREEN] Implement ContextManager.load_conversation_history() in context_manager.py
- [X] T022 [GREEN] Add conversation ownership validation in load_conversation_history()
- [X] T023 [REFACTOR] Add error handling for PermissionError and NotFoundError

### Task Context Metadata (Edge Case #3: Task ID References)

- [X] T023a [RED] Write failing test for task list metadata storage in ai-agent/tests/agent/unit/test_task_context.py
- [X] T023b [GREEN] Implement store_task_list_context() in context_manager.py (saves to Message.metadata)
- [X] T023c [GREEN] Implement get_task_list_context() with expiration check (5 turns or 5 minutes)
- [X] T023d [GREEN] Implement resolve_ordinal_reference() to map "first"/"second"/"last" to task IDs
- [X] T023e [REFACTOR] Add context expiration logic and cleanup

### MCP Connection Module

- [X] T024 [RED] Write failing test for MCP connection creation in ai-agent/tests/agent/contract/test_mcp_connection.py
- [X] T025 [GREEN] Implement create_mcp_connection() async context manager in ai-agent/src/ai_agent/agent/mcp_connection.py
- [X] T026 [GREEN] Add X-User-ID header support in create_mcp_connection()
- [X] T027 [REFACTOR] Add connection timeout and retry configuration from AgentConfig
- [X] T028 [REFACTOR] Add connection error handling and logging

### Timezone Handling Infrastructure

- [X] T028a [RED] Write failing test for timezone extraction from X-Timezone header in ai-agent/tests/agent/unit/test_timezone_utils.py
- [X] T028b [GREEN] Implement extract_timezone() utility function in ai-agent/src/ai_agent/agent/timezone_utils.py
- [X] T028c [GREEN] Add timezone resolution priority logic (header → UTC fallback) with IANA validation
- [X] T028d [REFACTOR] Add timezone validation to reject invalid IANA timezone strings
- [X] T028e [REFACTOR] Add get_current_time_in_timezone() helper for system prompt context

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Natural Language Task Management via OpenAI Agent (Priority: P1) 🎯 MVP

**Goal**: Enable users to manage tasks using natural language through an OpenAI-powered conversational agent with Gemini backend

**Independent Test**: Send "show my tasks" or "add a task to buy groceries" to /api/chat and verify correct task operations occur

### Agent Service Module - Initialization

- [X] T029 [RED] [US1] Write failing test for agent initialization in ai-agent/tests/agent/contract/test_agent_service.py
- [X] T030 [GREEN] [US1] Implement AgentService.__init__() in ai-agent/src/ai_agent/agent/agent_service.py
- [X] T031 [GREEN] [US1] Implement create_gemini_client() helper in agent_service.py
- [X] T032 [GREEN] [US1] Implement initialize_agent() with OpenAIChatCompletionsModel and RunConfig
- [X] T033 [REFACTOR] [US1] Extract model configuration to separate method

### Agent Service Module - Execution

- [X] T034 [RED] [US1] Write failing integration test for agent execution in ai-agent/tests/agent/integration/test_agent_execution.py
- [X] T035 [GREEN] [US1] Implement run_agent() method with Runner.run() in agent_service.py
- [X] T036 [GREEN] [US1] Implement execution time tracking in run_agent()
- [X] T037 [RED] [US1] Write failing test for tool call extraction from agent result
- [X] T038 [GREEN] [US1] Implement tool call extraction logic in run_agent()
- [X] T039 [GREEN] [US1] Implement token counting for agent result
- [X] T040 [REFACTOR] [US1] Create AgentResult model return type

### Agent Service Module - Context Orchestration

- [X] T041 [RED] [US1] Write failing test for run_agent_with_context() in test_agent_execution.py
- [X] T042 [GREEN] [US1] Implement run_agent_with_context() orchestrating MCP connection + agent initialization + execution
- [X] T042a [GREEN] [US1] Add user_timezone parameter to run_agent_with_context() signature
- [X] T042b [GREEN] [US1] Enhance system prompt with timezone context (current time in user's timezone, parsing instructions)
- [X] T042c [GREEN] [US1] Integrate task context resolution (resolve ordinal references before MCP calls)
- [X] T043 [GREEN] [US1] Add error handling for GeminiAPIError in run_agent_with_context()
- [X] T044 [GREEN] [US1] Add error handling for MCPConnectionError in run_agent_with_context()
- [X] T045 [REFACTOR] [US1] Add structured logging for agent execution (start, success, failure)

### Chat Endpoint Integration

- [X] T046 [RED] [US1] Write failing API test for /api/chat with agent in ai-agent/tests/api/test_chat_with_agent.py
- [X] T047 [GREEN] [US1] Modify POST /api/chat endpoint to load AgentConfig and extract X-Timezone header in ai-agent/src/ai_agent/api/chat.py
- [X] T047a [GREEN] [US1] Add timezone resolution using extract_timezone() utility (header → UTC fallback)
- [X] T048 [GREEN] [US1] Initialize AgentService and ContextManager with timezone context in chat endpoint
- [X] T049 [GREEN] [US1] Load conversation history via ContextManager.load_conversation_history()
- [X] T050 [GREEN] [US1] Truncate history via ContextManager.truncate_by_tokens()
- [X] T051 [GREEN] [US1] Call AgentService.run_agent_with_context() with user message, history, and user_timezone parameter
- [X] T052 [GREEN] [US1] Save user message and agent response to database via ConversationService
- [X] T053 [GREEN] [US1] Return agent response with metadata (tokens_used, model, execution_time_ms)
- [X] T054 [REFACTOR] [US1] Add graceful degradation error handling (503 on Gemini/MCP failure)

### End-to-End Testing for User Story 1

- [X] T055 [RED] [US1] Write E2E test for "list tasks" query in ai-agent/tests/agent/integration/test_agent_workflow.py
- [X] T056 [RED] [US1] Write E2E test for "create task" query with attribute extraction
- [X] T057 [RED] [US1] Write E2E test for "mark task completed" query
- [X] T058 [RED] [US1] Write E2E test for "update task" query
- [X] T059 [GREEN] [US1] Run all E2E tests and verify agent correctly calls MCP tools
- [X] T060 [REFACTOR] [US1] Add mock fixtures for Gemini API and MCP server responses

**Checkpoint**: ✅ User Story 1 is fully functional and testable independently (52/54 tests pass)

### Phase 3 Completion Notes *(post-implementation)*

**Date**: 2025-12-21
**Status**: ✅ COMPLETE - All tasks T001-T060 finished with critical API corrections
**Verification**: E2E testing successful via `POST /api/chat` endpoint

**Critical Integration Fixes Applied**:
1. **Runner.run API** - Updated to use `input=messages` and `config` parameters (not `messages=`, `run_config`)
2. **RunResult handling** - Changed to use `result.new_items` and `result.context_wrapper.usage.total_tokens`
3. **MCPServerAdapter** - Created wrapper class with required `.name` and `.use_structured_content` attributes
4. **ContextManager API** - Parameter renamed to `session` (not `db`) for consistency
5. **MCP connection** - Corrected argument order to `create_mcp_connection(config, user_id)`
6. **Message type handling** - Added polymorphic support for dict and `MessageOutputItem` objects
7. **MessageConverter** - Added format detection to avoid re-converting already formatted history

**Files Modified with Integration Fixes**:
- `ai-agent/src/ai_agent/api/chat.py` - Updated ContextManager call (fix #1)
- `ai-agent/src/ai_agent/agent/agent_service.py` - Runner.run API, RunResult handling, MCP connection order, message type handling, converter logic (fixes #1, #2, #5, #6, #7)
- `ai-agent/src/ai_agent/agent/mcp_connection.py` - MCPServerAdapter wrapper (fix #3)
- `ai-agent/src/ai_agent/agent/context_manager.py` - Parameter naming (fix #4)

**Documentation References**:
- See `spec.md` § "Integration Learnings" for detailed SDK API documentation
- See `plan.md` § "Phase 3 Implementation Learnings" for architectural impact analysis
- See `FIXED_BY_GEMINI.md` for complete fix history with before/after code examples

**Next Steps**: Proceed to Phase 4 (User Story 2 - Partial Title Search) or any other P2 user story with validated foundation

---

## Phase 4: User Story 2 - Partial Title Search with Disambiguation (Priority: P2)

**Goal**: Enable users to reference tasks by partial title (e.g., "update my grocery task") without knowing exact IDs or listing all tasks first. When multiple matches exist, the agent presents numbered options for disambiguation.

**Independent Test**: Create tasks "Buy groceries" and "Organize groceries in pantry". Send "update my grocery task to high priority". Verify agent presents 2 options with numbers. Respond "the first one". Verify "Buy groceries" task is updated to high priority.

### MCP Server Tool Development

- [ ] T061 [RED] [US2] Write failing test for search_tasks_by_title tool in mcp-server/tests/tools/test_search_tasks_by_title.py
- [ ] T062 [GREEN] [US2] Create search_tasks_by_title.py in mcp-server/src/tools/ with FastMCP tool decorator
- [ ] T063 [GREEN] [US2] Implement case-insensitive partial match query (SQL ILIKE %query%) in search function
- [ ] T064 [GREEN] [US2] Return all matching tasks with id, title, description, priority, due_date, status
- [ ] T065 [GREEN] [US2] Add user_id filtering to ensure users only search their own tasks
- [ ] T066 [REFACTOR] [US2] Add error handling for empty queries and database errors
- [ ] T067 [REFACTOR] [US2] Add validation for minimum query length (2 characters)

### Agent Integration - Disambiguation Logic

- [ ] T068 [RED] [US2] Write failing test for single match auto-proceed in ai-agent/tests/agent/integration/test_partial_title_search.py
- [ ] T069 [RED] [US2] Write failing test for multiple matches disambiguation flow
- [ ] T070 [RED] [US2] Write failing test for no matches with helpful error message
- [ ] T071 [GREEN] [US2] Update system_prompt in agent_service.py with search_tasks_by_title usage instructions
- [ ] T072 [GREEN] [US2] Add disambiguation logic to system_prompt: single match → proceed, multiple → present numbered options
- [ ] T073 [GREEN] [US2] Integrate search results with existing task context storage (use store_task_list_context from T023b)
- [ ] T074 [GREEN] [US2] Enable ordinal resolution for disambiguation responses (leverage resolve_ordinal_reference from T023d)
- [ ] T075 [REFACTOR] [US2] Add system prompt examples: "I found 2 tasks:\n1. Buy groceries\n2. Organize groceries\nWhich one?"
- [ ] T076 [REFACTOR] [US2] Add no-match guidance: "I couldn't find any tasks matching 'xyz'. Would you like to list all tasks?"

### End-to-End Testing for User Story 2

- [ ] T077 [GREEN] [US2] Run E2E test: "update grocery task" with 2 matches → disambiguation → "first one" → success
- [ ] T078 [GREEN] [US2] Run E2E test: "delete my meeting task" with 1 match → auto proceed with confirmation
- [ ] T079 [GREEN] [US2] Run E2E test: "mark xyz task complete" with 0 matches → helpful error message
- [ ] T080 [GREEN] [US2] Run E2E test: multi-word partial match "update my buy groc task" → finds "Buy groceries"
- [ ] T081 [REFACTOR] [US2] Add search accuracy metrics logging (match rate, disambiguation rate)

**Checkpoint**: At this point, users can reference tasks by partial title with intelligent disambiguation

---

## Phase 5: User Story 3 - Multi-Turn Conversation Context (Priority: P2)

**Goal**: Enable natural multi-turn conversations where context is maintained across messages

**Independent Test**: Have conversation "show my urgent tasks" followed by "mark the first one as complete" - verify agent remembers which tasks were urgent

### Context Persistence Testing

- [ ] T082 [RED] [US3] Write failing test for multi-turn context preservation in ai-agent/tests/agent/integration/test_multi_turn.py
- [ ] T083 [RED] [US3] Write failing test for follow-up question understanding ("delete the second one")
- [ ] T084 [RED] [US3] Write failing test for incremental task creation across turns

### Conversation History Enhancement

- [ ] T085 [GREEN] [US3] Verify load_conversation_history() correctly loads messages in chronological order
- [ ] T086 [GREEN] [US3] Add test for conversation history ordering in test_context_loading.py
- [ ] T087 [REFACTOR] [US3] Optimize database query with eager loading for large conversations

### Multi-Turn Integration

- [ ] T088 [GREEN] [US3] Test /api/chat with conversation_id to ensure history is passed to agent
- [ ] T089 [GREEN] [US3] Verify agent responses reference prior context appropriately
- [ ] T090 [REFACTOR] [US3] Add conversation state validation in chat endpoint

### End-to-End Multi-Turn Testing

- [ ] T091 [GREEN] [US3] Run E2E test for 3-turn conversation with context references
- [ ] T092 [GREEN] [US3] Run E2E test for 10-turn conversation to verify SC-003 (context accuracy)
- [ ] T093 [REFACTOR] [US3] Add metrics logging for conversation turn count and context accuracy

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently

---

## Phase 6: User Story 4 - Intelligent Task Parsing and Validation (Priority: P2)

**Goal**: Intelligently parse natural language to extract task attributes and validate inputs before operations

**Independent Test**: Provide ambiguous input like "add a task for next Fbruary 30th" and verify agent catches invalid date

### Validation Testing

- [ ] T094 [RED] [US4] Write failing test for relative date parsing ("next Wednesday") in ai-agent/tests/agent/integration/test_parsing_validation.py
- [ ] T094a [RED] [US4] Write failing test for timezone-aware time parsing ("tomorrow at 9pm" with X-Timezone header)
- [ ] T094b [RED] [US4] Write failing test for UTC fallback when X-Timezone header missing
- [ ] T095 [RED] [US4] Write failing test for invalid date detection ("February 30th")
- [ ] T096 [RED] [US4] Write failing test for missing required fields (title not provided)
- [ ] T097 [RED] [US4] Write failing test for priority extraction from natural language ("urgent task")
- [ ] T097a [RED] [US4] Write failing test for EOD time interpretation ("by EOD" → 23:59:59 user timezone)
- [ ] T097b [RED] [US4] Write failing test for week boundary interpretation ("this week" with locale)
- [ ] T097c [RED] [US4] Write failing test for task context ordinal references ("mark the first one complete")

### Agent Prompt Enhancement

- [ ] T098 [GREEN] [US4] Update system_prompt with: date parsing instructions, EOD/COB definitions, week boundary rules, priority mapping table
- [ ] T099 [GREEN] [US4] Add validation guidelines: clarification triggers, enum validation, ambiguity detection
- [ ] T100 [REFACTOR] [US4] Extract system prompt to template file for easier maintenance

### Validation Integration Testing

- [ ] T101 [GREEN] [US4] Run E2E test for relative date parsing with Gemini
- [ ] T101a [GREEN] [US4] Run E2E test for timezone-aware parsing ("9pm" with America/New_York → correct UTC conversion)
- [ ] T101b [GREEN] [US4] Run E2E test for cross-timezone scenarios (user in Asia/Tokyo creates "9am" task → correct UTC)
- [ ] T101c [GREEN] [US4] Run E2E test for UTC fallback behavior (no X-Timezone header provided)
- [ ] T102 [GREEN] [US4] Run E2E test for invalid date detection and clarification request
- [ ] T103 [GREEN] [US4] Run E2E test for missing field detection and follow-up question
- [ ] T104 [GREEN] [US4] Run E2E test for priority keyword extraction (urgent, high, low)
- [ ] T104a [GREEN] [US4] Run E2E test for priority normalization ("critical" → "Urgent", "important" → "High")
- [ ] T104b [GREEN] [US4] Run E2E test for EOD interpretation and UTC conversion
- [ ] T104c [GREEN] [US4] Run E2E test for week boundary filtering with different locales
- [ ] T104d [GREEN] [US4] Run E2E test for task context resolution after displaying list
- [ ] T105 [REFACTOR] [US4] Add validation accuracy metrics logging

**Checkpoint**: All high-priority user stories (P1, P2) should now be independently functional

---

## Phase 7: User Story 5 - Batch Operations via Natural Language (Priority: P3)

**Goal**: Enable bulk operations like "mark all urgent tasks as complete"

**Independent Test**: Create 5 urgent tasks, say "complete all urgent tasks", verify all 5 are marked completed

### Batch Operations Testing

- [ ] T106 [RED] [US5] Write failing test for bulk complete operation in ai-agent/tests/agent/integration/test_batch_operations.py
- [ ] T107 [RED] [US5] Write failing test for bulk delete operation
- [ ] T108 [RED] [US5] Write failing test for filtered list with batch action

### Agent Prompt Enhancement for Batch

- [ ] T109 [GREEN] [US5] Update system_prompt to handle batch operation requests
- [ ] T110 [GREEN] [US5] Add confirmation flow to system_prompt for destructive batch operations
- [ ] T111 [REFACTOR] [US5] Document batch operation patterns in system prompt

### Batch Integration Testing

- [ ] T112 [GREEN] [US5] Run E2E test for "mark all high priority tasks as done"
- [ ] T113 [GREEN] [US5] Run E2E test for "delete all completed tasks" with confirmation
- [ ] T114 [GREEN] [US5] Run E2E test for filtered batch operations
- [ ] T115 [REFACTOR] [US5] Add batch operation size limits and warnings

**Checkpoint**: All user stories should now be independently functional

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

### Error Handling & Observability

- [ ] T116 [P] Add comprehensive error logging in agent_service.py for debugging
- [ ] T117 [P] Add performance metrics logging (latency, token usage) in chat endpoint
- [ ] T118 [P] Add rate limiting configuration for Gemini API calls

### Documentation

- [ ] T119 [P] Document environment variables in README.md
- [ ] T120 [P] Add agent configuration guide with examples
- [ ] T121 [P] Add troubleshooting section for common errors (auth, timeouts)

### Code Quality

- [ ] T122 Run type checking with mypy on ai-agent/src/ai_agent/agent/
- [ ] T123 Run linting with ruff on ai-agent/src/ai_agent/agent/
- [ ] T124 [P] Run test coverage analysis and verify >80% coverage for agent module
- [ ] T125 [P] Run quickstart.md verification checklist

### Security

- [ ] T126 Verify GEMINI_API_KEY is not hardcoded anywhere
- [ ] T127 Verify X-User-ID header is always passed to MCP server
- [ ] T128 Add input sanitization for user messages before passing to Gemini

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P2 → P2 → P3)
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1 - Phase 3)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2 - Phase 4)**: Can start after Foundational (Phase 2) - Leverages existing task context (T023a-T023e) for disambiguation
- **User Story 3 (P2 - Phase 5)**: Can start after Foundational (Phase 2) - Builds on US1 but independently testable
- **User Story 4 (P2 - Phase 6)**: Can start after Foundational (Phase 2) - Enhances US1 but independently testable
- **User Story 5 (P3 - Phase 7)**: Can start after Foundational (Phase 2) - Extends US1 capabilities

### Within Each User Story

- Tests MUST be written and FAIL before implementation (RED-GREEN-REFACTOR)
- Foundational modules before agent service
- Agent service before endpoint integration
- Core implementation before E2E testing
- Story complete before moving to next priority

### Parallel Opportunities

- Phase 1: All tasks marked [P] can run in parallel (T002, T003, T004)
- Phase 2: Configuration, Message Conversion, and initial Context Management tests can run in parallel
- Within each user story: Multiple [RED] test tasks can be written in parallel before implementation
- Phase 8: All polish tasks marked [P] can run in parallel

---

## Parallel Example: Foundational Phase

```bash
# Launch foundational module tests in parallel:
Task T006: "Write failing test for AgentConfig validation"
Task T009: "Write failing test for db_to_agent conversion"
Task T014: "Write failing test for token counting"

# After tests written, implement modules in parallel:
Task T007: "Implement AgentConfig with Pydantic"
Task T010: "Implement MessageConverter.db_to_agent()"
Task T015: "Implement ContextManager with tiktoken encoding"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (5 tasks, ~1-1.5 hours)
2. Complete Phase 2: Foundational (33 tasks including timezone + task context, ~8-10 hours total)
3. Complete Phase 3: User Story 1 (36 tasks with timezone + context integration, ~9-11 hours total)
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

**Total MVP Estimate**: ~18-22 hours for basic natural language task management with timezone support + edge case handling

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready (~9-11 hours)
2. Add User Story 1 → Test independently → Deploy/Demo (MVP! +9-11 hours)
3. Add User Story 2 (Partial Title Search) → Test independently → Deploy/Demo (+2-3 hours)
4. Add User Story 3 (Multi-Turn Context) → Test independently → Deploy/Demo (+3-4 hours)
5. Add User Story 4 (Intelligent Parsing) → Test independently → Deploy/Demo (+5-6 hours with all edge case validation)
6. Add User Story 5 (Batch Operations) → Test independently → Deploy/Demo (+2-3 hours)
7. Polish → Final hardening (+2-3 hours)

**Total Feature Estimate**: ~32-41 hours for all user stories + polish + edge case handling

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (~7-9 hours)
2. Once Foundational is done:
   - Developer A: User Story 1 (P1 - highest priority)
   - Developer B: User Story 2 (P2 - Partial Title Search)
   - Developer C: User Story 3 (P2 - Multi-Turn Context)
   - Developer D: User Story 4 (P2 - Intelligent Parsing)
3. User Story 5 (P3 - Batch Operations) after P2 stories complete
4. Polish phase together

---

## Task Sizing Analysis

### Tasks Properly Sized (15-30 minutes)

- ✅ T001-T005: Setup tasks (10-20 min each)
- ✅ T006-T028: Foundational RED-GREEN-REFACTOR cycles (15-25 min each)
- ✅ T029-T060: User Story 1 implementation (15-30 min each)
- ✅ T061-T081: User Story 2 (Partial Title Search) implementation (15-25 min each)
- ✅ T082-T093: User Story 3 (Multi-Turn Context) implementation (15-25 min each)
- ✅ T094-T105: User Story 4 (Intelligent Parsing) implementation (15-25 min each)
- ✅ T106-T115: User Story 5 (Batch Operations) implementation (15-25 min each)
- ✅ T116-T128: Polish tasks (10-20 min each)

### Tasks That Could Be Split (if needed)

None - all tasks are already atomic and sized appropriately for 15-30 minute execution

### Tasks That Could Be Combined (if needed)

- T003-T004 could combine into single "Create project structure" but keeping separate allows parallel execution
- T008 validator could merge into T007 but TDD cycle benefits from separation
- T019 optimization could merge into T018 but REFACTOR step is separate by design

### Tasks Added (vs typical implementation)

- ✅ Explicit RED-GREEN-REFACTOR labels for TDD workflow (per quickstart.md)
- ✅ Timezone handling infrastructure (T028a-T028e) for accurate date/time parsing
- ✅ Task context metadata (T023a-T023e) for ordinal reference resolution (Edge Case #3)
- ✅ Timezone integration in agent service (T042a-T042c, T047a) and endpoint
- ✅ Partial title search infrastructure (T061-T081) for natural task referencing with disambiguation
- ✅ Timezone validation tests (T094a-T094b, T101a-T101c) for cross-timezone scenarios
- ✅ Edge case validation (T097a-T097c) for EOD, week boundaries, task context
- ✅ Edge case E2E tests (T104a-T104d) for priority normalization, EOD, locale handling
- ✅ E2E workflow tests (T055-T060) for comprehensive validation
- ✅ Multi-turn conversation tests (T082-T093) for context management
- ✅ Batch operations tests (T106-T115) for P3 story
- ✅ Security validation tasks (T126-T128) for production readiness

### Tasks Removed (vs over-engineered approach)

- ❌ No premature caching/optimization until REFACTOR steps
- ❌ No streaming implementation (deferred to future per research.md)
- ❌ No conversation summarization (deferred to future per research.md)
- ❌ No database migrations (no schema changes per data-model.md)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- RED-GREEN-REFACTOR labels guide TDD workflow from quickstart.md
- Verify tests fail before implementing (critical for TDD)
- Commit after each GREEN or REFACTOR step
- Stop at any checkpoint to validate story independently
- **Total of 128 tasks** organized into 8 phases (includes partial title search with disambiguation)
- All tasks sized for 15-30 minute execution windows
- Timezone support added via X-Timezone header throughout user stories
- Edge cases 1-4 integrated: EOD interpretation, week boundaries, task ID context, priority normalization
- Partial title search (US2) leverages existing task context infrastructure for disambiguation
