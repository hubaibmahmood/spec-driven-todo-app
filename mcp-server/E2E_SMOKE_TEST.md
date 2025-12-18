# Manual End-to-End Smoke Test Guide

This guide provides step-by-step instructions for manually testing the todo-app MCP server with Claude Desktop.

## Prerequisites

- [ ] Claude Desktop installed and configured (see [CLAUDE_DESKTOP_SETUP.md](./CLAUDE_DESKTOP_SETUP.md))
- [ ] FastAPI backend running on http://localhost:8000
- [ ] MCP server configured in Claude Desktop
- [ ] User authenticated in Claude Desktop

## Test Environment Setup

### 1. Start Backend

```bash
cd backend
uv run uvicorn src.main:app --reload --port 8000
```

Verify backend health:
```bash
curl http://localhost:8000/health
# Expected: {"status": "ok"}
```

### 2. Verify Claude Desktop Configuration

Check that `claude_desktop_config.json` includes:
- Correct absolute path to mcp-server
- Valid SERVICE_AUTH_TOKEN
- FASTAPI_BASE_URL: http://localhost:8000

### 3. Restart Claude Desktop

1. Quit Claude Desktop completely
2. Restart Claude Desktop
3. Open a new conversation

---

## Test Suite

### Test 1: Tool Discovery ✅

**Objective**: Verify all 5 MCP tools are available to Claude

**Steps**:
1. In Claude Desktop, type:
   ```
   What MCP tools do you have access to?
   ```

**Expected Response**:
Claude should list 5 tools:
- ✅ `list_tasks` - List all tasks for authenticated user
- ✅ `create_task` - Create a new task
- ✅ `mark_task_completed` - Mark a task as completed
- ✅ `update_task` - Update task fields (title, description, priority, due_date)
- ✅ `delete_task` - Delete a task

**Pass Criteria**: All 5 tools listed with correct descriptions

---

### Test 2: List Tasks (Initially Empty) ✅

**Objective**: Verify `list_tasks` tool works and returns empty list for new user

**Steps**:
1. Type in Claude Desktop:
   ```
   Show me my tasks
   ```

**Expected Response**:
```
You currently have no tasks in your todo list.
```
or
```
Your task list is empty.
```

**Pass Criteria**:
- Claude successfully calls `list_tasks` tool
- Response indicates empty list
- No errors displayed

---

### Test 3: Create Task (Basic) ✅

**Objective**: Verify `create_task` tool creates a task

**Steps**:
1. Type in Claude Desktop:
   ```
   Add "Buy milk" to my todo list
   ```

**Expected Response**:
Claude should:
- Confirm task created
- Display task ID (1)
- Show title: "Buy milk"
- Show default priority: "Medium"
- Show completed: false

Example:
```
✅ I've added "Buy milk" to your todo list.

Task Details:
- ID: 1
- Title: Buy milk
- Priority: Medium
- Status: Not completed
```

**Pass Criteria**:
- Task created successfully
- Task ID assigned (1)
- Default values applied correctly

---

### Test 4: Create Task (With Options) ✅

**Objective**: Verify `create_task` accepts optional parameters

**Steps**:
1. Type in Claude Desktop:
   ```
   Add "Write report" with high priority and description "Q4 financial report" to my tasks
   ```

**Expected Response**:
```
✅ I've added "Write report" to your todo list.

Task Details:
- ID: 2
- Title: Write report
- Description: Q4 financial report
- Priority: High
- Status: Not completed
```

**Pass Criteria**:
- Task created with ID 2
- Title, description, and priority correctly set
- Optional fields properly handled

---

### Test 5: List Tasks (After Creation) ✅

**Objective**: Verify created tasks appear in list

**Steps**:
1. Type in Claude Desktop:
   ```
   Show me all my tasks
   ```

**Expected Response**:
Claude should list 2 tasks:

```
You have 2 tasks:

1. Buy milk
   - Priority: Medium
   - Status: Not completed

2. Write report
   - Description: Q4 financial report
   - Priority: High
   - Status: Not completed
```

**Pass Criteria**:
- Both tasks (1 and 2) displayed
- Task details match creation parameters
- Tasks persisted correctly (SC-002)

---

### Test 6: Mark Task Completed ✅

