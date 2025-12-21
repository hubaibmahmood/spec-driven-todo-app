---
id: 0005
title: adr-recreation-and-edge-cases-1-4
stage: misc
date: 2025-12-20
surface: agent
model: claude-sonnet-4-5
feature: 008-openai-agents-sdk-integration
branch: 008-openai-agents-sdk-integration
user: developer
command: user-request
labels: ["adr", "edge-cases", "sp-adr-workflow", "EOD", "week-boundaries", "task-context", "priority-normalization"]
links:
  spec: specs/008-openai-agents-sdk-integration/spec.md
  ticket: null
  adr: history/adr/0001-timezone-handling-for-agent-date-parsing.md
  pr: null
files:
  - history/adr/0001-timezone-handling-for-agent-date-parsing.md
  - specs/008-openai-agents-sdk-integration/EDGE_CASES.md
  - specs/008-openai-agents-sdk-integration/spec.md
  - specs/008-openai-agents-sdk-integration/tasks.md
tests:
  - T023a-T023e: Task context metadata tests
  - T076a-T076c: Edge case validation tests
  - T083a-T083d: Edge case E2E tests
---

## Prompt

Recreate adr using sp.adr workflow (follows standard, uses template)
Add edge cases 1-4 but document all these edge cases in a file so I can look at them later on for either testing or implementing the remaining ones.

## Response snapshot

**1. ADR Recreation Using sp.adr Workflow** ✅

Properly recreated ADR-0001 following the official workflow:
- Used `create-adr.sh --title "Timezone Handling for Agent Date Parsing" --json`
- Filled template placeholders (not manual creation)
- Followed decision clustering approach (3 integrated components: client detection, backend resolution, agent prompt)
- Removed old manually created ADR (001-timezone-handling-for-agent-date-parsing.md)
- New ADR: 0001-timezone-handling-for-agent-date-parsing.md (proper format)

**2. Edge Cases Documentation** ✅

Created comprehensive EDGE_CASES.md with all 7 edge cases:
- Implementation status legend (✅ Implemented, 🚧 In Spec, 📋 Future)
- Detailed problem/solution for each edge case
- References to FRs, tasks, ADRs
- Test recommendations and priority matrix
- 2-phase implementation plan (MVP vs Post-MVP)

**3. Added Edge Cases 1-4 to spec.md** ✅

- Edge Case #1 (EOD): FR-018 (EOD = 23:59:59 user timezone, COB = 17:00)
- Edge Case #2 (Week Boundaries): FR-019 (locale-based week start)
- Edge Case #3 (Task ID Context): FR-020 (metadata storage, 5-turn/5-min expiration)
- Edge Case #4 (Priority Normalization): FR-021 (mapping table: critical→Urgent, important→High, etc.)

**4. Updated tasks.md** ✅

Added 13 new tasks (119 → 132 total):
- T023a-T023e: Task context metadata (Edge Case #3)
- T042c: Context resolution integration
- T076a-T076c: Edge case validation tests
- T083a-T083d: Edge case E2E tests
- Updated T077-T078: System prompt with EOD, week boundaries, priority mapping

**Summary by Edge Case**:
1. EOD interpretation → System prompt update (T077)
2. Week boundaries → System prompt update (T077)
3. Task ID context → 5 new foundational tasks + 1 integration task
4. Priority normalization → System prompt update (T077) + validation tests

**Updated Estimates**:
- MVP: 18-22 hours (was 17-21)
- Full feature: 30-38 hours (was 28-36)

## Outcome

- ✅ Impact: ADR now follows official sp.adr workflow. 4 critical edge cases fully integrated. Comprehensive edge case documentation created for future reference.
- 🧪 Tests: Added 7 new edge case tests (validation + E2E) across foundational and US3 phases
- 📁 Files: Recreated ADR-0001, created EDGE_CASES.md, updated spec.md (+4 FRs), updated tasks.md (+13 tasks)
- 🔁 Next prompts: Implement foundational tasks (Phase 2), review EDGE_CASES.md for future enhancements
- 🧠 Reflection: sp.adr workflow enforces decision clustering and template consistency. EDGE_CASES.md serves as living documentation for monitoring production issues and prioritizing future work.

## Evaluation notes (flywheel)

- Failure modes observed: Initial ADR was comprehensive but didn't follow sp.adr template/workflow (manual creation)
- Graders run and results (PASS/FAIL): Template compliance PASS - new ADR follows adr-template.md structure with decision clustering
- Prompt variant (if applicable): Standard sp.adr workflow (create-adr.sh → fill placeholders)
- Next experiment (smallest change to try): Execute Phase 2 foundational tasks to validate edge case implementations work as designed
