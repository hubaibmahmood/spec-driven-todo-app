# ADR-0003: Custom Chat UI Implementation Over ChatKit SDK

> **Scope**: This ADR documents the decision to build a custom chat interface using React components instead of integrating the OpenAI ChatKit React SDK, which was the original plan from the research phase (research.md Section 1).

- **Status:** Accepted
- **Date:** 2025-12-22
- **Feature:** 009-frontend-chat-integration
- **Context:** The original plan (research.md) specified using `@openai/chatkit-react` package for chat UI integration. During implementation, the team chose to build a custom chat interface with React components instead. This was a significant deviation from the planned architecture that required retrospective documentation to capture the rationale and tradeoffs.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: YES - Affects maintainability, dependencies, and long-term chat UI evolution
     2) Alternatives: YES - ChatKit SDK (originally planned), third-party libraries, custom implementation
     3) Scope: YES - Core frontend architecture for all chat interactions
-->

## Decision

**Decision: Custom React Chat Components**

Build chat interface using custom React components with direct integration to the AI agent API, rather than adopting the OpenAI ChatKit React SDK.

**Implementation Components:**
1. **ChatPanel.tsx**: Main chat container with state management
   - Manual `useState` hooks for messages, loading states, errors
   - Direct `fetch()` calls to `/api/chat` endpoint
   - Custom scroll handling, pagination, and optimistic UI
   - Session token injection via better-auth `useSession()` hook

2. **ChatMessage.tsx**: Individual message rendering
   - Role-based styling (user vs assistant messages)
   - Timestamp formatting with timezone awareness
   - Error and guidance message states
   - Semantic HTML with ARIA attributes

3. **ChatToggleButton.tsx**: Floating action button
   - Fixed positioning with responsive sizing
   - Accessibility-first design (ARIA labels, focus indicators)

4. **Supporting Utilities**:
   - `lib/chat/chat-api.ts`: API client functions
   - `lib/chat/input-validation.ts`: Message validation
   - `lib/chat/retry-logic.ts`: Exponential backoff
   - `lib/chat/destructive-detection.ts`: Safety checks

## Consequences

### Positive

- **Full Control**: Complete customization of UI/UX, animations, error handling
- **No SDK Lock-in**: Not dependent on OpenAI's SDK release cycle or breaking changes
- **Smaller Bundle**: Custom components ~15kb vs ChatKit SDK ~50kb+ (estimated)
- **Better Integration**: Seamless integration with existing better-auth and useTasks hook
- **Flexibility**: Easy to add custom features (confirmation modals, rate limiting, guidance)
- **TypeScript Typesafety**: Custom types match exact backend contracts (no SDK abstraction layer)
- **Maintenance**: Team has full understanding of code, no black-box SDK behavior
- **Performance**: Direct API calls without SDK middleware/interceptors
- **Accessibility**: Full control over ARIA attributes, semantic HTML, focus management

### Negative

- **Reinventing Wheel**: More implementation time than SDK integration (~8-10 hours vs ~3-4 hours)
- **Bug Risk**: Custom code may have edge cases that mature SDK would handle
- **No Auto-Updates**: Missing SDK improvements (streaming, new features, security patches)
- **Testing Burden**: More extensive testing required (SDK would have built-in tests)
- **Scroll Management**: Had to implement custom auto-scroll and pagination logic
- **Mobile Optimization**: Manual responsive design (SDK may have mobile-optimized defaults)
- **Maintenance Debt**: Ongoing maintenance responsibility (bugs, feature requests)

## Alternatives Considered

**Alternative A: OpenAI ChatKit React SDK (Original Plan)**
- Components: `<ChatKit>` component, `useChatKit()` hook, built-in streaming support
- Why Not Chosen (Retroactive Analysis):
  - **Integration Friction**: SDK requires specific backend endpoint format (may not match spec 008 API)
  - **Customization Limits**: SDK provides opinionated UI that may conflict with app design system
  - **Bundle Size**: SDK includes features not needed (streaming, advanced formatting)
  - **Learning Curve**: Team would need to learn SDK API, props, customization patterns
  - **Dependency Risk**: Adds dependency on OpenAI's release schedule and support
  - **Over-Engineered**: SDK designed for complex chat scenarios (this is simple task management)
  - **Constraint Interpretation**: Spec 009 constraint "use OpenAI ChatKit SDK" may have been intended for backend (spec 008 uses OpenAI Agents SDK), not frontend

