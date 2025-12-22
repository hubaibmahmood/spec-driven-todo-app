# ADR-0002: Task Synchronization via Polling and Event Dispatch

> **Scope**: This ADR documents the decision for synchronizing task updates between the chat interface and the main todo list, including the choice of polling with custom events over WebSocket or SSE-based real-time communication.

- **Status:** Accepted
- **Date:** 2025-12-22
- **Feature:** 009-frontend-chat-integration
- **Context:** When users create or modify tasks via the chat interface, the main todo list must update to reflect these changes. Without a synchronization mechanism, users would need to manually refresh the page to see chat-created tasks appear in their todo list, creating a disjointed user experience.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: YES - Affects real-time UX, frontend performance, and backend coupling
     2) Alternatives: YES - Multiple viable options (WebSocket, SSE, polling, shared state)
     3) Scope: YES - Cross-cutting pattern for all chat-to-task-list synchronization
-->

## Decision

**Decision: Polling with Custom Event Dispatch + Optimistic UI**

This decision encompasses two integrated components:

1. **Frontend Event-Driven Refresh**
   - Chat component dispatches `tasks-updated` custom event via `window.dispatchEvent()`
   - Todo list components listen for this event and call `refreshTodos()` to fetch latest data
   - Polling strategy: 5 retry attempts with 400ms interval (2-second window)
   - Implementation:
     ```typescript
     // After AI agent completes task operation
     const pollRefresh = async () => {
       window.dispatchEvent(new CustomEvent('tasks-updated'));
       if (refreshAttempts < maxAttempts) {
         setTimeout(pollRefresh, pollInterval);
       }
     };
     ```

2. **Optimistic UI Updates**
   - Chat displays user message and "Processing..." indicator immediately
   - Task list shows loading state during refresh
   - API response confirms actual state, replacing optimistic updates
   - Provides perceived <500ms feedback (SC-003 requirement)

## Consequences

### Positive

- **Simple Implementation**: No backend changes required, works with existing REST API (spec 008)
- **Single-User Optimized**: Polling overhead minimal for single-user app (5 requests over 2 seconds)
- **Graceful Degradation**: If event dispatch fails, users can manually refresh
- **Framework Agnostic**: Custom events work across React components without prop drilling
- **Testable**: Easy to mock events and verify refresh behavior
- **Meets Performance Goals**: <500ms perceived latency via optimistic UI (SC-003)
- **No External Dependencies**: Uses native browser APIs (CustomEvent, setTimeout)
- **Stateless**: No persistent WebSocket connections to maintain

### Negative

- **Duplicate API Calls**: Up to 5 API requests within 2 seconds (acceptable for single-user)
- **Brief Inconsistency Window**: 400ms gaps between polls where state may be stale
- **Network Overhead**: More requests than ideal (mitigated by 400ms interval, not continuous)
- **No True Real-Time**: Not suitable for multi-user collaboration scenarios
- **Polling Waste**: Continues polling even if backend hasn't finished (acceptable trade-off)

## Alternatives Considered

**Alternative A: WebSocket Bi-Directional Communication**
- Components: WebSocket server endpoint, client connection management, reconnection logic, message parsing
- Why Rejected:
  - Requires backend changes (spec 008 doesn't support WebSocket, out of scope for spec 009)
  - Overkill for single-user app (WebSocket designed for multi-user real-time)
  - Adds complexity: connection management, reconnection logic, ping/pong heartbeats
  - Backend PostgreSQL + FastAPI already optimized for request/response (not streaming)
  - Implementation: ~12+ hours vs. 1 hour for polling (6x effort)

**Alternative B: Server-Sent Events (SSE)**
- Components: SSE endpoint streaming task updates, EventSource client, connection management
- Why Rejected:
  - Requires backend changes (new SSE endpoint, streaming response logic)
  - Half-duplex communication (server → client only), still need POST for chat
  - Browser connection limits (6 per domain), could block other features
  - Implementation: ~8 hours vs. 1 hour for polling (4x effort)
  - Spec 008 doesn't include SSE infrastructure

**Alternative C: React Context/Zustand Shared State**
- Components: Global state manager, task CRUD actions update shared store, chat + todo list subscribe
- Why Rejected:
  - Violates YAGNI principle (plan.md line 230: "No state management library added")
  - Doesn't eliminate API calls (still need to fetch after chat response)
  - Adds dependency and learning curve for team
  - Polling still needed to ensure backend sync (doesn't solve core problem)
  - Increases bundle size (Zustand: ~1kb, but adds complexity debt)

**Alternative D: Short Polling (1-2 second interval)**
- Components: Continuous polling at 1-2s intervals while chat is open
- Why Rejected:
  - Excessive API calls (30-60 requests per minute vs. 5 requests per operation)
  - Drains mobile battery (continuous background polling)
  - Violates SC-005 (60fps smoothness requirement - polling could cause jank)
  - Higher backend load (unnecessary requests when no operations happening)

**Alternative E: No Real-Time Updates (Manual Refresh Only)**
- Components: Button to manually refresh task list, or page reload
- Why Rejected:
  - Terrible UX (user must remember to refresh)
  - Violates FR-008 ("MUST show task operations reflected in both views in real-time")
  - Violates SC-003 (<500ms feedback requirement)
  - Not competitive with modern web applications

**Why Polling + Event Dispatch Chosen**:
Best balance of simplicity, performance, and UX for single-user MVP. Meets all functional requirements (FR-008, SC-003) without backend changes. Polling overhead is acceptable (5 requests over 2 seconds, only during active operations). Optimistic UI provides instant perceived feedback. Enables future migration to WebSocket/SSE without breaking changes (event dispatch pattern stays same, just remove polling logic).

## Implementation Details

**Polling Configuration:**
- Max attempts: 5
- Interval: 400ms
- Total window: 2 seconds (5 × 400ms)
- Trigger: After AI agent responds to chat message

**Why 400ms interval?**
- Balances responsiveness with API load
- Gives backend 400ms to complete operation (typical task CRUD: 50-200ms)
- 5 attempts cover edge cases (slow network, concurrent operations)
- Avoids overwhelming backend with sub-second requests

**Future Migration Path:**
If multi-user collaboration is added, migration is straightforward:
1. Backend: Add WebSocket endpoint emitting `task:updated` events
2. Frontend: Replace polling logic with WebSocket listener
3. Keep `window.dispatchEvent()` pattern unchanged
4. No changes needed in todo list components (still listen for same event)

## References

- Feature Spec: [specs/009-frontend-chat-integration/spec.md](../../specs/009-frontend-chat-integration/spec.md) (FR-008, SC-003, A-009)
- Research: [specs/009-frontend-chat-integration/research.md](../../specs/009-frontend-chat-integration/research.md) (Section 5: Real-time Updates Implementation)
- Implementation Plan: [specs/009-frontend-chat-integration/plan.md](../../specs/009-frontend-chat-integration/plan.md) (Line 231: Simplicity over WebSocket)
- Code: `frontend/components/chat/ChatPanel.tsx` (lines 309-328: polling implementation)
- Related ADRs: None
