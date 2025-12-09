# Feature Specification: FastAPI REST API Conversion

**Feature Branch**: `003-fastapi-rest-api`
**Created**: 2025-12-09
**Status**: Draft
**Input**: User description: "Convert todo app to FastAPI RESTful API endpoints"

## Clarifications

### Session 2025-12-09
- Q: Should rate limiting primarily track by authenticated user_id (when JWT present) or by IP address? → A: User-based with IP fallback (track by user_id when JWT is present, fall back to IP address for unauthenticated requests or failed auth)
- Q: How should session tokens be validated (claim extraction vs database lookup)? → A: Database-driven validation - FastAPI validates opaque session tokens by querying user_sessions table directly in shared Neon PostgreSQL database (no JWT decoding or cryptographic verification)
- Q: What are the column names in the user_sessions table? → A: id (UUID), user_id (UUID FK to users.id), token_hash (string 255, unique), refresh_token_hash (string 255, nullable), ip_address (text), user_agent (text), created_at (timestamp), expires_at (timestamp), last_activity_at (timestamp), revoked (boolean)
- Q: What are the specific rate limit values for read and write operations? → A: Read operations: 100 requests per minute, Write operations: 30 requests per minute (3:1 read/write ratio)
- Q: What are the allowed CORS origins for the API? → A: localhost:3000 for development, production domain configured via environment variables for production deployment
- Q: How is the session token extracted and validated? → A: HTTPBearer security scheme extracts bearer token from Authorization header, token is hashed using shared secret (SESSION_HASH_SECRET env var) and queried against user_sessions table (WHERE token_hash = hashed_token AND expires_at > now)
- Q: Should session tokens be hashed before database storage/lookup? → A: Yes, use token hashing with shared SESSION_HASH_SECRET environment variable between auth-server and FastAPI backend for consistent hashing (security best practice - protects tokens if database is compromised)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View All Tasks via API (Priority: P1)

A web application needs to fetch and display all tasks from the todo system. The frontend makes an HTTP GET request to retrieve the complete list of tasks with their details.

**Why this priority**: This is the foundational read operation that every web interface needs. Without the ability to list tasks, no other functionality is valuable. This delivers immediate value by making existing data accessible to web clients.

**Independent Test**: Can be fully tested by making a GET request to the tasks endpoint and verifying the response contains all tasks in JSON format. Delivers immediate value by exposing existing todo data to web applications.

**Acceptance Scenarios**:

1. **Given** the system has multiple tasks, **When** a client sends GET request to the tasks endpoint, **Then** all tasks are returned with ID, title, description, completion status, and creation timestamp
2. **Given** the system has no tasks, **When** a client sends GET request to the tasks endpoint, **Then** an empty list is returned with HTTP 200 status
3. **Given** tasks exist with varying completion statuses, **When** a client retrieves all tasks, **Then** both completed and incomplete tasks are included in the response

---

### User Story 2 - Create Task via API (Priority: P1)

A web application allows users to add new tasks. When a user submits a task through the web form, the frontend sends an HTTP POST request with the task details to create it in the system.

**Why this priority**: Task creation is the second most critical operation. Users need to add new tasks to get value from the system. This is testable independently and creates a usable MVP when combined with User Story 1 (view tasks).

**Independent Test**: Can be fully tested by sending POST requests with task data and verifying tasks are created with auto-generated IDs and proper validation. Delivers value by allowing web users to create new tasks.

**Acceptance Scenarios**:

1. **Given** valid task data with title and description, **When** client sends POST request, **Then** task is created with auto-generated ID and returned with all fields including creation timestamp
2. **Given** task data with title only (no description), **When** client sends POST request, **Then** task is created successfully with null description
3. **Given** task data with empty or whitespace-only title, **When** client sends POST request, **Then** request fails with HTTP 400 and validation error message
4. **Given** task data with title exceeding 200 characters, **When** client sends POST request, **Then** request fails with HTTP 400 and specific error about character limit
5. **Given** task data with description exceeding 1000 characters, **When** client sends POST request, **Then** request fails with HTTP 400 and specific error about description limit

---

### User Story 3 - Retrieve Single Task via API (Priority: P2)

A web application needs to display detailed information about a specific task. The frontend makes an HTTP GET request with a task ID to retrieve that task's complete details.

**Why this priority**: While viewing all tasks (P1) provides basic functionality, viewing individual task details is essential for task detail pages and edit workflows. This is independently testable and delivers value for detailed task inspection.

