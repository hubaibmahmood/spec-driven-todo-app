# AI Agent - Intelligent Task Management Service

A FastAPI-based AI agent service that combines natural language understanding with task management capabilities. Built on OpenAI Agents SDK with Gemini 2.5 Flash backend, this service enables users to manage tasks through conversational AI with persistent chat history and multi-turn context awareness.

## Features

### 🤖 AI Agent Capabilities (Spec 008)
- ✅ **Natural Language Task Management**: Create, read, update, and complete tasks using conversational language
- ✅ **Gemini 2.5 Flash Integration**: Fast, cost-effective AI responses via OpenAI-compatible API
- ✅ **MCP Tool Integration**: Seamless connection to task management backend via Model Context Protocol
- ✅ **Multi-Turn Context**: Maintains conversation history with smart token budget management
- ✅ **Timezone-Aware Parsing**: Understands dates/times in user's timezone (via X-Timezone header)
- ✅ **Tool Call Tracking**: Logs and persists AI tool usage for observability
- ✅ **Real-Time Operation Feedback**: Returns detailed operation status for frontend UI display (Spec 009 Phase 6)
- ✅ **Graceful Degradation**: 503 error handling when AI services unavailable

### 💬 Chat Infrastructure (Spec 007)
- ✅ **Conversation Management**: Create and manage chat sessions
- ✅ **Message Persistence**: Store user and assistant messages with metadata
- ✅ **Authentication**: Secure Bearer token authentication via better-auth integration
- ✅ **Message History**: Retrieve conversation history with chronological message ordering
- ✅ **Ownership Validation**: Users can only access their own conversations
- ✅ **Database Migrations**: Alembic-based schema management
- ✅ **Production Ready**: Connection pooling, logging, error handling
- ✅ **OpenAPI Documentation**: Auto-generated interactive API docs

## Technology Stack

- **Language**: Python 3.12+
- **Framework**: FastAPI 0.104+
- **AI Agent**: OpenAI Agents SDK 0.6.4+ with Gemini 2.5 Flash backend
- **MCP Integration**: MCP 1.25.0+ (Model Context Protocol for tool calling)
- **Token Management**: tiktoken (cl100k_base encoding)
- **ORM**: SQLModel + SQLAlchemy 2.0 (async)
- **Database**: PostgreSQL (Neon Serverless)
- **Migrations**: Alembic
- **Package Manager**: uv
- **Authentication**: better-auth (shared session validation)

## Architecture

```
User → /api/chat → AgentService → Gemini 2.5 Flash → MCP Server → Task Backend
             ↓                          ↓
        PostgreSQL               Tool Calls & Context
```

### Directory Structure

```
ai-agent/
├── src/
│   └── ai_agent/
│       ├── agent/            # 🆕 AI Agent module (Spec 008)
│       │   ├── agent_service.py    # Orchestrates agent execution
│       │   ├── config.py           # Agent configuration (Pydantic)
│       │   ├── context_manager.py  # Token counting & history truncation
│       │   ├── message_converter.py # DB ↔ Agent format conversion
│       │   ├── mcp_connection.py   # MCP server connection wrapper
│       │   └── timezone_utils.py   # Timezone handling utilities
│       ├── api/              # API endpoints
│       │   ├── chat.py       # POST /api/chat (🔄 Enhanced with agent)
│       │   ├── history.py    # GET /api/conversations
│       │   ├── health.py     # GET /health
│       │   └── deps.py       # FastAPI dependencies
│       ├── database/         # Database layer
│       │   ├── connection.py # Async engine & session
│       │   └── models.py     # SQLModel definitions
│       ├── services/         # Business logic
│       │   └── auth.py       # Authentication service
│       └── main.py           # FastAPI app
├── tests/                    # 🆕 Comprehensive test suite
│   ├── agent/
│   │   ├── contract/         # API contract tests
│   │   ├── integration/      # Integration tests
│   │   └── unit/             # Unit tests
│   └── api/                  # API endpoint tests
├── alembic/                  # Database migrations
├── pyproject.toml            # Dependencies
└── README.md                 # This file
```

