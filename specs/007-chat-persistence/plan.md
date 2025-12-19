# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

This feature implements the foundational persistence layer for chat functionality. It provides a FastAPI service (`ai-agent` directory) with endpoints to create conversations, save messages, and retrieve history. Authentication is handled via direct database validation of `better-auth` tokens.

**Important**: This spec provides the persistence foundation only. The message schema is designed to be OpenAI-compatible (using `assistant`/`tool` roles and `metadata` field) to support future integration with OpenAI Agents SDK (spec 008) and frontend chatbot (spec 009). For now, the API returns simple echo responses.

## Technical Context

**Language/Version**: Python 3.12+ (managed by uv)  
**Primary Dependencies**: FastAPI, SQLModel, SQLAlchemy, Alembic (for migrations), httpx  
**Storage**: PostgreSQL (Neon)  
**Testing**: pytest (unit, integration, contract)  
**Target Platform**: Linux/Docker (Cloud Deployment)
**Project Type**: Web application (Microservice)  
**Performance Goals**: API response < 500ms for DB operations  
**Constraints**: Authenticated access only; Strict ownership validation  
**Scale/Scope**: CRUD for Conversations and Messages; History retrieval

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Test-First Development**: Mandatory for `ai-agent`. Tests must precede endpoints.
- [x] **Clean Code & Simplicity**: PEP 8 and type hints required.
- [x] **Proper Project Structure**: `ai-agent/src` and `ai-agent/tests` used.
- [!] **In-Memory Data Storage**: VIOLATION (PostgreSQL required for persistence). See Complexity Tracking.
- [x] **UV Package Manager**: Mandatory for dependency management.

## Project Structure

### Documentation (this feature)

```text
specs/007-chat-persistence/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── openapi.json
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
ai-agent/
├── pyproject.toml
├── src/
│   ├── ai_agent/
│   │   ├── api/          # Endpoints
│   │   ├── database/     # DB models and connection
│   │   ├── services/     # OpenAI and Auth logic
│   │   └── main.py       # App entry point
└── tests/
    ├── contract/
    ├── integration/
    └── unit/
```

**Structure Decision**: A dedicated `ai-agent` directory in the root, matching the pattern of `auth-server` and `backend`, but specialized for the AI service.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| External Database (PostgreSQL) | Persistence requirement for chat history across sessions. | In-memory storage is lost on restart, failing the core requirement of "Persistence". |
