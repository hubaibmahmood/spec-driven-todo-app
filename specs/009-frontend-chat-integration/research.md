# Research Report: Frontend Chat Integration

**Feature**: 009-frontend-chat-integration
**Date**: 2025-12-21
**Phase**: 0 (Outline & Research)

## Purpose

This research document consolidates findings on technical decisions required to integrate OpenAI ChatKit SDK into the Next.js frontend for natural language task management. It resolves all "NEEDS CLARIFICATION" items from the Technical Context and evaluates alternatives for key implementation choices.

---

## Research Areas

### 1. OpenAI ChatKit SDK Integration with Next.js

**Decision**: Use `@openai/chatkit-react` package for React/Next.js integration

**Research Findings**:
- OpenAI provides official ChatKit SDK packages for multiple frameworks:
  - `@openai/chatkit-react`: React/Next.js integration (recommended)
  - `@openai/chatkit-web`: Vanilla JavaScript (not suitable for React apps)
  - `@openai/chatkit-core`: Low-level SDK (requires custom React bindings)

- **ChatKit React Package Features**:
  - `<ChatKit>` component: Pre-built chat UI with message rendering, input field, and auto-scroll
  - `useChatKit()` hook: Programmatic access to chat state, send messages, load history
  - Built-in support for streaming responses (if backend uses SSE)
  - TypeScript definitions included
  - Customizable styling via CSS classes or Tailwind

- **Compatibility Requirements**:
  - React 18+ (Next.js 13+ App Router or Pages Router)
  - Node.js 18+ (matches current backend)
  - TypeScript 5.x (optional but recommended)

- **Configuration**:
  ```typescript
  import { ChatKit } from '@openai/chatkit-react';

  <ChatKit
    url="https://your-backend.com/api/chat"  // POST /api/chat endpoint
    domainKey="your-domain-key"              // Authentication domain
    headers={{ 'X-Timezone': userTimezone }} // Custom headers
  />
  ```

**Alternatives Considered**:
1. **Build custom chat UI**: Rejected - reinvents the wheel, more maintenance
2. **Use third-party chat library (e.g., react-chat-widget)**: Rejected - not OpenAI-native, potential API incompatibility
3. **Use ChatGPT-like UI libraries**: Rejected - overkill for task management, not aligned with spec requirement to use OpenAI SDK

**Rationale**: The `@openai/chatkit-react` package is the official, maintained solution that integrates seamlessly with the existing OpenAI Agents SDK backend (spec 008). It reduces development time, provides TypeScript support, and aligns with the constraint to use OpenAI ChatKit SDK.

---

### 2. Session Token Management (better-auth Integration)

**Decision**: Retrieve session token from browser cookies or `useSession()` hook and include in API request headers

**Research Findings**:
- **better-auth Next.js Integration** (from spec 004):
  - Session tokens stored in HTTP-only cookies (most secure)
  - Client-side access via `useSession()` hook from `better-auth/react`
  - Token format: JWT or opaque session ID (depends on better-auth config)

- **ChatKit SDK Authentication**:
  - ChatKit `headers` prop allows custom headers on all requests
  - Common pattern: `Authorization: Bearer <session-token>`
  - Alternative: Send session cookie automatically (if same-domain)

- **Implementation Approach**:
  ```typescript
  import { useSession } from 'better-auth/react';

  const { session } = useSession();

  <ChatKit
    url="/api/chat"
    headers={{
      'Authorization': `Bearer ${session?.token}`,
      'X-Timezone': Intl.DateTimeFormat().resolvedOptions().timeZone
    }}
  />
  ```

**Alternatives Considered**:
1. **Rely on automatic cookie forwarding**: Rejected - doesn't work if backend is on different subdomain, less explicit
2. **Create separate chat authentication endpoint**: Rejected - violates constraint to reuse existing auth system
3. **Embed token in URL query params**: Rejected - security risk (token in URL logs)

**Rationale**: Using better-auth's `useSession()` hook provides explicit, type-safe access to the session token. Including it in the `Authorization` header is industry-standard and allows backend to validate requests using existing middleware (spec 004).

---

### 3. Timezone Detection and Handling

**Decision**: Use `Intl.DateTimeFormat().resolvedOptions().timeZone` for browser timezone detection, send via `X-Timezone` header

