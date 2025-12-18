# Feature Specification: MCP Server Integration

**Feature Branch**: `006-mcp-server-integration`
**Created**: 2025-12-17
**Status**: Draft
**Input**: User description: "Create an MCP server that exposes our FastAPI todo backend endpoints as AI-accessible tools. The MCP server should: Use the official MCP Python SDK (FastMCP), Support HTTP transport for microservices architecture, Implement service-to-service authentication, Propagate user context via X-User-ID header, Expose tools for: list_tasks, create_task, update_task, delete_task, bulk_delete_tasks, Work with our existing better-auth session management, Call our FastAPI backend with service token authentication"

## Clarifications

### Session 2025-12-17

- Q: The current FastAPI backend validates user session tokens via `Depends(get_current_user)`. To support MCP server with SERVICE_AUTH_TOKEN + X-User-ID, what changes are required? → A: Backend must be modified to support dual authentication (user tokens from frontend, service token + X-User-ID from MCP)
- Q: FR-018 requires logging "all backend API calls with request/response details for debugging." What logging level and detail should be used? → A: INFO level with request/response logging (includes timestamps, endpoints, status codes, user IDs, error details)
- Q: Edge Cases mention "network failures between MCP server and FastAPI backend." What timeout and retry strategy should be used for backend HTTP requests? → A: 30 second timeout with 2 retries (exponential backoff: 1s, 2s)
- Q: Edge Cases mention "MCP server receives malformed tool parameters." How should parameter validation be handled before backend requests? → A: Validate parameters against JSON schema, return structured error with field-level details before calling backend
- Q: User Story 3 states "task status updates and user is notified." What notification mechanism should be implemented to inform the user of task updates? → A: No notification mechanism - "notified" means the tool returns updated task data in the response

## User Scenarios & Testing *(mandatory)*

### User Story 1 - AI Assistant Task Retrieval (Priority: P1)

An AI assistant needs to retrieve all tasks for a user when they ask "what's on my todo list?". The MCP server receives the user context, authenticates with the backend using service credentials, and returns the user's tasks.

**Why this priority**: This is the foundation of read-only operations and the most common user request. It establishes the authentication and user context propagation pattern that all other operations depend on.

**Independent Test**: Can be fully tested by asking an AI assistant "show me my tasks" and verifying it returns the authenticated user's task list without accessing other users' data. Delivers immediate value by making existing tasks visible to AI assistants.

**Acceptance Scenarios**:

1. **Given** an authenticated AI session with user context, **When** the AI calls list_tasks tool, **Then** only that user's tasks are returned
2. **Given** multiple users with different tasks, **When** each AI session calls list_tasks, **Then** each receives only their own tasks
3. **Given** an AI session without valid service credentials, **When** list_tasks is called, **Then** authentication fails with clear error message
4. **Given** a user with no tasks, **When** AI calls list_tasks, **Then** an empty list is returned successfully

---

### User Story 2 - AI Assistant Task Creation (Priority: P1)

An AI assistant creates a task when a user says "remind me to buy milk tomorrow". The MCP server receives the task details and user context, authenticates with the backend, and creates the task for that user.

**Why this priority**: Task creation is the core write operation and equally critical as retrieval. Together with P1 list_tasks, this provides a minimal viable AI-powered todo system.

**Independent Test**: Can be fully tested by asking an AI assistant "add 'buy milk' to my todo list" and verifying: (1) task appears in user's task list, (2) task is owned by correct user, (3) task data matches request. Delivers immediate value for AI-assisted task management.

**Acceptance Scenarios**:

1. **Given** an authenticated AI session, **When** user requests to create a task via AI, **Then** task is created and assigned to correct user
2. **Given** task creation request with title only, **When** create_task is called, **Then** task is created with title and default values for optional fields
3. **Given** task creation request with title, description, priority, and due date, **When** create_task is called, **Then** all fields are stored correctly
4. **Given** invalid task data (e.g., empty title), **When** create_task is called, **Then** validation error is returned with specific field errors

---

### User Story 3 - AI Assistant Task Updates (Priority: P2)

An AI assistant updates a task when a user says "mark the milk task as done" or "change the due date for project review to Friday". The MCP server identifies the task, validates ownership, and updates it.

**Why this priority**: Completing and modifying tasks is essential for task management but less critical than creating and viewing. Users can tolerate a brief period where they create and view tasks before being able to update them.

**Independent Test**: Can be fully tested by creating a task via AI, then asking "mark task X as complete" and verifying the task status changes. Then test "change task X description to Y" and verify field updates. Delivers value for managing task lifecycle through AI.

**Acceptance Scenarios**:

1. **Given** a user's task exists, **When** AI calls update_task to mark it complete, **Then** task status updates and updated task data is returned in the response (AI assistant informs user via natural language)
2. **Given** a user's task exists, **When** AI calls update_task to change title/description/priority/due_date, **Then** specified fields are updated and complete updated task is returned
3. **Given** a task owned by another user, **When** AI attempts to update it, **Then** operation is denied with authorization error
4. **Given** a non-existent task ID, **When** AI calls update_task, **Then** "task not found" error is returned