**Objective**: Verify `mark_task_completed` tool updates completion status

**Steps**:
1. Type in Claude Desktop:
   ```
   Mark task 1 as complete
   ```

**Expected Response**:
```
✅ I've marked "Buy milk" as completed!

Updated Task:
- ID: 1
- Title: Buy milk
- Status: ✅ Completed
```

**Pass Criteria**:
- Task 1 marked as completed
- Confirmation message displayed
- `updated_at` timestamp changed (SC-004)

---

### Test 7: Verify Completion in List ✅

**Objective**: Verify completion status reflected in list

**Steps**:
1. Type in Claude Desktop:
   ```
   Show my tasks
   ```

**Expected Response**:
```
You have 2 tasks:

1. Buy milk
   - Status: ✅ Completed

2. Write report
   - Description: Q4 financial report
   - Priority: High
   - Status: Not completed
```

**Pass Criteria**:
- Task 1 shows completed status
- Task 2 remains not completed
- Status change persisted (SC-003, SC-004)

---

### Test 8: Update Task Fields ✅

**Objective**: Verify `update_task` modifies task properties

**Steps**:
1. Type in Claude Desktop:
   ```
   Change task 2's priority to Urgent and update the description to "Q4 financial report - due Friday"
   ```

**Expected Response**:
```
✅ I've updated task 2.

Updated Details:
- ID: 2
- Title: Write report
- Description: Q4 financial report - due Friday
- Priority: Urgent
- Status: Not completed
```

**Pass Criteria**:
- Task 2 priority changed to "Urgent"
- Description updated
- Title unchanged
- `updated_at` timestamp changed (SC-003)

---

### Test 9: Verify Update in List ✅

**Objective**: Verify field updates reflected in list

**Steps**:
1. Type in Claude Desktop:
   ```
   List my tasks
   ```

**Expected Response**:
```
You have 2 tasks:

1. Buy milk
   - Status: ✅ Completed

2. Write report
   - Description: Q4 financial report - due Friday
   - Priority: Urgent
   - Status: Not completed
```

**Pass Criteria**:
- Task 2 shows updated priority and description
- Changes persisted correctly (SC-003)

---

### Test 10: Delete Task ✅

**Objective**: Verify `delete_task` removes task

**Steps**:
1. Type in Claude Desktop:
   ```
   Delete task 1
   ```

**Expected Response**:
```
✅ I've successfully deleted task 1 ("Buy milk") from your todo list.
```

**Pass Criteria**:
- Confirmation message displayed
- Task ID and title mentioned
- No errors

---

### Test 11: Verify Deletion in List ✅

**Objective**: Verify deleted task no longer appears

**Steps**:
1. Type in Claude Desktop:
   ```
   Show my tasks
   ```

**Expected Response**:
```
You have 1 task:

1. Write report
   - Description: Q4 financial report - due Friday
   - Priority: Urgent
   - Status: Not completed
```

**Pass Criteria**:
- Only task 2 remains (task 1 deleted)
- Task count reduced to 1
- Deletion persisted (SC-004)

---

### Test 12: AI-Friendly Error Handling ✅

**Objective**: Verify AI-friendly error messages

**Steps**:
1. Type in Claude Desktop:
   ```
   Delete task 999
   ```

**Expected Response**:
Claude should explain the error naturally:
```
I couldn't delete task 999 because it doesn't exist.

Your current tasks:
1. Write report

Would you like to delete a different task?
```

**Pass Criteria**:
- Error message is clear and actionable
- Claude provides context and suggestions
- No technical error codes exposed to user
- Error translation working (SC-008)

---

### Test 13: Natural Language Flexibility ✅

**Objective**: Verify AI understands varied phrasing

**Steps**:
Try different phrasings:

1. "What's on my todo list?"
2. "Can you create a task called 'Call dentist'?"
3. "I finished task 2"
4. "Make task 3 low priority"
5. "Remove the dentist task"

**Expected Behavior**:
Claude should correctly interpret and use appropriate tools for each command.

**Pass Criteria**:
- All natural language variants understood
- Correct tools called
- User intent satisfied

---

### Test 14: Complex Workflow ✅

**Objective**: Test real-world multi-step interaction

