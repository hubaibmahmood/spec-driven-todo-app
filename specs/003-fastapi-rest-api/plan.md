# Implementation Plan: FastAPI REST API Conversion

**Branch**: `003-fastapi-rest-api` | **Date**: 2025-12-10 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-fastapi-rest-api/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Convert the interactive CLI todo application to a production-ready FastAPI REST API with PostgreSQL persistence, session-based authentication via better-auth integration, and rate limiting. The API will expose RESTful endpoints for CRUD operations on user-specific tasks, validate sessions through database lookups in a shared Neon PostgreSQL instance, and enforce rate limits (100 req/min for reads, 30 req/min for writes) using user-based tracking with IP fallback.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: FastAPI 0.104+, SQLAlchemy 2.0+ (async ORM), Pydantic 2.0+, Uvicorn (ASGI server)
**Storage**: Neon serverless PostgreSQL (shared with better-auth Node.js server)
**Testing**: pytest, pytest-asyncio, httpx (async test client), factory-boy (test data)
**Target Platform**: Linux/macOS server, containerizable
**Project Type**: Web API (single backend service)
**Performance Goals**: <300ms response time for collections up to 1000 tasks, <100ms session validation, <200ms single-task operations
**Constraints**:
- Must integrate with existing better-auth server (no modifications allowed)
- Session validation via database lookup only (no JWT decoding)
- Rate limiting must work in distributed deployments
- Must share Neon PostgreSQL instance with auth server
- Response times: <300ms (collections), <100ms (session validation), <200ms (single ops)
**Scale/Scope**: Multi-user system, ~1000 tasks per user, distributed deployment capable

### Key Technical Decisions Requiring Research

1. **Database Driver Selection**: NEEDS CLARIFICATION - asyncpg vs psycopg3 for Neon PostgreSQL async connection
2. **Rate Limiting Strategy**: NEEDS CLARIFICATION - slowapi vs fastapi-limiter, Redis-backed vs in-memory for distributed deployments
3. **Token Hashing Algorithm**: NEEDS CLARIFICATION - hashlib algorithm to match better-auth server (must be coordinated via SESSION_HASH_SECRET)
4. **Migration Tool**: NEEDS CLARIFICATION - Alembic best practices for SQLAlchemy 2.0 async models
5. **Connection Pooling**: NEEDS CLARIFICATION - SQLAlchemy async engine configuration for Neon serverless (pool size, timeout settings)
6. **CORS Middleware**: NEEDS CLARIFICATION - FastAPI CORS configuration for localhost:3000 + production domain
7. **Error Response Format**: NEEDS CLARIFICATION - Standard JSON error structure for validation/auth/rate-limit errors
8. **Testing Strategy**: NEEDS CLARIFICATION - Integration testing patterns for FastAPI with async PostgreSQL

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Test-First Development (NON-NEGOTIABLE)

**Status**: ✅ PASS (with enforcement plan)

- All API endpoints will be developed using TDD (write tests first, then implementation)
- Contract tests for API request/response validation
- Integration tests for database operations and session validation
- Unit tests for business logic and validators
- Red-Green-Refactor cycle mandatory for all features

**Enforcement**: Each user story in spec has explicit acceptance scenarios that translate directly to test cases.

### II. Clean Code & Simplicity

**Status**: ⚠️ CONDITIONAL PASS (complexity justified)

**Violations**:
- Adding FastAPI web framework (previously CLI-only)
- Adding PostgreSQL persistence (previously in-memory)
- Adding authentication layer (previously none)
- Adding rate limiting middleware (previously none)

**Justification**: These additions are explicitly required by the feature spec. Each addresses a specific production requirement:
- FastAPI: Required for REST API endpoints (FR-001)
- PostgreSQL: Required for multi-user data persistence (FR-015)
- Authentication: Required for user data isolation (FR-021-029)
- Rate limiting: Required for API protection (FR-029-032)

**Mitigation**:
- Reuse existing Task model validation logic
- Keep business logic separate from web layer
- Use dependency injection to maintain testability
- Follow single responsibility principle for all new modules

