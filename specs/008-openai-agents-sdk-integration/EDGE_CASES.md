# Edge Cases: OpenAI Agents SDK Integration

**Feature**: 008-openai-agents-sdk-integration
**Date**: 2025-12-20
**Purpose**: Comprehensive documentation of edge cases for natural language task management with AI agent

This document captures all identified edge cases for the OpenAI Agents SDK integration feature. Edge cases are organized by implementation status and priority.

---

## Implementation Status Legend

- ✅ **IMPLEMENTED**: Already in spec.md and tasks.md, ready for development
- 🚧 **IN SPEC**: Added to spec.md, awaiting task breakdown
- 📋 **DOCUMENTED**: Captured here for future implementation
- ⚠️ **NEEDS DECISION**: Requires architectural decision or user clarification

---

## Edge Case #1: "EOD" (End of Day) Ambiguity 🚧 IN SPEC

**Priority**: HIGH
**Status**: 🚧 Added to spec.md (FR-018)
**Affects**: User Story 3 (Intelligent Parsing), User Story 1 (Task Creation)

### Problem

When a user says "finish report by EOD" (End of Day), the system needs to determine:
- What time is "EOD"? (5pm business hours, 6pm, midnight?)
- Which timezone's EOD? (user's local time or UTC?)
- Does "EOD" mean end of business day or end of calendar day?

**Example Failure**:
```
User (EST): "urgent task: finish report by EOD"
→ Agent interprets EOD as UTC midnight → 2025-12-22T00:00:00Z
→ User sees: 7pm EST (expected midnight EST)
→ Task due 5 hours earlier than user intended!
```

### Solution

**Approach**: EOD = User's timezone midnight (23:59:59) by default, with configurable business hours option for future

**Implementation**:
1. **Default Interpretation**: EOD → 23:59:59 in user's timezone
2. **Agent System Prompt**:
   ```
   EOD (End of Day) Interpretation:
   - "by EOD", "EOD today" → 23:59:59 in user's timezone
   - "COB" (Close of Business) → 17:00:00 in user's timezone
   - "midnight" → 00:00:00 next day in user's timezone
   - Always convert to UTC before creating tasks
   ```
3. **Validation**: Agent confirms ambiguous times
   - "By EOD, I'll set the deadline to 11:59pm today in your timezone. Is that correct?"

**Future Enhancement**: User profile setting for business hours (e.g., user sets EOD = 5pm)

### References
- **Spec**: FR-018 (added 2025-12-20)
- **Tasks**: T077-T079 (agent prompt enhancement - update system prompt with EOD rules)
- **Related**: Edge Case #0 (Timezone handling) - requires timezone context

---

## Edge Case #2: "This Week" vs "Next Week" Boundary 🚧 IN SPEC

**Priority**: MEDIUM
**Status**: 🚧 Added to spec.md (FR-019)
**Affects**: User Story 4 (Batch Operations), User Story 1 (Task Filtering)

### Problem

Calendar week boundaries vary by culture and convention:
- Does the week start on Sunday (US) or Monday (ISO 8601)?
- If today is Saturday, does "this week" include today or only Mon-Fri?
- What is the boundary between "this week" and "next week"?

**Example Failure**:
```
Today: Saturday, Dec 21, 2025
User: "show me tasks due this week"
→ Agent uses Sunday-start week → includes Dec 15-21 (correct)
→ OR Agent uses Monday-start week → includes Dec 16-21 (misses Sunday tasks!)
```

### Solution

**Approach**: Use locale-based week start day with ISO 8601 as default

**Implementation**:
1. **Week Start Detection**:
   - Check `Accept-Language` header for locale (e.g., "en-US" → Sunday start, "en-GB" → Monday start)
   - Default to ISO 8601 (Monday start) if no locale provided
2. **Agent System Prompt**:
   ```
   Week Boundary Rules (ISO 8601 default):
   - Week starts: Monday (unless user locale specifies Sunday)
   - "this week" = current calendar week (Mon-Sun or Sun-Sat based on locale)
   - "next week" = following calendar week
   - "business week" = Monday-Friday of current week
   ```
3. **Clarification**: Agent asks if ambiguous
   - "By 'this week', do you mean the current calendar week (Dec 16-22) or just business days (Dec 16-20)?"

**Future Enhancement**: User profile setting for preferred week start day

### References
- **Spec**: FR-019 (added 2025-12-20)
- **Tasks**: T077-T079 (agent prompt enhancement), T080-T084 (validation tests)
- **Related**: Edge Case #0 (Timezone) - week boundaries respect user timezone

