# ADR-0001: Timezone Handling for Agent Date Parsing

> **Scope**: This ADR documents the decision cluster for timezone-aware natural language date/time parsing in the AI agent, including client timezone detection, backend resolution strategy, and agent prompt enhancement.

- **Status:** Accepted
- **Date:** 2025-12-20
- **Feature:** 008-openai-agents-sdk-integration
- **Context:** Users interact with the AI agent using natural language expressions like "tomorrow at 9pm" or "add task by EOD". Without timezone context, the agent would parse times as UTC, causing incorrect task scheduling for international users (e.g., EST user creates "9pm" task → stored as UTC 9pm → displays as 4pm EST, 5 hours wrong).

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: YES - Long-term consequence for data accuracy and international UX
     2) Alternatives: YES - Multiple viable options (user profile, IP geolocation, conversational, header-based)
     3) Scope: YES - Cross-cutting concern affecting all date/time parsing in agent system
-->

## Decision

**Decision Cluster: X-Timezone Header Strategy with Multi-Layer Fallback**

This decision encompasses three integrated components:

1. **Client Timezone Detection**
   - Web/mobile clients auto-detect timezone using `Intl.DateTimeFormat().resolvedOptions().timeZone`
   - Clients send IANA timezone identifier (e.g., "America/New_York") in `X-Timezone` HTTP header
   - CLI clients detect system timezone or use config file setting

2. **Backend Timezone Resolution**
   - FastAPI `/api/chat` endpoint extracts `X-Timezone` header
   - Validation against IANA timezone database using Python `zoneinfo.available_timezones()`
   - Resolution priority: Header → UTC fallback (user profile deferred to future)
   - Invalid timezones logged and defaulted to UTC

3. **Agent Prompt Enhancement**
   - System prompt includes user timezone context with current time in user's timezone
   - Agent parses natural language dates/times in user's timezone
   - Agent converts all parsed datetimes to UTC before MCP tool calls
   - Example: "9pm America/New_York" → "2025-12-22T02:00:00Z"

## Consequences

### Positive

- **Accurate for All Users**: Client always knows the correct timezone (browser/device API), ensuring accurate parsing regardless of user location
- **Simple Implementation**: No database schema changes required, ~3 hours implementation time (12 tasks across 3 phases)
- **Works Immediately**: Auto-detected from browser/device APIs, no user configuration needed
- **Multi-Device Friendly**: Each device sends its own timezone (correct behavior for traveling users)
- **Graceful Degradation**: Falls back to UTC if header missing or invalid, with clear logging
- **Testable**: Easy to write E2E tests for different timezones (NYC, Tokyo, London) and DST scenarios
- **Standards-Based**: Uses IANA timezone identifiers (industry standard), Python zoneinfo (built-in since 3.9)
- **Meets Requirements**: Satisfies FR-016 (X-Timezone header acceptance), FR-017 (UTC conversion), SC-004 (90% parsing accuracy)

### Negative

- **Client Dependency**: Requires frontend/mobile clients to implement header sending (one-time effort per client)
- **CLI Complexity**: CLI tools need explicit timezone configuration or system detection
- **Header Spoofing**: Clients could send incorrect timezone (mitigated: only affects their own experience, not a security risk)
- **No Persistence**: Timezone not stored between sessions (must be sent with every request)
- **Potential Confusion**: Users on VPNs may have system timezone differ from physical location (rare edge case)

## Alternatives Considered

**Alternative Cluster A: User Profile Timezone (Database-Stored)**
- Components: Database migration (add users.timezone column), profile settings UI, backend lookup per request
- Why Rejected: Requires database schema changes (violates spec 008 constraint of no DB changes), over-engineering for MVP, user must manually configure, incorrect if user travels, adds database query overhead

**Alternative Cluster B: IP Geolocation-Based Detection**
- Components: IP extraction from request, geolocation service integration (e.g., MaxMind), timezone mapping
- Why Rejected: Unreliable (IP location ≠ user location, fails for VPNs/proxies), requires external service (cost, latency), privacy concerns (tracking user location), not accurate enough for time-sensitive parsing

**Alternative Cluster C: Conversational Timezone Detection**
- Components: Agent asks "What timezone are you in?" on first use, store in conversation metadata
- Why Rejected: Poor UX (interrupts task creation flow), must ask every new conversation, doesn't work for single-query mode, users may not know IANA timezone format

**Alternative Cluster D: UTC-Only (No Timezone Handling)**
- Components: Always interpret times as UTC, document that users must specify timezone explicitly
- Why Rejected: Terrible UX (users expect local time interpretation), violates FR-002 (accurate NL parsing), violates SC-004 (parsing accuracy requirement), not competitive with modern applications

**Why X-Timezone Header Chosen**: Best balance of accuracy, simplicity, and user experience for MVP. Aligns with REST API best practices (client provides context via headers). Enables future enhancements (user profile, smart detection) without blocking initial implementation.

## References

- Feature Spec: [specs/008-openai-agents-sdk-integration/spec.md](../../specs/008-openai-agents-sdk-integration/spec.md) (FR-016, FR-017, Edge Cases)
- Implementation Plan: [specs/008-openai-agents-sdk-integration/plan.md](../../specs/008-openai-agents-sdk-integration/plan.md)
- Tasks: [specs/008-openai-agents-sdk-integration/tasks.md](../../specs/008-openai-agents-sdk-integration/tasks.md) (T028a-T028e, T042a-T042b, T047a, T073a-T073b, T080a-T080c)
- Related ADRs: None (first ADR for this feature)
- Evaluator Evidence: [history/prompts/008-openai-agents-sdk-integration/0004-timezone-handling-for-agent-enhancement.misc.prompt.md](../prompts/008-openai-agents-sdk-integration/0004-timezone-handling-for-agent-enhancement.misc.prompt.md)
