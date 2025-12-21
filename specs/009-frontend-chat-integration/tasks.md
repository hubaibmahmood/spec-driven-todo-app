# Tasks: Frontend Chat Integration

**Input**: Design documents from `/specs/009-frontend-chat-integration/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Component and E2E tests included as specified in quickstart.md (TDD approach)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Monorepo structure**: `frontend/` for Next.js app
- All paths relative to repository root
- Frontend code: `frontend/components/chat/`, `frontend/lib/chat/`, `frontend/types/`
- Tests: `frontend/__tests__/` (unit, component, e2e)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Install @openai/chatkit-react, date-fns, date-fns-tz dependencies via npm in frontend/
- [X] T002 [P] Install testing libraries (@testing-library/react, @testing-library/jest-dom, @testing-library/user-event) in frontend/
- [X] T003 [P] Install Playwright for E2E tests via npm in frontend/
- [X] T004 [P] Create frontend/types/chat.ts with all TypeScript interfaces from data-model.md
- [X] T005 [P] Create frontend/lib/utils/ directory structure
- [X] T006 [P] Create frontend/lib/chat/ directory structure
- [X] T007 [P] Create frontend/components/chat/ directory structure
- [X] T008 [P] Create frontend/__tests__/lib/utils/ test directory
- [X] T009 [P] Create frontend/__tests__/lib/chat/ test directory
- [X] T010 [P] Create frontend/__tests__/components/chat/ test directory
- [X] T011 [P] Create frontend/__tests__/e2e/ test directory

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core utilities and API infrastructure that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T012 [P] Write unit test for getUserTimezone() in frontend/__tests__/lib/utils/timezone.test.ts (TDD - write test FIRST)
- [X] T013 Implement getUserTimezone() function in frontend/lib/utils/timezone.ts (make test pass)
- [X] T014 [P] Write unit tests for usePanelState() hook in frontend/__tests__/lib/chat/panel-state.test.ts (TDD - write tests FIRST)
- [X] T015 Implement usePanelState() hook with localStorage persistence in frontend/lib/chat/panel-state.ts (make tests pass)
- [X] T016 [P] Write unit tests for sendChatMessage() in frontend/__tests__/lib/chat/chat-api.test.ts (TDD - write tests FIRST)
- [X] T017 Implement sendChatMessage() function in frontend/lib/chat/chat-api.ts with session token and timezone headers
- [X] T018 [P] Write unit tests for fetchConversationHistory() in frontend/__tests__/lib/chat/chat-api.test.ts
- [X] T019 Implement fetchConversationHistory() function in frontend/lib/chat/chat-api.ts with pagination support
- [X] T020 [P] Write unit tests for getOrCreateConversation() in frontend/__tests__/lib/chat/chat-api.test.ts
- [X] T021 Implement getOrCreateConversation() function in frontend/lib/chat/chat-api.ts
- [X] T022 Add Date parsing utilities to chat-api.ts for converting ISO strings to Date objects
- [X] T023 Configure environment variable NEXT_PUBLIC_API_URL in frontend/.env.local for API base URL

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Authentication and Session Management (Priority: P1) 🎯 MVP

**Goal**: Ensure all chat requests include authentication session token and only authenticated users can access chat

**Independent Test**: Verify chat requests include session token, unauthorized requests are rejected, and different users see only their own conversations

### Implementation for User Story 1

- [X] T024 [P] [US1] Write component test for ChatToggleButton in frontend/__tests__/components/chat/ChatToggleButton.test.tsx (TDD)
- [X] T025 [P] [US1] Create ChatToggleButton component in frontend/components/chat/ChatToggleButton.tsx with click handler
- [X] T026 [US1] Add aria-label accessibility attribute to ChatToggleButton for screen readers
- [X] T027 [US1] Style ChatToggleButton with Tailwind CSS (fixed position, responsive, mobile-first)
- [X] T028 [P] [US1] Write integration test for session token inclusion in API requests in frontend/__tests__/lib/chat/chat-session-integration.test.ts
- [X] T029 [US1] Create useChat hook to integrate with better-auth useSession for automatic session token management
- [X] T030 [US1] Add Authorization header with Bearer token to all chat API requests in chat-api.ts
- [X] T031 [US1] Implement 401 error handling (session expired) in sendChatMessage() with user-friendly error message
- [X] T032 [US1] Add error state display in ChatPanel for authentication failures

**Checkpoint**: At this point, authentication is working - chat requests include session tokens and handle auth errors

---

## Phase 4: User Story 2 - Embedded Chat UI with Collapsible Panel (Priority: P1)

**Goal**: Provide a responsive chat panel that users can toggle open/closed with state persisting across sessions

**Independent Test**: Toggle chat panel, navigate between pages, verify panel state persists via localStorage

### Implementation for User Story 2

- [X] T033 [P] [US2] Write component test for ChatMessage component in frontend/__tests__/components/chat/ChatMessage.test.tsx (TDD)
- [X] T034 [P] [US2] Create ChatMessage component in frontend/components/chat/ChatMessage.tsx with role-based styling
- [X] T035 [US2] Add timestamp formatting using date-fns-tz in ChatMessage component
- [X] T036 [US2] Add error message display in ChatMessage for failed operations (metadata.status === 'error')
- [X] T037 [US2] Style ChatMessage with Tailwind CSS (user vs assistant message alignment and colors)
- [X] T038 [P] [US2] Write component test for ChatPanel component in frontend/__tests__/components/chat/ChatPanel.test.tsx (TDD)
- [X] T039 [P] [US2] Integrate OpenAI ChatKit React SDK (@openai/chatkit-react) in ChatPanel component
- [X] T040 [US2] ChatKit SDK handles messages container with scroll handling automatically
- [X] T041 [US2] ChatKit SDK implements scrollToBottom() functionality internally
- [X] T042 [US2] ChatKit SDK manages scroll positioning automatically
- [X] T043 [US2] Add responsive CSS classes for desktop (≥768px side panel) and mobile (<768px full-screen overlay)
- [X] T044 [US2] Implement panel open/close animation with 300ms transition duration
- [X] T045 [US2] Integrate usePanelState() hook in dashboard layout to persist open/closed state
- [X] T046 [US2] Add ChatPanel to frontend/app/(dashboard)/layout.tsx after main content div
- [X] T047 [US2] Add ChatToggleButton to frontend/app/(dashboard)/layout.tsx with toggleChatPanel handler
- [X] T048 [US2] Implement toggleChatPanel() function in dashboard layout with lastOpenedAt tracking
- [X] T049 [US2] Test responsive behavior by resizing browser window (768px breakpoint)
- [X] T050 [US2] Add ESC key handler to close chat panel (keyboard accessibility)
- [X] T051 [US2] Panel state persists across page navigation using localStorage via usePanelState hook

**Checkpoint**: At this point, chat UI is fully functional with collapsible panel and persistent state

---

## Phase 5: User Story 3 - Basic Natural Language Task Creation (Priority: P1)

**Goal**: Allow users to create tasks using natural language through the chat interface

**Independent Test**: Send natural language task request, verify task appears in todo list with correct details

### Implementation for User Story 3

- [ ] T052 [P] [US3] Create ChatInput component in frontend/components/chat/ChatInput.tsx (form with input and submit button)
- [ ] T053 [US3] Add multi-line support to ChatInput field (textarea instead of input)
- [ ] T054 [US3] Add Enter key handler to submit message (Shift+Enter for new line)
- [ ] T055 [US3] Add input validation (min 1 char, max 5000 chars) with error message display
- [ ] T056 [US3] Integrate ChatInput into ChatPanel component
- [ ] T057 [P] [US3] Write integration test for handleSendMessage() in ChatPanel component test
- [ ] T058 [US3] Implement handleSendMessage() function in ChatPanel with optimistic UI update
- [ ] T059 [US3] Add temporary user message to messages array while waiting for API response
- [ ] T060 [US3] Replace temporary message with backend message after API response
- [ ] T061 [US3] Add loading state indicator during message send (disable input, show spinner)
- [ ] T062 [US3] Implement error handling for message send failure with retry option
- [ ] T063 [US3] Add loadConversation() function to fetch conversation on ChatPanel mount
- [ ] T064 [US3] Call getOrCreateConversation() in useEffect when panel opens
- [ ] T065 [US3] Update TaskContext when operations array contains task operations (integrate with existing useTasks hook)
- [ ] T066 [US3] Add optimistic task addition to TaskContext.addTask() for immediate UI feedback
- [ ] T067 [US3] Verify task appears in main TaskList component after chat message
- [ ] T068 [P] [US3] Write E2E test for task creation via chat in frontend/__tests__/e2e/chat-workflow.spec.ts
- [ ] T069 [US3] Test complete flow: open panel → send message → verify task in list

**Checkpoint**: At this point, users can create tasks via chat and see them appear in the todo list immediately

---

## Phase 6: User Story 4 - Real-time Task Operation Feedback (Priority: P2)

**Goal**: Provide real-time status updates as AI agent processes task operations

**Independent Test**: Send task operations and observe real-time status messages in chat

### Implementation for User Story 4

- [ ] T070 [P] [US4] Add loading indicator component for message processing in ChatPanel
- [ ] T071 [US4] Display status message when AI agent begins processing (e.g., "Processing request...")
- [ ] T072 [US4] Render operation success messages from metadata.status === 'success' in ChatMessage
- [ ] T073 [US4] Render operation error messages from metadata.errorMessage in ChatMessage
- [ ] T074 [US4] Add checkmark icon (✓) for successful operations in ChatMessage
- [ ] T075 [US4] Add warning icon (⚠️) for failed operations in ChatMessage
- [ ] T076 [US4] Update TaskList component optimistically when chat operations complete
- [ ] T077 [US4] Add refreshTasks() call to TaskContext after operations complete (ensure backend sync)
- [ ] T078 [US4] Test multiple task operations (e.g., "update all high priority tasks to next Monday")
- [ ] T079 [US4] Verify individual confirmation messages appear for each operation

**Checkpoint**: At this point, users see real-time feedback for all task operations with clear success/error states

---

## Phase 7: User Story 5 - Conversation History and Context (Priority: P2)

**Goal**: Load and display conversation history when user opens chat panel

**Independent Test**: Create conversation, close app, reopen, verify chat history is preserved

### Implementation for User Story 5

- [ ] T080 [P] [US5] Write integration test for loadConversation() in ChatPanel component test
- [ ] T081 [US5] Call fetchConversationHistory() with limit=50, offset=0 on panel open
- [ ] T082 [US5] Set messages state with fetched history (ordered chronologically)
- [ ] T083 [US5] Set hasMore flag based on ConversationHistoryResponse.hasMore
- [ ] T084 [US5] Add "Load More" button at top of messages list when hasMore is true
- [ ] T085 [US5] Implement loadMoreMessages() function with pagination (offset increment by 50)
- [ ] T086 [US5] Prepend older messages to messages array (maintain chronological order)
- [ ] T087 [US5] Maintain scroll position after loading more messages (don't auto-scroll to bottom)
- [ ] T088 [US5] Add loading spinner to "Load More" button during fetch
- [ ] T089 [US5] Disable "Load More" button when isLoading is true
- [ ] T090 [US5] Test conversation history loads within 1 second (performance requirement)
- [ ] T091 [P] [US5] Write E2E test for conversation history persistence
- [ ] T092 [US5] Test: send messages → close panel → reopen → verify history is displayed

**Checkpoint**: At this point, conversation history loads correctly with pagination and persists across sessions

---

## Phase 8: User Story 6 - Timezone-Aware Task Scheduling (Priority: P2)

**Goal**: Ensure task due dates are calculated in user's local timezone, not UTC

**Independent Test**: Set browser timezone, create tasks with times, verify due dates match user's timezone

### Implementation for User Story 6

- [ ] T093 [P] [US6] Write unit test for timezone detection edge cases (DST transitions, etc.)
- [ ] T094 [US6] Verify getUserTimezone() is called on every chat message send
- [ ] T095 [US6] Add X-Timezone header to all API requests in sendChatMessage()
- [ ] T096 [US6] Verify timezone header matches request body timezone field
- [ ] T097 [US6] Test task creation with "tomorrow at 5pm" in different timezones (manual QA)
- [ ] T098 [US6] Verify due dates displayed in ChatMessage use user's local timezone (formatInTimeZone)
- [ ] T099 [US6] Test timezone handling when user travels (browser timezone changes)
- [ ] T100 [P] [US6] Write E2E test for timezone-aware task scheduling
- [ ] T101 [US6] Mock browser timezone in test, verify due dates match expected timezone

**Checkpoint**: At this point, all task scheduling is timezone-aware and displays correctly for user's location

---

## Phase 9: Edge Cases and Polish

**Purpose**: Handle edge cases and improve user experience

- [ ] T102 [P] Handle empty/ambiguous input ("hello", "help") with helpful guidance message
- [ ] T103 [P] Implement session timeout handling mid-conversation (prompt re-auth, preserve state)
- [ ] T104 Add confirmation dialog for destructive bulk operations ("delete all tasks")
- [ ] T105 Show number of affected tasks in confirmation dialog before execution
- [ ] T106 [P] Add network failure retry logic with exponential backoff
- [ ] T107 [P] Display network error state with retry button in ChatPanel
- [ ] T108 Add rate limiting check on rapid message sends (debounce 500ms)
- [ ] T109 [P] Handle unsupported operations gracefully (e.g., "send email to my team")
- [ ] T110 Add browser back button handler (close panel instead of navigate away)
- [ ] T111 [P] Test chat panel on small screens (320px minimum width)
- [ ] T112 Verify touch target sizes meet accessibility standards (44px minimum)
- [ ] T113 [P] Add keyboard navigation (Tab, Shift+Tab, Esc) for accessibility
- [ ] T114 Test screen reader support (aria-labels, semantic HTML)
- [ ] T115 [P] Verify color contrast meets WCAG 2.1 AA standards
- [ ] T116 Add focus indicators for keyboard navigation
- [ ] T117 Test concurrent task modifications (chat + UI edits on same task)
- [ ] T118 [P] Run TypeScript type checking (npm run type-check)
- [ ] T119 [P] Run ESLint with zero warnings (npm run lint)
- [ ] T120 [P] Run all unit tests and verify 80%+ coverage
- [ ] T121 [P] Run all component tests and verify they pass
- [ ] T122 [P] Run all E2E tests and verify they pass
- [ ] T123 Manual QA: Test on Chrome, Firefox, Safari, Edge (last 2 versions)
- [ ] T124 [P] Performance test: Verify messages render within 200ms
- [ ] T125 [P] Performance test: Verify history loads within 1 second
- [ ] T126 [P] Performance test: Verify panel animation completes within 300ms
- [ ] T127 Run quickstart.md validation checklist
- [ ] T128 Document any architectural decisions as ADRs if significant tradeoffs were made

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - US1 (Auth) should complete first as it's foundational for security
  - US2 (UI) should complete second as it provides the interface
  - US3 (Task Creation) is the core value proposition
  - US4-6 can proceed in parallel after US1-3 complete
- **Polish (Phase 9)**: Depends on all user stories being functional

### User Story Dependencies

- **User Story 1 (P1 - Auth)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1 - UI)**: Can start after US1 - Needs auth for session context
- **User Story 3 (P1 - Task Creation)**: Can start after US1 & US2 - Needs auth and UI components
- **User Story 4 (P2 - Real-time Feedback)**: Can start after US3 - Enhances task creation
- **User Story 5 (P2 - History)**: Can start after US1 & US2 - Independent of task operations
- **User Story 6 (P2 - Timezone)**: Can start after US3 - Enhances task scheduling

### Recommended Sequential Order

1. Complete Phase 1 (Setup) → 15-30 minutes total
2. Complete Phase 2 (Foundational) → 2-3 hours total
3. Complete Phase 3 (US1 - Auth) → 1.5-2 hours total
4. Complete Phase 4 (US2 - UI) → 3-4 hours total
5. Complete Phase 5 (US3 - Task Creation) → 2.5-3 hours total
6. **STOP and VALIDATE MVP** (US1-3 complete)
7. Complete Phase 6 (US4 - Feedback) → 1.5-2 hours total
8. Complete Phase 7 (US5 - History) → 1.5-2 hours total
9. Complete Phase 8 (US6 - Timezone) → 1.5-2 hours total
10. Complete Phase 9 (Polish) → 3-4 hours total

### Parallel Opportunities

- **Setup tasks (T001-T011)**: All can run in parallel
- **Foundational tests (T012, T014, T016, T018, T020)**: All test files can be written in parallel
- **Component tests within each user story**: Tests marked [P] can run in parallel
- **Different user stories**: US4, US5, US6 can be worked on in parallel by different team members after US1-3 complete

---

## Parallel Example: Foundational Phase

```bash
# Launch all test files together (TDD approach):
Task T012: "Write unit test for getUserTimezone()"
Task T014: "Write unit tests for usePanelState() hook"
Task T016: "Write unit tests for sendChatMessage()"
Task T018: "Write unit tests for fetchConversationHistory()"
Task T020: "Write unit tests for getOrCreateConversation()"

