# Implementation Plan: Better Auth Server for FastAPI Integration

**Branch**: `004-auth-server` | **Date**: 2025-12-10 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-auth-server/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement a separate Node.js authentication server using better-auth library that integrates with the existing FastAPI backend through a shared PostgreSQL database. The auth server handles user registration, login, password reset, and OAuth2 flows (Google), while the FastAPI backend validates session tokens from the Authorization header to enable protected API endpoints. This microservices architecture separates authentication concerns and leverages Node.js strengths for auth while maintaining Python/FastAPI for application logic.

## Technical Context

### Auth Server (Node.js/Express)
**Language/Version**: Node.js 20+ with TypeScript 5.x
**Primary Dependencies**:
  - better-auth 1.x (authentication library with Prisma adapter)
  - Express 4.x (web framework)
  - Prisma 5.x (ORM for PostgreSQL)
  - @node-rs/bcrypt (password hashing)
  - Resend (email service for verification/password reset)
**Storage**: Neon Serverless PostgreSQL (shared with FastAPI)
**Testing**: Vitest (unit/integration tests for auth flows)
**Target Platform**: Vercel Serverless Functions (production), Node.js server (development)
**Module System**: ESM (`"type": "module"` in package.json)

### FastAPI Backend (Python)
**Language/Version**: Python 3.12+
**Primary Dependencies**:
  - FastAPI 0.104+ (web framework)
  - SQLAlchemy 2.0+ async (ORM for session validation)
  - Pydantic 2.0+ (data validation)
  - python-jose or PyJWT (JWT token validation - if JWT strategy)
  - Uvicorn (ASGI server)
**Storage**: Neon Serverless PostgreSQL (shared with auth server)
**Testing**: pytest with pytest-asyncio (async endpoint tests)
**Target Platform**: Render (production), Uvicorn server (development)

### Shared Infrastructure
**Database**: Neon Serverless PostgreSQL with connection pooling
**Schema Management**:
  - Auth Server: Prisma migrations
  - FastAPI Backend: Alembic migrations
  - **CRITICAL**: Must coordinate schema changes (especially `users` and `user_sessions` tables)
**Session Strategy**: Database lookup (selected for real-time session revocation capability)
**Performance Goals**:
  - Auth endpoints: <500ms p95 latency
  - Token validation: <50ms p95 latency (database lookup overhead)
  - Support 1000+ concurrent authentication requests
**Constraints**:
  - Session tokens stored as httpOnly cookies from auth server
  - FastAPI validates tokens from Authorization Bearer header
  - CORS configured for cross-origin requests (frontend at different domain)
  - Email verification mandatory (15-minute token expiration)
  - Password reset tokens: 1-hour expiration
**Scale/Scope**:
  - Support multiple concurrent sessions per user
  - Device and location tracking per session
  - Individual session management (view/revoke)
  - Initial OAuth: Google (extensible to GitHub, Apple)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Test-First Development ✅ REQUIRES JUSTIFICATION
- **Status**: VIOLATION - This is auth infrastructure setup, not TDD-driven
- **Justification**: Authentication server setup involves:
  1. Configuration and infrastructure files (package.json, tsconfig.json, .env)
  2. Third-party library integration (better-auth with prescribed patterns)
  3. Database schema definitions (Prisma schema)
  4. Integration code following better-auth documentation
- **Mitigation**: Will write integration tests AFTER setup to verify auth flows work correctly
- **Rationale**: Better-auth is a well-tested library; our tests focus on integration points and custom routes

### II. Clean Code & Simplicity ✅ PASS
- Using established patterns from better-auth documentation
- Type hints in Python (FastAPI dependencies)
- TypeScript for Node.js (compile-time safety)
- Single responsibility: Auth server handles auth, FastAPI handles business logic
- YAGNI: Only implementing requested features (email/password, Google OAuth, password reset)

### III. Proper Project Structure ⚠️ MODIFIED
- **Existing**: `src/` (Python CLI), `tests/` (Python tests)
- **Adding**: `auth-server/` (separate Node.js service)
- **Rationale**: Microservices architecture requires separate directory for auth server
- **Structure**:
  ```
  auth-server/           # New Node.js service
  ├── src/
  ├── prisma/
  └── tests/

  backend/              # Existing FastAPI (to be created or enhanced)
  ├── src/
  └── tests/

  src/                  # Existing Python CLI (unchanged)
  tests/                # Existing Python tests (unchanged)
  ```

### IV. In-Memory Data Storage ❌ VIOLATION - JUSTIFIED
- **Status**: VIOLATION - Using PostgreSQL instead of in-memory storage
- **Justification**: Authentication REQUIRES persistent storage:
  1. User credentials must survive server restarts
  2. Session management requires database for revocation
  3. Email verification tokens need persistence
  4. OAuth state management requires storage
- **Constitution Section**: "Data layer MUST be isolated to enable future persistence additions"
  - This IS the persistence addition, properly isolated in separate auth service
- **Approved**: Authentication is explicitly exempt from in-memory constraint

### V. Command-Line Interface Excellence ⚠️ NOT APPLICABLE
- **Status**: N/A - This feature adds REST API authentication, not CLI commands
- **Note**: Existing CLI (src/cli/) remains unchanged and continues to follow CLI standards
- **New Interface**: REST API endpoints (POST /api/auth/signup, /api/auth/signin, etc.)
  - Will provide clear error messages with HTTP status codes
  - OpenAPI documentation for API interface

### VI. UV Package Manager Integration ✅ PASS (Python) / N/A (Node.js)
- **Python/FastAPI**: Continue using UV for Python dependencies
- **Node.js/Auth Server**: Uses npm/pnpm (standard for Node.js ecosystem)
- **Rationale**: UV is Python-specific; Node.js has its own package management

