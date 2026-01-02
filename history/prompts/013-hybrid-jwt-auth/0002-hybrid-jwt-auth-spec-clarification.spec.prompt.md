---
id: 0002
title: Hybrid JWT Auth Spec Clarification
stage: spec
date: 2026-01-02
surface: agent
model: claude-sonnet-4-5
feature: 013-hybrid-jwt-auth
branch: 013-hybrid-jwt-auth
user: user
command: /sp.clarify
labels: ["spec", "clarification", "authentication", "jwt", "security", "migration-strategy"]
links:
  spec: ../../specs/013-hybrid-jwt-auth/spec.md
  ticket: null
  adr: ../../history/adr/0004-hybrid-jwt-authentication-architecture.md
  pr: null
files:
  - specs/013-hybrid-jwt-auth/spec.md
tests:
  - N/A (clarification phase)
---

## Prompt

User invoked `/sp.clarify` command to identify and resolve ambiguities in the Hybrid JWT Authentication feature specification before proceeding to planning phase.

## Response snapshot

Conducted structured ambiguity scan across 11 coverage categories (Functional Scope, Domain & Data Model, Interaction & UX Flow, Non-Functional Quality Attributes, Observability, Security, Integration & External Dependencies, Edge Cases, Constraints & Tradeoffs, Terminology, Completion Signals).

**5 Clarification Questions Asked & Answered:**

1. **Migration Strategy**: Feature flag-based gradual rollout (new users get JWT by default, existing users migrate via percentage rollout: 10% → 25% → 50% → 100%, with A/B testing and easy rollback)

2. **Refresh Token Storage Security**: Hash refresh tokens before database storage using SHA-256 or bcrypt (industry best practice to prevent token theft in case of database compromise)

3. **Multi-Tab Token Refresh Coordination**: Shared lock with single refresh - one tab refreshes and broadcasts new token to other tabs via localStorage events or BroadcastChannel API (prevents duplicate refresh requests, most efficient)

4. **Token Refresh Retry Logic**: 3 retry attempts with exponential backoff (1s, 2s, 4s delays, ~7 seconds total). Distinguish network errors (retry) from auth errors (immediate redirect to login).

5. **Cookie Security Attributes**: SameSite=Strict, Secure=true, HttpOnly=true for refresh token cookies (strongest CSRF and XSS protection, acceptable trade-off of requiring re-login from external links)

**Spec Sections Updated:**
- Added Clarifications section with Session 2026-01-02 (5 Q&A pairs)
- FR-004: Added refresh token hashing requirement with validation process
- FR-014: Specified cookie security attributes (HttpOnly, Secure, SameSite=Strict, Max-Age)
- FR-015/FR-016: Added retry logic with exponential backoff and error type distinction
- FR-017: Added multi-tab token synchronization requirement
- FR-023/FR-024: Detailed migration strategy with gradual rollout controls
- Key Entities: Updated Refresh Token and Session Record definitions
- Edge Cases: Enhanced multi-tab and refresh endpoint failure scenarios

**Coverage Summary Result:**
- All 11 categories: ✅ Clear or Resolved
- Outstanding Issues: None
- Ready to proceed to `/sp.plan`

## Outcome

- ✅ Impact: Resolved 5 critical architectural ambiguities covering migration strategy, security best practices (token hashing, cookie attributes), error handling (retry with backoff), and multi-tab coordination. Spec is now actionable and ready for planning phase.
- 🧪 Tests: N/A (clarification phase, no code changes)
- 📁 Files: 1 file modified (specs/013-hybrid-jwt-auth/spec.md - added Clarifications section + updated 6 requirement sections + enhanced 2 edge cases + refined Key Entities)
- 🔁 Next prompts: /sp.plan (recommended next step)
- 🧠 Reflection: Clarification session successfully identified high-impact decision points. All 5 questions targeted areas where ambiguity would cause implementation rework or security weaknesses. User choices aligned with industry best practices (hashing tokens, strict cookies, retry with backoff, coordinated multi-tab refresh). Migration strategy enables safe gradual rollout with rollback capability.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A (spec clarification, no tests)
- Prompt variant (if applicable): standard sp.clarify workflow
- Next experiment (smallest change to try): N/A