# Then implement in sequence to make tests pass:
Task T013: "Implement getUserTimezone()"
Task T015: "Implement usePanelState()"
Task T017-T021: "Implement chat API functions"
```

---

## Implementation Strategy

### MVP First (User Stories 1-3 Only)

1. Complete Phase 1: Setup → ~30 minutes
2. Complete Phase 2: Foundational → ~2-3 hours
3. Complete Phase 3: User Story 1 (Auth) → ~1.5-2 hours
4. Complete Phase 4: User Story 2 (UI) → ~3-4 hours
5. Complete Phase 5: User Story 3 (Task Creation) → ~2.5-3 hours
6. **STOP and VALIDATE**: Test MVP independently → ~30 minutes
7. Total MVP time: **10-13 hours**

At this point, you have a fully functional chat interface for task creation with authentication and responsive UI.

### Incremental Delivery (Add P2 Features)

After MVP validation:
1. Add User Story 4 (Real-time Feedback) → ~1.5-2 hours → Deploy/Demo
2. Add User Story 5 (Conversation History) → ~1.5-2 hours → Deploy/Demo
3. Add User Story 6 (Timezone Awareness) → ~1.5-2 hours → Deploy/Demo
4. Complete Phase 9 (Polish & Edge Cases) → ~3-4 hours → Final deployment

Total feature time: **18-23 hours**

### Parallel Team Strategy

With multiple developers:

1. **Team completes Setup + Foundational together** → ~3 hours
2. **Sequential P1 stories** (must be done in order):
   - Developer A: User Story 1 (Auth) → ~2 hours
   - Then Developer A: User Story 2 (UI) → ~4 hours
   - Then Developer A: User Story 3 (Task Creation) → ~3 hours
3. **Parallel P2 stories** (after MVP complete):
   - Developer B: User Story 4 (Real-time Feedback) → ~2 hours
   - Developer C: User Story 5 (Conversation History) → ~2 hours
   - Developer D: User Story 6 (Timezone Awareness) → ~2 hours
4. **All developers**: Phase 9 (Polish) → ~4 hours

Parallel team completion time: **12-15 hours** (with 3-4 developers)

---

## Task Sizing Analysis

### Task Size Breakdown (15-30 minute target)

**Appropriately Sized Tasks (15-30 min)**:
- ✅ T001-T011: Setup and directory creation (simple operations)
- ✅ T012-T023: Unit test writing and function implementation (focused, testable)
- ✅ T024-T032: Component creation with tests (small, focused components)
- ✅ T033-T051: UI component implementation (incremental feature additions)
- ✅ T052-T069: Natural language integration (step-by-step API integration)
- ✅ T070-T079: Real-time feedback (small UI enhancements)
- ✅ T080-T092: Conversation history (incremental pagination features)
- ✅ T093-T101: Timezone handling (focused utility functions)
- ✅ T102-T128: Edge cases and polish (small, isolated improvements)

**Tasks That Could Be Split Further** (if needed):
- T038-T042: ChatPanel component (currently 5 tasks, could combine T040-T042 into one 25-min task)
- T063-T067: Task integration (currently 5 tasks, but appropriately sized for complexity)

**Tasks That Could Be Combined** (if needed):
- T005-T011: Directory creation (could be 1 task, but kept separate for parallel execution)
- T118-T122: Test runs (could be 1 task, but kept separate for parallel CI/CD runs)

### Validation

All tasks meet the **15-30 minute sizing requirement**:
- Simple tasks (directory creation, imports): **10-15 minutes**
- Unit test writing: **15-20 minutes per function**
- Component implementation: **20-30 minutes per component**
- Integration tasks: **20-30 minutes per integration point**
- Testing/QA tasks: **15-25 minutes per test type**

**Total Tasks**: 128 tasks
**Estimated Total Time**: 18-23 hours (as calculated above)
**Average Task Time**: ~10-15 minutes (accounting for parallelization)

---

## Notes

- [P] tasks = different files, no dependencies (can run in parallel)
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Follow TDD: Write tests FIRST, ensure they FAIL before implementing
- Commit after each logical group of tasks (e.g., after completing a component)
- Stop at any checkpoint to validate story independently
- All tasks are sized for 15-30 minute completion time
- Tasks requiring more time have been split into smaller subtasks
