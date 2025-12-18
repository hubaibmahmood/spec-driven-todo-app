---
id: 0004
title: Replace bulk delete with mark completed tool
stage: plan
date: 2025-12-18
surface: agent
model: claude-sonnet-4-5
feature: 006-mcp-server-integration
branch: 006-mcp-server-integration
user: developer
command: manual artifact update
labels: ["mcp", "tools", "api-design", "user-feedback"]
links:
  spec: specs/006-mcp-server-integration/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/006-mcp-server-integration/spec.md
 - specs/006-mcp-server-integration/plan.md
 - specs/006-mcp-server-integration/research.md
 - specs/006-mcp-server-integration/data-model.md
 - specs/006-mcp-server-integration/quickstart.md
 - specs/006-mcp-server-integration/contracts/mcp-tools.yaml
 - CLAUDE.md
tests:
 - None (planning phase artifact update)
---

## Prompt

User identified critical feature missing: Instead of bulk_delete_tasks, the MCP server should expose mark_task_completed as a dedicated tool. This is because marking tasks complete is a frequent, fundamental operation that deserves its own focused tool, separate from the general update_task tool.

Requirement: Update all planning artifacts using Option A (keep update_task for title/description/priority/due_date AND add dedicated mark_task_completed tool).

## Response snapshot

Successfully updated all planning artifacts to replace bulk_delete_tasks with mark_task_completed:

**Changes Applied**:

1. **spec.md**:
   - Replaced User Story 5 (bulk deletion P3) with mark_task_completed (P2 priority)
   - Updated FR-007 to clarify update_task excludes completion status
   - Updated FR-009 to define mark_task_completed tool
   - Updated Key Entities and Success Criteria

2. **plan.md**:
   - Updated summary and tool list
   - Updated project structure (tool filenames and test filenames)

3. **research.md**:
   - Added mark_task_completed example to tool description template
   - Updated summary to reflect 5 tools with mark_completed

4. **data-model.md**:
   - Updated UpdateTaskParams to remove completed field (added note)
   - Replaced BulkDeleteTasksParams and BulkDeleteResponse with MarkTaskCompletedParams
   - Added BackendCompletionUpdateRequest schema
   - Updated summary with tool separation notes

5. **contracts/mcp-tools.yaml**:
   - Updated update_task tool description and removed completed parameter
   - Replaced bulk_delete_tasks tool (Tool 5) with mark_task_completed
   - Updated backend_endpoints section with PATCH endpoint for mark_task_completed
   - Updated examples to reflect new tool behavior

6. **quickstart.md**:
   - Updated tool implementation list
   - Updated server.py registration code
   - Updated BackendClient to add mark_task_completed method
   - Removed bulk_delete_tasks references

7. **CLAUDE.md**:
   - Added recent change note about tool replacement

**Tool Design Rationale**:
- mark_task_completed: Simple, focused tool for common completion operation (uses PATCH /tasks/{id})
- update_task: Handles other field changes - title, description, priority, due_date (uses PUT /tasks/{id})
- Separation improves AI tool selection accuracy and user experience

## Outcome

- ✅ Impact: All planning artifacts updated consistently. Mark task completed is now a dedicated P2 tool. Update_task simplified to exclude completion status. MCP server design improved based on user feedback.
- 🧪 Tests: No tests executed (planning phase). Tool separation will require dedicated test files.
- 📁 Files: Updated 7 files (6 planning artifacts + CLAUDE.md)
- 🔁 Next prompts: Run /sp.tasks to generate updated task breakdown reflecting the new tool structure
- 🧠 Reflection: User feedback identified a critical UX issue - marking tasks complete is so common it deserves a dedicated tool rather than being buried in update_task. The change improves tool clarity and aligns with user mental models. Option A preserves update_task functionality for other fields while adding focused mark_task_completed tool.

## Evaluation notes (flywheel)

- Failure modes observed: Initial planning missed the importance of marking tasks complete as a standalone operation
- Graders run and results (PASS/FAIL): User review: FAIL (missing critical feature) → PASS after update
- Prompt variant (if applicable): User-driven refinement during planning phase
- Next experiment (smallest change to try): Validate that PATCH endpoint for completion works correctly with service authentication