**Independent Test**: Can be fully tested by requesting specific task IDs and verifying correct task details are returned, or appropriate errors for non-existent IDs. Delivers value by enabling task detail views in web applications.

**Acceptance Scenarios**:

1. **Given** a task exists with ID 5, **When** client sends GET request for task 5, **Then** complete task details are returned with HTTP 200
2. **Given** no task exists with ID 999, **When** client sends GET request for task 999, **Then** HTTP 404 is returned with appropriate error message
3. **Given** client sends GET request with invalid ID format (non-numeric), **When** request is processed, **Then** HTTP 400 is returned with validation error

---

### User Story 4 - Update Task Completion Status via API (Priority: P2)

A web application shows tasks with checkboxes. When a user clicks a checkbox to mark a task complete (or incomplete), the frontend sends an HTTP PATCH/PUT request to update the completion status.

**Why this priority**: Marking tasks complete is a core todo list operation. This is independently testable and delivers value by allowing users to track task completion through the web interface.

**Independent Test**: Can be fully tested by sending update requests and verifying the completion status changes and previous state is preserved. Delivers value by enabling task completion tracking.

**Acceptance Scenarios**:

1. **Given** an incomplete task, **When** client sends request to mark it complete, **Then** task completion status updates to true and other fields remain unchanged
2. **Given** a complete task, **When** client sends request to mark it incomplete, **Then** task completion status updates to false
3. **Given** client sends update for non-existent task, **When** request is processed, **Then** HTTP 404 is returned with error message

---

### User Story 5 - Update Task Details via API (Priority: P3)

A web application has an "edit task" form where users can modify the task title and description. The frontend sends an HTTP PUT/PATCH request with updated task data.

**Why this priority**: While useful, editing task content is less critical than basic CRUD operations. Users can work around this by deleting and recreating tasks. This is independently testable and delivers editing functionality.

**Independent Test**: Can be fully tested by sending update requests with new title/description and verifying changes are persisted with proper validation. Delivers value by enabling task editing.

**Acceptance Scenarios**:

1. **Given** an existing task, **When** client sends update with new title and description, **Then** task is updated with new values and ID/creation time remain unchanged
2. **Given** an existing task, **When** client sends update with invalid title (empty or too long), **Then** HTTP 400 is returned with validation error and task remains unchanged
3. **Given** client sends update for non-existent task, **When** request is processed, **Then** HTTP 404 is returned

---

### User Story 6 - Delete Task via API (Priority: P3)

A web application shows a delete button next to each task. When a user clicks delete, the frontend sends an HTTP DELETE request to remove the task from the system.

**Why this priority**: Deletion is important but less critical than creation and viewing. This is independently testable and completes the full CRUD operation set.

**Independent Test**: Can be fully tested by sending DELETE requests and verifying tasks are removed and subsequent requests return 404. Delivers value by allowing task cleanup.

**Acceptance Scenarios**:

1. **Given** a task exists with ID 3, **When** client sends DELETE request for task 3, **Then** task is removed and HTTP 200/204 is returned
2. **Given** task is deleted, **When** client attempts to retrieve deleted task, **Then** HTTP 404 is returned
3. **Given** client sends DELETE for non-existent task, **When** request is processed, **Then** HTTP 404 is returned with error message
4. **Given** a task exists, **When** client sends DELETE request and task has been deleted by another request, **Then** HTTP 404 is returned (idempotency)

---

### User Story 7 - Bulk Delete Tasks via API (Priority: P3)

A web application has a "select multiple tasks" feature with a bulk delete button. The frontend sends a single request with multiple task IDs to delete them all at once.

**Why this priority**: This is a convenience feature that improves UX but isn't essential. Users can delete tasks one at a time. This is independently testable.

**Independent Test**: Can be fully tested by sending requests with multiple IDs and verifying all are deleted, with proper reporting of successes and failures. Delivers value by improving efficiency for batch operations.

**Acceptance Scenarios**:

1. **Given** tasks with IDs 1, 2, 3 exist, **When** client sends bulk delete request with those IDs, **Then** all three tasks are deleted and success response lists all deleted IDs
2. **Given** tasks 1 and 3 exist but task 2 does not, **When** client sends bulk delete for IDs 1, 2, 3, **Then** tasks 1 and 3 are deleted and response indicates task 2 was not found
3. **Given** client sends bulk delete with empty ID list, **When** request is processed, **Then** HTTP 400 is returned with validation error

