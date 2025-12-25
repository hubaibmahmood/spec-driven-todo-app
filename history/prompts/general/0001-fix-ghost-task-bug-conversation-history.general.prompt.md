---
id: 0001
title: Fix ghost task bug conversation history
stage: general
date: 2025-12-25
surface: agent
model: claude-sonnet-4-5-20251101
feature: none
branch: 010-settings-ui-api-keys
user: hubaib
command: /sp.phr
labels: ["debugging", "ai-agent", "conversation-history", "ghost-tasks", "mcp-tools", "tracing"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - ai-agent/src/ai_agent/agent/context_manager.py
 - ai-agent/src/ai_agent/api/chat.py
 - ai-agent/src/ai_agent/agent/agent_service.py
 - ai-agent/src/ai_agent/main.py
 - ai-agent/.env
 - ai-agent/src/ai_agent/agent/config.py
tests:
 - Manual testing: "Update Buy clothes task" query
 - Verified AI calls list_tasks() tool correctly
 - Confirmed no ghost Task 2 appears in response
---

## Prompt

I just noticed a bug. When I ask it to update Buy clothes task desc. then somehow it's fetching task that aren't even in database. There is only 1 task with having "buy clothes as its title. But the chatbot is responding with:

My apologies, I see there are indeed two tasks with the title "Buy clothes".

Could you please specify which one you'd like to update by providing its Task ID?

*   **Task 22**: Buy clothes (description: "shirt, suit, pant")
*   **Task 2**: Buy clothes (description: "shirt, suit, pant, coat")

How it's getting the task 2? when it's not even in the database

OK finally now it seems to be working with the conversation history. Lets create phr for this issue and how we resolved it.

## Response snapshot

Through extensive debugging with tracing enabled, we discovered the AI was referencing deleted tasks from conversation history instead of calling list_tasks() to get current database state. The solution involved three layers:

1. **Conversation history sanitization** - Removing task ID patterns from old messages
2. **Tracing implementation** - Enabled OpenAI Agents SDK tracing to visualize AI decision-making
3. **Aggressive message filtering** - Completely removing assistant messages containing task references

The breakthrough came when testing without history showed the AI correctly called list_tasks(). This confirmed conversation history was overwhelming the system prompt, even with explicit instructions to call the tool first.

## Outcome

- ✅ Impact: Fixed critical bug where AI showed deleted "ghost tasks" to users by implementing aggressive conversation history filtering that removes all assistant messages containing task-specific information
- 🧪 Tests: Manual end-to-end testing confirmed AI now calls list_tasks() and shows only Task 22 (actual database state), no phantom Task 2
- 📁 Files: Modified 6 core files - context_manager.py (added _contains_task_references method), chat.py (re-enabled filtered history), agent_service.py (enabled tracing), main.py (configured logging), .env (updated system prompt), config.py (updated default prompt)
- 🔁 Next prompts: Monitor for edge cases where removing task messages breaks conversation flow; consider implementing response validation as additional safety layer; evaluate token usage impact of aggressive filtering
- 🧠 Reflection: System prompts alone are insufficient to control AI behavior when conversation history contains conflicting data - architectural solutions (data filtering/injection) are more reliable than prompt engineering

## Evaluation notes (flywheel)

- Failure modes observed: Initial sanitization approach only removed task IDs but left contextual clues (different descriptions, task counts) that AI used to reconstruct ghost tasks; system prompt instructions were completely ignored when conversation history provided alternative data source; AI chose not to call list_tasks() tool despite explicit MANDATORY instructions in multiple prompt iterations
- Graders run and results (PASS/FAIL): PASS - Ghost task no longer appears; PASS - AI calls list_tasks() tool; PASS - Conversation history preserved (non-task messages); PASS - Tracing enabled for future debugging
- Prompt variant (if applicable): Tested 5 system prompt variants with increasing urgency/explicitness - all failed; final solution bypassed prompt engineering entirely
- Next experiment (smallest change to try): A/B test conversation history window size (currently unlimited) vs last N messages to reduce stale data exposure while preserving context; measure impact on conversation quality and token usage; consider hybrid approach where task-specific messages expire after X minutes
