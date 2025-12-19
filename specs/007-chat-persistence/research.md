# Research: Chat Persistence & Chat Service Foundation

**Feature**: Chat Persistence (Branch: `007-chat-persistence`)
**Date**: 2025-12-19
**Status**: Research Complete

## 1. Authentication Strategy (Better-Auth + Python)

**Decision**: **Direct Database Session Validation**.
- **Rationale**: Replicate the logic from `backend/src/services/auth_service.py` to ensure consistent authentication across the system.
- **Mechanism**:
  1. Extract the `tokenId` from the Bearer token.
  2. Query `user_sessions` (camelCase columns: `userId`, `token`, `expiresAt`).
  3. Validate that `expiresAt` is in the future.

## 2. Database Design (SQLModel)

**Decision**: **Single PostgreSQL Database (Neon)**.
- **Rationale**: Shared data access with `auth-server` and `backend` services.
- **Schema**:
  - `conversations`: Stores session metadata.
  - `messages`: Stores history.
  - `user_sessions`: (Read-only) for auth validation.

## 3. API Design

**Decision**: **Standard REST (JSON)**.
- **Rationale**: For this phase, we don't need SSE or WebSockets as the system simply saves and echoes/retrieves messages. This keeps the implementation robust and easy to test.

## 4. Architecture

**Structure**:
```text
ai-agent/
├── src/
│   ├── ai_agent/
│   │   ├── api/
│   │   │   ├── deps.py      # Auth and DB dependencies
│   │   │   ├── chat.py      # POST /api/chat
│   │   │   └── history.py   # GET /api/conversations
│   │   ├── database/
│   │   │   ├── connection.py
│   │   │   └── models.py    # SQLModel definitions
│   │   ├── services/
│   │   │   └── auth.py      # Shared auth logic
│   │   └── main.py
└── tests/
```