---

### User Story 8 - Protected Endpoints with Session Authentication (Priority: P1)

A user logs in through the better-auth authentication server, receives a session token, and the web application includes this token in subsequent API requests. FastAPI validates the session by querying the user_sessions table in the shared database and authorizes access to user-specific tasks.

**Why this priority**: Authentication is foundational for a production web application. Without it, all tasks would be public, which is unacceptable. This must be implemented early to ensure proper data isolation.

**Independent Test**: Can be fully tested by sending requests with valid/invalid/expired session tokens and verifying proper authorization via database lookup. Delivers value by securing the API.

**Acceptance Scenarios**:

1. **Given** a valid session token from better-auth server, **When** client sends request with token in Authorization header, **Then** FastAPI queries user_sessions table, validates session, and user accesses their own tasks
2. **Given** no session token provided, **When** client sends request to protected endpoint, **Then** HTTP 401 Unauthorized is returned
3. **Given** an expired or invalid session token, **When** client sends request, **Then** database lookup finds no active session and HTTP 401 Unauthorized is returned with appropriate error message
4. **Given** a valid session token for User A, **When** client attempts to access User B's tasks, **Then** HTTP 403 Forbidden is returned (user_id from session doesn't match task owner)
5. **Given** session token validation, **When** session is validated, **Then** user_sessions table in shared Neon PostgreSQL database is queried to verify session validity and extract user_id

---

### User Story 9 - Rate Limiting for API Protection (Priority: P2)

The API implements rate limiting to prevent abuse and ensure fair resource usage. Clients receive appropriate feedback when they exceed rate limits.

**Why this priority**: Rate limiting is essential for production APIs to prevent abuse and ensure stability. This is independently testable and protects the system.

**Independent Test**: Can be fully tested by sending rapid successive requests and verifying rate limit enforcement. Delivers value by protecting API resources.

**Acceptance Scenarios**:

1. **Given** a client makes requests within rate limits, **When** requests are sent, **Then** all requests are processed successfully
2. **Given** a client exceeds the rate limit, **When** additional requests are sent, **Then** HTTP 429 Too Many Requests is returned with Retry-After header
3. **Given** rate limit is exceeded, **When** client waits for the specified time period, **Then** subsequent requests are processed normally
4. **Given** different endpoints have different rate limits, **When** client accesses various endpoints, **Then** limits are enforced independently per endpoint

---

### Edge Cases

- What happens when a client sends malformed JSON in the request body?
- How does the API handle concurrent updates to the same task?
- What happens when the database connection to Neon PostgreSQL fails or times out?
- How does the system handle very large response payloads (thousands of tasks)?
- What happens when a client sends requests with missing required fields?
- How does the API respond to unsupported HTTP methods (e.g., PATCH instead of PUT)?
- What happens when task ID in URL doesn't match any existing task?
- How does the system handle special characters and Unicode in task titles/descriptions?
- What happens when the shared database is unavailable during session validation?
- How does the system handle session tokens that exist in user_sessions but reference users who no longer exist in the users table?
- What happens if FastAPI uses a different hashing algorithm than the auth server for token validation?
- How does the system handle sessions marked as revoked=true in the database?
- What happens when rate limit state needs to be shared across multiple API instances?
- How does the system handle database transaction failures during task operations?

## Requirements *(mandatory)*

### Functional Requirements

#### Core API Operations
- **FR-001**: System MUST expose RESTful HTTP endpoints for all task operations (create, read, update, delete)
- **FR-002**: System MUST accept and return JSON-formatted data for all API requests and responses
- **FR-003**: System MUST validate incoming task data and return appropriate HTTP status codes (400 for validation errors, 401 for unauthorized, 403 for forbidden, 404 for not found, 429 for rate limit, 200/201 for success)
- **FR-004**: System MUST preserve existing business logic and validation rules (title length limits, description limits, ID validation)
- **FR-005**: System MUST generate unique task IDs for new tasks (implementation can use auto-increment or UUID)
- **FR-006**: System MUST handle errors gracefully and return structured error responses with descriptive messages
- **FR-007**: System MUST support retrieval of all tasks for authenticated user as a collection
- **FR-008**: System MUST support retrieval of individual tasks by ID (user can only access their own tasks)
- **FR-009**: System MUST allow updating task completion status independently from other fields
- **FR-010**: System MUST allow full task updates (title, description)
- **FR-011**: System MUST support single task deletion by ID
- **FR-012**: System MUST support bulk deletion of multiple tasks by ID list
- **FR-013**: System MUST include appropriate HTTP headers (Content-Type, Authorization, etc.) in all responses
- **FR-014**: System MUST handle CORS allowing localhost:3000 for development and production domain (configured via environment variable) for production deployment