**Steps**:
1. "Add three tasks: 'Morning run', 'Team meeting', and 'Code review'"
2. "Make the team meeting high priority"
3. "I finished my morning run"
4. "Show my tasks"
5. "Delete the code review task"
6. "What tasks do I have left?"

**Expected Flow**:
- 3 tasks created (IDs 3, 4, 5)
- Task 4 priority updated to High
- Task 3 marked completed
- List shows all 3 tasks with correct statuses
- Task 5 deleted
- Final list shows 2 remaining tasks

**Pass Criteria**:
- All operations complete successfully
- State changes persist across operations
- Final state matches expectations

---

## Post-Test Verification

### Check Backend Logs

```bash
# Review backend logs for audit trail
tail -f backend/logs/uvicorn.log

# Look for:
# - Service authentication logs
# - Task CRUD operations
# - User context (X-User-ID headers)
# - No token exposure in logs
```

### Check MCP Server Logs

```bash
# macOS
tail -f ~/Library/Logs/Claude/mcp-todo-mcp-server.log

# Look for:
# - Tool invocations
# - User context extraction
# - Backend API calls with timing
# - No token exposure in logs
```

### Verify Database State

```bash
cd backend
uv run python -c "
from src.database.connection import get_db_sync
from src.database.models import Task

with get_db_sync() as db:
    tasks = db.query(Task).all()
    print(f'Total tasks: {len(tasks)}')
    for task in tasks:
        print(f'  - [{task.id}] {task.title} (completed: {task.completed})')
"
```

---

## Success Criteria Summary

All tests should pass with:
- ✅ All 5 tools functional
- ✅ Task persistence (SC-002)
- ✅ Field updates reflected (SC-003)
- ✅ Deletion/completion reflected (SC-004)
- ✅ AI-friendly error messages (SC-008)
- ✅ Natural language understanding
- ✅ Secure authentication (no token leaks)
- ✅ User data isolation (SC-001)

---

## Troubleshooting

### Issue: Tools Not Available

**Check**:
1. Claude Desktop config file path correct
2. MCP server started (check Claude Desktop logs)
3. No Python errors in MCP server logs

### Issue: Authentication Errors

**Check**:
1. SERVICE_AUTH_TOKEN matches in backend/.env and Claude config
2. Backend is running and accessible
3. Check backend logs for 401 errors

### Issue: Empty Responses

**Check**:
1. User context propagation (X-User-ID header)
2. Backend database connection
3. Task filtering by user_id working correctly

### Issue: Slow Responses

**Check**:
1. Backend response times (<2s requirement)
2. Network latency to backend
3. Database query performance

---

## Test Results Template

Copy this template to record your test results:

```markdown
## Test Execution Results

Date: _____________
Tester: _____________
Environment: _____________

| Test # | Test Name | Status | Notes |
|--------|-----------|--------|-------|
| 1 | Tool Discovery | ☐ PASS ☐ FAIL | |
| 2 | List Tasks (Empty) | ☐ PASS ☐ FAIL | |
| 3 | Create Task (Basic) | ☐ PASS ☐ FAIL | |
| 4 | Create Task (Options) | ☐ PASS ☐ FAIL | |
| 5 | List Tasks (After Creation) | ☐ PASS ☐ FAIL | |
| 6 | Mark Task Completed | ☐ PASS ☐ FAIL | |
| 7 | Verify Completion in List | ☐ PASS ☐ FAIL | |
| 8 | Update Task Fields | ☐ PASS ☐ FAIL | |
| 9 | Verify Update in List | ☐ PASS ☐ FAIL | |
| 10 | Delete Task | ☐ PASS ☐ FAIL | |
| 11 | Verify Deletion in List | ☐ PASS ☐ FAIL | |
| 12 | Error Handling | ☐ PASS ☐ FAIL | |
| 13 | Natural Language | ☐ PASS ☐ FAIL | |
| 14 | Complex Workflow | ☐ PASS ☐ FAIL | |

**Overall Result**: ☐ ALL PASS ☐ SOME FAILURES

**Issues Encountered**:
-

**Recommendations**:
-
```

---

**Next Steps After Successful Testing**:
1. Document any issues found
2. Update success criteria verification (T059)
3. Prepare for production deployment
4. Set up monitoring and alerting
