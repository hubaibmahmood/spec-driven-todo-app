---
id: 0003
title: Hybrid JWT Authentication Planning
stage: plan
date: 2026-01-02
surface: agent
model: claude-sonnet-4-5-20250929
feature: 013-hybrid-jwt-auth
branch: 013-hybrid-jwt-auth
user: mac
command: /sp.plan
labels: ["jwt", "authentication", "planning", "architecture", "performance"]
links:
  spec: /specs/013-hybrid-jwt-auth/spec.md
  ticket: null
  adr: /history/adr/0004-hybrid-jwt-authentication-architecture.md
  pr: null
files:
  - specs/013-hybrid-jwt-auth/plan.md
  - specs/013-hybrid-jwt-auth/research.md
  - specs/013-hybrid-jwt-auth/data-model.md
  - specs/013-hybrid-jwt-auth/quickstart.md
  - specs/013-hybrid-jwt-auth/contracts/openapi.yaml
  - CLAUDE.md
tests:
  - No tests executed (planning phase)
---

## Prompt

sp.plan

## Response snapshot

Executed /sp.plan workflow for feature 013-hybrid-jwt-auth (Hybrid JWT Authentication).

**Planning Artifacts Generated**:

1. **plan.md**: Implementation plan with technical context, constitution check, and project structure
   - Technical Context: Python 3.12+ (FastAPI backend), TypeScript 5.x (auth-server & frontend), Neon PostgreSQL
   - Performance Goals: <1ms JWT validation (p95), 90%+ reduction in auth DB queries, 1000+ concurrent users
   - Constitution Check: PASS with justified database persistence deviation
   - Source structure: 3 microservices (backend, auth-server, frontend) with file-level change annotations

2. **research.md**: Consolidated research findings (Phase 0)
   - JWT Library: PyJWT with HS256 (industry standard, symmetric key)
   - Refresh Token Storage: SHA-256 hashing in PostgreSQL (fast, secure)
   - Cross-Tab Sync: BroadcastChannel API with localStorage fallback
   - Retry Logic: 3 attempts with exponential backoff (1s, 2s, 4s)
   - Migration Strategy: Feature flags with gradual rollout (0% → 10% → 25% → 50% → 100%)
   - Database Schema: Reuse existing user_sessions table (zero migration complexity)
   - Performance Targets: <1ms validation, <100ms refresh, 90% query reduction

3. **data-model.md**: Entity definitions and validation rules (Phase 1)
   - Access Token (JWT): 30-minute lifetime, stateless validation, HS256 signature
   - Refresh Token: 7-day lifetime, cryptographically random (32 bytes), SHA-256 hashed storage
   - User Session Record: Existing PostgreSQL table shared with better-auth
   - Token Pair: Composite entity returned from login/refresh endpoints
   - Authentication State Machine: 5 states with transitions (unauthenticated → authenticated → expired → refreshed → revoked)

4. **contracts/openapi.yaml**: REST API specification (Phase 1)
   - POST /api/auth/refresh: Exchange refresh token for new access token
   - POST /api/auth/logout: Revoke refresh token (session termination)
   - GET /api/auth/me: Validate access token (example endpoint)
   - Security schemes: Bearer JWT (access token), httpOnly cookie (refresh token)
   - Error responses: 401 (expired/invalid/revoked), 429 (rate limit), 500 (internal)

5. **quickstart.md**: Developer implementation guide (Phase 1)
   - Prerequisites: Python 3.12+, Node.js 20+, PostgreSQL, environment variables
   - Implementation workflow: TDD approach for backend (JWT service, refresh endpoint), auth-server JWT issuance, frontend token refresh hook
   - Testing: Unit tests (PyJWT contract), integration tests (refresh flow), E2E tests (Playwright)
   - Deployment: Gradual rollout strategy (0% → 100%), feature flag configuration, monitoring metrics
   - Troubleshooting: Common issues (signature mismatch, missing cookies, clock skew, cross-tab coordination)

6. **CLAUDE.md**: Updated agent context with new technologies (via update-agent-context.sh)

**Constitution Check Results**:
- ✅ Test-First Development: TDD workflow demonstrated in quickstart
- ✅ Clean Code & Simplicity: Industry-standard libraries, proven patterns
- ✅ Proper Project Structure: Changes isolated to services/dependencies/routers
- ⚠️ Data Storage: Justified deviation (database is existing infrastructure, required for security)
- ❌ CLI Excellence: Not applicable (web API feature)
- ✅ UV Package Manager: Backend uses pyproject.toml

**Overall Assessment**: PASS - All technical unknowns resolved, no unresolved "NEEDS CLARIFICATION" items, architecture fully defined.

## Outcome

- ✅ Impact: Complete architectural plan for hybrid JWT authentication with 90%+ database query reduction target
- 🧪 Tests: No tests executed (planning phase); test strategy documented in quickstart.md
- 📁 Files: Created 5 planning artifacts (plan.md, research.md, data-model.md, quickstart.md, contracts/openapi.yaml)
- 🔁 Next prompts: Run /sp.tasks to generate task breakdown, then /sp.implement to execute implementation
- 🧠 Reflection: Planning phase comprehensive - all research findings consolidated, API contracts defined, quickstart guide provides clear TDD workflow

## Evaluation notes (flywheel)

- Failure modes observed: None - all planning phases completed successfully
- Graders run and results (PASS/FAIL): N/A (planning phase, no code implementation)
- Prompt variant (if applicable): Standard /sp.plan command
- Next experiment (smallest change to try): Validate PyJWT library version compatibility with Python 3.12+ modern datetime APIs (datetime.now(UTC))
