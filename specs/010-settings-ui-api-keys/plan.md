# Implementation Plan: Settings UI for API Key Management

**Branch**: `010-settings-ui-api-keys` | **Date**: 2025-12-24 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/010-settings-ui-api-keys/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement a secure settings interface for users to manage their Gemini API keys. The feature adds a Settings tab in the Next.js frontend with password-masked input fields, API key validation (format and connectivity testing), and secure encrypted storage in PostgreSQL via FastAPI backend. Each user's API key is encrypted at rest using a master ENCRYPTION_KEY environment variable (AES-256/Fernet) and stored in a dedicated `user_api_keys` table. The AI agent backend will retrieve per-user keys for Gemini API calls, failing with clear error messages when keys are not configured (no global key fallback).

## Technical Context

**Language/Version**:
- Backend: Python 3.12+
- Frontend: TypeScript 5.x with Next.js 16.0.9 / React 19.2.1

**Primary Dependencies**:
- Backend: FastAPI 0.127.0+, SQLAlchemy 2.0+ (async), Alembic 1.13+, Pydantic 2.0+, cryptography 46.0.3+ (Fernet encryption), google-generativeai 0.8.6+ (Gemini SDK)
- Frontend: Next.js 16, React 19, Tailwind CSS 4, better-auth 1.4.6, lucide-react (icons)

**Storage**:
- Neon Serverless PostgreSQL (shared with FastAPI backend and auth server)
- New `user_api_keys` table with encrypted_key column

**Testing**:
- Backend: pytest with async support, pytest-cov, httpx (for async HTTP tests)
- Frontend: Jest 30+ with React Testing Library, Playwright for E2E

**Target Platform**:
- Backend: Linux server (Dockerized FastAPI with Uvicorn)
- Frontend: Web application (browser, responsive 320px-2560px)

**Project Type**: Web application (microservices: backend + frontend + ai-agent + auth-server + mcp-server)

**Performance Goals**:
- API key save operation: <500ms p95
- Settings page load: <1 second
- Test Connection API call: <3 seconds
- API key retrieval (for AI agent): <50ms added latency

**Constraints**:
- Security: API keys MUST be encrypted at rest (AES-256/Fernet with ENCRYPTION_KEY env var)
- Security: API keys MUST NEVER be logged in plaintext
- Security: Input field MUST be password-type (masked) by default
- User isolation: Each user has exactly one API key (unique constraint on user_id + provider)
- No fallback: AI agent MUST fail with error message if user has no configured key
- Backward compatibility: Must integrate with existing better-auth authentication

**Scale/Scope**:
- Multi-user support (10k+ users expected)
- Single API provider initially (Gemini only, extensible to others via `provider` column)
- 5 user stories (3 P1, 2 P2)
- 16 functional requirements, 8 non-functional requirements

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Test-First Development (NON-NEGOTIABLE)
- ✅ **PASS**: Spec includes testable acceptance scenarios for all 5 user stories
- ✅ **PASS**: Backend will use pytest with contract/integration/unit test structure
- ✅ **PASS**: Frontend will use Jest + React Testing Library for component tests
- ⚠️ **NOTE**: TDD cycle (Red-Green-Refactor) must be strictly followed during implementation

### Clean Code & Simplicity
- ✅ **PASS**: Python backend follows PEP 8, uses type hints (mypy strict mode enabled)
- ✅ **PASS**: TypeScript frontend uses strict type checking
- ✅ **PASS**: Single-purpose modules: models (UserApiKey), services (encryption, API key CRUD), API routes
- ✅ **PASS**: YAGNI principle respected: only implementing requested features (no multi-provider support yet despite extensible schema)

### Proper Project Structure
- ✅ **PASS**: Backend follows established structure (src/models/, src/services/, src/api/)
- ✅ **PASS**: Frontend follows established structure (app/, components/, lib/)
- ✅ **PASS**: Tests organized by type (contract/, integration/, unit/)
- ✅ **PASS**: Clear separation of concerns (data model, business logic, API layer, UI layer)