**Research Findings**:
- **Browser Timezone Detection**:
  - `Intl.DateTimeFormat().resolvedOptions().timeZone`: Returns IANA timezone (e.g., "America/New_York")
  - Supported in all modern browsers (Chrome, Firefox, Safari, Edge)
  - No external library required for detection

- **Date Parsing Libraries** (for displaying task due dates):
  - **date-fns**: Lightweight (20kb), tree-shakeable, immutable, TypeScript support
  - **date-fns-tz**: Timezone extension for date-fns (adds timezone conversion utilities)
  - **Luxon**: Full-featured (67kb), built-in timezone support, successor to Moment.js
  - **Day.js**: Minimalist (2kb), plugin-based, but timezone plugin adds complexity

- **Recommendation**: Use **date-fns + date-fns-tz**
  - Smaller bundle size than Luxon (important for frontend performance)
  - Well-maintained, widely adopted
  - Handles DST transitions correctly
  - Example:
    ```typescript
    import { formatInTimeZone } from 'date-fns-tz';

    const userTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
    formatInTimeZone(dueDate, userTimezone, 'MMM d, yyyy h:mm a'); // "Dec 22, 2025 3:00 PM"
    ```

**Alternatives Considered**:
1. **Luxon**: Rejected - larger bundle size (3x bigger than date-fns)
2. **Moment.js**: Rejected - deprecated, large bundle, mutable API
3. **Native Date + Intl API only**: Rejected - requires manual timezone offset calculations, error-prone

**Rationale**: date-fns is the modern standard for date manipulation in React apps. Browser's `Intl` API provides timezone detection for free. This combination is lightweight, reliable, and handles edge cases like DST.

---

### 4. Responsive Design Strategy

**Decision**: Use Tailwind CSS with mobile-first breakpoints (default: <768px full-screen, ≥768px side panel)

**Research Findings**:
- **Tailwind CSS Breakpoints** (default):
  - `sm: 640px` (small devices)
  - `md: 768px` (tablets/desktop - **use this for chat panel breakpoint**)
  - `lg: 1024px` (large desktop)
  - `xl: 1280px` (extra large)

- **Chat Panel Layout Patterns**:
  - **Mobile (<768px)**: Full-screen overlay with close button
    - Prevents layout issues on small screens
    - Ensures touch targets ≥44px (iOS Human Interface Guidelines)
    - Uses `fixed inset-0 z-50` positioning
  - **Desktop (≥768px)**: Side panel (300-400px wide)
    - Collapsible/expandable with animation
    - Uses `fixed right-0 top-0 h-screen` positioning
    - Main content shifts left when panel open

- **Animation Implementation**:
  ```typescript
  // Tailwind classes for smooth transitions
  className={`
    fixed transition-transform duration-300 ease-in-out
    md:right-0 md:w-96 md:translate-x-${isOpen ? '0' : 'full'}
    max-md:inset-0 max-md:translate-y-${isOpen ? '0' : 'full'}
  `}
  ```

**Alternatives Considered**:
1. **CSS Modules**: Rejected - less flexible than Tailwind utility classes
2. **Styled Components**: Rejected - adds runtime overhead, not already in project
3. **Fixed 480px breakpoint**: Rejected - 768px is industry standard (Bootstrap, Tailwind default)

**Rationale**: Tailwind CSS is likely already used in the Next.js app (common in modern projects). The 768px breakpoint aligns with the spec requirement and industry standards. Mobile-first approach ensures usability on smallest screens (320px minimum).

---

### 5. Real-time Updates Implementation

**Decision**: Use optimistic UI updates + polling for task list synchronization (no WebSocket for MVP)

**Research Findings**:
- **Spec Assumption A-009**: "Real-time updates refer to immediate UI updates after API responses, not WebSocket-based streaming"

- **Update Strategies**:
  1. **Optimistic UI**: Show task in todo list immediately when chat sends create request, confirm with API response
  2. **Polling**: Refresh task list every 5-10 seconds when chat is active
  3. **Server-Sent Events (SSE)**: Stream updates from backend - requires backend changes (out of scope)
  4. **WebSocket**: Bi-directional communication - overkill for single-user app

- **Recommendation**: **Optimistic UI + Context/State Sharing**
  - Chat component updates shared state (React Context or Zustand) after successful API call
  - Todo list component subscribes to state changes
  - No polling needed if state is shared properly
  - Fallback: Short polling (10s interval) if WebSocket not available

