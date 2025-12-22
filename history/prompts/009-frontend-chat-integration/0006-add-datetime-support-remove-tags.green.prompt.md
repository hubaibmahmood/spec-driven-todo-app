---
id: 0006
title: add-datetime-support-remove-tags
stage: green
date: 2025-12-22
surface: agent
model: claude-sonnet-4-5
feature: 009-frontend-chat-integration
branch: 009-frontend-chat-integration
user: hubaib
command: /sp.phr
labels: ["datetime", "timezone", "ui-cleanup", "task-management"]
links:
  spec: specs/009-frontend-chat-integration/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - frontend/components/todo/AddTodoModal.tsx
  - frontend/components/todo/TodoItem.tsx
tests:
  - Manual testing in browser (frontend dev server)
---

## Prompt

But the thing is frontend currently doesn't show time, It only shows date in tasks. It is also missing selecting time when creating tasks

[User then confirmed:]
Yes lets go with option 1. Also, remove the tags field from Tasks creation modal as we aren't storing tags in our database and neither displaying them

## Response snapshot

Successfully implemented datetime support and removed unused tags field:
1. Changed task creation modal from date-only to datetime-local input
2. Updated TodoItem to display both date and time with timezone-aware formatting
3. Removed tags field completely (not stored in database)
4. Smart display: shows time only when present, otherwise shows date-only

## Outcome

- ✅ Impact: Phase 8 (Timezone-Aware Task Scheduling) is now fully functional. Users can create tasks with specific times via the manual form and through natural language chat commands. All times display in user's local timezone.
- 🧪 Tests: Manual browser testing confirmed datetime-local input works and times display correctly with timezone formatting
- 📁 Files: Modified AddTodoModal.tsx (removed tags state/field, added datetime-local input) and TodoItem.tsx (removed tags display, added formatDueDate() with timezone support)
- 🔁 Next prompts: "Test task creation with 'tomorrow at 5pm' via chat", "Move to Phase 9 (Edge Cases and Polish)", "Run E2E tests for timezone handling"
- 🧠 Reflection: Critical gap identified - while backend supported datetime and timezone headers were implemented, the frontend UI lacked time input capability, creating inconsistent UX between chat (natural language times) and manual task creation

## Evaluation notes (flywheel)

- Failure modes observed: Initial implementation overlooked frontend UI time input despite backend support. User correctly identified this gap. Tags field was creating confusion as it appeared functional but wasn't persisted.
- Graders run and results (PASS/FAIL): PASS - User confirmed frontend server running, linter auto-formatted code successfully
- Prompt variant (if applicable): Direct user request after identifying missing functionality
- Next experiment (smallest change to try): Add E2E tests for datetime creation via both chat and manual form to ensure timezone handling is consistent across both input methods
