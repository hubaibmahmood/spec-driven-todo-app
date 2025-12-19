# Quickstart: Chat Persistence Service

## Prerequisites
- Python 3.12+
- `uv` package manager
- Access to the PostgreSQL database (Neon) with `user_sessions` table
- Valid session token from better-auth authentication

## Local Setup

1. **Navigate to the service**:
   ```bash
   cd ai-agent
   ```

2. **Install dependencies**:
   ```bash
   uv sync
   ```

3. **Environment Variables**:
   Create a `.env` file in the `ai-agent/` directory:
   ```env
   DATABASE_URL=postgresql+asyncpg://user:password@host:port/database?ssl=require
   SERVICE_AUTH_TOKEN=your_secret_token
   ENV=development
   LOG_LEVEL=INFO
   ```

   **Note**: The `DATABASE_URL` must use `ssl=require` (not `sslmode=require`) for asyncpg compatibility.

4. **Run migrations**:
   ```bash
   uv run alembic upgrade head
   ```

5. **Run the service**:
   ```bash
   uv run fastapi dev src/ai_agent/main.py
   ```

   The service will start on `http://localhost:8000`

## API Endpoints

### 0. Health Check
Verify the service is running:

```bash
curl http://localhost:8000/health
```

**Response**:
```json
{
  "status": "healthy",
  "service": "ai-agent"
}
```

### 1. Send Message (Create New Conversation)

Create a new conversation by sending a message without a `conversation_id`:

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer 5Q66xXPymKOcq6GKdirPNbq7aAUdIqDz" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, how are you?"}'
```

**Response**:
```json
{
  "conversation_id": 1,
  "user_message": "Hello, how are you?",
  "assistant_message": "Echo: Hello, how are you?"
}
```

**Note**: In spec 007, the assistant provides echo responses. This will be replaced with OpenAI Agents SDK in spec 008.

### 2. Continue Conversation

Send a follow-up message to an existing conversation:

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer 5Q66xXPymKOcq6GKdirPNbq7aAUdIqDz" \
  -H "Content-Type: application/json" \
  -d '{"message": "Tell me more", "conversation_id": 1}'
```

**Response**:
```json
{
  "conversation_id": 1,
  "user_message": "Tell me more",
  "assistant_message": "Echo: Tell me more"
}
```

### 3. List All Conversations

Get all conversations for the authenticated user (ordered by most recent first):

```bash
curl -H "Authorization: Bearer 5Q66xXPymKOcq6GKdirPNbq7aAUdIqDz" \
  http://localhost:8000/api/conversations
```

**Response**:
```json
[
  {
    "id": 2,
    "title": "Chat - 2025-12-19 19:30",
    "created_at": "2025-12-19T19:30:15.123456",
    "updated_at": "2025-12-19T19:32:45.789012"
  },
  {
    "id": 1,
    "title": "Chat - 2025-12-19 18:15",
    "created_at": "2025-12-19T18:15:30.654321",
    "updated_at": "2025-12-19T18:20:10.987654"
  }
]
```

### 4. Get Conversation History

Get full conversation details including all messages (ordered chronologically):

```bash
curl -H "Authorization: Bearer 5Q66xXPymKOcq6GKdirPNbq7aAUdIqDz" \
  http://localhost:8000/api/conversations/1
```

**Response**:
```json
{
  "id": 1,
  "title": "Chat - 2025-12-19 18:15",
  "created_at": "2025-12-19T18:15:30.654321",
  "updated_at": "2025-12-19T18:20:10.987654",
  "messages": [
    {
      "id": 1,
      "role": "user",
      "content": "Hello, how are you?",
      "message_metadata": null,
      "created_at": "2025-12-19T18:15:30.654321"
    },
    {
      "id": 2,
      "role": "assistant",
      "content": "Echo: Hello, how are you?",
      "message_metadata": null,
      "created_at": "2025-12-19T18:15:30.789456"
    },
    {
      "id": 3,
      "role": "user",
      "content": "Tell me more",
      "message_metadata": null,
      "created_at": "2025-12-19T18:20:10.123456"
    },
    {
      "id": 4,
      "role": "assistant",
      "content": "Echo: Tell me more",
      "message_metadata": null,
      "created_at": "2025-12-19T18:20:10.987654"
    }
  ]
}
```

## Error Responses

### 401 Unauthorized - Missing or Invalid Token
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'
```

**Response**:
```json
{
  "detail": "Missing Authorization header"
}
```

### 404 Not Found - Conversation Doesn't Exist or No Access
```bash
curl -H "Authorization: Bearer 5Q66xXPymKOcq6GKdirPNbq7aAUdIqDz" \
  http://localhost:8000/api/conversations/999
```

**Response**:
```json
{
  "detail": "Conversation not found or you don't have access"
}
```

## Complete Workflow Example

Here's a complete workflow demonstrating all endpoints:

```bash
# 1. Check service health
curl http://localhost:8000/health

# 2. Get a valid session token from the database
# (In production, this comes from better-auth login)
export TOKEN="5Q66xXPymKOcq6GKdirPNbq7aAUdIqDz"

# 3. Create a new conversation
curl -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the weather today?"}' \
  | jq '.'

# Save the conversation_id from the response (e.g., 1)

# 4. Send follow-up messages
curl -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Thanks for the info!", "conversation_id": 1}' \
  | jq '.'

# 5. List all conversations
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/conversations | jq '.'

# 6. Get full conversation history
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/conversations/1 | jq '.'
```

## Getting a Session Token

To get a valid session token for testing:

```bash
# Query a session token from the database
cd ai-agent
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

## API Documentation

Once the service is running, visit:
- **Interactive API docs (Swagger)**: http://localhost:8000/docs
- **Alternative API docs (ReDoc)**: http://localhost:8000/redoc

## Troubleshooting

### Database Connection Issues

If you see `asyncpg` connection errors:
- Ensure `DATABASE_URL` uses `ssl=require` (not `sslmode=require`)
- Verify database credentials are correct
- Check network connectivity to Neon PostgreSQL

### Authentication Errors

If you get 401 errors:
- Verify the session token exists in the `user_sessions` table
- Check that the token hasn't expired (`expiresAt` column)
- Ensure the `Authorization` header format is correct: `Bearer <token>`

### Migration Errors

If migrations fail:
- Check that `DATABASE_URL` is set correctly in `.env`
- Ensure the database is accessible
- Run `uv run alembic current` to check migration status

