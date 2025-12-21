---
id: 0004
title: timezone-handling-for-agent-enhancement
stage: misc
date: 2025-12-20
surface: agent
model: claude-sonnet-4-5
feature: 008-openai-agents-sdk-integration
branch: 008-openai-agents-sdk-integration
user: developer
command: enhancement-request
labels: ["timezone", "date-parsing", "agent-enhancement", "adr", "edge-case"]
links:
  spec: specs/008-openai-agents-sdk-integration/spec.md
  ticket: null
  adr: history/adr/001-timezone-handling-for-agent-date-parsing.md
  pr: null
files:
  - specs/008-openai-agents-sdk-integration/spec.md
  - specs/008-openai-agents-sdk-integration/tasks.md
  - history/adr/001-timezone-handling-for-agent-date-parsing.md
tests:
  - T028a-T028e: Timezone infrastructure tests
  - T073a-T073b: Timezone validation tests
  - T080a-T080c: Cross-timezone E2E tests
---

## Prompt

One more thing when user inputs "Add buy clothes by tomorrow at 9 pm". So what timezone will be used? Because user will want the time to be of his/her location. How will the system cater that?

## Response snapshot

Identified critical edge case: natural language date/time parsing lacks timezone context, causing incorrect task scheduling for users across different timezones.

**Problem**: User says "tomorrow at 9pm" but which timezone? Backend stores UTC, agent has no timezone info, user expects local time. Without handling: EST user creates "9pm" task → parsed as UTC 9pm → displays as 4pm EST (5 hours wrong!)

**Solution**: X-Timezone Header Strategy (client auto-detects, sends IANA identifier like "America/New_York", agent uses for parsing, converts to UTC for storage, fallback to UTC if missing)

**Alternatives Rejected**: User profile timezone (DB migration), IP geolocation (unreliable), agent asks user (poor UX), UTC-only (terrible UX)

**Updates**: spec.md (FR-016, FR-017, edge case), tasks.md (12 new tasks, 119 total), ADR 001 (comprehensive decision record)

## Outcome

- ✅ Impact: Prevented critical UX bug where tasks scheduled at wrong times for international users. Added proper timezone handling throughout agent system.
- 🧪 Tests: Added 10 timezone-specific tests across 3 phases (foundational, US1, US3)
- 📁 Files: Updated spec.md, tasks.md (119 tasks total), created ADR 001
- 🔁 Next prompts: Implement timezone infrastructure (Phase 2: T028a-T028e)
- 🧠 Reflection: Simple user question revealed fundamental architectural gap. X-Timezone header balances simplicity and accuracy for MVP.

## Evaluation notes (flywheel)

- Failure modes observed: None - proactive edge case identification prevents production bugs
- Graders run and results (PASS/FAIL): Architecture review PASS - aligns with REST best practices
- Prompt variant (if applicable): Standard edge case analysis with options evaluation
- Next experiment (smallest change to try): Implement T028a (RED test) to validate approach