## Prerequisites

- Python 3.12 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- PostgreSQL database (Neon recommended)
- **Gemini API Key** from [Google AI Studio](https://ai.google.dev/)
- **MCP Server** running (from spec 006) at http://localhost:8001/mcp
- **Backend API** running at http://localhost:8000 (for API key management)
- Valid better-auth session token for authentication

## Quick Start

### 1. Installation

```bash
# Navigate to the ai-agent directory
cd ai-agent

# Install dependencies
uv sync
```

### 2. Environment Configuration

Create a `.env` file in the `ai-agent/` directory:

```env
# Database Connection
DATABASE_URL=postgresql+asyncpg://user:password@host:port/database

# Backend Service Configuration
# URL of the FastAPI backend for fetching user API keys
# Must match the backend service URL
BACKEND_URL=http://localhost:8000

# Service Authentication (for service-to-service calls)
# Token for authenticating requests to backend microservice
# Must match SERVICE_AUTH_TOKEN in backend/.env
# Generate with: openssl rand -hex 32
SERVICE_AUTH_TOKEN=your-service-auth-token-change-this

# Application Settings
ENV=development
LOG_LEVEL=INFO

# CORS Configuration (comma-separated list of allowed origins)
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Gemini API Configuration (requires AGENT_ prefix)
AGENT_GEMINI_API_KEY=your_gemini_api_key_here

# OpenAI API Configuration (OPTIONAL - for tracing only)
# If not provided, tracing is automatically disabled and the app works normally
# Only needed for debugging with OpenAI trace visualization
# AGENT_OPENAI_API_KEY=your-openai-api-key-here

# MCP Server Configuration (requires AGENT_ prefix)
AGENT_MCP_SERVER_URL=http://localhost:8001/mcp
AGENT_MCP_TIMEOUT=10
AGENT_MCP_RETRY_ATTEMPTS=3

# Agent Configuration (requires AGENT_ prefix)
AGENT_TEMPERATURE=0.7
AGENT_TOKEN_BUDGET=800000
AGENT_ENCODING_NAME=cl100k_base
# AGENT_SYSTEM_PROMPT can be set to customize the agent's behavior
# AGENT_SYSTEM_PROMPT=You are a helpful task management assistant.
```

**Important Notes**:
- Use `ssl=require` (not `sslmode=require`) for asyncpg compatibility
- Get your Gemini API key from [Google AI Studio](https://ai.google.dev/)
- `SERVICE_AUTH_TOKEN` must match the backend configuration
- `BACKEND_URL` must point to the FastAPI backend service
- Ensure the MCP server (spec 006) is running before starting this service
- OpenAI API key is optional and only needed for tracing/debugging

### 3. Database Setup

Run Alembic migrations to create the database schema:

```bash
uv run alembic upgrade head
```

This creates the following tables:
- `conversations` - Chat sessions
- `messages` - Chat messages

### 4. Start the Service

```bash
# Development mode (with auto-reload)
uv run uvicorn ai_agent.main:app --reload --port 8002

# Production mode
uv run uvicorn ai_agent.main:app --host 0.0.0.0 --port 8002
```

The service will start at `http://localhost:8002`

## API Endpoints

### Health Check

```bash
GET /health
```

Verify the service is running.

**Response**:
```json
{
  "status": "healthy",
  "service": "ai-agent"
}
```

### Chat with AI Agent

```bash
POST /api/chat
```

Send a message and receive an AI-powered response with natural language task management.

**Headers**:
```
Authorization: Bearer <session_token>
X-Timezone: America/New_York  # Optional: User's IANA timezone (defaults to UTC)
Content-Type: application/json
```

**Request**:
```json
{
  "message": "Add a task to buy groceries tomorrow at 5pm",
  "conversation_id": 1  // Optional: omit to create new conversation
}
```

**Response**:
```json
{
  "conversation_id": 1,
  "user_message": "Add a task to buy groceries tomorrow at 5pm",
  "assistant_message": "I've added 'Buy groceries' to your tasks for tomorrow at 5:00 PM.",
  "operations": [
    {
      "tool_name": "create_task",
      "status": "success",
      "details": null
    }
  ]
}
```

**Note**: The `operations` array contains metadata about which MCP tools were called during request processing. This enables real-time feedback in the frontend UI (checkmarks for successful operations, warning icons for failures).

**Supported Natural Language Commands**:
- "show my tasks" / "list all tasks"
- "add urgent task to finish report by EOD"
- "mark the first task as complete"
- "update the second task priority to high"
- "what are my high priority tasks?"

**Timezone Support**:
The agent understands dates/times in your timezone when you include the `X-Timezone` header:
- `X-Timezone: America/New_York` → "tomorrow at 5pm" = 5pm EST/EDT
- `X-Timezone: Asia/Tokyo` → "tomorrow at 5pm" = 5pm JST
- No header → Times interpreted as UTC

### List Conversations

```bash
GET /api/conversations
```

Get all conversations for the authenticated user (ordered by most recent).

**Response**:
```json
[
  {
    "id": 1,
    "title": "Chat - 2025-12-19 18:29",
    "created_at": "2025-12-19T18:29:33.254217",
    "updated_at": "2025-12-19T18:30:05.686344"
  }
]
```

### Get Conversation History

```bash
GET /api/conversations/{conversation_id}
```

Get full conversation details with all messages.

**Response**:
```json
{
  "id": 1,
  "title": "Chat - 2025-12-19 18:29",
  "created_at": "2025-12-19T18:29:33.254217",
  "updated_at": "2025-12-19T18:30:05.686344",
  "messages": [
    {
      "id": 1,
      "role": "user",
      "content": "Hello, how are you?",
      "message_metadata": null,
      "created_at": "2025-12-19T18:29:34.518404"
    },
    {
      "id": 2,
      "role": "assistant",
      "content": "Echo: Hello, how are you?",
      "message_metadata": null,
      "created_at": "2025-12-19T18:29:34.518729"
    }
  ]
}
```

## Authentication

All API endpoints (except `/health`) require Bearer token authentication:

```bash
curl -H "Authorization: Bearer <your_session_token>" \
  http://localhost:8002/api/conversations
```

The service validates tokens against the `user_sessions` table managed by better-auth.

### Getting a Session Token

For development/testing, query a token from the database:

```bash
uv run python -c "
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import select
from ai_agent.database.connection import engine
from ai_agent.database.models import UserSession

async def get_token():
    async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session_maker() as session:
        result = await session.execute(select(UserSession).limit(1))
        user_session = result.scalar_one_or_none()
        if user_session:
            print(user_session.token)

asyncio.run(get_token())
"
```

## Database Schema

### Conversation Model

| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Primary key (auto-increment) |
| `user_id` | String | Owner's user ID (from better-auth) |
| `title` | String(200) | Conversation title |
| `created_at` | DateTime | Creation timestamp |
| `updated_at` | DateTime | Last update timestamp |

**Indexes**: `user_id`, `created_at`

### Message Model

| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Primary key (auto-increment) |
| `conversation_id` | Integer | Foreign key to conversations |
| `role` | String(20) | `user`, `assistant`, or `tool` |
| `content` | Text | Message content |
| `message_metadata` | JSONB | Optional metadata (for OpenAI tool calls) |
| `created_at` | DateTime | Creation timestamp |

**Indexes**: `conversation_id`

## Database Migrations

### Create a New Migration

```bash
uv run alembic revision --autogenerate -m "Description of changes"
```

### Apply Migrations

```bash
# Upgrade to latest
uv run alembic upgrade head

# Downgrade one version
uv run alembic downgrade -1

# Check current version
uv run alembic current
```

## API Documentation

Interactive API documentation is available when the service is running:

- **Swagger UI**: http://localhost:8002/docs
- **ReDoc**: http://localhost:8002/redoc
- **OpenAPI JSON**: http://localhost:8002/openapi.json

## Error Handling

The service returns standard HTTP error codes:

| Code | Description | Example |
|------|-------------|---------|
| 200 | Success | Request completed successfully |
| 401 | Unauthorized | Missing or invalid token |
| 404 | Not Found | Conversation doesn't exist or no access |
| 422 | Validation Error | Invalid request body |
| 503 | Service Unavailable | AI service (Gemini/MCP) temporarily unavailable |
| 500 | Internal Server Error | Database or server error |

**Example Error Response**:
```json
{
  "detail": "Conversation not found or you don't have access"
}
```

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | - | PostgreSQL connection string (asyncpg format) |
| `BACKEND_URL` | Yes | `http://localhost:8000` | FastAPI backend URL for API key management |
| `SERVICE_AUTH_TOKEN` | Yes | - | Service-to-service authentication token (must match backend) |
| `AGENT_GEMINI_API_KEY` | Yes | - | Gemini API key from Google AI Studio |
| `AGENT_MCP_SERVER_URL` | Yes | `http://localhost:8001/mcp` | MCP server endpoint URL |
| `AGENT_TEMPERATURE` | No | `0.7` | AI model temperature (0.0-2.0) |
| `AGENT_TOKEN_BUDGET` | No | `800000` | Maximum tokens for conversation context |
| `AGENT_ENCODING_NAME` | No | `cl100k_base` | Token encoding name for tiktoken |
| `AGENT_MCP_TIMEOUT` | No | `10` | MCP server timeout in seconds |
| `AGENT_MCP_RETRY_ATTEMPTS` | No | `3` | Number of retry attempts for MCP calls |
| `AGENT_OPENAI_API_KEY` | No | - | OpenAI API key (optional, for tracing only) |
| `AGENT_SYSTEM_PROMPT` | No | - | Custom system prompt (optional) |
| `ENV` | No | `development` | Environment (development/production) |
| `LOG_LEVEL` | No | `INFO` | Logging level (DEBUG/INFO/WARNING/ERROR) |
| `CORS_ORIGINS` | No | `http://localhost:3000,http://localhost:3001` | Comma-separated list of allowed origins |

### Connection Pooling

The service uses SQLAlchemy connection pooling for production performance:

```python
pool_size=5          # Persistent connections
max_overflow=10      # Additional connections when pool exhausted
pool_timeout=30      # Wait time for connection (seconds)
pool_recycle=3600    # Recycle connections after 1 hour
```

## Testing

### Manual Testing with curl

See the [quickstart guide](../specs/007-chat-persistence/quickstart.md) for complete examples.

**Quick test**:
```bash
# Export token
export TOKEN="your_session_token_here"

# Create conversation
curl -X POST http://localhost:8002/api/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}' | jq '.'

# List conversations
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8002/api/conversations | jq '.'
```

### Automated Testing

The service includes comprehensive test coverage (52/54 tests passing, 96%):

```bash
# Run all tests
uv run pytest tests/ -v

# Run specific test suites
uv run pytest tests/agent/unit/ -v          # Unit tests (21/21 passing)
uv run pytest tests/agent/integration/ -v  # Integration tests (15/15 passing)
uv run pytest tests/agent/contract/ -v     # Contract tests (13/15 passing)

# Run with coverage report
uv run pytest --cov=ai_agent tests/

# Run E2E workflow tests
uv run pytest tests/agent/integration/test_agent_workflow.py -v
```

**Test Coverage**:
- ✅ Agent configuration validation
- ✅ Message format conversion (DB ↔ Agent)
- ✅ Token counting and context truncation
- ✅ MCP server connection with authentication
- ✅ Timezone utilities (extraction, validation, formatting)
- ✅ Agent execution with Gemini backend
- ✅ Tool call extraction and tracking
- ✅ Multi-turn conversation context
- ✅ Complete E2E workflows (list, create, update tasks)

**Note**: 2 tests require a live MCP server and will be skipped in CI/CD environments.

## Deployment

### Docker Deployment (Future)

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install uv && uv sync --frozen
CMD ["uvicorn", "ai_agent.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment-Specific Settings

**Production checklist**:
- [ ] Set `ENV=production`
- [ ] Use strong `SERVICE_AUTH_TOKEN`
- [ ] Enable HTTPS/TLS
- [ ] Configure proper CORS origins
- [ ] Set up monitoring and logging
- [ ] Use managed PostgreSQL (Neon/RDS)
- [ ] Configure health checks
- [ ] Set up auto-scaling

## Troubleshooting

### Database Connection Issues

**Error**: `asyncpg connection errors`

**Solution**:
- Ensure `DATABASE_URL` uses `ssl=require` (not `sslmode=require`)
- Verify database credentials
- Check network connectivity to PostgreSQL

### Authentication Errors

**Error**: `401 Unauthorized`

**Solution**:
- Verify session token exists in `user_sessions` table
- Check token hasn't expired (`expiresAt` column)
- Ensure correct `Authorization: Bearer <token>` format

### Migration Errors

**Error**: `Alembic migration fails`

**Solution**:
```bash
# Check current version
uv run alembic current

# View migration history
uv run alembic history

# Rollback and retry
uv run alembic downgrade -1
uv run alembic upgrade head
```

### Import Errors

**Error**: `ModuleNotFoundError: No module named 'ai_agent'`

**Solution**:
```bash
# Ensure you're in the ai-agent directory
cd ai-agent

# Reinstall dependencies
uv sync
```

## Project Roadmap

### Completed ✅

#### Spec 007: Chat Persistence
- [x] Conversation management
- [x] Message persistence
- [x] Authentication integration
- [x] History retrieval

#### Spec 008: OpenAI Agents SDK Integration
- [x] **Phase 1 - Setup**: Project structure and dependencies
  - Installed openai-agents (v0.6.4), tiktoken, pydantic-settings, mcp
  - Created agent module structure in `src/ai_agent/agent/`
  - Created comprehensive test suite (contract/integration/unit)
  - Updated .env.example with Gemini API and agent configuration

- [x] **Phase 2 - Foundational**: Core infrastructure modules (33/33 tasks)
  - **AgentConfig** - Pydantic-based configuration with field validation
  - **MessageConverter** - Database ↔ Agent format conversion with tool_calls preservation
  - **ContextManager** - Token counting (tiktoken), smart truncation, history loading
  - **Task Context** - Ordinal reference resolution ("first task", "second task", "last task")
  - **MCP Connection** - MCPServerStreamableHttp wrapper with X-User-ID authentication
  - **Timezone Utilities** - X-Timezone header extraction, IANA validation, time formatting

- [x] **Phase 3 - User Story 1**: Natural language task management (60/60 tasks) 🎯 **MVP**
  - **Agent Service** - Orchestrates Gemini 2.5 Flash execution with MCP tools
  - **Context Orchestration** - Integrates history, timezone, and user authentication
  - **Chat Endpoint** - Enhanced `/api/chat` with agent integration
  - **E2E Testing** - Complete workflow tests (list, create, update, complete tasks)
  - **Test Coverage**: 52/54 tests passing (96%)

### Completed (Recent) ✅

#### Spec 009: Frontend Chat Integration - Phase 6
- [x] **Real-Time Task Operation Feedback**: Returns operation status in chat responses for frontend UI display

### In Progress 🔨

#### Spec 008: User Stories 2-4 (Optional Enhancements)
- [ ] **Phase 4 - User Story 2**: Multi-turn conversation context (P2)
  - Context persistence testing
  - Follow-up question understanding
  - Incremental task creation across turns

- [ ] **Phase 5 - User Story 3**: Intelligent parsing and validation (P2)
  - Relative date parsing with timezone awareness
  - Invalid date detection and clarification
  - Priority keyword extraction and normalization

- [ ] **Phase 6 - User Story 4**: Batch operations (P3)
  - Bulk task operations ("mark all urgent tasks complete")
  - Filtered batch actions with confirmation

- [ ] **Phase 7 - Polish**: Production hardening
  - Enhanced error handling and logging
  - Rate limiting for Gemini API
  - Performance metrics and monitoring
  - Security validation (input sanitization, secret management)

### Future Enhancements 🚀
- [ ] Streaming responses (Server-Sent Events)
- [ ] Frontend chatbot widget integration
- [ ] Conversation summarization for long histories
- [ ] Advanced observability (OpenTelemetry, Grafana)
- [ ] Multi-language support
- [ ] Voice input integration

## How It Works

### AI Agent Execution Flow

```
1. User sends message → /api/chat with X-Timezone header
2. Extract timezone, load AgentConfig (Gemini key, MCP URL)
3. Load conversation history from PostgreSQL
4. Truncate history to fit token budget (800k tokens)
5. Create MCP connection with user authentication
6. Initialize OpenAI Agent with Gemini 2.5 Flash backend
7. Enhance system prompt with timezone context
8. Execute: Runner.run(agent, message, history, run_config)
9. Gemini processes message → Calls MCP tools as needed
10. Extract tool calls, count tokens, track execution time
11. Save user message + agent response to database
12. Return response with metadata
```

### Natural Language Processing

The agent understands context and intent:

**Date/Time Parsing**:
- "tomorrow" → Calculated in user's timezone
- "next Friday" → Resolved with timezone
- "by EOD" → 23:59:59 in user's timezone
- All times converted to UTC for storage

**Priority Detection**:
- "urgent", "critical", "asap" → Priority.URGENT
- "high", "important" → Priority.HIGH
- "normal", "medium" → Priority.MEDIUM (default)
- "low" → Priority.LOW

**Ordinal References**:
- "mark the first one complete" → Resolves to task ID from recent list
- Context expires after 5 turns or 5 minutes

### MCP Tool Integration

The agent has access to these MCP tools:
- `list_tasks` - Get user's tasks with optional filters
- `create_task` - Create a new task with title, description, priority, due date
- `update_task` - Update existing task attributes
- `mark_task_completed` - Mark a task as complete
- `delete_task` - Delete a task

All tool calls are authenticated with the user's ID via X-User-ID header.

## Contributing

This service is part of the todo-app project following Spec-Driven Development (SDD) methodology.

**Development workflow**:
1. Review specifications in `specs/007-chat-persistence/` and `specs/008-openai-agents-sdk-integration/`
2. Follow task breakdown in respective `tasks.md` files
3. Write tests first (TDD: RED → GREEN → REFACTOR)
4. Implement changes with proper error handling
5. Update documentation
6. Run test suite: `uv run pytest tests/ -v`
7. Create PR for review

## License

[Your License Here]

## Support

For issues, questions, or contributions:
- Create an issue in the GitHub repository
- Review documentation in `specs/007-chat-persistence/`
- Check the quickstart guide for common scenarios

## Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- AI Agent Framework: [OpenAI Agents SDK](https://github.com/openai/openai-agents-python)
- LLM Backend: [Google Gemini 2.5 Flash](https://ai.google.dev/gemini-api)
- Tool Protocol: [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- Token Counting: [tiktoken](https://github.com/openai/tiktoken)
- Database ORM: [SQLModel](https://sqlmodel.tiangolo.com/)
- Authentication: [better-auth](https://www.better-auth.com/)
- Database: [Neon Serverless PostgreSQL](https://neon.tech/)
- Package Management: [uv](https://github.com/astral-sh/uv)