### III. Proper Project Structure

**Status**: ✅ PASS (with structure evolution)

Current structure (`src/` with CLI) will be preserved and extended:
```
src/
├── models/          # Existing Task model + new SQLAlchemy models
├── services/        # Existing TaskService + new database layer
├── cli/             # Preserved for backward compatibility
├── api/             # NEW: FastAPI routers and endpoints
├── auth/            # NEW: Session validation middleware
└── database/        # NEW: SQLAlchemy setup, migrations
```

**Rationale**: Extends existing structure without breaking CLI functionality. Clear separation of web layer (`api/`) from business logic (`services/`).

### IV. In-Memory Data Storage

**Status**: ❌ VIOLATION (explicitly overridden by feature requirement)

**Previous**: "Tasks MUST be stored in memory (no database or file persistence initially)"

**Current Requirement**: PostgreSQL persistence required (FR-015)

**Justification**: The constitution anticipated this evolution with "Data layer MUST be isolated to enable future persistence additions". This feature is that future addition.

**Impact**: Existing in-memory MemoryStore will be replaced with PostgreSQL-backed repository using SQLAlchemy async ORM.

**Migration Path**: Existing abstraction (`TaskService`) allows swapping storage implementation without changing business logic.

### V. Command-Line Interface Excellence

**Status**: ✅ PASS (CLI preserved, API added)

- Existing CLI remains functional (backward compatibility)
- New FastAPI endpoints provide web access to same underlying logic
- CLI and API share the same business logic layer (services/)
- Error handling patterns from CLI inform API error responses

**Rationale**: This is an additive change. CLI users can continue using the application; web users gain API access.

### VI. UV Package Manager Integration

**Status**: ✅ PASS

- Continue using UV for package management
- Add new dependencies (FastAPI, SQLAlchemy, etc.) to pyproject.toml
- Maintain Python 3.12+ requirement
- All tools (pytest, ruff, mypy) remain UV-managed

**Enforcement**: All dependencies declared explicitly, runnable via `uv run` commands.

---

### Overall Gate Status: ⚠️ CONDITIONAL PASS

**Summary**: 2 violations (Clean Code complexity, In-Memory storage) are **explicitly justified** by feature requirements. The constitution's "future persistence" clause and data layer isolation anticipated this evolution. All other principles maintained.

**Pre-Phase 0 Decision**: Proceed with research phase. The violations are necessary for the feature and align with constitution's evolution path.

---

### Post-Design Re-evaluation (Phase 1 Complete)

**Date**: 2025-12-10
**Status**: ✅ APPROVED

After completing Phase 1 design (research.md, data-model.md, contracts, quickstart.md), re-evaluating constitution compliance:

#### I. Test-First Development
**Status**: ✅ PASS (maintained)
- Testing strategy defined (pytest-asyncio, httpx AsyncClient, transaction rollback)
- TDD workflow documented in research.md (red-green-refactor)
- Test fixtures and patterns specified
- Contract, integration, and unit test structure planned

#### II. Clean Code & Simplicity
**Status**: ✅ PASS (complexity still justified)
- All added complexity directly addresses spec requirements
- Repository pattern maintains testability
- Dependency injection used for clean separation
- Pydantic schemas provide validation at API boundary
- **No additional unnecessary abstractions introduced during design**

#### III. Proper Project Structure
**Status**: ✅ PASS (enhanced)
- Clear separation: `api/` (web), `services/` (business logic), `database/` (data)
- Existing `cli/` preserved (backward compatibility)
- Test structure mirrors source (unit/, contract/, integration/)
- Alembic migrations organized under `database/migrations/`

#### IV. In-Memory Data Storage
**Status**: ❌ VIOLATION (unchanged - still required by spec)
- Neon PostgreSQL required for multi-user persistence
- Migration path clear: MemoryStore → PostgreSQL repository
- Justification unchanged: Feature explicitly requires database

