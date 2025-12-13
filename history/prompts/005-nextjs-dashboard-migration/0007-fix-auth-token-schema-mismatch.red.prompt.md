---
id: 0007
title: fix-auth-token-schema-mismatch
stage: red
date: 2025-12-12
surface: agent
model: claude-sonnet-4-5-20250929
feature: 005-nextjs-dashboard-migration
branch: 005-nextjs-dashboard-migration
user: hubaib
command: /sp.phr
labels: ["authentication", "debugging", "better-auth", "fastapi", "database-schema", "token-format"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - backend/src/models/database.py
  - backend/src/services/auth_service.py
  - backend/src/api/routers/tasks.py
  - backend/src/api/dependencies.py
  - backend/src/api/main.py
  - frontend/app/api/[...all]/route.ts
tests:
  - Manual API testing with curl
  - Database schema inspection queries
---

## Prompt

Now getting this error when trying to create tasks:

2025-12-12 22:09:24,291 INFO sqlalchemy.engine.Engine BEGIN (implicit)
2025-12-12 22:09:24,297 INFO sqlalchemy.engine.Engine SELECT user_sessions.id, user_sessions.user_id, user_sessions.token, user_sessions.expires_at, user_sessions.revoked, user_sessions.refresh_token_hash, user_sessions.ip_address, user_sessions.user_agent, user_sessions.created_at, user_sessions.updated_at, user_sessions.last_activity_at
FROM user_sessions
WHERE user_sessions.token = $1::VARCHAR AND user_sessions.expires_at > $2::TIMESTAMP WITH TIME ZONE AND user_sessions.revoked = false
2025-12-12 22:09:24,298 INFO sqlalchemy.engine.Engine [generated in 0.00023s] ('B67MDk9Xio3pw5D0aoxFNp7JJA3cJR3P.+diYbFCtrfAuD2FFpc9nbjsmD1Kac4JszmoKfILNlUA=', datetime.datetime(2025, 12, 12, 17, 9, 23, 687462, tzinfo=datetime.timezone.utc))
2025-12-12 22:09:24,988 INFO sqlalchemy.engine.Engine ROLLBACK

## Response snapshot

Fixed multiple authentication integration issues between FastAPI and better-auth:

1. **Type mismatch**: Changed all `current_user: UUID` to `current_user: str` in task endpoints since better-auth uses CUID format (not UUID).

2. **Column name mismatch**: Updated `UserSession` model to map Python snake_case attributes to database camelCase columns (`user_id` → `"userId"`, `expires_at` → `"expiresAt"`, etc.).

3. **Schema mismatch**: Removed non-existent columns (`revoked`, `refreshTokenHash`, `lastActivityAt`) from the model to match actual database schema.

4. **Token format**: Better-auth sends tokens as `{tokenId}.{signature}` but only stores `tokenId` in the database. Updated `validate_session()` to extract token ID before querying.

5. **Timezone handling**: Fixed datetime comparison to use naive UTC time (matching database's `timestamp without time zone` type).

6. **204 No Content bug**: Fixed Next.js proxy to handle HTTP 204 responses correctly (they must not have a body).

## Outcome

- ✅ Impact: Authentication now works correctly; users can create, read, update, and delete tasks with session-based auth
- 🧪 Tests: Manual API testing with curl, database schema inspection queries
- 📁 Files: Modified 6 files across backend and frontend
- 🔁 Next prompts: Test all CRUD operations through the Next.js dashboard UI, implement proper error handling for expired sessions
- 🧠 Reflection: Better-auth's token format and database schema conventions differ significantly from typical FastAPI patterns - explicit column mapping and token parsing are essential for integration

## Evaluation notes (flywheel)

- Failure modes observed: Initial type annotations assumed UUID format; SQLAlchemy model didn't account for camelCase column naming; token comparison used full token instead of extracting ID portion; timezone-aware datetime comparison failed against naive timestamps
- Graders run and results (PASS/FAIL): PASS - All authentication errors resolved, tasks can now be created/deleted successfully
- Prompt variant (if applicable): Standard debugging workflow with incremental error log analysis
- Next experiment (smallest change to try): Add comprehensive error logging for auth failures to catch similar schema mismatches earlier in development