#### Database Persistence
- **FR-015**: System MUST persist all task data to Neon serverless PostgreSQL database
- **FR-016**: System MUST use async database operations to maintain performance
- **FR-017**: System MUST handle database connection pooling for efficient resource usage
- **FR-018**: System MUST maintain data integrity through proper transaction management
- **FR-019**: System MUST associate each task with a user ID (owner) for proper data isolation
- **FR-020**: System MUST handle database migration and schema versioning

#### Authentication & Authorization
- **FR-021**: System MUST extract bearer token from Authorization header using HTTPBearer security scheme
- **FR-022**: System MUST hash the extracted token using SESSION_HASH_SECRET environment variable (same secret shared with auth server)
- **FR-023**: System MUST query user_sessions table WHERE token_hash = hashed_token AND expires_at > current_timestamp
- **FR-024**: System MUST verify session is not revoked (revoked = false) from query result
- **FR-025**: System MUST extract user_id (UUID) from the validated session record
- **FR-026**: System MUST use the shared Neon PostgreSQL database instance that auth server also uses for session management
- **FR-027**: System MUST enforce user isolation (users can only access their own tasks via user_id from session)
- **FR-028**: System MUST return HTTP 401 for missing or invalid session tokens (not found in user_sessions, expired, or revoked)
- **FR-029**: System MUST return HTTP 403 when authenticated user attempts unauthorized access

#### Rate Limiting
- **FR-029**: System MUST implement rate limiting using user-based tracking (by user_id UUID from session validation) for authenticated requests, falling back to IP-based tracking for unauthenticated or failed authentication requests
- **FR-030**: System MUST return HTTP 429 with Retry-After header when rate limits are exceeded
- **FR-031**: System MUST enforce rate limits of 100 requests per minute for read operations (GET endpoints) and 30 requests per minute for write operations (POST, PUT, PATCH, DELETE endpoints)
- **FR-032**: System MUST persist rate limit state to handle distributed deployments

### Key Entities

- **Task**: Represents a todo item with attributes: ID (unique identifier, auto-generated), user_id (UUID, foreign key reference to users.id), title (1-200 characters, required), description (0-1000 characters, optional), completion status (boolean), creation timestamp (datetime), last updated timestamp (datetime)
- **UserSession**: Represents validated session from user_sessions table with attributes: id (UUID), user_id (UUID), token_hash (string 255), expires_at (timestamp), revoked (boolean), last_activity_at (timestamp), ip_address (text), user_agent (text)
- **TaskCollection**: Represents a list of tasks for authenticated user returned by the "get all tasks" endpoint, includes array of task objects
- **ErrorResponse**: Represents validation or system errors with attributes: error message, error code/type, HTTP status code
- **RateLimitInfo**: Represents rate limiting state with attributes: requests remaining, reset time, limit window

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Web clients can retrieve all tasks in under 300 milliseconds for collections of up to 1000 tasks (including database query time)
- **SC-002**: API endpoints return appropriate HTTP status codes (200, 201, 400, 401, 403, 404, 429) for all scenarios as defined in acceptance criteria
- **SC-003**: 100% of existing CLI validation rules are preserved and enforced in API endpoints
- **SC-004**: API successfully handles concurrent requests from multiple clients without data corruption
- **SC-005**: Error responses include clear, actionable messages that help developers debug issues
- **SC-006**: All CRUD operations are accessible via standard REST conventions (GET, POST, PUT/PATCH, DELETE)
- **SC-007**: API responses follow consistent JSON structure across all endpoints
- **SC-008**: Session token validation via database lookup completes in under 100 milliseconds
- **SC-009**: Rate limiting prevents any single user from exceeding configured limits (100 requests per minute for reads, 30 requests per minute for writes)
- **SC-010**: Database operations use connection pooling and maintain response times under 200ms for single-task operations
- **SC-011**: Users can only access their own tasks (100% data isolation enforcement)
- **SC-012**: API successfully reconnects to Neon PostgreSQL after temporary network failures

## Assumptions *(mandatory)*

