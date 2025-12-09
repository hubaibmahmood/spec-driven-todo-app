---
id: 0003
title: FastAPI Spec Clarification Session
stage: spec
date: 2025-12-09
surface: agent
model: claude-sonnet-4-5-20250929
feature: 003-fastapi-rest-api
branch: 003-fastapi-rest-api
user: mac
command: /sp.clarify
labels: ["clarification", "specification", "authentication", "rate-limiting", "database-schema"]
links:
  spec: specs/003-fastapi-rest-api/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/003-fastapi-rest-api/spec.md
tests:
 - None (specification phase)
---

## Prompt

/sp.clarify (no arguments provided)

User provided critical architecture clarifications during session:
1. Authentication architecture: Database-driven session validation (not JWT claim extraction)
2. Shared database: Auth server and FastAPI share same Neon PostgreSQL instance
3. User sessions schema: Complete table structure with token_hash, user_id (UUID), expires_at, revoked, etc.

## Response snapshot

Conducted 5-question clarification session resolving critical ambiguities in FastAPI REST API specification:

**Questions & Answers**:

1. **Rate Limiting Granularity**: User-based tracking (by user_id from session) with IP fallback for unauthenticated requests
   - Chosen: Option A - User-based with IP fallback
   - Rationale: Prevents authenticated users from bypassing limits by IP hopping while still protecting against unauthenticated abuse

2. **Authentication Method**: Database-driven session validation via user_sessions table queries (not JWT decoding)
   - User provided: Auth server and FastAPI share same Neon PostgreSQL database
   - Session tokens validated by querying user_sessions table directly
   - No inter-service HTTP calls to auth server

3. **User Sessions Schema**: Complete table schema documented
   - User provided: Full SQLAlchemy table definition
   - Columns: id (UUID), user_id (UUID FK), token_hash (string 255, unique), refresh_token_hash, ip_address, user_agent, created_at, expires_at, last_activity_at, revoked (boolean)
   - Critical: Tokens stored as hashes, not plaintext

4. **Rate Limit Values**: Read: 100/min, Write: 30/min (3:1 ratio)
   - Chosen: Option B - Balanced approach
   - Rationale: 100 reads/min = ~1.6/sec (good for UI polling), 30 writes/min = 1 every 2 seconds (prevents spam)

5. **CORS Origins**: localhost:3000 for development, production domain via environment variable
   - Accepted suggested pattern
   - Environment-based configuration for deployment flexibility

**Major Specification Updates**:

- **Clarifications section**: Created new section with Session 2025-12-09 documenting all 5 Q&A pairs
- **Authentication requirements** (FR-021 to FR-028): Complete rewrite from JWT-based to database-driven session validation
  - Added token hashing requirement (FR-021)
  - Added session validity checks: expires_at > now AND revoked = false (FR-024)
  - Removed JWT libraries from dependencies
- **Rate limiting** (FR-031): Specified exact values (100/min read, 30/min write)
- **CORS** (FR-014): Specified allowed origins (localhost:3000 + env var)
- **User Story 8**: Updated from "JWT Authentication" to "Session Authentication" with database lookup scenarios
- **Key Entities**: Added complete UserSession entity with all table columns
- **Assumptions**: Added token hashing, shared database architecture, UUID usage
- **Constraints**: Added cannot modify auth server tables
- **Dependencies**: Removed JWT libraries, added hashlib for token hashing
- **Edge Cases**: Added 2 new cases for token hashing mismatch and revoked sessions

**Coverage Analysis**: All 10 taxonomy categories resolved (Functional Scope, Domain Model, Integration, Security, NFRs, Edge Cases, Constraints, Terminology, Completion Signals, Misc)

## Outcome

- ✅ Impact: 5 critical ambiguities resolved, specification updated with production-ready authentication architecture (database-driven session validation)
- 🧪 Tests: No tests (specification phase) - clarifications will guide test design during implementation
- 📁 Files: Updated spec.md with Clarifications section and 8 other sections modified
- 🔁 Next prompts: `/sp.plan` to create architectural design with fastapi-developer agent
- 🧠 Reflection: User-provided architecture details (shared database, user_sessions schema) were essential - initial spec assumed JWT claim extraction which would have been incorrect implementation path

## Evaluation notes (flywheel)

- Failure modes observed: Initial spec made incorrect assumption about JWT validation approach; user correction prevented major rework
- Graders run and results (PASS/FAIL): Coverage analysis - PASS (all 10 categories resolved, no outstanding items)
- Prompt variant (if applicable): Interactive multi-turn clarification with user-provided technical details
- Next experiment (smallest change to try): Proceed to `/sp.plan` - architecture design should leverage database-driven session validation pattern