---

## Edge Case #3: Task ID References in Multi-Turn Conversations 🚧 IN SPEC

**Priority**: HIGH
**Status**: 🚧 Added to spec.md (FR-020)
**Affects**: User Story 2 (Multi-Turn Context), User Story 1 (Task Operations)

### Problem

When a user says "mark the first one as complete" after viewing a task list, the system must resolve:
- Does "first one" refer to the first task ID (e.g., ID 42) or the first position in the displayed list?
- What if the user opens a new conversation tab and references "the first task" without context?
- How long should the system remember which tasks were displayed?

**Example Failure**:
```
User: "show my urgent tasks"
Agent: "3 urgent tasks: 1. Buy milk (ID: 42), 2. Call dentist (ID: 55), 3. Finish report (ID: 101)"
User: "mark the first one as complete"
→ Agent doesn't remember task list context!
→ Agent asks: "Which task do you want to mark complete?"
→ User frustrated: "I JUST showed you the list!"
```

### Solution

**Approach**: Store displayed task list in conversation metadata with expiration

**Implementation**:
1. **Conversation Metadata Schema** (spec 007 Message.metadata field):
   ```json
   {
     "displayed_tasks": [
       {"position": 1, "id": 42, "title": "Buy milk"},
       {"position": 2, "id": 55, "title": "Call dentist"},
       {"position": 3, "id": 101, "title": "Finish report"}
     ],
     "displayed_at": "2025-12-20T14:30:00Z",
     "expires_after_turns": 5
   }
   ```
2. **Context Resolution Logic**:
   - When user says "first one", "second task", "last one" → resolve against `displayed_tasks`
   - If no recent display context (or expired) → agent asks for clarification
   - Expiration: 5 turns or 5 minutes, whichever comes first
3. **Agent Behavior**:
   - After showing task list, store metadata
   - When resolving ordinal references ("first", "second", "last"), check metadata
   - If ambiguous (multiple lists shown), use most recent
   - If expired, ask: "Which task? Please provide the task ID or title."

**Future Enhancement**: Support complex references like "the urgent one I mentioned earlier"

### References
- **Spec**: FR-020 (added 2025-12-20)
- **Tasks**: NEW TASKS NEEDED
  - T023a: Add displayed_tasks metadata schema to conversation models
  - T023b: Implement context storage after list operations
  - T023c: Implement context expiration logic (5 turns or 5 minutes)
  - T042c: Add ordinal reference resolution ("first one" → task ID lookup)
- **Related**: User Story 2 (Multi-Turn Context), Spec 007 (Message.metadata field)

---

## Edge Case #4: Priority Value Normalization 🚧 IN SPEC

**Priority**: MEDIUM
**Status**: 🚧 Added to spec.md (FR-021)
**Affects**: User Story 3 (Intelligent Parsing), User Story 1 (Task Creation)

### Problem

Users express priority in many natural language forms, but the backend API expects enum values:
- Valid backend values: `"Low"` | `"Medium"` | `"High"` | `"Urgent"`
- User says: "critical", "important", "ASAP", "whenever", "normal"
- Agent must map natural language → valid enum value

**Example Failure**:
```
User: "add a critical task to finish the presentation"
→ Agent sets priority: "Critical" (not in enum!)
→ MCP server validation error: Invalid priority value
→ Task creation fails
```

### Solution

**Approach**: Define priority mapping in agent system prompt with strict validation

**Implementation**:
1. **Priority Mapping Table** (Agent System Prompt):
   ```
   Priority Normalization (MUST use exact values):
   - "urgent", "critical", "asap", "immediately", "emergency" → "Urgent"
   - "high", "important", "significant", "key" → "High"
   - "normal", "regular", "standard", "medium" → "Medium"
   - "low", "whenever", "sometime", "eventually", "minor" → "Low"
   - Default (if not specified): "Medium"

   IMPORTANT: Only use exact enum values: "Urgent", "High", "Medium", "Low"
   ```
