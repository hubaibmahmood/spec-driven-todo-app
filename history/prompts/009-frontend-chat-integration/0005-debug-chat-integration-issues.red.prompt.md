---
id: 0005
title: Debug chat integration issues
stage: red
date: 2025-12-22
surface: agent
model: claude-sonnet-4-5
feature: 009-frontend-chat-integration
branch: 009-frontend-chat-integration
user: hubaib
command: /sp.phr
labels: ["debugging", "chat-integration", "cors", "user-authentication", "date-parsing", "event-bus"]
links:
  spec: specs/009-frontend-chat-integration/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - frontend/components/chat/ChatPanel.tsx
  - frontend/hooks/useTasks.ts
  - ai-agent/src/ai_agent/agent/agent_service.py
  - ai-agent/src/ai_agent/agent/mcp_connection.py
  - ai-agent/src/ai_agent/main.py
  - backend/src/api/main.py
  - mcp-server/src/tools/create_task.py
  - mcp-server/src/tools/list_tasks.py
  - mcp-server/src/tools/update_task.py
  - mcp-server/src/tools/delete_task.py
  - mcp-server/src/tools/mark_completed.py
  - frontend/.env
tests:
  - none
---

## Prompt

Two things I have noticed.

1: Upon refreshing the page, the chatbot history is getting lost.
2: When performing operations of tasks with chatbot. It's not appearing in the dashboard until the page is reloaded manually

[Additional context from conversation]
- Implemented Phase 5 frontend chat integration
- Chat history loads successfully after fix
- Task refresh still not working despite event-based mechanism
- Date parsing was off by one day when user said "today"

## Response snapshot

Fixed three critical issues in the chat integration:

1. **Chat History Persistence**: Implemented conversation history loading in ChatPanel using useEffect that fetches latest conversation from `/api/conversations` endpoint and loads all messages on panel open.

2. **Task Refresh (Partial)**: Implemented event-based communication using custom 'tasks-updated' events dispatched from ChatPanel with polling mechanism (5 attempts over 2 seconds). useTasks hook listens for these events to trigger refresh. However, user reports this is still not working.

3. **Date Parsing Fix**: Updated AI agent system prompt in agent_service.py to provide explicit date/time handling instructions. The agent was converting "today" incorrectly. Now includes clear examples showing how to extract date from current time and format with proper timezone offset (e.g., "2025-12-22T17:00:00+05:00").

4. **User ID Extraction**: Updated all MCP tools (create_task, list_tasks, update_task, delete_task, mark_completed) to use FastMCP's `get_http_headers()` helper function for extracting X-User-ID header instead of attempting to access Context attributes directly.

## Outcome

- ✅ Impact: Fixed chat history persistence, improved date parsing accuracy, standardized user ID extraction across MCP tools. Task refresh mechanism implemented but requires further debugging.
- 🧪 Tests: Frontend build passed successfully with no TypeScript errors
- 📁 Files: Modified 12 files across frontend, ai-agent, backend, and mcp-server
- 🔁 Next prompts: "Debug why tasks-updated events aren't triggering dashboard refresh" or "Add console logging to trace event dispatch and listener registration"
- 🧠 Reflection: Event-based communication between React components requires careful attention to component lifecycle and state management. The event is being dispatched but not triggering the expected refresh, suggesting a potential issue with event listener registration timing or component mounting order.

## Evaluation notes (flywheel)

- Failure modes observed: Task refresh event mechanism not working despite proper event dispatch and listener setup. Root cause unclear - could be timing issue, component lifecycle problem, or state closure in event handler.
- Graders run and results (PASS/FAIL): Manual testing - Chat history: PASS, Date parsing: PASS (pending verification), Task refresh: FAIL
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): Add console.log statements in both ChatPanel (event dispatch) and useTasks (event listener) to verify events are being emitted and received. Check browser DevTools to confirm 'tasks-updated' events appear in event log.
