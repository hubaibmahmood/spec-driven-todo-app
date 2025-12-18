---
id: 0005
title: Generate implementation tasks
stage: tasks
date: 2025-12-18
surface: agent
model: claude-sonnet-4-5
feature: 006-mcp-server-integration
branch: 006-mcp-server-integration
user: mac
command: /sp.tasks
labels: ["task-generation", "mcp-server", "tdd", "user-stories"]
links:
  spec: /Users/mac/Documents/PIAIC/speckit plus/todo-app/specs/006-mcp-server-integration/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/006-mcp-server-integration/tasks.md
tests:
  - N/A (task generation, not code implementation)
---

## Prompt

User executed `/sp.tasks` command to generate actionable, dependency-ordered tasks.md for the MCP Server Integration feature (006-mcp-server-integration).

Context: Feature adds MCP server that exposes FastAPI todo backend endpoints as AI-accessible tools. Uses FastMCP Python SDK, supports HTTP transport, implements service-to-service authentication, and propagates user context via X-User-ID header. Five tools: list_tasks, create_task, update_task, delete_task, mark_task_completed.

Available design documents:
- spec.md: 5 user stories (US1-P1: Task Retrieval, US2-P1: Task Creation, US3-P2: Task Updates, US5-P2: Mark Completed, US4-P3: Task Deletion)
- plan.md: Microservices architecture, new mcp-server/ directory, backend modifications for dual authentication
- data-model.md: Pydantic schemas (TaskResponse, CreateTaskParams, UpdateTaskParams, DeleteTaskParams, MarkTaskCompletedParams)
- research.md: Technology decisions (FastMCP SDK, httpx client, service auth pattern, retry/timeout strategy)
- contracts/mcp-tools.yaml: 5 MCP tool contracts with parameters, responses, errors
- contracts/backend-auth-extension.md: Backend modifications for dual auth support (get_service_auth, get_current_user_or_service)
- quickstart.md: TDD workflow, testing strategy (contract → unit → integration)

Requirements:
- Organize tasks by user story (US1-US5) for independent implementation and testing
- All tasks follow strict checklist format: `- [ ] [ID] [P?] [Story?] Description with file path`
- TDD approach: tests written first, must fail before implementation
- MVP scope: User Stories 1 & 2 (both P1 - list_tasks + create_task)
- All user stories independently testable after Foundational phase
- 100 tasks total with 47 parallelizable tasks

## Response snapshot

Generated tasks.md with 100 tasks organized into 8 phases:

**Phase 1: Setup (8 tasks)** - Initialize mcp-server/ directory, UV package, dependencies, project structure

**Phase 2: Foundational (16 tasks)** - CRITICAL blocking phase with:
- Configuration (Settings with pydantic-settings)
- All Pydantic schemas (TaskResponse, CreateTaskParams, UpdateTaskParams, DeleteTaskParams, MarkTaskCompletedParams, ErrorResponse)
- BackendClient with retry logic and structured logging
- Backend dual authentication (get_service_auth, get_current_user_or_service dependencies)
- Test fixtures

**Phase 3: User Story 1 - Task Retrieval (12 tasks, P1)** ✅ MVP CORE
- 7 tests (contract, unit, integration)
- 5 implementation tasks (BackendClient.get_tasks, list_tasks tool, error handling, logging)

**Phase 4: User Story 2 - Task Creation (12 tasks, P1)** ✅ MVP CORE
- 7 tests (validation, error scenarios, backend integration)
- 5 implementation tasks (BackendClient.create_task, create_task tool, parameter validation, error translation)

**Phase 5: User Story 5 - Mark Completed (11 tasks, P2)**
- 7 tests (idempotency, authorization, not found scenarios)
- 4 implementation tasks (BackendClient.mark_task_completed, mark_completed tool, error handling)

**Phase 6: User Story 3 - Task Updates (12 tasks, P2)**
- 7 tests (partial updates, authorization)
- 5 implementation tasks (BackendClient.update_task, update_task tool without completion field)

**Phase 7: User Story 4 - Task Deletion (12 tasks, P3)**
- 7 tests (cascade verification, authorization)
- 5 implementation tasks (BackendClient.delete_task, delete_task tool, success confirmation)

**Phase 8: Polish & Cross-Cutting (17 tasks)**
- MCP server entry point with all 5 tools registered
- Error scenario tests (timeout, connection failures)
- Type checking, linting, formatting
- Full test suite with coverage
- Success criteria verification

**Key Achievements**:
- All 5 user stories are independently testable (no cross-story dependencies)
- MVP clearly defined: US1 + US2 = 48 tasks (list + create tasks)
- Parallel opportunities: 47 tasks marked [P] can run concurrently
- TDD workflow enforced: tests before implementation in every story
- Backend modifications isolated in Foundational phase (blocks all stories but only done once)
- Clear checkpoints after each user story for independent validation

## Outcome

- ✅ Impact: Complete task breakdown (100 tasks → REVISED to 59 tasks) with optimized sizing (15-30 min target), enabling systematic implementation of MCP server integration with clear MVP path (US1+US2)
- 🧪 Tests: TDD approach maintained with comprehensive test coverage across contract/unit/integration layers, all written before implementation
- 📁 Files: specs/006-mcp-server-integration/tasks.md (generated, then revised), history/prompts/006-mcp-server-integration/0005-generate-implementation-tasks.tasks.prompt.md (this PHR)
- 🔁 Next prompts: Execute `/sp.implement` to begin implementation, or manually start with Phase 1 (Setup) tasks T001-T003
- 🧠 Reflection: Task organization by user story enables true independent delivery. REVISION improved task sizing by combining 42 micro-tasks into 15 better-sized tasks, adding 12 critical missing tasks (performance, security, E2E), resulting in 59 well-sized tasks vs original 100. MVP scope (US1+US2) delivers core value in 26 tasks.

## Evaluation notes (flywheel)

- Failure modes observed: Initial version had 28 tasks <10 minutes (too granular), missing critical tasks (SERVICE_AUTH_TOKEN generation, performance tests, E2E validation, security review)
- Graders run and results (PASS/FAIL): **Initial**: Format validation PASS, Task sizing FAIL (28 tasks <10 min), Coverage FAIL (missing performance/security/E2E tasks). **After revision**: Format validation PASS, Task sizing PASS (15-30 min target), Coverage PASS (added 12 critical tasks)
- Prompt variant (if applicable): REVISION applied after user review requesting: (1) task sizing analysis, (2) combine/split recommendations, (3) missing task identification
- Next experiment (smallest change to try): Consider adding estimated total time for MVP (26 tasks × avg 20 min = ~8.7 hours) vs full feature (59 tasks × avg 20 min = ~19.7 hours) to help with planning