### Summary
**Gates Status**:
- ✅ 2 PASS (Clean Code, UV for Python)
- ⚠️ 2 MODIFIED (Project Structure - microservices, CLI - N/A for this feature)
- ❌ 2 JUSTIFIED VIOLATIONS (TDD - infrastructure setup, Persistent Storage - required for auth)

**Proceed**: YES - All violations are justified with clear rationale
**Re-check Required**: After Phase 1 design (verify auth integration tests planned)

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
auth-server/                    # New Node.js authentication service
├── src/
│   ├── auth/
│   │   ├── auth.config.ts      # better-auth configuration
│   │   ├── routes.ts           # Custom auth routes (/me, /verify-token)
│   │   ├── types.ts            # TypeScript type definitions
│   │   └── validation.ts       # Request validation schemas
│   ├── config/
│   │   └── env.ts              # Environment variable validation
│   ├── database/
│   │   └── client.ts           # Prisma client singleton
│   ├── middleware/
│   │   ├── errorHandler.ts    # Global error handling
│   │   └── logger.ts           # Request logging
│   ├── utils/
│   │   ├── logger.ts           # Logging utility (Winston/Pino)
│   │   └── errors.ts           # Custom error classes
│   ├── app.ts                  # Express app configuration
│   └── index.ts                # Entry point
├── prisma/
│   └── schema.prisma           # Database schema (users, sessions, etc.)
├── api/
│   └── index.ts                # Vercel serverless entry point
├── tests/
│   ├── integration/
│   │   └── auth.test.ts        # Auth flow tests
│   └── unit/
│       └── validation.test.ts  # Validation logic tests
├── package.json                # Dependencies (better-auth, express, prisma)
├── tsconfig.json               # TypeScript config (ESM)
├── .env.example                # Environment template
└── vercel.json                 # Vercel deployment config

backend/                        # FastAPI application (existing or new)
├── src/
│   ├── auth/
│   │   ├── dependencies.py     # get_current_user dependency
│   │   ├── models.py           # Pydantic models (User, Session)
│   │   └── __init__.py
│   ├── database/
│   │   ├── connection.py       # Async PostgreSQL connection
│   │   └── migrations/
│   │       └── versions/
│   │           └── 001_auth_tables.py  # Alembic migration
│   ├── middleware/
│   │   └── cors.py             # CORS configuration
│   ├── api/
│   │   └── routes/
│   │       └── protected.py    # Example protected endpoints
│   └── main.py                 # FastAPI app entry point
├── tests/
│   ├── integration/
│   │   └── test_auth_flow.py   # End-to-end auth tests
│   └── unit/
│       └── test_dependencies.py # Auth dependency tests
├── requirements.txt            # Python dependencies
├── .env.example                # Environment template
└── render.yaml                 # Render deployment config

src/                            # Existing Python CLI (UNCHANGED)
├── models/
├── services/
├── cli/
└── storage/

tests/                          # Existing CLI tests (UNCHANGED)
├── contract/
├── integration/
└── unit/

.env.example                    # Shared environment template
docker-compose.yml              # Local development orchestration (optional)
```

**Structure Decision**: **Microservices Web Application**

We're implementing a microservices architecture with two separate services:
1. **Auth Server** (`auth-server/`) - Node.js/Express service handling authentication
2. **API Server** (`backend/`) - FastAPI service handling business logic and protected endpoints
3. **Existing CLI** (`src/`, `tests/`) - Remains unchanged

This structure enables:
- Language-specific strengths (Node.js for auth libraries, Python for AI/ML)
- Independent deployment and scaling
- Clear separation of concerns
- Shared PostgreSQL database for data consistency

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|--------------------------------------|
| **Microservices Architecture** (adds 2nd service) | Authentication requires Node.js ecosystem (better-auth library) while business logic benefits from Python/FastAPI. Separate services enable independent scaling and deployment. | **Monolithic FastAPI with Python auth libs**: Python authentication libraries (Authlib, FastAPI-Users) lack better-auth's comprehensive feature set (built-in OAuth, session management, email verification). Better-auth is battle-tested with 10k+ stars, extensive documentation, and active maintenance. |
| **Persistent Storage** (violates in-memory constraint) | Authentication fundamentally requires persistence: user credentials, session tokens, email verification tokens, OAuth state must survive restarts. Security audit trail needs permanent storage. | **In-memory storage**: Cannot meet FR-001 through FR-010 requirements. Session revocation impossible without persistence. User accounts would be lost on restart. |
| **TDD Suspension** (infrastructure setup first) | Auth server setup involves configuration files, third-party integrations, and schema definitions that follow better-auth prescribed patterns. Testing integration points after setup is more practical. | **Pure TDD approach**: Would require writing tests for better-auth library behavior (already tested) rather than our integration. Infrastructure files (tsconfig.json, package.json) have no testable logic. Will write integration tests after setup to verify auth flows. |
| **Shared Database** (coupling concern) | Both services need access to user and session data for token validation. Separate databases would require synchronization mechanism, adding complexity and latency. | **Separate databases with sync**: Adds event bus, message queue, or polling sync mechanism. Introduces data consistency challenges, higher latency (2-phase validation), and operational overhead. Shared DB with coordinated migrations is simpler. |

**Mitigation Strategies**:
1. **Microservices**: Document API contract clearly; use docker-compose for local development; maintain backward compatibility
2. **Persistence**: Isolate database layer in both services; use migrations for schema changes; follow 12-factor app principles
3. **TDD**: Write comprehensive integration tests post-setup; test custom auth routes and middleware; verify error handling
4. **Shared DB**: Coordinate schema changes via migration reviews; use database-level constraints; implement health checks