---

### User Story 4 - AI Assistant Single Task Deletion (Priority: P3)

An AI assistant deletes a task when a user says "remove the milk task". The MCP server verifies ownership and deletes the specified task.

**Why this priority**: Single task deletion is important for cleanup but less critical than CRUD operations. Users can tolerate accumulating completed tasks temporarily.

**Independent Test**: Can be fully tested by creating a task via AI, then asking "delete task X" and verifying: (1) task no longer appears in list, (2) subsequent operations on that task ID fail with "not found". Delivers value for AI-assisted task cleanup.

**Acceptance Scenarios**:

1. **Given** a user's task exists, **When** AI calls delete_task with task ID, **Then** task is removed from user's list
2. **Given** a task owned by another user, **When** AI attempts to delete it, **Then** operation is denied with authorization error
3. **Given** a non-existent task ID, **When** AI calls delete_task, **Then** "task not found" error is returned
4. **Given** a deleted task, **When** AI attempts to retrieve or update it, **Then** "task not found" error is returned

---

### User Story 5 - AI Assistant Mark Task Completed (Priority: P2)

An AI assistant marks a task as completed when a user says "mark task X as done" or "complete the milk task". The MCP server provides a simple, focused tool for this common operation.

**Why this priority**: Marking tasks complete is a frequent, fundamental operation that deserves a dedicated tool. While `update_task` can change completion status, having a focused `mark_task_completed` tool is more intuitive and simpler for AI assistants to use for this common action.

**Independent Test**: Can be fully tested by creating a task via AI, then asking "mark task X as complete" and verifying: (1) task completed status changes to true, (2) other fields remain unchanged, (3) updated task is returned. Delivers immediate value for the most common task lifecycle operation.

**Acceptance Scenarios**:

1. **Given** a user's incomplete task exists, **When** AI calls mark_task_completed with task ID, **Then** task completed status is set to true and updated task is returned
2. **Given** a user's task is already completed, **When** AI calls mark_task_completed with task ID, **Then** operation succeeds (idempotent) and task remains completed
3. **Given** a task owned by another user, **When** AI attempts to mark it complete, **Then** operation is denied with authorization error
4. **Given** a non-existent task ID, **When** AI calls mark_task_completed, **Then** "task not found" error is returned

---

### Edge Cases

- What happens when service authentication token is missing or invalid?
- What happens when user context (X-User-ID header) is missing from the request?
- How does the system handle network failures between MCP server and FastAPI backend? → MCP retries up to 2 times with exponential backoff (1s, 2s), then returns connection error to AI client after 30s total timeout
- What happens when the FastAPI backend is temporarily unavailable? → Same retry strategy as network failures; after exhausting retries, AI receives "service unavailable" error
- How does the system handle concurrent operations from the same AI session?
- What happens when MCP server receives malformed tool parameters? → Parameters are validated against JSON schema before backend call; structured validation error with field-level details returned immediately to AI without calling backend
- How does the system handle rate limiting if implemented on the backend?
- What happens when a user's session expires mid-operation?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: MCP server MUST use the official MCP Python SDK (FastMCP) for implementation
- **FR-002**: MCP server MUST support HTTP transport protocol for microservices communication
- **FR-003**: MCP server MUST implement service-to-service authentication using a dedicated service token (Bearer token in Authorization header)
- **FR-004**: MCP server MUST propagate user context to FastAPI backend via X-User-ID header in all requests
- **FR-021**: FastAPI backend MUST be modified to support dual authentication: (1) user session tokens from frontend via better-auth, and (2) service token + X-User-ID header from MCP server
- **FR-005**: MCP server MUST expose list_tasks tool that retrieves all tasks for the authenticated user
- **FR-006**: MCP server MUST expose create_task tool that creates a new task with title, description (optional), priority (optional), and due_date (optional)
- **FR-007**: MCP server MUST expose update_task tool that modifies task fields (title, description, priority, due_date) - completion status is handled by mark_task_completed
- **FR-008**: MCP server MUST expose delete_task tool that removes a single task by ID
- **FR-009**: MCP server MUST expose mark_task_completed tool that marks a task as completed by ID
- **FR-010**: MCP server MUST validate user context exists before making backend API calls
- **FR-011**: MCP server MUST authenticate all backend requests with service token in Authorization header
- **FR-012**: MCP server MUST handle and translate FastAPI error responses into user-friendly MCP error messages
- **FR-013**: MCP server MUST validate tool input parameters against JSON schema before making backend API calls, returning structured validation errors with field-level details for invalid parameters
- **FR-014**: MCP server MUST preserve error details from backend (404, 401, 403, 422) and communicate them appropriately to AI client
- **FR-026**: MCP server validation errors MUST include: error type (validation_error), list of invalid fields with specific error messages, and suggested corrections where applicable
- **FR-015**: MCP server MUST support JSON serialization for task data including datetime fields
- **FR-016**: Service token MUST be stored in environment variable (SERVICE_AUTH_TOKEN) and never hardcoded
- **FR-017**: FastAPI backend base URL MUST be configurable via environment variable (FASTAPI_BASE_URL)
- **FR-018**: MCP server MUST log all backend API calls at INFO level with request/response details including: timestamps, endpoint paths, HTTP status codes, user IDs (from X-User-ID header), and error details when failures occur
- **FR-019**: MCP server MUST use async/await patterns to match FastAPI backend's async architecture
- **FR-020**: MCP server tools MUST return structured data in JSON format compatible with AI assistant consumption
- **FR-027**: All write operations (create, update, delete) MUST return the complete resulting state in the response (created task, updated task, deletion confirmation) to enable AI assistant to inform the user
- **FR-022**: MCP server logging MUST be configurable via environment variable (MCP_LOG_LEVEL) with default value of INFO
- **FR-023**: MCP server MUST implement 30 second timeout for all backend HTTP requests
- **FR-024**: MCP server MUST retry failed backend requests up to 2 times with exponential backoff (1 second after first failure, 2 seconds after second failure)
- **FR-025**: MCP server MUST handle network errors and timeouts gracefully, returning structured error responses to AI client indicating the failure type (timeout, connection refused, etc.)

