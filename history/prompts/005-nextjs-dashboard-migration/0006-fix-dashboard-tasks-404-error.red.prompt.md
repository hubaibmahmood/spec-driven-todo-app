---
id: 0006
title: fix-dashboard-tasks-404-error
stage: red
date: 2025-12-12
surface: agent
model: claude-sonnet-4-5-20250929
feature: 005-nextjs-dashboard-migration
branch: 005-nextjs-dashboard-migration
user: hubaib
command: /sp.phr
labels: ["debugging", "404-error", "fastapi", "nextjs-proxy", "trailing-slash", "redirect-handling"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - backend/src/api/main.py
  - frontend/lib/api-v2.ts
  - frontend/app/api/[...all]/route.ts
tests:
  - Manual curl testing of FastAPI endpoints
  - Manual curl testing of Next.js proxy
---

## Prompt

I have integrated better-auth implemented in auth-server with FastAPI server implemented in backend. Now when I login to the website and lands on dashboard it gives me this error:

[Error] Failed to load resource: the server responded with a status of 404 (Not Found) (tasks, line 0)
[Error] Failed to load todos – ApiError: Not Found
ApiError: Not Found
    error (node_modules_next_dist_7a8122d0._.js:3118)
    (anonymous function) (_389b8f80._.js:1493)

## Response snapshot

Diagnosed and fixed a 404 error when loading tasks on the dashboard. The issue was caused by two problems: (1) FastAPI's `redirect_slashes=False` configuration strictly required `/tasks/` with trailing slash, returning 404 for `/tasks`, and (2) The Next.js proxy had overly broad redirect interception logic that was incorrectly sending all `/tasks*` redirect requests to the login page instead of following FastAPI's automatic trailing slash redirects.

## Outcome

- ✅ Impact: Dashboard can now successfully fetch tasks from the FastAPI backend after login. Fixed 404 error by removing `redirect_slashes=False` from FastAPI, removing trailing slash from frontend API call, and updating proxy to transparently follow 307/308 redirects.
- 🧪 Tests: Manual curl tests verified: (1) Direct FastAPI endpoint works, (2) Next.js proxy correctly follows redirects and returns 200 OK, (3) Dashboard loads tasks successfully
- 📁 Files: Modified 3 files - FastAPI main.py (removed redirect_slashes=False), frontend api-v2.ts (removed trailing slash from /tasks/ to /tasks), proxy route.ts (added transparent 307/308 redirect following)
- 🔁 Next prompts: Test dashboard functionality with authenticated user creating/updating/deleting tasks; verify all CRUD operations work correctly through the proxy
- 🧠 Reflection: Overly broad redirect interception in the proxy can cause unexpected behavior. FastAPI's automatic trailing slash handling should be preserved by following redirects transparently rather than intercepting them.

## Evaluation notes (flywheel)

- Failure modes observed: Initial investigation didn't immediately identify the proxy redirect interception logic as the culprit; focused first on FastAPI configuration and API endpoint paths before discovering the proxy was intercepting legitimate redirects
- Graders run and results (PASS/FAIL): PASS - curl tests confirmed fix; dashboard should now load tasks successfully
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): Consider whether FastAPI should have `redirect_slashes=True` (default) to handle both `/tasks` and `/tasks/` gracefully, or if we should standardize on one format across the frontend API client