### Data Storage (Modified for Web App Context)
- ✅ **PASS**: Using PostgreSQL (established in spec 003) for persistent storage
- ✅ **PASS**: Data layer isolated via SQLAlchemy ORM models and repository/service pattern
- ✅ **PASS**: Migration-based schema evolution (Alembic)

### Interface Excellence (Web Context)
- ✅ **PASS**: Clear REST API contracts with validation and error messages
- ✅ **PASS**: User-friendly settings UI with password-masked inputs, show/hide toggle, status indicators
- ✅ **PASS**: Specific error messages for validation failures (format errors, connectivity issues, missing keys)
- ✅ **PASS**: Responsive design (320px mobile to 2560px desktop)

### Additional Constitution Considerations
- ✅ **PASS**: UV package manager used for Python backend dependencies
- ✅ **PASS**: All dependencies explicitly declared in pyproject.toml and package.json
- ✅ **PASS**: Quality gates defined: pytest, ruff, mypy for backend; Jest, ESLint, TypeScript for frontend

**Initial Constitution Check Result**: ✅ **PASS** - No violations detected. Feature aligns with established principles.

## Project Structure

### Documentation (this feature)

```text
specs/010-settings-ui-api-keys/
├── spec.md              # Feature specification (user stories, requirements)
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   ├── api-keys.openapi.yaml
│   └── api-keys.postman.json
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── config.py                # UPDATED: Add ENCRYPTION_KEY env var
│   ├── models/
│   │   └── user_api_key.py      # NEW: SQLAlchemy model for user_api_keys table
│   ├── services/
│   │   ├── encryption_service.py    # NEW: AES-256/Fernet encryption/decryption
│   │   ├── api_key_service.py       # NEW: CRUD operations for API keys
│   │   └── gemini_validator.py      # NEW: Gemini API key validation (format + connectivity)
│   ├── api/
│   │   ├── routers/
│   │   │   └── api_keys.py      # NEW: /api/user-api-keys endpoints (GET, POST, DELETE, /test)
│   │   └── schemas/
│   │       └── api_key.py       # NEW: Pydantic schemas for requests/responses
│   └── database/                # Existing: connection.py, repository.py
├── alembic/
│   └── versions/
│       └── XXXX_create_user_api_keys_table.py  # NEW: Migration for user_api_keys table
└── tests/
    ├── contract/
    │   └── test_user_api_key_model.py           # NEW: Model CRUD contract tests
    ├── integration/
    │   ├── test_api_key_endpoints.py            # NEW: API endpoint integration tests
    │   └── test_gemini_validation.py            # NEW: Gemini API connectivity tests
    └── unit/
        ├── test_encryption_service.py           # NEW: Encryption/decryption unit tests
        └── test_api_key_service.py              # NEW: API key service unit tests

frontend/
├── app/
│   └── (authenticated)/
│       └── settings/
│           └── page.tsx             # NEW: Settings page component
├── components/
│   ├── settings/
│   │   ├── ApiKeyInput.tsx          # NEW: Password input with show/hide toggle
│   │   ├── ApiKeyStatus.tsx         # NEW: Status indicator (configured/not configured)
│   │   └── TestConnectionButton.tsx # NEW: Test connection button with loading state
│   └── ui/
│       └── PasswordInput.tsx        # NEW: Reusable password input with toggle (if not exists)
├── lib/
│   ├── api/
│   │   └── apiKeys.ts               # NEW: API client for /api/user-api-keys endpoints
│   └── hooks/
│       └── useApiKey.ts             # NEW: React hook for API key state management
└── __tests__/
    └── settings/
        ├── ApiKeyInput.test.tsx     # NEW: Component unit tests
        └── ApiKeyStatus.test.tsx    # NEW: Component unit tests

ai-agent/
├── src/ai_agent/
│   ├── services/
│   │   └── api_key_retrieval.py     # NEW: Fetch user-specific API key from backend
│   └── agent/
│       └── agent_service.py         # UPDATED: Use per-user API key (fail if missing)
└── tests/
    └── integration/
        └── test_per_user_api_key.py # NEW: Test AI agent with per-user keys
```