#### V. Command-Line Interface Excellence
**Status**: ✅ PASS (CLI preserved)
- Existing CLI remains functional
- API adds web access without breaking CLI
- Shared business logic layer

#### VI. UV Package Manager Integration
**Status**: ✅ PASS
- All dependencies added via UV
- pyproject.toml updated with FastAPI stack
- Development workflow uses `uv run` commands

**Overall Assessment**: Design maintains constitutional principles while adding necessary complexity for production API requirements. All violations remain justified and documented in Complexity Tracking table.

**Approval**: Ready to proceed to Phase 2 (tasks.md generation)

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
src/
├── models/
│   ├── __init__.py
│   ├── task.py              # Existing Task dataclass (preserved)
│   └── database.py           # NEW: SQLAlchemy models (Task, UserSession)
├── services/
│   ├── __init__.py
│   ├── task_service.py       # Existing business logic (adapted for DB)
│   └── auth_service.py       # NEW: Session validation service
├── database/
│   ├── __init__.py
│   ├── connection.py         # NEW: SQLAlchemy async engine setup
│   ├── repository.py         # NEW: Task repository (async CRUD)
│   └── migrations/           # NEW: Alembic migrations
│       └── versions/
├── api/
│   ├── __init__.py
│   ├── main.py               # NEW: FastAPI app initialization
│   ├── dependencies.py       # NEW: Dependency injection (DB session, current user)
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── tasks.py          # NEW: Task CRUD endpoints
│   │   └── health.py         # NEW: Health check endpoint
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── auth.py           # NEW: Session validation middleware
│   │   └── rate_limit.py     # NEW: Rate limiting middleware
│   └── schemas/
│       ├── __init__.py
│       ├── task.py           # NEW: Pydantic request/response models
│       └── error.py          # NEW: Error response models
├── cli/
│   ├── __init__.py
│   ├── main.py               # Existing CLI (preserved for backward compat)
│   ├── commands.py
│   └── validators.py         # Existing validators (reused in API)
└── storage/
    └── memory_store.py       # Existing in-memory (deprecated but preserved)

tests/
├── contract/
│   ├── test_task_model.py    # Existing tests
│   └── test_api_schemas.py   # NEW: Pydantic schema validation tests
├── integration/
│   ├── test_cli.py           # Existing CLI tests
│   ├── test_api_endpoints.py # NEW: Full API workflow tests
│   ├── test_auth_flow.py     # NEW: Session validation integration
│   └── test_database.py      # NEW: Database operations integration
└── unit/
    ├── test_validators.py    # Existing tests
    ├── test_task_service.py  # Existing tests (adapted for async)
    ├── test_auth_service.py  # NEW: Auth service unit tests
    └── test_repository.py    # NEW: Repository pattern unit tests

alembic.ini                   # NEW: Alembic configuration
.env.example                  # NEW: Environment variables template
pyproject.toml                # Updated with new dependencies
```

**Structure Decision**: Selected **Single project (Option 1)** extended for web API. This maintains backward compatibility with existing CLI while adding FastAPI web layer. The structure preserves existing `src/` organization and adds new directories (`api/`, `database/`) for web-specific concerns. Clear separation between CLI (`cli/`), API (`api/`), and shared business logic (`services/`, `models/`).

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| PostgreSQL persistence | Multi-user data isolation & persistence (FR-015) | In-memory storage cannot handle multi-user scenarios or persist data across restarts |
| FastAPI framework | REST API endpoints required (FR-001) | CLI cannot serve web requests; feature explicitly requires HTTP API |
| Authentication layer | User data isolation mandated (FR-021-029) | Public access violates security requirements; better-auth integration required |
| Rate limiting | API protection required (FR-029-032) | Unprotected API vulnerable to abuse; production requirement |
| Repository pattern | Abstraction over SQLAlchemy for testability | Direct ORM usage in routes/services creates tight coupling, harder to test |
| Async SQLAlchemy | Performance requirement (<200ms ops) | Sync DB calls block event loop, cannot meet latency requirements |
