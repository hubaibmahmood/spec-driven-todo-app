# AI Agent - Chat Persistence Service

A FastAPI-based microservice for managing AI conversation history and message persistence. This service provides RESTful endpoints for creating conversations, storing messages, and retrieving chat history with secure authentication.

## Features

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
- **ORM**: SQLModel + SQLAlchemy 2.0 (async)
- **Database**: PostgreSQL (Neon Serverless)
- **Migrations**: Alembic
- **Package Manager**: uv
- **Authentication**: better-auth (shared session validation)

## Architecture

```
ai-agent/
├── src/
│   └── ai_agent/
│       ├── api/              # API endpoints
│       │   ├── chat.py       # POST /api/chat
│       │   ├── history.py    # GET /api/conversations
│       │   ├── health.py     # GET /health
│       │   └── deps.py       # FastAPI dependencies
│       ├── database/         # Database layer
│       │   ├── connection.py # Async engine & session
│       │   └── models.py     # SQLModel definitions
│       ├── services/         # Business logic
│       │   └── auth.py       # Authentication service
│       └── main.py           # FastAPI app
├── alembic/                  # Database migrations
├── tests/                    # Test suite (future)
├── pyproject.toml            # Dependencies
└── README.md                 # This file
```

## Prerequisites

- Python 3.12 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- PostgreSQL database (Neon recommended)
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
# Database Configuration
DATABASE_URL=postgresql+asyncpg://user:password@host:port/database?ssl=require

# Service Authentication
SERVICE_AUTH_TOKEN=your_secret_token

# Application Settings
ENV=development
LOG_LEVEL=INFO
```

**Important**: Use `ssl=require` (not `sslmode=require`) for asyncpg compatibility.

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
uv run uvicorn ai_agent.main:app --reload --port 8001

# Production mode
uv run uvicorn ai_agent.main:app --host 0.0.0.0 --port 8001
```

The service will start at `http://localhost:8001`

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

### Create Conversation

```bash
POST /api/chat
```

Create a new conversation or send a message to an existing one.

**Request**:
```json
{
  "message": "Hello, how are you?",
  "conversation_id": 1  // Optional: omit to create new conversation
}
```

**Response**:
```json
{
  "conversation_id": 1,
  "user_message": "Hello, how are you?",
  "assistant_message": "Echo: Hello, how are you?"
}
```

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
  http://localhost:8001/api/conversations
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

- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc
- **OpenAPI JSON**: http://localhost:8001/openapi.json

## Error Handling

The service returns standard HTTP error codes:

| Code | Description | Example |
|------|-------------|---------|
| 200 | Success | Request completed successfully |
| 401 | Unauthorized | Missing or invalid token |
| 404 | Not Found | Conversation doesn't exist or no access |
| 422 | Validation Error | Invalid request body |
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
| `SERVICE_AUTH_TOKEN` | No | - | Service-to-service authentication token |
| `ENV` | No | `development` | Environment (development/production) |
| `LOG_LEVEL` | No | `INFO` | Logging level (DEBUG/INFO/WARNING/ERROR) |

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
curl -X POST http://localhost:8001/api/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}' | jq '.'

# List conversations
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8001/api/conversations | jq '.'
```

### Automated Testing (Future)

```bash
# Run tests (when implemented)
uv run pytest tests/

# Run with coverage
uv run pytest --cov=ai_agent tests/
```

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

### Current (Spec 007) ✅
- [x] Conversation management
- [x] Message persistence
- [x] Authentication integration
- [x] History retrieval
- [x] Echo responses

### Future (Spec 008+)
- [ ] OpenAI Agents SDK integration
- [ ] Real AI responses (replace echo)
- [ ] Tool call support (via `message_metadata`)
- [ ] Streaming responses
- [ ] Frontend chatbot integration
- [ ] Unit and integration tests
- [ ] Performance optimization
- [ ] Monitoring and observability

## Contributing

This service is part of the todo-app project following Spec-Driven Development (SDD) methodology.

**Development workflow**:
1. Review specification in `specs/007-chat-persistence/`
2. Follow task breakdown in `specs/007-chat-persistence/tasks.md`
3. Implement changes with proper error handling
4. Update documentation
5. Test manually or with automated tests
6. Create PR for review

## License

[Your License Here]

## Support

For issues, questions, or contributions:
- Create an issue in the GitHub repository
- Review documentation in `specs/007-chat-persistence/`
- Check the quickstart guide for common scenarios

## Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Database ORM: [SQLModel](https://sqlmodel.tiangolo.com/)
- Authentication: [better-auth](https://www.better-auth.com/)
- Database: [Neon Serverless PostgreSQL](https://neon.tech/)
- Package Management: [uv](https://github.com/astral-sh/uv)
