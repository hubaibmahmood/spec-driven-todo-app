# Testing the MCP Server

## ✅ Prerequisites

1. **FastAPI Backend Running**
   ```bash
   cd backend
   uv run uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Environment Configuration**
   - Ensure `mcp-server/.env` has correct `SERVICE_AUTH_TOKEN` (must match `backend/.env`)
   - Backend URL should be `http://localhost:8000`

## 🧪 Automated Testing

Run the test script to verify both tools work:

```bash
cd mcp-server
uv run python test_mcp_server.py
```

**Expected Output:**
- ✅ List tasks (retrieves user's tasks)
- ✅ Create task (creates new task with validation)
- ✅ Validation errors (handles empty title gracefully)
- ✅ List tasks again (shows newly created task)

## 🤖 Testing with Claude Desktop

### Step 1: Configure Claude Desktop

Add the MCP server to your Claude Desktop configuration file:

**macOS/Linux:** `~/Library/Application Support/Claude/claude_desktop_config.json`

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "todo-mcp-server": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/mac/Documents/PIAIC/speckit plus/todo-app/mcp-server",
        "run",
        "mcp-server"
      ],
      "env": {
        "SERVICE_AUTH_TOKEN": "dOQqrfQZH7DtQhAeEoKzwPo3DkvfqB2p-OxRuwXN3uk",
        "FASTAPI_BASE_URL": "http://localhost:8000",
        "MCP_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

**Important:** Update the `--directory` path to match your project location.

### Step 2: Restart Claude Desktop

Close and reopen Claude Desktop for the configuration to take effect.

### Step 3: Verify Tools are Available

In Claude Desktop, you should see the MCP server tools available:
- 🔍 **list_tasks** - List all tasks for authenticated user
- ➕ **create_task** - Create new task with validation

### Step 4: Test with Natural Language

Try these commands in Claude Desktop:

```
1. "Show me my tasks"
   → Should call list_tasks tool

2. "Add 'buy milk' to my todo list"
   → Should call create_task tool

3. "Create a high priority task: Complete project report, due December 31st"
   → Should create task with priority and due date

4. "What tasks do I have?"
   → Should list all tasks including newly created ones
```

## 🔍 Available Tools

### 1. **list_tasks**
Retrieves all tasks for the authenticated user.

**Parameters:** None (uses user context from session)

**Returns:**
- Success: Array of task objects
- Error: Error object with type, message, and suggestions

**Example Response:**
```json
[
  {
    "id": 1,
    "title": "Buy milk",
    "description": "Get 2% milk from store",
    "completed": false,
    "priority": "Medium",
    "due_date": null,
    "created_at": "2025-12-18T10:00:00Z",
    "updated_at": "2025-12-18T10:00:00Z",
    "user_id": "test_user_123"
  }
]
```

### 2. **create_task**
Creates a new task for the authenticated user.

**Parameters:**
- `title` (required): Task title (1-200 characters)
- `description` (optional): Task description
- `priority` (optional): "Low", "Medium", "High", or "Urgent" (default: "Medium")
- `due_date` (optional): ISO 8601 date format (e.g., "2025-12-31T23:59:59Z")

**Returns:**
- Success: Created task object with ID and timestamps
- Validation Error: Detailed field-level errors with suggestions
- Error: Error object with type, message, and suggestions

**Example Response:**
```json
{
  "id": 2,
  "title": "Complete project report",
  "description": "Q4 2025 report with charts",
  "completed": false,
  "priority": "High",
  "due_date": "2025-12-31T23:59:59Z",
  "created_at": "2025-12-18T11:00:00Z",
  "updated_at": "2025-12-18T11:00:00Z",
  "user_id": "test_user_123"
}
```

## 🐛 Troubleshooting

### Issue: "Service authentication failed"
**Solution:** Verify `SERVICE_AUTH_TOKEN` matches between `mcp-server/.env` and `backend/.env`

### Issue: "Unable to connect to backend service"
**Solution:**
1. Check FastAPI backend is running: `curl http://localhost:8000/health`
2. Verify `FASTAPI_BASE_URL` in `mcp-server/.env` is correct

### Issue: "Missing user context in session"
**Solution:** This indicates the MCP client is not providing user_id in the session context. For testing, modify the test script to include the user_id.

### Issue: Tools not showing in Claude Desktop
**Solution:**
1. Check Claude Desktop config file path is correct
2. Verify JSON syntax is valid
3. Restart Claude Desktop
4. Check Claude Desktop logs for MCP server errors

## 📊 Test Coverage

### Unit Tests (mcp-server/tests/unit/)
- ✅ BackendClient.get_tasks (8 tests)
- ✅ BackendClient.create_task (5 tests)

### Integration Tests (mcp-server/tests/integration/)
- ✅ list_tasks tool (6 tests)
- ✅ create_task tool (6 tests)

### Contract Tests (mcp-server/tests/contract/)
- ✅ TaskResponse schema (7 tests)
- ✅ CreateTaskParams schema (8 tests)
- ✅ PriorityLevel enum (2 tests)

### Backend Tests (backend/tests/integration/)
- ✅ Service authentication (7 tests)

**Total: 49 tests passing**

## 🎯 MVP Features Tested

1. ✅ **User Authentication** - Service token + X-User-ID header
2. ✅ **Task Retrieval** - List all tasks for authenticated user
3. ✅ **Task Creation** - Create tasks with validation
4. ✅ **Data Isolation** - Users can only see their own tasks
5. ✅ **Input Validation** - Field-level errors with helpful suggestions
6. ✅ **Error Handling** - Timeout, connection, authentication errors
7. ✅ **Retry Logic** - Exponential backoff on failures

## 🚀 Next Steps

After MVP testing is successful, you can:
1. Implement User Story 5 (mark_task_completed)
2. Implement User Story 3 (update_task)
3. Implement User Story 4 (delete_task)
4. Deploy to production
5. Configure for real users with better-auth integration
