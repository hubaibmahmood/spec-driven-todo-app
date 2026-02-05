---
id: 0007
title: Auth proxy for cross-origin JWT cookies
stage: green
date: 2026-01-07
surface: agent
model: claude-sonnet-4-5
feature: 013-hybrid-jwt-auth
branch: 013-hybrid-jwt-auth
user: hubaib
command: /sp.phr
labels: ["authentication", "jwt", "cookies", "proxy", "cors", "race-condition", "next.js", "react-context"]
links:
  spec: specs/013-hybrid-jwt-auth/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - frontend/app/api/auth-proxy/[...path]/route.ts (created)
  - frontend/lib/jwt-auth-client.ts (modified)
  - frontend/contexts/AuthContext.tsx (created)
  - frontend/app/layout.tsx (modified)
  - frontend/hooks/useTasks.ts (modified)
  - auth-server/src/auth/jwt-auth.routes.ts (modified)
  - auth-server/src/app.ts (modified)
  - auth-server/package.json (modified - added cookie-parser)
tests:
  - Manual browser testing: Token refresh endpoint returns 200 with new access token
  - Manual browser testing: Tasks endpoint receives Authorization header correctly
  - Manual browser testing: No race condition - tasks load after token initialization
---

## Prompt

We have implemented till phase 7 so everything should work by now. But seems like it's not refreshing the tokens. I re ran all the servers again after few hours and then navigate to localhost:3000/login. Even though it took to dashboard but the console is showing these logs:

jwt-auth-client.ts:171  POST http://localhost:8080/api/auth/refresh 404 (Not Found)

[User then shared full browser console error stack trace showing the refresh endpoint returning 404]

## Response snapshot

Identified and fixed critical missing implementation: the `/api/auth/refresh` endpoint was completely missing from the auth server, and cross-origin cookie restrictions prevented cookies from being sent between localhost:3000 (frontend) and localhost:8080 (auth-server).

Implemented three-part solution:
1. **Auth server refresh endpoint** - Added `jwtRefresh` function in `jwt-auth.routes.ts` with cookie-parser middleware to handle refresh token validation and new access token generation
2. **Next.js proxy layer** - Created `/api/auth-proxy/[...path]/route.ts` to forward auth requests from same-origin (localhost:3000) to auth server (localhost:8080), solving cookie cross-origin restrictions
3. **Race condition fix** - Created `AuthContext` provider to ensure token initialization completes before API calls are made, preventing 401 errors on initial page load

## Outcome

- ✅ Impact: Fixed broken token refresh mechanism and eliminated race condition causing 401 errors. JWT authentication now works correctly in development with cross-origin cookie handling via proxy pattern. This was a critical gap in the Phase 7 implementation that was not included in the original tasks.
- 🧪 Tests: Manual browser testing confirmed: (1) refresh endpoint returns 200 with valid access token, (2) tasks endpoint receives Authorization header correctly, (3) no race condition on page load
- 📁 Files: 8 files modified/created across frontend (5) and auth-server (3) - proxy route, auth context, JWT client updates, refresh endpoint implementation
- 🔁 Next prompts: Document this as missing task T096-T098 in tasks.md for future reference; consider adding automated E2E tests for token refresh flow
- 🧠 Reflection: The original Phase 7 tasks assumed CORS would be sufficient for cross-origin auth, but missed the critical interaction between `sameSite` cookie restrictions and cross-port JavaScript fetch requests. Proxy pattern is essential for local development with JWT cookies.

## Evaluation notes (flywheel)

- Failure modes observed: Original implementation spec missed auth proxy requirement. Tasks assumed direct cross-origin requests would work with CORS alone, but `sameSite: 'lax'` blocks cookies on cross-origin POST requests via fetch. Race condition between token initialization and data loading was not anticipated in component design.
- Graders run and results (PASS/FAIL): Manual testing - PASS (refresh works, tasks load correctly, no 401 errors)
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): Add automated Playwright E2E test to verify token refresh flow survives server restarts and handles expired tokens correctly