- Neon serverless PostgreSQL database will be used for persistent storage of tasks and is shared between auth server and FastAPI backend
- The better-auth Node.js server is already implemented and manages user authentication, creating session records in user_sessions table
- Session tokens are provided by better-auth and stored hashed (as token_hash) in the user_sessions table along with user_id (UUID), expires_at, revoked status
- Both FastAPI backend and auth-server share the same JWT_SECRET and JWT_ALGORITHM environment variables to ensure consistent token hashing across services
- The API will be accessed by a web frontend that handles authentication flow with better-auth and passes session tokens in Authorization header
- FastAPI and auth server share the same Neon PostgreSQL database instance (no inter-service HTTP calls needed for session validation)
- Auth server manages users and user_sessions tables (UUIDs for all IDs); FastAPI manages tasks table
- Standard REST conventions will be followed (GET for reads, POST for creates, PUT/PATCH for updates, DELETE for deletes)
- JSON will be the only supported request/response format (no XML, form data, etc.)
- CORS configuration will allow localhost:3000 for development and production domain specified via environment variable
- The API may run as multiple instances behind a load balancer (rate limiting must account for this)
- Task IDs will use database-generated identifiers (auto-generated, integer or UUID)
- The existing task validation logic (title length, description length) meets all current needs
- Rate limiting configuration will be environment-specific (stricter in production)

## Constraints *(mandatory)*

- Must reuse existing Task model and validation logic from CLI version (adapt for database persistence)
- Must maintain compatibility with existing task data structure and validation rules
- Must integrate with existing better-auth Node.js authentication server (cannot modify auth server or user_sessions schema)
- Must use shared Neon serverless PostgreSQL instance with auth server (specified database provider)
- Must use the same JWT_SECRET and JWT_ALGORITHM as auth server for consistent token hashing (configured via environment variables)
- API must be runnable locally for development with local/dev database connection
- Must follow Python type hints and existing code quality standards (ruff, mypy, pytest)
- Response times must be under 300ms for operations including database queries
- Must use standard HTTP status codes and REST conventions
- Session validation via database lookup must not add more than 100ms latency to requests
- Rate limiting must work in distributed deployment scenarios (multiple API instances)
- Database migrations must be reversible and version-controlled
- Must not modify tables managed by auth server (users, user_sessions)

## Dependencies *(mandatory)*

#### Core Framework
- **FastAPI framework**: Required for building REST API endpoints
- **Pydantic**: Required for request/response validation and serialization (comes with FastAPI)
- **Uvicorn**: Required as ASGI server to run FastAPI application
- **Python 3.12+**: Current runtime requirement

#### Database
- **SQLAlchemy 2.0+**: Async ORM for database operations
- **asyncpg** or **psycopg3**: Async PostgreSQL driver for Neon database connection
- **Alembic**: Database migration tool for schema versioning

#### Authentication & Security
- **hashlib** or equivalent: For hashing session tokens before database lookup (must match auth server's hashing algorithm)

#### Rate Limiting
- **slowapi** or **fastapi-limiter**: Rate limiting middleware for FastAPI
- **redis-py** (optional): If using Redis for distributed rate limit state

#### Testing
- **pytest**: Test framework
- **pytest-asyncio**: Async test support
- **httpx**: Async HTTP client for API testing
- **factory-boy**: Test data factories

#### Development
- **Existing codebase**: Task model (src/models/task.py), validators (src/cli/validators.py) - to be adapted for database use

#### External Services
- **better-auth server**: Node.js authentication server (external dependency, not installed via pip)
- **Neon PostgreSQL**: Serverless database service (external dependency)

## Out of Scope *(mandatory)*

- **User registration and password management** (handled by better-auth server)
- **Token refresh flows** (handled by better-auth server)
- **Email verification and password reset** (handled by better-auth server)
- Real-time updates via WebSockets or Server-Sent Events
- API versioning (will be single version)
- Comprehensive logging and monitoring infrastructure (basic logging only)
- Deployment configuration and containerization (development setup only)
- Frontend web application (separate phase)
- Data migration from existing CLI in-memory data to PostgreSQL (will start fresh)
- GraphQL or other API paradigms
- File upload/download for task attachments
- Task categories, tags, or labels
- Task prioritization or ordering
- Recurring tasks or task scheduling
- Task history and audit trail
- Bulk update operations (bulk delete is in scope, bulk update is not)
- Task sharing between users
- Team/workspace features
- Advanced search and filtering (basic filtering by completion status acceptable)
