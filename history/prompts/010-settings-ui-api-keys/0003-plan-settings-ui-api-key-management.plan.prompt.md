---
id: 0003
title: Plan Settings UI API Key Management
stage: plan
date: 2025-12-24
surface: agent
model: claude-sonnet-4-5
feature: 010-settings-ui-api-keys
branch: 010-settings-ui-api-keys
user: hubaib
command: /sp.plan
labels: ["planning", "architecture", "design", "research", "encryption", "api-keys", "security"]
links:
  spec: specs/010-settings-ui-api-keys/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/010-settings-ui-api-keys/plan.md
  - specs/010-settings-ui-api-keys/research.md
  - specs/010-settings-ui-api-keys/data-model.md
  - specs/010-settings-ui-api-keys/contracts/api-keys.openapi.yaml
  - specs/010-settings-ui-api-keys/quickstart.md
tests:
  - N/A (planning phase - no tests executed)
---

## Prompt

/sp.plan --args "make sure each tasks is sized right (20-30 minutes, not hours or minutes)"

Additional context:
- User requested to pull main branch first to sync
- Switched to 010-settings-ui-api-keys branch (local only, not pushed to remote)
- Executed planning workflow with Phase 0 (Research) and Phase 1 (Design)

## Response snapshot

Successfully completed comprehensive implementation planning for Settings UI API Key Management feature (010-settings-ui-api-keys).

### Phase 0: Research & Unknowns (5 parallel research agents)

Resolved 5 critical technical unknowns:

1. **Encryption Library**: Selected `cryptography` (Fernet) for AES-256 encryption
   - Industry standard with secure defaults
   - Simple API for encrypt/decrypt operations
   - Async-compatible

2. **Gemini API Validation**: Use `generateContent` endpoint with 1-word prompt ("hi")
   - Minimal cost (~$0.0000017 per validation)
   - Full functionality test with 10-second timeout
   - Distinguishes error types (invalid key, rate limit, network)

3. **Better-Auth Integration**: Database query pattern (already implemented)
   - Production-ready pattern in backend/src/services/auth_service.py
   - Stateful session IDs (not JWTs)
   - Leverage existing `get_current_user` dependency

4. **React Password Input**: Password-type input with Eye/EyeOff toggle (lucide-react)
   - Default masked (type="password")
   - Allow copy/paste for password managers
   - WCAG 2.1 AA compliant

5. **SQLAlchemy Encryption**: Service-layer encryption (NOT TypeDecorator)
   - Perfect async compatibility
   - Easier testing (no database needed for unit tests)
   - Explicit and maintainable

### Phase 1: Design & Contracts

Created comprehensive design artifacts:

1. **data-model.md**: Complete database schema for `user_api_keys` table
   - SQLAlchemy model with 8 columns (encrypted_key, validation_status, timestamps)
   - Unique constraint on (user_id, provider)
   - Alembic migration script
   - Encryption flow diagrams
   - Validation status state machine

2. **contracts/api-keys.openapi.yaml**: OpenAPI 3.0 specification
   - GET /api/user-api-keys/current (retrieve masked key + status)
   - POST /api/user-api-keys (save/update encrypted key)
   - DELETE /api/user-api-keys/current (remove key)
   - POST /api/user-api-keys/test (test connectivity)
   - Request/response schemas with Pydantic models
   - Error response formats (400, 401, 404, 500)

3. **quickstart.md**: Developer setup guide
   - ENCRYPTION_KEY generation and configuration
   - Alembic migration steps
   - Testing instructions (unit, contract, integration, E2E)
   - Deployment checklist (backend, frontend, ai-agent, security)
   - Troubleshooting section with common issues

### Constitution Check

✅ **ALL GATES PASSED**
- Test-First Development: Testable acceptance scenarios for all 5 user stories
- Clean Code & Simplicity: PEP 8, type hints, mypy strict mode, single-purpose modules
- Proper Project Structure: Clear separation (models, services, API routes, UI components)
- Data Storage: PostgreSQL with SQLAlchemy ORM, Alembic migrations
- Interface Excellence: Clear REST API contracts, user-friendly UI, responsive design

### Technical Context Summary

- **Backend**: Python 3.12+, FastAPI 0.104+, SQLAlchemy 2.0+ (async), cryptography, google-generativeai
- **Frontend**: TypeScript 5.x, Next.js 16.0.9, React 19.2.1, Tailwind CSS 4, lucide-react
- **Storage**: Neon Serverless PostgreSQL (shared with existing backend)
- **Testing**: pytest (backend), Jest + React Testing Library (frontend)
- **Performance**: <500ms p95 for API key save, <1s settings page load, <3s test connection

### Security Requirements

- API keys encrypted at rest (AES-256/Fernet with ENCRYPTION_KEY env var)
- API keys NEVER logged in plaintext
- Input field password-masked by default
- Per-user key isolation (unique constraint)
- No global key fallback (hard fail with error message)

## Outcome

- ✅ Impact: Comprehensive planning artifacts created for Settings UI API Key Management feature. All research unknowns resolved, design contracts defined, and developer quickstart guide prepared.
- 🧪 Tests: No tests executed (planning phase only). Test strategy documented in plan.md and quickstart.md for future implementation.
- 📁 Files: Created 5 new files (plan.md, research.md, data-model.md, api-keys.openapi.yaml, quickstart.md). Updated CLAUDE.md via agent context script.
- 🔁 Next prompts: Run `/sp.tasks` to generate 20-30 minute atomic implementation tasks (per user requirement in args). Then follow TDD cycle (Red-Green-Refactor) for implementation.
- 🧠 Reflection: Planning workflow executed smoothly after initial branch corrections. Parallel research agents significantly improved efficiency (5 research tasks completed simultaneously). Service-layer encryption decision (vs. TypeDecorator) was critical for async compatibility. User requirement for 20-30 minute task sizing documented in plan.md Phase 2 section for enforcement during /sp.tasks execution.

## Evaluation notes (flywheel)

- Failure modes observed: Initial error attempting to run check-prerequisites.sh on main branch instead of feature branch. Resolved by pulling main and switching to 010-settings-ui-api-keys branch. Avoided pulling from remote since branch hasn't been pushed yet.
- Graders run and results (PASS/FAIL): Constitution Check: ALL PASS (Test-First Development, Clean Code, Project Structure, Data Storage, Interface Excellence)
- Prompt variant (if applicable): Standard /sp.plan command with custom args "--args 'make sure each tasks is sized right (20-30 minutes, not hours or minutes)'" to enforce task sizing during Phase 2
- Next experiment (smallest change to try): During /sp.tasks execution, validate that all generated tasks meet 20-30 minute sizing criteria. Consider auto-splitting tasks that exceed 30 minutes into smaller units. Consider auto-grouping trivial tasks that are under 5 minutes.