2. **Validation Before MCP Call**:
   - Agent service validates priority value against enum before calling create_task
   - If invalid (shouldn't happen with good prompt), default to "Medium" and log warning
3. **Confirmation for Unusual Mappings**:
   - If user says "critical" → agent confirms: "I'll set this as Urgent priority. Is that correct?"

**Future Enhancement**: User-defined priority keywords (custom mappings)

### References
- **Spec**: FR-021 (added 2025-12-20)
- **Tasks**: T077-T079 (update system prompt with priority mapping)
- **Related**: MCP server API contract (spec 006 - task priority enum)

---

## Edge Case #5: Duplicate Task Detection 📋 DOCUMENTED

**Priority**: LOW-MEDIUM
**Status**: 📋 Documented only (future enhancement)
**Affects**: User Story 3 (Intelligent Parsing), User Experience

### Problem

Users may unintentionally create duplicate tasks:
- User creates "buy groceries" at 2pm
- User forgets and says "remind me to buy groceries" at 3pm
- System creates a second identical task

**Example Failure**:
```
User (2pm): "add task to buy groceries"
Agent: "✓ Created task 'buy groceries'"
---
User (3pm): "remind me to buy groceries"
Agent: "✓ Created task 'buy groceries'"
→ User now has 2 identical tasks!
```

### Solution (Future)

**Approach**: Fuzzy duplicate detection with user confirmation

**Implementation** (when prioritized):
1. **Similarity Check**: Before creating task, check for similar existing tasks
   - Title similarity threshold: 80% (using Levenshtein distance or fuzzy matching)
   - Same due date (within 1 day)
   - Not already completed
2. **Agent Behavior**:
   - Finds similar task → "You already have a task 'buy groceries' due tomorrow. Do you want to update it or create a new one?"
   - User confirms → create new or update existing
3. **Performance**: Only check last 50 incomplete tasks (avoid slow queries)

**Why Deferred**:
- Not critical for MVP (users can manually delete duplicates)
- Adds complexity (fuzzy matching, query performance)
- Risk of false positives (blocking legitimate task creation)

### Future Implementation
- Add to User Story 3 (Intelligent Parsing) or Polish phase
- Estimate: 4-6 tasks (~2 hours)
- Requires: Fuzzy string matching library, optimized task queries

---

## Edge Case #6: Token Limit Mid-Conversation 📋 DOCUMENTED

**Priority**: MEDIUM
**Status**: 📋 Documented only (monitoring needed first)
**Affects**: User Story 2 (Multi-Turn Context), Long Conversations

### Problem

Long conversations (50+ turns) approach Gemini 2.5 Flash token limit:
- FR-014 implements token truncation (oldest messages dropped at 80% capacity)
- User references something from earlier in conversation ("the task I mentioned earlier")
- Context was truncated → agent can't fulfill request

**Example Failure**:
```
[After 60-turn conversation, tokens at 85% capacity]
User (turn 5): "remind me to call the dentist next Tuesday"
[System truncates messages 1-40 to stay under budget]
User (turn 61): "mark the dentist task as complete"
→ Agent: "I don't see any dentist task in our conversation. Can you provide the task ID?"
→ User: "You literally created it yourself earlier!"
```

### Solution (Future)

**Approach Option A**: Conversation summarization (deferred per research.md)
**Approach Option B**: Warn user before truncation + preserve key facts

**Implementation** (when prioritized):
1. **Warning at 70% Token Capacity**:
   - Agent: "This conversation is getting long. Important context may be lost soon. Consider starting a new conversation for complex tasks."
2. **Key Fact Preservation**:
   - Extract task IDs and titles from truncated messages
   - Store in conversation metadata: `{"preserved_tasks": [{"id": 42, "title": "call dentist"}]}`
   - Agent can reference preserved facts even after truncation
3. **Graceful Failure**:
   - If user references something not in context or metadata → agent apologizes and asks for clarification
   - Provide option: "Would you like me to search your tasks for 'dentist'?"

**Why Deferred**:
- Need real-world usage data to see if users hit this limit
- Summarization is complex (research.md marked as future)
- Current truncation strategy (FR-014) may be sufficient for MVP

### Future Implementation
- Monitor token usage in production
- Add to User Story 2 or Polish phase if needed
- Estimate: 8-10 tasks (~4 hours for warning + metadata, 15+ hours for summarization)

---

## Edge Case #7: Ambiguous Pronouns ("it", "that", "this") ✅ IMPLEMENTED

**Priority**: HIGH
**Status**: ✅ Already in spec.md Edge Cases section
**Affects**: User Story 1 (Task Creation), User Story 3 (Intelligent Parsing)

### Problem

User uses pronouns without clear antecedent:
- User: "I need to buy milk and call the dentist"
- User: "add it as a task"
- What is "it"? Buy milk? Call dentist? Both?

**Solution**: Already documented in spec.md edge cases
- Agent detects ambiguous pronouns and asks for clarification
- "I see you mentioned two things. Do you want to create a task for 'buy milk', 'call dentist', or both?"

### References
- **Spec**: Edge Cases section (line 120)
- **FR-007**: System MUST handle ambiguous queries by asking clarifying questions
- **Tasks**: Covered by existing US1 and US3 tasks

---

## Edge Case #0: Timezone Handling ✅ IMPLEMENTED

**Priority**: HIGH
**Status**: ✅ Fully implemented in spec.md, tasks.md, ADR-0001
**Affects**: All User Stories (any date/time parsing)

### Problem
User says "tomorrow at 9pm" but system doesn't know which timezone.

### Solution
X-Timezone header strategy with multi-layer fallback (see ADR-0001)

### References
- **ADR**: ADR-0001 (Timezone Handling for Agent Date Parsing)
- **Spec**: FR-016, FR-017, Edge Case (line 126)
- **Tasks**: T028a-T028e, T042a-T042b, T047a, T073a-T073b, T080a-T080c (12 tasks)

---

## Summary Table

| # | Edge Case | Priority | Status | Tasks Needed | Estimated Hours |
|---|-----------|----------|--------|--------------|-----------------|
| 0 | Timezone handling | HIGH | ✅ Implemented | 12 tasks (done) | ~3 hours |
| 1 | EOD ambiguity | HIGH | 🚧 In Spec | Update T077-T079 | ~0.5 hours |
| 2 | Week boundaries | MEDIUM | 🚧 In Spec | Update T077-T079 | ~0.5 hours |
| 3 | Task ID context | HIGH | 🚧 In Spec | 4 new tasks | ~2 hours |
| 4 | Priority normalization | MEDIUM | 🚧 In Spec | Update T077-T079 | ~0.5 hours |
| 5 | Duplicate detection | LOW-MED | 📋 Future | 4-6 tasks | ~2 hours |
| 6 | Token limit handling | MEDIUM | 📋 Future | 8-10 tasks | ~4 hours |
| 7 | Ambiguous pronouns | HIGH | ✅ In Spec | Covered by US1/US3 | N/A |

**Total Implemented**: 1 edge case (timezone)
**Total In Spec**: 4 edge cases (EOD, week boundaries, task ID context, priority normalization)
**Total Future**: 2 edge cases (duplicate detection, token limits)

---

## Testing Recommendations

### Edge Cases to Test in MVP (Priority: HIGH, Status: 🚧)

1. **EOD Time Interpretation**
   - Input: "finish by EOD"
   - Expected: Task due 23:59:59 in user's timezone (converted to UTC)
   - Test Scenarios: EST, PST, JST timezones

2. **Task ID Context Resolution**
   - Setup: Show task list with 3 tasks
   - Input: "mark the first one complete"
   - Expected: Agent resolves "first one" to first task ID from displayed list
   - Test Scenarios: Happy path, expired context (5+ turns later), no context

3. **Priority Normalization**
   - Input: "critical task to finish presentation"
   - Expected: Priority set to "Urgent" (valid enum value)
   - Test Scenarios: All natural language priority keywords → correct enum mapping

4. **Week Boundary Interpretation**
   - Input (Saturday): "show tasks due this week"
   - Expected: Respects user's locale week start (Sunday vs Monday)
   - Test Scenarios: en-US locale (Sunday), en-GB locale (Monday), no locale (ISO 8601)

### Future Edge Cases to Monitor

5. **Duplicate Detection**: Track user reports of duplicate tasks (decide if worth implementing)
6. **Token Limits**: Monitor conversation length in production (add warning if users hit limits)

---

## Implementation Priority

### Phase 1: MVP (Before Launch)
- ✅ Edge Case #0: Timezone handling (DONE)
- 🚧 Edge Case #1: EOD interpretation (UPDATE SYSTEM PROMPT)
- 🚧 Edge Case #3: Task ID context (ADD 4 TASKS)
- 🚧 Edge Case #4: Priority normalization (UPDATE SYSTEM PROMPT)

### Phase 2: Post-MVP (Monitor First)
- 📋 Edge Case #2: Week boundaries (may not be needed if users don't filter by week)
- 📋 Edge Case #5: Duplicate detection (add only if user complaints)
- 📋 Edge Case #6: Token limits (add only if users hit limits in production)

---

**Document Maintenance**: Update this file when new edge cases are discovered or implementation status changes.