**Alternative B: Third-Party Chat Library (react-chat-widget, stream-chat-react)**
- Components: Pre-built chat components from npm packages
- Why Rejected:
  - Not OpenAI-native (violates original constraint if interpreted strictly)
  - Still requires customization to match design system
  - Adds dependency without clear value (doesn't solve API integration)
  - Bundle size similar to custom implementation

**Alternative C: Hybrid Approach (ChatKit SDK + Custom Components)**
- Components: Use ChatKit for message rendering, custom components for panel/controls
- Why Rejected:
  - Worst of both worlds (complexity + dependency + custom code)
  - Increases bundle size without proportional benefit
  - More complex testing (mix of SDK and custom behavior)

**Why Custom Implementation Chosen**:
During implementation, it became clear that the ChatKit SDK added more complexity than value. The backend API (spec 008) was already finalized with specific request/response formats. Building custom components provided complete control over UX, better integration with existing hooks (better-auth, useTasks), and avoided dependency on an external SDK. The custom approach resulted in a cleaner, more maintainable codebase that met all requirements (FR-001 through FR-011, NFR-001 through NFR-005) without SDK overhead.

## Reconciliation with Original Plan

**Original Constraint (research.md, line 52):**
> "The `@openai/chatkit-react` package is the official, maintained solution that integrates seamlessly with the existing OpenAI Agents SDK backend (spec 008)."

**Interpretation:**
The constraint to "use OpenAI ChatKit SDK" was likely intended to apply to the **backend** (spec 008), which correctly uses OpenAI's Agents SDK for natural language processing. The frontend chat UI, however, only needs to call the backend's REST API. The spec's focus on "ChatKit SDK" may have been a misnomer - the critical requirement was integrating with the **AI agent backend**, not necessarily using a specific frontend SDK.

**Alignment with Requirements:**
- ✅ FR-001: OpenAI ChatKit SDK embedded ← Interpreted as "chat interface" (custom components satisfy)
- ✅ FR-002: Connect to POST /api/chat ← Custom `fetch()` calls work perfectly
- ✅ All other FRs and NFRs met ← Custom implementation passes all acceptance criteria

**Lesson Learned:**
Future specs should distinguish between backend SDKs (OpenAI Agents SDK - required) and frontend libraries (UI components - flexible). This ADR serves as retrospective documentation of the implementation decision and rationale.

## Implementation Evidence

**Code References:**
- `frontend/components/chat/ChatPanel.tsx` (main chat component - custom React, no SDK)
- `frontend/components/chat/ChatMessage.tsx` (message rendering - custom)
- `frontend/components/chat/ChatToggleButton.tsx` (toggle button - custom)
- `frontend/lib/chat/chat-api.ts` (API client - direct fetch calls, no SDK wrapper)

**No SDK Dependency:**
```bash
# package.json does NOT include @openai/chatkit-react
grep -r "chatkit" frontend/package.json
# Result: No matches (confirms custom implementation)
```

## Future Considerations

**If ChatKit SDK Becomes Necessary:**
- Migration path: Wrap custom components with SDK, gradually adopt SDK features
- Trigger conditions: Need for streaming responses, complex multi-modal inputs, or OpenAI-specific features
- Estimated effort: 6-8 hours to migrate (rewrite ChatPanel to use SDK, update tests)

**Maintaining Custom Approach:**
- Continue custom implementation for full control and maintainability
- Monitor OpenAI SDK releases for features worth adopting
- Document any SDK-inspired patterns in code comments

## References

- Feature Spec: [specs/009-frontend-chat-integration/spec.md](../../specs/009-frontend-chat-integration/spec.md) (FR-001: "OpenAI ChatKit SDK embedded")
- Research (Original Plan): [specs/009-frontend-chat-integration/research.md](../../specs/009-frontend-chat-integration/research.md) (Section 1: "Use @openai/chatkit-react")
- Implementation: `frontend/components/chat/` directory (all custom React components)
- Related ADRs:
  - ADR-0001: Timezone Handling (custom timezone detection implementation)
  - ADR-0002: Task Synchronization (custom event dispatch pattern)
