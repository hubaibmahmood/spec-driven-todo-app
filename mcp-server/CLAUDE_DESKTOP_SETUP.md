# Claude Desktop MCP Server Configuration

This guide shows how to configure Claude Desktop to use the todo-app MCP server.

## Prerequisites

1. FastAPI backend running on `http://localhost:8000`
2. MCP server dependencies installed (`uv sync` in `mcp-server/`)
3. Environment variables configured (see `.env.example`)
4. SERVICE_AUTH_TOKEN generated and shared between backend and MCP server

## Configuration Steps

### 1. Locate Claude Desktop Configuration File

**macOS**:
```bash
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Windows**:
```bash
%APPDATA%\Claude\claude_desktop_config.json
```

**Linux**:
```bash
~/.config/Claude/claude_desktop_config.json
```

### 2. Add MCP Server Configuration

Edit the configuration file and add the todo-mcp-server:

```json
{
  "mcpServers": {
    "todo-mcp-server": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/todo-app/mcp-server",
        "run",
        "mcp-server"
      ],
      "env": {
        "SERVICE_AUTH_TOKEN": "your-32-char-service-token-here",
        "FASTAPI_BASE_URL": "http://localhost:8000",
        "MCP_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

**IMPORTANT**: Replace `/absolute/path/to/todo-app/mcp-server` with the actual absolute path on your system.

### 3. Generate SERVICE_AUTH_TOKEN

If you haven't already generated a service token:

```bash
# Generate a secure 32+ character token
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Add this token to:
1. `backend/.env` as `SERVICE_AUTH_TOKEN=<token>`
2. Claude Desktop config (as shown above)

### 4. Verify Backend is Running

Start the FastAPI backend:

```bash
cd backend
uv run uvicorn src.main:app --reload --port 8000
```

Verify it's accessible:
```bash
curl http://localhost:8000/health
# Should return: {"status": "ok"}
```

### 5. Restart Claude Desktop

1. Quit Claude Desktop completely
2. Restart Claude Desktop
3. The MCP server will start automatically when Claude Desktop launches

### 6. Verify MCP Server Connection

In Claude Desktop, you should see the MCP server tools available:

1. Open a new conversation
2. Type a message like "What tools do you have access to?"
3. Claude should list the 5 todo-app MCP tools:
   - `list_tasks`
   - `create_task`
   - `mark_task_completed`
   - `update_task`
   - `delete_task`

## User Context Configuration

The MCP server uses session-based user context. When you interact with Claude Desktop:

1. Claude Desktop provides user session information to the MCP server
2. The MCP server extracts `user_id` from the session metadata
3. The MCP server forwards this `user_id` to the backend via `X-User-ID` header
4. The backend filters all task operations by this `user_id`

**No additional configuration needed** - user context propagation is automatic!

## Testing the Integration

Try these commands in Claude Desktop:

1. **List tasks**:
   ```
   Show me my tasks
   ```

2. **Create task**:
   ```
   Add "Buy groceries" to my todo list with high priority
   ```

3. **Mark complete**:
   ```
   Mark task 1 as complete
   ```

4. **Update task**:
   ```
   Change task 2's priority to urgent
   ```

5. **Delete task**:
   ```
   Delete task 3
   ```

## Troubleshooting

### Tools Not Appearing

**Check Claude Desktop logs**:

**macOS**:
```bash
tail -f ~/Library/Logs/Claude/mcp*.log
```

**Common issues**:
- Incorrect absolute path in config
- MCP server dependencies not installed (`uv sync`)
- Python version incompatible (requires Python 3.12+)

### Authentication Errors

**Symptoms**: "Invalid service authentication token" errors

**Solutions**:
1. Verify `SERVICE_AUTH_TOKEN` matches in both:
   - `backend/.env`
   - Claude Desktop config
2. Ensure backend is running and accessible at `FASTAPI_BASE_URL`
3. Check backend logs for authentication failures

### Connection Errors

**Symptoms**: "Connection refused" or timeout errors

**Solutions**:
1. Verify FastAPI backend is running: `curl http://localhost:8000/health`
2. Check `FASTAPI_BASE_URL` in Claude Desktop config
3. Ensure no firewall blocking localhost connections
4. Check backend logs for errors

### Missing User Context

**Symptoms**: "Missing X-User-ID header" errors

**Solutions**:
1. Ensure you're testing with an authenticated user session
2. Check MCP server logs for user_id extraction
3. Verify Claude Desktop session is active

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SERVICE_AUTH_TOKEN` | ✅ Yes | - | Service-to-service auth token (32+ chars) |
| `FASTAPI_BASE_URL` | ✅ Yes | - | Backend URL (e.g., http://localhost:8000) |
| `MCP_LOG_LEVEL` | ❌ No | INFO | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `MCP_SERVER_PORT` | ❌ No | 3000 | MCP server port (usually auto-managed) |
| `BACKEND_TIMEOUT` | ❌ No | 30.0 | Request timeout in seconds |
| `BACKEND_MAX_RETRIES` | ❌ No | 2 | Number of retry attempts |

## Advanced Configuration

### Custom Logging

For debugging, set `MCP_LOG_LEVEL` to `DEBUG`:

```json
{
  "mcpServers": {
    "todo-mcp-server": {
      "env": {
        "MCP_LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

### Multiple Environments

You can configure different backends for different environments:

```json
{
  "mcpServers": {
    "todo-mcp-server-dev": {
      "command": "uv",
      "args": ["--directory", "/path/to/mcp-server", "run", "mcp-server"],
      "env": {
        "FASTAPI_BASE_URL": "http://localhost:8000"
      }
    },
    "todo-mcp-server-prod": {
      "command": "uv",
      "args": ["--directory", "/path/to/mcp-server", "run", "mcp-server"],
      "env": {
        "FASTAPI_BASE_URL": "https://api.example.com"
      }
    }
  }
}
```

## Security Notes

1. **Never commit** `claude_desktop_config.json` to version control
2. **Rotate** `SERVICE_AUTH_TOKEN` periodically
3. **Use HTTPS** for production `FASTAPI_BASE_URL`
4. **Restrict** backend API to trusted IPs in production
5. **Monitor** audit logs for suspicious activity

## Next Steps

After successful configuration:

1. Test all 5 MCP tools with Claude Desktop
2. Verify user data isolation (multiple users)
3. Review audit logs in MCP server and backend
4. Set up monitoring for production deployment

---

**For more information**:
- [MCP Server README](./README.md)
- [FastAPI Backend Docs](../backend/README.md)
- [Security Review](./SECURITY_REVIEW.md)