### Key Entities

- **MCP Tool**: Represents an AI-accessible operation (list_tasks, create_task, update_task, delete_task, mark_task_completed) that wraps a FastAPI backend endpoint
- **Service Token**: Authentication credential that identifies the MCP server as a trusted service to the FastAPI backend
- **User Context**: User identifier (user_id) extracted from AI session and propagated to backend via X-User-ID header
- **Task**: Todo item with attributes (id, title, description, completed, priority, due_date, created_at, updated_at, user_id) managed by backend
- **Backend Client**: HTTP client component that handles authentication, request construction, and error handling for FastAPI communication

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: AI assistants can successfully retrieve task lists for authenticated users without accessing other users' data (100% data isolation)
- **SC-002**: AI assistants can create tasks that persist in the backend database and appear in subsequent list operations
- **SC-003**: AI assistants can update task properties and the changes are reflected immediately in backend data
- **SC-004**: AI assistants can delete tasks and mark tasks completed, with changes reflected immediately in backend storage
- **SC-005**: MCP server rejects operations with missing or invalid service authentication with clear error messages
- **SC-006**: MCP server rejects operations with missing user context (X-User-ID) and returns actionable error details
- **SC-007**: All MCP tools complete operations within 2 seconds under normal network conditions
- **SC-008**: Error messages from backend validation failures are translated into AI-understandable format (not raw HTTP errors)
- **SC-009**: MCP server handles at least 100 concurrent AI requests without degradation
- **SC-010**: Service-to-service authentication prevents unauthorized access (no direct user session tokens accepted by MCP server)
- **SC-011**: Invalid tool parameters are rejected immediately with field-level validation errors before backend is called (fail fast validation)

## Assumptions

1. **Service Token Generation**: We assume a service authentication token will be generated externally and provided via environment variable. The MCP server does not need to implement token generation or rotation.

2. **User Context Extraction**: We assume the AI client (e.g., Claude Desktop) provides user context to the MCP server through standard MCP mechanisms. The MCP server extracts this context and forwards it to the backend.

3. **Backend API Stability**: We assume the FastAPI backend endpoints (/tasks) are stable and follow the documented API contract. The MCP server does not need to handle breaking changes in backend API structure.

4. **Single Backend Instance**: We assume a single FastAPI backend URL for all environments. Load balancing and service discovery are handled externally if needed.

5. **Error Handling Strategy**: We assume that returning detailed error messages to AI assistants is acceptable and does not pose a security risk. The AI client is considered a trusted intermediary.

6. **Network Reliability**: We assume standard internet reliability between MCP server and FastAPI backend. The MCP server implements retry logic (2 retries with exponential backoff) to handle transient failures but does not handle extended outages beyond the 30-second timeout window.

7. **Task Data Format**: We assume the task schema (TaskCreate, TaskResponse, TaskUpdate, etc.) from the backend remains compatible with MCP tool parameter types (strings, booleans, integers, ISO date strings).

8. **Deployment Model**: We assume the MCP server runs as a separate process from the FastAPI backend, enabling independent scaling and deployment.

## Dependencies

- **External Dependency**: Official MCP Python SDK (FastMCP) - provides MCP server implementation framework
- **External Dependency**: FastAPI backend (/tasks endpoints) - provides task management API that MCP server wraps; requires modification to support dual authentication
- **External Dependency**: Better-auth session management system - provides user authentication (consumed indirectly through user context)
- **External Dependency**: Neon PostgreSQL database - stores task data (accessed only through FastAPI backend)
- **Configuration Dependency**: SERVICE_AUTH_TOKEN environment variable - required for service-to-service authentication
- **Configuration Dependency**: FASTAPI_BASE_URL environment variable - required to locate backend API
- **Implementation Dependency**: Backend authentication layer modification - `get_current_user` dependency must support both user session tokens and service token + X-User-ID pattern
