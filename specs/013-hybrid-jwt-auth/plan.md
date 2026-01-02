# Implementation Plan: Hybrid JWT Authentication

**Branch**: `013-hybrid-jwt-auth` | **Date**: 2026-01-02 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/013-hybrid-jwt-auth/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement hybrid JWT authentication system combining short-lived access tokens (30 minutes, validated via signature without database queries) with long-lived refresh tokens (7 days, stored hashed in database). This architecture reduces authentication database queries by 90%+ while maintaining 7-day seamless sessions with automatic token refresh. The implementation must support gradual migration from existing better-auth session system using feature flags, ensuring backward compatibility during rollout.

## Technical Context

**Language/Version**: Python 3.12+ (backend), TypeScript 5.x (auth-server & frontend)
**Primary Dependencies**:
- Backend: FastAPI 0.127.0+, SQLAlchemy 2.0+ (async ORM), Pydantic 2.0+, PyJWT (for JWT signing/verification), bcrypt/cryptography (for refresh token hashing)
- Auth Server: Node.js 20+, better-auth 1.4.6, Express 4.x, Prisma (database client)
- Frontend: Next.js 16.0.9, React 19.2.1, better-auth 1.4.6 (React client)
**Storage**: Neon serverless PostgreSQL (shared database across auth-server and FastAPI backend)
**Testing**: pytest (Python backend), jest (TypeScript frontend), Playwright (E2E)
**Target Platform**: Web application (Linux server backend, browser-based frontend)
**Project Type**: Web (microservices: FastAPI backend + Node.js auth-server + Next.js frontend)
**Performance Goals**: <1ms auth validation (p95), 1000+ concurrent users, <100ms token refresh (p95)
**Constraints**: Must maintain backward compatibility with existing better-auth sessions during migration, 30-minute revocation delay acceptable
**Scale/Scope**: 10k+ users, gradual rollout with feature flags (0% → 10% → 25% → 50% → 100%)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Test-First Development ✅
- **Status**: PASS
- **Justification**: Implementation will follow TDD workflow with contract tests for token generation/validation, integration tests for auth flows, and unit tests for hashing/signing logic. All code written after tests.

### II. Clean Code & Simplicity ✅
- **Status**: PASS
- **Justification**: JWT library (PyJWT) is industry-standard. Token refresh pattern is well-established. No over-engineering - using proven cryptographic primitives (HMAC-SHA256 for JWT, bcrypt/SHA-256 for refresh tokens). Modern APIs: `datetime.now(UTC)` for all timestamps.

### III. Proper Project Structure ✅
- **Status**: PASS
- **Justification**: Follows existing microservices structure. Backend changes isolated to `src/services/jwt_service.py`, `src/api/dependencies.py`, `src/models/database.py`. Clear separation: JWT logic in service layer, validation in dependency layer, storage in models.

### IV. Data Storage ⚠️
- **Status**: CONDITIONAL PASS (deviation justified)
- **Original Principle**: In-memory storage for CLI app
- **Current Requirement**: PostgreSQL database for refresh tokens
- **Justification**: This principle applies to the original CLI todo app (specs 001-002). Current codebase evolved to web application with FastAPI backend (spec 003) and better-auth integration (spec 004). Database persistence is required for:
  - Refresh token storage with expiration tracking
  - Session revocation capability
  - Multi-device session management
  - Audit trail (IP, user agent)
- **Complexity Justification**: Database storage is NOT added complexity - it's the existing infrastructure. Reusing `user_sessions` table from better-auth minimizes changes.

### V. CLI Excellence ❌
- **Status**: NOT APPLICABLE
- **Justification**: This principle applies only to CLI-based features (specs 001-002). Current feature is backend authentication infrastructure for web API. No CLI interaction involved.

### VI. UV Package Manager ✅
- **Status**: PASS (Python only)
- **Justification**: Backend Python project uses standard `pyproject.toml` with proper dependency management. UV compatibility maintained. Auth-server uses npm (Node.js standard), frontend uses npm (Next.js standard).

**Overall Assessment**: PASS with documented deviations. Constitution principles written for CLI app phase; current codebase is web application. Deviations are evolution, not violations.

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
backend/ (Python FastAPI - JWT validation & refresh endpoints)
├── src/
│   ├── models/
│   │   └── database.py                    # [MODIFY] Add RefreshToken model
│   ├── services/
│   │   ├── auth_service.py                # [MODIFY] Add JWT validation path
│   │   ├── jwt_service.py                 # [NEW] JWT generation/validation
│   │   └── refresh_token_service.py       # [NEW] Refresh token hashing/storage
│   ├── api/
│   │   ├── dependencies.py                # [MODIFY] Add get_current_user_jwt dependency
│   │   └── routers/
│   │       └── auth.py                    # [NEW] /auth/refresh endpoint
│   └── config.py                          # [MODIFY] Add JWT_SECRET, JWT_ALGORITHM, etc.
└── tests/
    ├── contract/
    │   ├── test_jwt_service.py            # [NEW] Token generation/validation contracts
    │   └── test_refresh_token_service.py  # [NEW] Hash/verify contracts
    ├── integration/
    │   ├── test_token_refresh_flow.py     # [NEW] End-to-end refresh flow
    │   └── test_hybrid_auth_migration.py  # [NEW] Session + JWT coexistence
    └── unit/
        └── test_jwt_validation.py         # [NEW] Edge cases (expired, invalid signature)

auth-server/ (Node.js better-auth - login/signup extended with JWT issuance)
├── src/
│   ├── index.ts                           # [MODIFY] Add JWT generation to login response
│   └── lib/
│       └── jwt.ts                         # [NEW] JWT signing logic (shared secret with backend)
└── prisma/
    └── schema.prisma                      # [READ ONLY] Reference existing user_sessions

frontend/ (Next.js React - token storage & refresh interceptor)
├── src/
│   ├── lib/
│   │   ├── auth-client.ts                 # [MODIFY] Store access token from login
│   │   └── api-client.ts                  # [MODIFY] Add refresh interceptor
│   └── hooks/
│       └── useTokenRefresh.ts             # [NEW] Cross-tab token sync logic
└── tests/
    └── integration/
        └── token-refresh.spec.ts          # [NEW] Playwright test for auto-refresh
```

**Structure Decision**: Web application with 3 microservices (FastAPI backend, Node.js auth-server, Next.js frontend). This is the established architecture from spec 004 (auth-server) and spec 003 (FastAPI). JWT implementation extends all three services:
- **Backend**: Validates JWTs, provides refresh endpoint
- **Auth-server**: Issues JWT pairs on login/signup
- **Frontend**: Stores tokens, handles automatic refresh

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Database persistence (Constitution IV) | Refresh token storage, expiration tracking, session revocation, audit trail | In-memory storage loses all sessions on restart; cannot revoke sessions; cannot track multi-device sessions; violates security requirements FR-004, FR-008, FR-009 |
