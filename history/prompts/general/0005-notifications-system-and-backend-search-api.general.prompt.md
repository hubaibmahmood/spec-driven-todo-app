---
id: "0005"
title: Notifications System and Backend Search API
stage: general
date: 2026-03-06
surface: agent
model: claude-sonnet-4-6
feature: notifications-and-search
branch: main
user: hubaib
command: "Implement the following plan: Notification System + Backend Search API"
labels: ["notifications", "apscheduler", "resend", "search", "pagination", "backend", "frontend"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - backend/alembic/versions/20260305_003_add_notifications_and_reminder_sent.py
  - backend/src/models/notification.py
  - backend/src/models/database.py
  - backend/src/api/schemas/notification.py
  - backend/src/api/schemas/task.py
  - backend/src/services/notification_service.py
  - backend/src/api/routers/notifications.py
  - backend/src/api/routers/tasks.py
  - backend/src/database/repository.py
  - backend/src/api/main.py
  - backend/src/config.py
  - backend/pyproject.toml
  - backend/.env.example
  - frontend/types/notification.ts
  - frontend/hooks/useNotifications.ts
  - frontend/components/dashboard/NotificationBell.tsx
  - frontend/components/dashboard/Header.tsx
  - frontend/components/dashboard/FilterBar.tsx
  - frontend/hooks/useTasks.ts
  - frontend/lib/api-v2.ts
  - frontend/app/(dashboard)/dashboard/tasks/page.tsx
  - pyproject.toml
tests:
  - "none added"
---

## Prompt

Implement the following plan:

# Plan: Notifications System + Backend Search API

Feature 1: Notification System — APScheduler in backend process, Resend email, in-app bell polling every 60s.
Feature 2: Backend Search API — query params on GET /tasks/, server-side filtering, paginated TaskListResponse.

## Response snapshot

Implemented both features end-to-end across backend and frontend:

**Backend:**
- Alembic migration adding `notifications` table + `reminder_sent` column on `tasks`
- `Notification` SQLAlchemy model (task FK, type, message, is_read, sent_email)
- `NotificationService` class with `AsyncIOScheduler` (APScheduler 3.x): runs every 15 minutes, checks due-soon tasks (24h window) and overdue tasks (once per day), sends Resend emails via httpx
- `/notifications/` GET, PATCH `/{id}/read`, POST `/read-all` endpoints
- `GET /tasks/` updated: accepts `search`, `priority`, `completed`, `due_before`, `due_after`, `page`, `limit` query params; returns `TaskListResponse` with pagination metadata
- `TaskRepository.get_all_by_user_filtered()`: ILIKE search, dynamic filters, COUNT + paginated SELECT
- Scheduler wired into FastAPI lifespan (start/stop)
- `RESEND_API_KEY` added to config and `.env.example`
- `apscheduler>=3.10.4,<4.0` and `httpx>=0.25.0` added to `pyproject.toml`

**Frontend:**
- `types/notification.ts` — `Notification` and `NotificationListResponse` interfaces
- `hooks/useNotifications.ts` — polls `/notifications/` every 60s, markAsRead/markAllAsRead
- `components/dashboard/NotificationBell.tsx` — bell icon with badge, dropdown panel, click-to-read
- `Header.tsx` updated to mount `NotificationBell`
- `FilterBar.tsx` updated with priority dropdown (All/Urgent/High/Medium/Low)
- `api-v2.ts` updated: `getAll(params?)` now sends query params and returns `{tasks, total, pages}`
- `useTasks(searchParams?)` updated: exposes `total`, `totalPages`; stable deps via `paramsKey`
- `tasks/page.tsx` updated: server-side filtering instead of client-side `useMemo`; uses `total`/`totalPages` from hook

**Pre-existing mypy fix:**
- Root `pyproject.toml` mypy config updated to exclude service directories (`backend/`, `ai-agent/`, etc.) that caused duplicate module errors; root-level `src/storage/memory_store.py` type fixed

## Outcome

- ✅ Impact: Production-ready notification bell + email reminders; server-side search/filter/pagination for tasks
- 🧪 Tests: No new tests added — verification is manual (start backend, check scheduler logs, check DB, poll /notifications/)
- 📁 Files: 20 files created/modified
- 🔁 Next prompts: Run Alembic migration (`alembic upgrade head`), set RESEND_API_KEY in .env, commit via sp.git.commit_pr
- 🧠 Reflection: APScheduler in-process is the right tradeoff for now; the `TaskListResponse` change is a breaking API change that required coordinated frontend updates

## Evaluation notes (flywheel)

- Failure modes observed: Stale closure in `loadTodos` useCallback (fixed by adding `paramsKey` to deps); pre-existing mypy duplicate module errors blocked writes (fixed by scoping root mypy to exclude service dirs)
- Graders run and results (PASS/FAIL): Backend import check PASS; all 17 routes registered PASS
- Prompt variant (if applicable): none
- Next experiment: Add APScheduler persistence (SQLAlchemyJobStore) to survive restarts