**Structure Decision**: Web application (microservices architecture). This feature primarily affects **backend** (new API endpoints, database table, encryption service) and **frontend** (new Settings page and components). Minor updates to **ai-agent** for per-user API key retrieval. The existing better-auth authentication (auth-server) provides user context via session cookies.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

*No violations detected. This section is intentionally left empty.*

## Phase 0: Research & Unknowns

### Research Tasks

The following unknowns require investigation before design:

1. **Encryption Library Selection**
   - **Question**: Which Python encryption library to use for AES-256/Fernet?
   - **Options**: cryptography (Fernet), PyCryptodome, nacl
   - **Decision Criteria**: Security audit history, async compatibility, key derivation support

2. **Gemini API SDK Integration**
   - **Question**: How to validate Gemini API keys programmatically?
   - **Research**: google-generativeai SDK usage, minimal test request pattern, error codes
   - **Outcome**: Identify generateContent endpoint usage with 1-word prompt

3. **Better-Auth Session Integration**
   - **Question**: How to retrieve authenticated user_id in FastAPI routes?
   - **Research**: better-auth session cookie format, JWT decoding, FastAPI dependency injection pattern
   - **Outcome**: Middleware or dependency to extract user_id from better-auth session

4. **Frontend Password Input Best Practices**
   - **Question**: How to implement secure password-type input with show/hide toggle in React?
   - **Research**: Input type switching, clipboard security, autocomplete prevention
   - **Outcome**: Component pattern for password masking with lucide-react eye icon

5. **Database Encryption-at-Rest**
   - **Question**: SQLAlchemy encrypted column implementation (application-level encryption)?
   - **Research**: SQLAlchemy TypeDecorator for automatic encryption/decryption, performance impact
   - **Outcome**: Custom EncryptedString column type vs. service-layer encryption

### Research Output

See [research.md](./research.md) for detailed findings and decisions.

## Phase 1: Design & Contracts

### Prerequisites
- `research.md` complete with all unknowns resolved

### Design Outputs

1. **Data Model** ([data-model.md](./data-model.md))
   - `user_api_keys` table schema with all columns, constraints, indexes
   - Encryption/decryption flow diagram
   - State machine for validation_status field

2. **API Contracts** ([contracts/](./contracts/))
   - OpenAPI 3.0 specification for `/api/user-api-keys` endpoints:
     - `GET /api/user-api-keys/current` - Retrieve current user's API key (masked)
     - `POST /api/user-api-keys` - Save/update API key
     - `DELETE /api/user-api-keys/current` - Remove API key
     - `POST /api/user-api-keys/test` - Test connection to Gemini API
   - Request/response schemas with Pydantic models
   - Error response formats (400, 401, 404, 500)

3. **Quickstart Guide** ([quickstart.md](./quickstart.md))
   - Developer setup: ENCRYPTION_KEY environment variable configuration
   - Database migration: Running Alembic migration for user_api_keys table
   - Testing: Running backend tests (encryption, API endpoints, validation)
   - Frontend development: Running Next.js dev server with settings page
   - End-to-end workflow: User configures API key → AI agent uses it

4. **Agent Context Update**
   - Run `.specify/scripts/bash/update-agent-context.sh claude`
   - Add new technologies to CLAUDE.md:
     - cryptography library (Fernet)
     - google-generativeai SDK
     - Password-type input components

### Design Validation
- Re-run Constitution Check after design artifacts are complete
- Verify all NEEDS CLARIFICATION items resolved
- Ensure API contracts align with spec functional requirements

## Phase 2: Task Breakdown (NOT IN THIS COMMAND)

Task generation is handled by `/sp.tasks` command after Phase 1 design is complete.

**User Requirement**: Ensure each task is sized right (20-30 minutes, not hours or minutes).

Tasks will be broken down with the following sizing guidelines:
- **20-30 minute tasks**: Atomic, testable units (e.g., "Write encryption_service.py with encrypt/decrypt methods + unit tests")
- **Avoid hour-long tasks**: Break complex work into smaller chunks (e.g., don't combine "Create API endpoints + write tests + update AI agent")
- **Avoid minute-long tasks**: Group trivial changes (e.g., don't separate "Add import statement" and "Add type hint" as separate tasks)

This will be enforced during `/sp.tasks` execution.
