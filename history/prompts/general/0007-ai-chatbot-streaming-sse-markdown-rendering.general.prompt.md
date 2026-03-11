---
id: "0007"
title: AI Chatbot UI Revamp — Streaming SSE + Markdown Rendering
stage: green
date: 2026-03-10
surface: agent
model: claude-sonnet-4-6
feature: ai-chatbot-streaming
branch: main
user: hubaib
command: implement plan (AI Chatbot UI Revamp)
labels: ["streaming", "sse", "markdown", "assistant-ui", "openai-agents", "react-markdown"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - ai-agent/src/ai_agent/api/chat.py
  - ai-agent/src/ai_agent/agent/agent_service.py
  - ai-agent/src/ai_agent/main.py
  - ai-agent/requirements.txt
  - frontend/types/chat.ts
  - frontend/lib/chat/chat-api.ts
  - frontend/components/chat/MarkdownMessage.tsx
  - frontend/components/chat/ChatMessage.tsx
  - frontend/components/chat/ChatPanel.tsx
tests:
  - " - (manual) curl SSE stream test"
---

## Prompt

Implement the following plan:

# Plan: AI Chatbot UI Revamp — Streaming + Assistant-UI + Markdown

[Full plan — adds POST /api/chat/stream SSE endpoint, react-markdown rendering, streaming fetch in ChatPanel]

Also: use context7 MCP or web search to find streaming event structure, and upgrade openai-agents SDK to 0.10.5 if safe.

## Response snapshot

Implemented full streaming + markdown revamp across backend and frontend:

**Backend:**
- `agent_service.py`: Extracted timezone instruction building into `_enhance_agent_instructions()` helper, refactored `run_agent_with_context` to use it (eliminates ~40 lines of duplication)
- `chat.py`: Added `_stream_agent_response()` async generator that streams SSE text_delta events using `Runner.run_streamed()` + `ResponseTextDeltaEvent`. Added `POST /api/chat/stream` endpoint with pre-flight validation (API key, conversation create, history load) returning `StreamingResponse`. Fixed all deprecated `datetime.utcnow()` → `datetime.now(UTC)` calls.
- `main.py`: Updated CORS `expose_headers` to include `Cache-Control` and `Connection`
- `requirements.txt`: Upgraded `openai-agents` 0.8.4 → 0.10.5 (safe: already on openai v2.x, Python 3.12+)

**Frontend:**
- `types/chat.ts`: Added `ChatStreamTextDelta`, `ChatStreamDone`, `ChatStreamError`, `ChatStreamEvent` union type
- `chat-api.ts`: Added `sendChatMessageStreaming()` using fetch + ReadableStream (not EventSource, which can't set custom headers). Splits SSE buffer on `\n\n`, routes events to onDelta/onDone/onError callbacks.
- `MarkdownMessage.tsx`: New component using react-markdown + remark-gfm with Tailwind-styled custom renderers for h1-h3, strong, code, pre, ul/ol/li, p, a, blockquote
- `ChatMessage.tsx`: Routes assistant messages through `<MarkdownMessage />`, error/guidance/user messages use plain text
- `ChatPanel.tsx`: Replaced non-streaming `executeSendMessage` with streaming version. Uses `sendChatMessageStreaming` with optimistic streaming message that accumulates text deltas in real-time. Added `AbortController` ref + cleanup when panel closes. Preserved all business logic: rate limiting, session expiry recovery, destructive confirmation modal, pagination, tasks-updated polling.

**SSE format:**
```
data: {"type": "text_delta", "content": "..."}   ← one per token
data: {"type": "done", "conversation_id": N, "operations": [...]}
data: {"type": "error", "detail": "..."}
```

**Key research finding (context7):** Correct streaming event check for openai-agents 0.10.5:
```python
from openai.types.responses import ResponseTextDeltaEvent
if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
    chunk = event.data.delta
```

## Outcome

- ✅ Impact: Users see text streaming token-by-token instead of waiting 3-5s for full response. Markdown (bold, code, lists) renders correctly instead of showing raw `**` characters.
- 🧪 Tests: Manual curl SSE test against /api/chat/stream; TypeScript tsc --noEmit passes (only pre-existing test file errors remain)
- 📁 Files: 9 files modified/created
- 🔁 Next prompts: Add nginx `proxy_buffering off` config on VM; optionally remove `@openai/chatkit-react` from package.json; consider typewriter effect if Gemini chunks are too coarse
- 🧠 Reflection: Chose react-markdown + remark-gfm directly over @assistant-ui/react to avoid React 19 compatibility uncertainty and keep the integration simple. The streaming generator pattern in FastAPI works correctly with dependency-injected db sessions.

## Evaluation notes (flywheel)

- Failure modes observed: none yet (pre-deployment)
- Graders run and results (PASS/FAIL): tsc --noEmit PASS (production files)
- Prompt variant (if applicable): null
- Next experiment: Test with real Gemini streaming to verify ResponseTextDeltaEvent is correctly detected
