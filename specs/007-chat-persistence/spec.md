# Feature Specification: Chat Persistence Service

**Feature Branch**: `007-chat-persistence`
**Created**: 2025-12-19
**Status**: Draft
**Input**: User description: "Stateless chat endpoint that persists conversation state to database"

## Clarifications

### Session 2025-12-19
- Q: Should we add explicit GET endpoints for history retrieval? → A: Yes, add `GET /api/conversations` and `GET /api/conversations/{id}`.
- Q: How should the Chat Session title be created without AI? → A: Use a default format: "Chat - [YYYY-MM-DD HH:MM]".
- Q: Should the API response wait for the DB save? → A: Yes, for this phase, the API will be a standard JSON POST/GET.

## User Scenarios & Testing

### User Story 1 - Start New Conversation (Priority: P1)

As a user, I want to send a message so that a new conversation is created and my message is saved.

**Acceptance Scenarios**:
1. **Given** an authenticated user, **When** they POST to `/api/chat` with `{"message": "Hello"}`, **Then** the system creates a `Conversation` record, saves the message, and returns a JSON response containing the new `conversation_id` and an "echo" response.

### User Story 2 - View Conversation History (Priority: P2)

As a user, I want to retrieve my previous messages so that I can see the context of my chat.

**Acceptance Scenarios**:
1. **Given** an existing conversation, **When** the user GETs `/api/conversations/{id}`, **Then** they receive a list of all messages (User and System) for that conversation.
2. **Given** a conversation ID belonging to another user, **When** a user tries to access it, **Then** the system returns 404/403.

## Requirements

### Functional Requirements

- **FR-001**: The system MUST expose a FastAPI service (`chat-service`).
- **FR-002**: The system MUST validate user authentication using `better-auth` session tokens in the shared DB.
- **FR-003**: The system MUST persist all messages to a PostgreSQL database (Neon).
- **FR-004**: If no `conversation_id` is provided, a new `Conversation` MUST be created.
- **FR-005**: The system MUST enforce that users can only access their own conversations.
- **FR-006**: Messages MUST have a `role` (`user`, `assistant`, or `tool`) and `content`. For this phase, assistant responses will be simple echo messages. The `tool` role and `metadata` field are reserved for future OpenAI Agents SDK integration (spec 008).
- **FR-007**: `GET /api/conversations` MUST list the authenticated user's chat sessions ordered by `updated_at`.
- **FR-008**: `GET /api/conversations/{id}` MUST return message history in chronological order.

### Key Entities

- **Conversation**: `id`, `user_id`, `title`, `created_at`, `updated_at`.
- **Message**: `id`, `conversation_id`, `role` (`user`|`assistant`|`tool`), `content`, `metadata` (JSONB, nullable), `created_at`.

## Future Integration

This spec provides the persistence foundation for a multi-phase AI agent system:

### Spec 008 (Planned): OpenAI Agents SDK + MCP Integration
This persistence layer will be extended to support:
- OpenAI Agents SDK for intelligent responses
- MCP tool invocation by the AI agent
- Full conversation thread management with tool calls
- The `metadata` field will store `tool_calls` and `tool_call_id` per OpenAI's message format

### Spec 009 (Planned): Frontend Chatbot
- OpenAI ChatKit integration
- Real-time chat interface
- Integration with the AI Agent FastAPI backend

### API Stability Guarantee
The `/api/chat` and `/api/conversations` endpoints are designed to remain stable across these enhancements. Future specs will only modify the response generation logic (replacing echo with AI), not the API contract or persistence layer.

## Success Criteria

- **SC-001**: 100% of messages are successfully persisted and retrievable via API.
- **SC-002**: Unauthorized users are blocked from accessing data with 100% accuracy.
