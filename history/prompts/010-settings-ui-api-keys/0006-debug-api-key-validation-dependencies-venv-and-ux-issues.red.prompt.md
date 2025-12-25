---
id: 0006
title: Debug API key validation dependencies venv and UX issues
stage: red
date: 2025-12-25
surface: agent
model: claude-sonnet-4-5-20250929
feature: 010-settings-ui-api-keys
branch: 010-settings-ui-api-keys
user: hubaib
command: /sp.phr
labels: ["debugging", "dependencies", "venv", "ux", "api-keys", "google-genai", "uv-workspace", "frontend-state", "timezone"]
links:
  spec: ../../specs/010-settings-ui-api-keys/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - backend/requirements.txt
 - backend/pyproject.toml
 - backend/src/services/gemini_validator.py
 - backend/src/api/routers/api_keys.py
 - backend/src/services/api_key_service.py
 - frontend/lib/hooks/useApiKey.ts
 - frontend/app/(dashboard)/dashboard/settings/page.tsx
tests:
 - none
---

## Prompt

User reported multiple issues after implementing the API key management feature:

1. **Issue 1**: /test endpoint returning "google-genai library not installed" error despite library being in pyproject.toml
2. **Issue 2**: After fixing dependencies, still getting the same error even after backend restart
3. **Issue 3**: Root cause investigation revealed uv workspace venv configuration issues
4. **Issue 4**: API key validation failing with wrong Gemini model name
5. **Issue 5**: Status indicator (verified/not verified) not updating after save until page refresh
6. **Issue 6**: last_validated_at timestamp not displaying correctly
7. **UX Issue**: Confusion about when to test API key - before or after saving
8. **Design Issue**: Removed /test endpoint not in original tasks.md, integrated validation into save endpoint

The debugging session involved:
- Investigating missing dependencies (google-genai, google-api-core)
- Understanding uv workspace shared .venv behavior
- Fixing model name from gemini-1.5-flash to gemini-2.5-flash
- Improving UX by auto-validating on save instead of separate test button
- Fixing frontend state management to refresh after save
- Correcting timezone handling for timestamps

## Response snapshot

Systematically debugged and fixed 7 issues:

1. **Missing dependencies**: Added google-genai and google-api-core to requirements.txt and pyproject.toml
2. **Workspace venv**: Ran `uv sync --package backend` from workspace root to install dependencies in shared .venv
3. **Model name**: Updated gemini-1.5-flash → gemini-2.5-flash in GeminiValidator
4. **UX improvement**: Integrated validation into save endpoint with rate limiting (5 tests/hour), removed confusing separate /test endpoint
5. **Frontend state**: Modified useApiKey hook to fetch updated status after save to get validation result
6. **Timestamp fix**: Changed datetime.now(timezone.utc).replace(tzinfo=None) → datetime.now(UTC) for proper timezone-aware timestamps
7. **Rate limiting**: Migrated rate limiting logic from /test to save endpoint to prevent abuse

## Outcome

- ✅ Impact: All 7 bugs fixed, API key validation working end-to-end, improved UX with single-step save-and-validate flow
- 🧪 Tests: Manual testing of save endpoint with valid/invalid keys, verification of status updates and timestamps
- 📁 Files: Modified 7 files across backend and frontend (routers, services, hooks, UI components)
- 🔁 Next prompts: Test rate limiting behavior, verify error messages are user-friendly, consider adding loading states during validation
- 🧠 Reflection: uv workspace shared venv requires understanding of --package flag for dependency syncing; better to validate-then-save than separate test endpoint for UX

## Evaluation notes (flywheel)

- Failure modes observed: Initial misunderstanding of uv workspace venv behavior (running uv sync in backend/ doesn't auto-install backend dependencies). Missing dependency (google-api-core) not caught until runtime due to try/except ImportError pattern masking the real issue.
- Graders run and results (PASS/FAIL): PASS - All validation tests working, status updates correctly, timestamps display properly
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): Add explicit dependency check on backend startup to fail fast if critical packages missing, rather than silently setting genai=None