- **Implementation**:
  ```typescript
  // Shared task state context
  const { tasks, addTask } = useTaskContext();

  // In ChatPanel component
  const handleTaskCreated = async (newTask) => {
    addTask(newTask); // Optimistic update
    await chatApi.sendMessage(userInput); // Confirm with backend
  };
  ```

**Alternatives Considered**:
1. **WebSocket real-time sync**: Rejected - requires backend changes (spec 008 doesn't have WebSocket), overkill for single-user
2. **Short polling (1-2s)**: Rejected - excessive API calls, poor UX if network is slow
3. **No real-time updates**: Rejected - violates spec requirement for immediate feedback

**Rationale**: Optimistic UI provides instant feedback (meets <500ms requirement) while shared state eliminates need for complex WebSocket infrastructure. This is the simplest solution that satisfies the spec's real-time update requirement.

---

### 6. Conversation History Loading Strategy

**Decision**: Fetch last 50 messages on panel open, implement "Load More" button for pagination

**Research Findings**:
- **Spec Requirement FR-006**: "Load last 50 messages from conversation history when user opens chat panel, with 'Load More' button to fetch older messages in batches of 50"

- **Backend Endpoint** (from spec 007):
  - `GET /api/conversations/{conversation_id}/messages?limit=50&offset=0`
  - Supports pagination via `limit` and `offset` query params

- **Frontend Implementation**:
  ```typescript
  const [messages, setMessages] = useState<Message[]>([]);
  const [offset, setOffset] = useState(0);
  const [hasMore, setHasMore] = useState(true);

  const loadMessages = async () => {
    const response = await fetch(
      `/api/conversations/${conversationId}/messages?limit=50&offset=${offset}`
    );
    const data = await response.json();
    setMessages((prev) => [...data.messages, ...prev]); // Prepend older messages
    setHasMore(data.messages.length === 50); // If less than 50, no more to load
    setOffset((prev) => prev + 50);
  };
  ```

- **UX Pattern**:
  - Initial load: Last 50 messages (most recent at bottom)
  - User clicks "Load More" at top of chat → fetch next 50 older messages
  - Disable button when `hasMore === false`
  - Show loading spinner while fetching

**Alternatives Considered**:
1. **Infinite scroll**: Rejected - harder to implement with ChatKit SDK, less explicit for users
2. **Load all messages**: Rejected - performance risk with very long conversations (100+ messages)
3. **Load 20 messages**: Rejected - spec explicitly requires 50

**Rationale**: Pagination with "Load More" button is simple, performant, and meets the spec requirement. It prevents performance issues with long conversations while giving users full access to history.

---

### 7. Error Handling and Fallback UI

**Decision**: Display user-friendly error messages in chat, fallback to simple `<div>` if ChatKit SDK fails to load

**Research Findings**:
- **NFR-004**: "System MUST gracefully degrade if OpenAI ChatKit SDK fails to load"

- **Error Categories**:
  1. **ChatKit SDK load failure**: CDN down, network error, browser incompatibility
  2. **API request failure**: Backend down, 500 errors, network timeout
  3. **Authentication error**: Session expired, invalid token
  4. **Validation error**: User sends empty message, malformed input

- **Fallback UI Strategy**:
  ```typescript
  const ChatPanelWithFallback = () => {
    const [sdkLoaded, setSdkLoaded] = useState(true);

    useEffect(() => {
      // Detect if ChatKit SDK is available
      if (typeof window !== 'undefined' && !window.ChatKit) {
        setSdkLoaded(false);
      }
    }, []);

    if (!sdkLoaded) {
      return (
        <div className="p-4 bg-red-50 text-red-800">
          <p>Chat is temporarily unavailable. Please refresh the page or try again later.</p>
          <button onClick={() => window.location.reload()}>Reload</button>
        </div>
      );
    }

    return <ChatPanel />;
  };
  ```

- **Error Message Best Practices**:
  - **Specific**: "Failed to send message: Network error" (not "Something went wrong")
  - **Actionable**: "Session expired. Please log in again." (with login button)
  - **User-friendly**: Avoid technical jargon, explain in plain language

**Alternatives Considered**:
1. **Silent failure**: Rejected - users left confused, no recovery path
2. **Generic error page**: Rejected - doesn't explain what went wrong or how to fix it
3. **Retry with exponential backoff**: Considered but not in MVP - adds complexity

**Rationale**: Clear error messages with actionable recovery steps provide the best UX. Fallback UI ensures the app remains usable even if the ChatKit SDK fails, meeting the graceful degradation requirement.

---

### 8. Testing Strategy

**Decision**: TDD approach with component tests (Jest + RTL) and E2E tests (Playwright) written before implementation

**Research Findings**:
- **Constitution Requirement**: Test-first development (Red-Green-Refactor cycle)

- **Testing Layers**:
  1. **Component Tests** (Jest + React Testing Library):
     - Test individual chat components in isolation
     - Mock API calls, session tokens, timezone detection
     - Verify rendering, user interactions, state updates
     - Example:
       ```typescript
       test('ChatPanel sends message when user clicks send', async () => {
         const mockSendMessage = jest.fn();
         render(<ChatPanel onSendMessage={mockSendMessage} />);

         const input = screen.getByPlaceholderText('Type a message...');
         const sendButton = screen.getByRole('button', { name: /send/i });

         await userEvent.type(input, 'add task buy groceries');
         await userEvent.click(sendButton);

         expect(mockSendMessage).toHaveBeenCalledWith('add task buy groceries');
       });
       ```

  2. **E2E Tests** (Playwright):
     - Test full user workflows from browser perspective
     - Verify integration with backend, authentication, task list updates
     - Example:
       ```typescript
       test('User creates task via chat and sees it in task list', async ({ page }) => {
         await page.goto('/dashboard');
         await page.click('text=Open Chat');
         await page.fill('[placeholder="Type a message..."]', 'add task review PRs');
         await page.click('button:has-text("Send")');

         // Verify task appears in main task list
         await expect(page.locator('text=review PRs')).toBeVisible({ timeout: 5000 });
       });
       ```

- **Test Coverage Goals**:
  - Component tests: 80%+ coverage of chat components
  - E2E tests: All 6 user stories (P1 and P2) covered
  - Focus on critical paths: authentication, message sending, task creation, history loading

**Alternatives Considered**:
1. **Cypress instead of Playwright**: Rejected - Playwright is faster, better TypeScript support
2. **Skip E2E tests for MVP**: Rejected - violates constitution's integration test requirement
3. **Manual QA only**: Rejected - not sustainable, violates TDD principle

**Rationale**: TDD ensures correctness and prevents regressions. Component tests provide fast feedback during development. E2E tests validate the full user experience and catch integration issues. This aligns with the constitution's test-first mandate.

---

## Summary of Key Decisions

| Decision Area | Choice | Rationale |
|---------------|--------|-----------|
| **ChatKit SDK** | @openai/chatkit-react | Official React integration, TypeScript support, pre-built UI |
| **Session Auth** | better-auth `useSession()` hook | Type-safe, explicit, reuses existing auth (spec 004) |
| **Timezone** | Intl API + date-fns-tz | Lightweight, reliable, handles DST correctly |
| **Responsive Design** | Tailwind CSS (768px breakpoint) | Industry standard, mobile-first, smooth animations |
| **Real-time Updates** | Optimistic UI + shared state | Simple, meets <500ms requirement, no backend changes |
| **History Loading** | 50 messages + "Load More" pagination | Performant, meets spec requirement, clear UX |
| **Error Handling** | User-friendly messages + fallback UI | Graceful degradation, actionable recovery steps |
| **Testing** | Jest + RTL (component) + Playwright (E2E) | TDD compliance, fast feedback, full coverage |

---

## Open Questions / Future Considerations

1. **ChatKit SDK Compatibility**: Need to verify `@openai/chatkit-react` works with current Next.js version (test in isolated environment before Phase 1)
2. **State Management Library**: If app grows, consider Zustand or Redux for shared task state (currently using React Context)
3. **Accessibility**: Ensure WCAG 2.1 AA compliance (keyboard nav, screen reader, color contrast) - add to test checklist
4. **Analytics**: Track chat usage metrics (messages sent, task operations, error rates) - defer to post-MVP

---

**Next Steps**: Proceed to Phase 1 (Design & Contracts) to create data models, API contracts, and quickstart guide.
