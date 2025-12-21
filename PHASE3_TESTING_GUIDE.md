# Phase 3 Production Testing Guide
## OpenAI Agents SDK Integration with Gemini 2.5 Flash

### Prerequisites

- Python 3.12+
- uv package manager
- PostgreSQL database (Neon)
- Gemini API key from [Google AI Studio](https://ai.google.dev/)
- Valid session token for authentication

### Architecture

```
User (curl) → AI Agent (8002) → Gemini API
                  ↓
              PostgreSQL (conversations/messages)
                  ↓
           MCP Server (8001) → Backend (8000) → PostgreSQL (tasks)
```

### Quick Start Commands

```bash
# Terminal 1: Backend (port 8000)
cd backend && uv run uvicorn src.api.main:app --reload --port 8000

# Terminal 2: MCP Server (port 8001)
cd mcp-server && uv run python -m src.server

# Terminal 3: AI Agent (port 8002)
cd ai-agent && uv run uvicorn ai_agent.main:app --reload --port 8002
```

---

## Step 1: Configure Environment Variables

### 1.1 Backend Service (.env in backend/)

```bash
cd backend

# Create .env if it doesn't exist
cat > .env << 'EOF'
# Database
DATABASE_URL=postgresql+asyncpg://user:password@host:port/database?ssl=require

# Service Authentication
SERVICE_AUTH_TOKEN=generate_a_secure_32_char_token_here

# Application
ENV=development
LOG_LEVEL=INFO
EOF
```

### 1.2 MCP Server (.env in mcp-server/)

```bash
cd ../mcp-server

# Create .env (must match backend SERVICE_AUTH_TOKEN)
cat > .env << 'EOF'
# Must match backend/.env SERVICE_AUTH_TOKEN
SERVICE_AUTH_TOKEN=same_token_as_backend_here

# Backend URL
FASTAPI_BASE_URL=http://localhost:8000

# Server Configuration
MCP_LOG_LEVEL=INFO
MCP_SERVER_PORT=8001
BACKEND_TIMEOUT=30.0
BACKEND_MAX_RETRIES=2
EOF
```

### 1.3 AI Agent Service (.env in ai-agent/)

```bash
cd ../ai-agent

# Create .env
cat > .env << 'EOF'
# Database (same as backend for shared user_sessions table)
DATABASE_URL=postgresql+asyncpg://user:password@host:port/database?ssl=require

# Service Authentication
SERVICE_AUTH_TOKEN=same_token_as_backend_here

# Gemini API Configuration (requires AGENT_ prefix)
AGENT_GEMINI_API_KEY=your_actual_gemini_api_key_from_google_ai_studio

# MCP Server Configuration (requires AGENT_ prefix)
AGENT_MCP_SERVER_URL=http://localhost:8001/mcp
AGENT_MCP_TIMEOUT=10
AGENT_MCP_RETRY_ATTEMPTS=3

# Agent Configuration (requires AGENT_ prefix)
AGENT_TEMPERATURE=0.7
AGENT_TOKEN_BUDGET=800000
AGENT_ENCODING_NAME=cl100k_base
AGENT_SYSTEM_PROMPT=You are a helpful task management assistant. Use the available tools to help users manage their tasks.

# Application
ENV=development
LOG_LEVEL=INFO
EOF
```

**Important Notes:**
- Replace `DATABASE_URL` with your actual Neon PostgreSQL connection string
- Get your Gemini API key from https://ai.google.dev/
- Ensure all three services use the **same** `SERVICE_AUTH_TOKEN`
- Use `ssl=require` (not `sslmode=require`) for asyncpg

---

## Step 2: Database Setup

### 2.1 Run Backend Migrations

```bash
cd backend
uv sync
uv run alembic upgrade head
```

This creates:
- `users` table
- `user_sessions` table
- `tasks` table

### 2.2 Run AI Agent Migrations

```bash
cd ../ai-agent
uv sync
uv run alembic upgrade head
```

This creates:
- `conversations` table
- `messages` table

### 2.3 Get or Create a Test User Session Token

For testing, you need a valid session token. Query from database:

```bash
cd backend
uv run python -c "
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import select
from src.database.connection import engine
from src.models.database import UserSession

async def get_token():
    async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session_maker() as session:
        result = await session.execute(select(UserSession).limit(1))
        user_session = result.scalar_one_or_none()
        if user_session:
            print(f'Token: {user_session.token}')
            print(f'User ID: {user_session.user_id}')
        else:
            print('No session found. Please create one via auth-server.')

asyncio.run(get_token())
"
```

Save this token - you'll need it for all API calls.

---

## Step 3: Start All Services

Open **three separate terminal windows**:

### Terminal 1: Backend Service (Port 8000)

```bash
cd backend
uv run uvicorn src.api.main:app --reload --port 8000
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process...
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Terminal 2: MCP Server (Port 8001)

```bash
cd mcp-server
uv run python -m src.server
```

Expected output:
```
2025-12-21 - src.server - INFO - Registering MCP tools...
2025-12-21 - src.server - INFO - Registered tool: list_tasks
2025-12-21 - src.server - INFO - Registered tool: create_task
2025-12-21 - src.server - INFO - Registered tool: mark_task_completed
2025-12-21 - src.server - INFO - Registered tool: update_task
2025-12-21 - src.server - INFO - Registered tool: delete_task
2025-12-21 - src.server - INFO - MCP server initialized with 5 tools
2025-12-21 - src.server - INFO - Starting todo-mcp-server
```

### Terminal 3: AI Agent Service (Port 8002)

**Note:** We use port **8002** to avoid conflict with MCP server on 8001.

```bash
cd ai-agent
uv run uvicorn ai_agent.main:app --reload --port 8002
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8002 (Press CTRL+C to quit)
INFO:     Started reloader process...
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

---

## Step 4: Verify All Services Are Running

Open a **fourth terminal** for testing:

### 4.1 Test Backend Health

```bash
curl http://localhost:8000/health
```

Expected: `{"status":"healthy"}`

### 4.2 Test MCP Server Health

```bash
curl http://localhost:8001/health
```

Expected: MCP server health response (or 404 if no health endpoint)

### 4.3 Test AI Agent Health

```bash
curl http://localhost:8002/health
```

Expected: `{"status":"healthy","service":"ai-agent"}`

---

## Step 5: Production Testing with curl

### 5.1 Export Your Session Token

Replace with your actual token from Step 2.3:

```bash
export TOKEN="your_session_token_here"
```

### 5.2 Test 1: Basic Chat (Create Conversation)

```bash
curl -X POST http://localhost:8002/api/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "X-Timezone: America/New_York" \
  -d '{
    "message": "Hello, can you help me manage my tasks?"
  }' | jq '.'
```

**Expected Response:**
```json
{
  "conversation_id": 1,
  "user_message": "Hello, can you help me manage my tasks?",
  "assistant_message": "Hello! I'd be happy to help you manage your tasks. I can help you:\n\n- List all your tasks\n- Create new tasks with priorities and due dates\n- Update existing tasks\n- Mark tasks as complete\n- Delete tasks\n\nWhat would you like to do?"
}
```

**What This Tests:**
- ✅ AI Agent service is responding
- ✅ Gemini API connection works
- ✅ Conversation is created in database
- ✅ Messages are persisted

### 5.3 Test 2: Natural Language Task Creation

```bash
curl -X POST http://localhost:8002/api/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "X-Timezone: America/New_York" \
  -d '{
    "message": "Add an urgent task to finish the quarterly report by tomorrow at 5pm",
    "conversation_id": 1
  }' | jq '.'
```

**Expected Response:**
```json
{
  "conversation_id": 1,
  "user_message": "Add an urgent task to finish the quarterly report by tomorrow at 5pm",
  "assistant_message": "I've created the task 'Finish quarterly report' with urgent priority, due tomorrow at 5:00 PM."
}
```

**What This Tests:**
- ✅ Agent understands natural language intent
- ✅ MCP server connection works
- ✅ `create_task` tool is called correctly
- ✅ Priority extraction works ("urgent")
- ✅ Date/time parsing with timezone works
- ✅ Task is created in backend database
- ✅ Multi-turn conversation context maintained

### 5.4 Test 3: List Tasks

```bash
curl -X POST http://localhost:8002/api/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Show me all my tasks",
    "conversation_id": 1
  }' | jq '.'
```

**Expected Response:**
```json
{
  "conversation_id": 1,
  "user_message": "Show me all my tasks",
  "assistant_message": "Here are your tasks:\n\n1. Finish quarterly report (Priority: Urgent, Due: 2025-12-22 17:00)"
}
```

**What This Tests:**
- ✅ Agent calls `list_tasks` MCP tool
- ✅ Backend returns user-specific tasks
- ✅ Agent formats response nicely
- ✅ Context is maintained (conversation_id)

### 5.5 Test 4: Mark Task Complete (Ordinal Reference)

```bash
curl -X POST http://localhost:8002/api/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Mark the first task as complete",
    "conversation_id": 1
  }' | jq '.'
```

**Expected Response:**
```json
{
  "conversation_id": 1,
  "user_message": "Mark the first task as complete",
  "assistant_message": "I've marked 'Finish quarterly report' as completed."
}
```

**What This Tests:**
- ✅ Ordinal reference resolution ("the first task")
- ✅ Task context metadata from previous list operation
- ✅ `mark_task_completed` MCP tool works
- ✅ Backend updates task status

### 5.6 Test 5: Update Task

```bash
curl -X POST http://localhost:8002/api/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Create a task to review budget with high priority",
    "conversation_id": 1
  }' | jq '.'
```

Then update it:

```bash
curl -X POST http://localhost:8002/api/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Change that task priority to low",
    "conversation_id": 1
  }' | jq '.'
```

**What This Tests:**
- ✅ Multi-turn context ("that task" refers to previous message)
- ✅ `update_task` MCP tool works
- ✅ Priority update functionality

### 5.7 Test 6: Timezone Awareness

```bash
curl -X POST http://localhost:8002/api/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "X-Timezone: Asia/Tokyo" \
  -d '{
    "message": "Add a task to call John at 9am tomorrow"
  }' | jq '.'
```

**What This Tests:**
- ✅ X-Timezone header is respected
- ✅ "9am" is interpreted as 9am Tokyo time (JST)
- ✅ Time is correctly converted to UTC for storage

### 5.8 Test 7: Error Handling (Invalid Date)

```bash
curl -X POST http://localhost:8002/api/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Add a task due on February 30th"
  }' | jq '.'
```

**Expected Behavior:**
- Agent should recognize invalid date
- Agent should ask for clarification or reject the date

### 5.9 Test 8: Long Conversation (Context Management)

Create 10+ turns of conversation and verify:
- ✅ Token counting works
- ✅ Context window management (truncation at 80%)
- ✅ Conversation history is maintained

---

## Step 6: Verify Database State

### 6.1 Check Conversations Table

```bash
cd ai-agent
uv run python -c "
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import select
from ai_agent.database.connection import engine
from ai_agent.database.models import Conversation

async def show_conversations():
    async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session_maker() as session:
        result = await session.execute(select(Conversation))
        conversations = result.scalars().all()
        for conv in conversations:
            print(f'ID: {conv.id}, Title: {conv.title}, User: {conv.user_id}')

asyncio.run(show_conversations())
"
```

### 6.2 Check Messages Table

```bash
uv run python -c "
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import select
from ai_agent.database.connection import engine
from ai_agent.database.models import Message

async def show_messages():
    async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session_maker() as session:
        result = await session.execute(select(Message).limit(10))
        messages = result.scalars().all()
        for msg in messages:
            print(f'ID: {msg.id}, Role: {msg.role}, Content: {msg.content[:50]}...')

asyncio.run(show_messages())
"
```

### 6.3 Check Tasks Table (Backend)

```bash
cd ../backend
uv run python -c "
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import select
from src.database.connection import engine
from src.models.database import Task

async def show_tasks():
    async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session_maker() as session:
        result = await session.execute(select(Task))
        tasks = result.scalars().all()
        for task in tasks:
            print(f'ID: {task.id}, Title: {task.title}, Status: {task.status}, Priority: {task.priority}')

asyncio.run(show_tasks())
"
```

---

## Step 7: Performance Metrics

### 7.1 Response Time Testing

```bash
time curl -X POST http://localhost:8002/api/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "List my tasks"
  }' -o /dev/null -s
```

**Success Criteria (from spec SC-002):**
- Simple operations (list tasks): < 3 seconds
- Complex operations (create with parsing): < 10 seconds

### 7.2 Check Logs for Tool Calls

In the AI Agent terminal (Terminal 3), you should see logs like:

```
INFO: Tool call detected: list_tasks
INFO: Tool call detected: create_task with params: {"title": "...", "priority": "Urgent"}
INFO: Execution time: 2.3s, Tokens used: 450
```

---

## Troubleshooting

### Issue: 401 Unauthorized

**Cause:** Invalid or expired session token

**Solution:**
```bash
# Re-query token from database
cd backend
uv run python -c "..." # (see Step 2.3)

# Update TOKEN environment variable
export TOKEN="new_token_here"
```

### Issue: 503 Service Unavailable

**Cause:** Gemini API or MCP server not reachable

**Check:**
1. Verify AGENT_GEMINI_API_KEY is valid in ai-agent/.env
2. Check MCP server is running: `curl http://localhost:8001/health`
3. Check backend is running: `curl http://localhost:8000/health`
4. Review logs in each terminal

### Issue: Agent doesn't call MCP tools

**Cause:** MCP connection failed

**Debug:**
```bash
# Check AGENT_MCP_SERVER_URL in ai-agent/.env
cat ai-agent/.env | grep AGENT_MCP_SERVER_URL

# Should be: AGENT_MCP_SERVER_URL=http://localhost:8001/mcp

# Test MCP server directly (requires MCP client)
# Check mcp-server terminal for connection logs
```

### Issue: Tasks not created

**Cause:** Backend authentication or database issue

**Debug:**
```bash
# Check backend logs (Terminal 1)
# Check SERVICE_AUTH_TOKEN matches in all three .env files
diff <(grep SERVICE_AUTH_TOKEN backend/.env) \
     <(grep SERVICE_AUTH_TOKEN mcp-server/.env) \
     <(grep SERVICE_AUTH_TOKEN ai-agent/.env)
```

### Issue: Timezone not working

**Cause:** X-Timezone header not sent or invalid

**Solution:**
```bash
# Use valid IANA timezone
curl -H "X-Timezone: America/New_York" ...

# Check timezone_utils logs in ai-agent terminal
```

---

## Success Criteria Checklist

### Phase 3 Completion (User Story 1)

- [ ] All three services start without errors
- [ ] Health checks pass for all services
- [ ] Agent responds to basic chat queries
- [ ] Natural language task creation works
- [ ] Agent calls correct MCP tools (list, create, update, mark_completed)
- [ ] Priority extraction works ("urgent" → Priority.URGENT)
- [ ] Date/time parsing with timezone works
- [ ] Ordinal references work ("mark the first task complete")
- [ ] Multi-turn conversation context maintained
- [ ] Messages persisted to database
- [ ] Response time < 3s for simple operations
- [ ] Response time < 10s for complex operations
- [ ] Tool calls logged with metadata
- [ ] 52/54 tests pass (see README.md)

### Production Readiness

- [ ] Environment variables properly configured
- [ ] Database migrations applied successfully
- [ ] Service-to-service authentication working
- [ ] Error handling graceful (503 on failures)
- [ ] Logs show structured information
- [ ] No hardcoded secrets in code
- [ ] Connection pooling configured
- [ ] Rate limiting considered for Gemini API

---

## Next Steps

After Phase 3 testing is complete, consider:

1. **Phase 4:** Multi-turn conversation enhancements (User Story 2)
2. **Phase 5:** Advanced parsing and validation (User Story 3)
3. **Phase 6:** Batch operations (User Story 4)
4. **Phase 7:** Production polish (logging, metrics, security)

---

## Quick Reference

### Service Ports

- Backend: `http://localhost:8000`
- MCP Server: `http://localhost:8001/mcp`
- AI Agent: `http://localhost:8002`

### Key Endpoints

- AI Agent Chat: `POST http://localhost:8002/api/chat`
- Conversation History: `GET http://localhost:8002/api/conversations`
- Health Check: `GET http://localhost:8002/health`

### Environment Variables

| Service | Key Variable | Example |
|---------|-------------|---------|
| Backend | DATABASE_URL | `postgresql+asyncpg://...` |
| MCP | FASTAPI_BASE_URL | `http://localhost:8000` |
| AI Agent | AGENT_GEMINI_API_KEY | `AIza...` |
| AI Agent | AGENT_MCP_SERVER_URL | `http://localhost:8001/mcp` |
| All | SERVICE_AUTH_TOKEN | (same 32+ char token) |

---

## Support

For issues:
1. Check service logs in each terminal
2. Verify environment variables
3. Review database state
4. Check network connectivity between services
5. Consult specifications in `specs/008-openai-agents-sdk-integration/`
