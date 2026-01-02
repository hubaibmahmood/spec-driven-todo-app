---
id: 0002
title: ADR Creation for Hybrid JWT Authentication
stage: general
date: 2026-01-01
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: main
user: user
command: /sp.adr
labels: ["architecture", "authentication", "scalability", "jwt", "adr", "performance"]
links:
  spec: null
  ticket: null
  adr: history/adr/0004-hybrid-jwt-authentication-architecture.md
  pr: null
files:
  - history/adr/0004-hybrid-jwt-authentication-architecture.md
  - history/prompts/general/0002-adr-creation-for-hybrid-jwt-authentication.general.prompt.md
tests:
  - N/A (architectural decision documentation)
---

## Prompt

**Initial Question:**
"How will JWT is getting used in our todo app?"

**Follow-up Discussion:**
User questioned whether session management, real-time revocation, and audit trails could be done with JWT, expressing concerns about the current database session approach not scaling with hundreds of users due to repeated database calls on every request.

**Final Command:**
`/sp.adr lets create architecture Decision then we will create a spec and implement the Hybrid approach`

**Workflow Clarification:**
User asked whether to create ADR first or spec first. Recommended approach was:
1. Create ADR first (capture architectural discussion while fresh)
2. Then create spec to formalize requirements
3. Then create tasks and implement

User agreed: "Lets go with your recommended approach"

## Response snapshot

### Phase 1: JWT Usage Investigation

Launched Explore agent to investigate how JWT/authentication is currently used in the todo app. Key findings:

**Current Architecture:**
- Uses better-auth with database-backed session tokens (NOT traditional JWTs)
- Session tokens stored as plain text in PostgreSQL `user_sessions` table
- Every authenticated request queries database for validation (`backend/src/services/auth_service.py:89-94`)
- 7-day session expiration
- httpOnly cookies for token storage

**Performance Analysis:**
- At 100 users (10 req/min): ~17 DB queries/second
- At 1,000 users: ~167 DB queries/second
- Database roundtrip: 5-20ms per request
- Bottleneck identified: Database becomes scalability constraint

### Phase 2: JWT vs Database Sessions Discussion

Explained that JWT **can** support session management, revocation, and audit trails, but requires hybrid stateful mechanisms:

**Tradeoff Analysis:**
- Pure JWT: Stateless but no revocation
- JWT + Blacklist: Requires Redis/DB lookup anyway
- JWT + Sessions Table: Hybrid approach (best of both worlds)

**Industry Pattern:**
- Google: 1-hour access tokens, 180-day refresh
- Facebook: 1-2 hour access, 60-day refresh
- GitHub: 8-hour access tokens
- Auth0: 15-60 min access, 30+ day refresh

**Silent Token Refresh:**
Explained that users are NOT logged out every 15 minutes. Frontend HTTP interceptor automatically refreshes expired access tokens in the background, transparent to users.

**Database Load Comparison:**
- Current: 1,000 queries/day per user
- Hybrid JWT: 96 queries/day per user (90.4% reduction)
- At 1,000 users: 167 queries/sec → ~1 query/sec (99.4% reduction)

### Phase 3: ADR Creation

**Workflow Discussion:**
Recommended approach per Spec-Kit Plus methodology:
1. Create ADR to capture architectural discussion (while fresh)
2. Create spec via `/sp.specify` to formalize requirements
3. Create plan via `/sp.plan` if needed (already discussed in detail)
4. Create tasks via `/sp.tasks`
5. Implement via `/sp.implement`

**ADR Created:**
- **ID:** ADR-0004
- **Title:** Hybrid JWT Authentication Architecture
- **Path:** `history/adr/0004-hybrid-jwt-authentication-architecture.md`
- **Status:** Proposed
- **Decision:** Implement two-token system (15-min JWT access tokens + 7-day opaque refresh tokens)

**Key ADR Sections:**
- Context: Current DB session bottleneck at scale
- Decision: Hybrid JWT with silent refresh, reusing `user_sessions` table
- Consequences: 90-99% DB reduction, improved latency, acceptable 15-min revocation delay
- Alternatives: Pure JWT (rejected - no revocation), Redis cache (rejected - not microservices-ready), Keep DB sessions (rejected - doesn't scale), Short-lived sessions (rejected - poor UX)
- Implementation checklist: 13 tasks covering backend JWT service, frontend interceptor, auth endpoints, testing, monitoring

**Performance Targets:**
- Auth queries: 167/sec → <5/sec
- Avg auth latency: 15ms → <1ms
- DB load reduction: 90-99%
- Revocation latency: Immediate → ≤15 min
- User session duration: 7 days (unchanged)

## Outcome

- ✅ Impact: Created comprehensive ADR documenting hybrid JWT authentication architecture, capturing scalability analysis, performance benchmarks, and detailed tradeoff evaluation with 4 alternatives considered
- 🧪 Tests: N/A (architectural decision documentation - tests will be created during implementation)
- 📁 Files: Created ADR-0004 (6.5KB, 286 lines) with complete decision context, alternatives analysis, implementation checklist, security considerations, and monitoring strategy
- 🔁 Next prompts: `/sp.specify "hybrid-jwt-authentication"` to create formal feature specification, then `/sp.tasks` to break down implementation, then `/sp.implement` to execute
- 🧠 Reflection: Successfully captured extensive architectural discussion in structured ADR format. Hybrid approach balances performance (90-99% DB reduction), security (revocation via refresh tokens), and UX (transparent token refresh). The 15-minute revocation window is an acceptable tradeoff for massive scalability gains.

## Evaluation notes (flywheel)

- Failure modes observed: None - ADR creation followed template, all significance criteria met (long-term impact, multiple alternatives, cross-cutting scope)
- Graders run and results (PASS/FAIL):
  * Decision clustering: PASS (authentication approach as integrated system, not atomic choices)
  * Alternatives documentation: PASS (4 alternatives with explicit pros/cons and rejection rationale)
  * Consequences: PASS (both positive and negative outcomes documented with metrics)
  * References: PASS (linked to technical discussion, ready for spec/plan links)
- Prompt variant (if applicable): Standard ADR workflow with recommended approach (ADR before spec)
- Next experiment (smallest change to try): Create spec.md to formalize requirements and link back to ADR-0004, validating the "ADR-first" workflow for capturing live architectural discussions
