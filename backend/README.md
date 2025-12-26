# Backend API - Task Management Service

A FastAPI-based RESTful API service for task management with PostgreSQL database, user authentication, and rate limiting. Built following clean architecture principles with async operations for high performance.

## Features

### 🎯 Core Functionality
- ✅ **CRUD Operations**: Create, Read, Update, Delete tasks
- ✅ **Task Completion**: Toggle task status with timestamp tracking
- ✅ **User Isolation**: Each user can only access their own tasks
- ✅ **Priority Levels**: URGENT, HIGH, MEDIUM, LOW priority support
- ✅ **Due Dates**: Task deadline management with timezone support
- ✅ **Tags**: Organize tasks with custom tags

### 🔐 Security
- ✅ **Session Authentication**: Bearer token validation via better-auth
- ✅ **Service-to-Service Auth**: X-Service-Auth header for microservices
- ✅ **User Context**: Automatic user ID extraction from session tokens
- ✅ **Data Isolation**: Row-level security ensuring users access only their data

### ⚡ Performance
- ✅ **Async Operations**: Non-blocking database queries with SQLAlchemy async
- ✅ **Connection Pooling**: Optimized database connection management
- ✅ **Rate Limiting**: User-based rate limits (100 req/min read, 30 req/min write)
- ✅ **CORS Support**: Configured for cross-origin requests

### 📊 Database
- ✅ **PostgreSQL**: Production-ready database with Neon serverless support
- ✅ **Migrations**: Alembic-based schema versioning
- ✅ **Async ORM**: SQLAlchemy 2.0+ with async/await support
- ✅ **Indexes**: Optimized queries with proper indexing

## Technology Stack

- **Language**: Python 3.12+
- **Framework**: FastAPI 0.127.0+
- **Database**: PostgreSQL (Neon Serverless)
- **ORM**: SQLAlchemy 2.0+ (async)
- **Validation**: Pydantic 2.0+
- **Server**: Uvicorn (ASGI)
- **Migrations**: Alembic 1.13+
- **Testing**: pytest, pytest-asyncio
- **Package Manager**: uv

## Architecture

```
Client (Frontend/AI Agent)
        ↓
Bearer Token / Service Auth
        ↓
FastAPI Backend (Port 8000)
        ↓
SQLAlchemy Async ORM
        ↓
PostgreSQL Database (Neon)
```

### Directory Structure

```
backend/
├── src/
│   ├── api/                     # API layer
│   │   ├── main.py             # FastAPI application
│   │   ├── dependencies.py     # Dependency injection
│   │   ├── middleware/         # Custom middleware
│   │   │   └── security_headers.py
│   │   ├── routers/            # Route handlers
│   │   │   ├── tasks.py        # Task endpoints
│   │   │   ├── api_keys.py     # API key management
│   │   │   └── health.py       # Health check
│   │   └── schemas/            # Pydantic models
│   │       ├── task.py         # Task schemas
│   │       ├── api_key.py      # API key schemas
│   │       └── error.py        # Error schemas
│   ├── models/                 # SQLAlchemy models
│   │   ├── database.py         # Task model
│   │   └── user_api_key.py     # API key model
│   ├── database/               # Database layer
│   │   ├── connection.py       # SQLAlchemy engine & session
│   │   ├── repository.py       # Data access layer
│   │   ├── migrations.py       # Custom migration functions
│   │   ├── add_priority_due_date_migration.py
│   │   └── migrate_user_api_keys.py
│   └── services/               # Business logic
│       ├── auth_service.py     # Authentication service
│       ├── api_key_service.py  # API key service
│       ├── encryption_service.py
│       ├── gemini_validator.py
│       └── rate_limiter.py
├── alembic/                    # Alembic configuration (optional)
│   ├── versions/               # Alembic migration scripts
│   └── env.py                  # Alembic config
├── tests/                      # Test suite
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   └── contract/               # API contract tests
├── pyproject.toml              # Dependencies (uv)
├── alembic.ini                 # Alembic configuration
└── README.md                   # This file
```

## Prerequisites

- Python 3.12 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- PostgreSQL database (Neon recommended)
- Auth server running (for session validation)

## Quick Start

### 1. Installation

```bash
# Navigate to backend directory
cd backend

# Install dependencies using uv
uv sync
```

### 2. Environment Configuration

Create a `.env` file in the `backend/` directory:

```env
# Database Configuration
# Neon PostgreSQL connection string
# Format: postgresql+asyncpg://user:password@host/database
DATABASE_URL=postgresql+asyncpg://user:password@your-neon-endpoint.neon.tech/todo_db

# Authentication Configuration
# Shared secret for hashing session tokens (HMAC-SHA256)
# Must match the auth-server SESSION_HASH_SECRET
# Generate with: openssl rand -hex 32
SESSION_HASH_SECRET=your-secret-key-change-this-in-production

# URL of the auth server for integration tests
AUTH_SERVER_URL=http://localhost:8080

# Service-to-Service Authentication
# Token for authenticating requests from ai-agent microservice
# Must match SERVICE_AUTH_TOKEN in ai-agent/.env
# Generate with: openssl rand -hex 32
SERVICE_AUTH_TOKEN=your-service-auth-token-change-this

# Application Configuration
# Environment: development, staging, production
ENVIRONMENT=development

# CORS Configuration
# Comma-separated list of allowed origins
# Development: http://localhost:3000
# Production: https://yourdomain.com,https://www.yourdomain.com
CORS_ORIGINS=http://localhost:3000

# SQLAlchemy Connection Pool Settings
# Pool size: number of connections to keep open
SQLALCHEMY_POOL_SIZE=10
# Max overflow: additional connections allowed above pool_size
SQLALCHEMY_POOL_OVERFLOW=20
# Pool timeout: seconds to wait for available connection
SQLALCHEMY_POOL_TIMEOUT=30
# Pool recycle: seconds before recycling connections (Neon serverless)
SQLALCHEMY_POOL_RECYCLE=3600
# Echo SQL: log all SQL queries (development only)
SQLALCHEMY_ECHO=false

# Redis Configuration (for rate limiting)
# Redis connection URL
REDIS_URL=redis://localhost:6379/0

# API Key Encryption Configuration
# Fernet encryption key for encrypting user API keys at rest
# CRITICAL: Generate a new key for production with the command below
# Generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# Store securely in secrets manager (AWS Secrets Manager, GitHub Secrets, etc.)
ENCRYPTION_KEY=your-fernet-encryption-key-change-this
```

**Important Notes**:
- Use `ssl=require` (not `sslmode=require`) for asyncpg compatibility
- `SESSION_HASH_SECRET` must match the auth-server configuration
- `SERVICE_AUTH_TOKEN` must match the ai-agent configuration
- `ENCRYPTION_KEY` is critical for API key security - generate a new Fernet key for production
- Ensure database URL matches your PostgreSQL instance

### 3. Database Setup

Run custom migration scripts to create the database schema:

```bash
# Method 1: Using custom migration scripts (Recommended)
# Initialize database and create tasks table
uv run python -c "import asyncio; from src.database.migrations import init_db; asyncio.run(init_db())"

# Add priority and due_date columns (if needed)
uv run python -c "import asyncio; from src.database.add_priority_due_date_migration import upgrade; asyncio.run(upgrade())"

# Migrate user API keys table (if needed)
uv run python -c "import asyncio; from src.database.migrate_user_api_keys import upgrade; asyncio.run(upgrade())"

# Method 2: Using Alembic (Alternative)
# Apply all Alembic migrations
uv run alembic upgrade head
```

This creates the following tables:
- `users` - User accounts (managed by auth server)
- `user_sessions` - Session tokens (managed by auth server)
- `tasks` - Task records with user ownership, priority, and due dates
- `user_api_keys` - Encrypted API keys for AI services (Gemini, etc.)

### 4. Start the Service

```bash
# Development mode (with auto-reload)
uv run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uv run uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will start at `http://localhost:8000`

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
  "service": "todo-backend"
}
```

### Task Management

All task endpoints require authentication via `Authorization: Bearer <session_token>` header.

#### Create Task

```bash
POST /api/tasks
```

**Headers**:
```
Authorization: Bearer <session_token>
Content-Type: application/json
```

**Request Body**:
```json
{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "priority": "MEDIUM",
  "dueDate": "2025-12-27T17:00:00Z",
  "tags": ["shopping", "personal"]
}
```

**Response** (201 Created):
```json
{
  "id": "uuid-here",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "status": "TODO",
  "priority": "MEDIUM",
  "dueDate": "2025-12-27T17:00:00Z",
  "tags": ["shopping", "personal"],
  "userId": "user-id",
  "createdAt": "2025-12-26T10:30:00Z",
  "updatedAt": "2025-12-26T10:30:00Z",
  "completedAt": null
}
```

#### Get All Tasks

```bash
GET /api/tasks
```

**Response** (200 OK):
```json
[
  {
    "id": "uuid-1",
    "title": "Buy groceries",
    "status": "TODO",
    "priority": "MEDIUM",
    "dueDate": "2025-12-27T17:00:00Z",
    "tags": ["shopping"],
    "userId": "user-id",
    "createdAt": "2025-12-26T10:30:00Z",
    "completedAt": null
  },
  {
    "id": "uuid-2",
    "title": "Finish report",
    "status": "COMPLETED",
    "priority": "HIGH",
    "dueDate": "2025-12-26T18:00:00Z",
    "tags": ["work"],
    "userId": "user-id",
    "createdAt": "2025-12-25T09:00:00Z",
    "completedAt": "2025-12-26T14:20:00Z"
  }
]
```

#### Get Single Task

```bash
GET /api/tasks/{task_id}
```

**Response** (200 OK): Same schema as Create Task response

#### Update Task

```bash
PATCH /api/tasks/{task_id}
```

**Request Body** (all fields optional):
```json
{
  "title": "Buy groceries and cook dinner",
  "description": "Updated description",
  "priority": "HIGH",
  "dueDate": "2025-12-27T19:00:00Z"
}
```

**Response** (200 OK): Updated task object

#### Toggle Task Completion

```bash
PATCH /api/tasks/{task_id}/complete
```

Toggles task between TODO and COMPLETED status. Sets `completedAt` timestamp when marked complete.

**Response** (200 OK): Updated task object

#### Delete Task

```bash
DELETE /api/tasks/{task_id}
```

**Response** (204 No Content)

## Authentication

The backend supports two authentication modes:

### 1. Session Authentication (Frontend/Users)

Used by frontend and direct API consumers:

```bash
curl -H "Authorization: Bearer <session_token>" \
  http://localhost:8000/api/tasks
```

- Session tokens are validated against the `user_sessions` table
- User ID is extracted from the session
- Tokens are managed by the auth server (better-auth)

### 2. Service Authentication (Microservices)

Used by internal services (MCP server, AI agent):

```bash
curl -H "X-Service-Auth: <service_token>" \
     -H "X-User-ID: <user_id>" \
  http://localhost:8000/api/tasks
```

- Service token is verified against `SERVICE_AUTH_TOKEN` env variable
- User context is provided via `X-User-ID` header
- Enables service-to-service communication with user isolation

## Database Schema

### Task Model

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Primary key (auto-generated) |
| `user_id` | String | Owner's user ID (foreign key) |
| `title` | String(200) | Task title (required) |
| `description` | Text | Task description (optional) |
| `status` | Enum | TODO, IN_PROGRESS, COMPLETED |
| `priority` | Enum | URGENT, HIGH, MEDIUM, LOW |
| `due_date` | DateTime | Task deadline (optional) |
| `tags` | Array[String] | Task tags (optional) |
| `created_at` | DateTime | Creation timestamp |
| `updated_at` | DateTime | Last update timestamp |
| `completed_at` | DateTime | Completion timestamp (nullable) |

**Indexes**: `user_id`, `status`, `priority`, `due_date`

## Database Migrations

The backend uses **custom migration scripts** for better control and flexibility. Migration scripts are located in `src/database/`.

### Available Custom Migrations

1. **migrations.py** - Core migration functions
   ```bash
   # Initialize database (create tables)
   uv run python -c "import asyncio; from src.database.migrations import init_db; asyncio.run(init_db())"

   # Reset database (drop and recreate tables - WARNING: deletes all data)
   uv run python -c "import asyncio; from src.database.migrations import reset_db; asyncio.run(reset_db())"
   ```

2. **add_priority_due_date_migration.py** - Add priority and due_date columns
   ```bash
   # Upgrade (add columns)
   uv run python -c "import asyncio; from src.database.add_priority_due_date_migration import upgrade; asyncio.run(upgrade())"

   # Downgrade (remove columns)
   uv run python -c "import asyncio; from src.database.add_priority_due_date_migration import downgrade; asyncio.run(downgrade())"
   ```

3. **migrate_user_api_keys.py** - Create user_api_keys table
   ```bash
   # Upgrade (create table)
   uv run python -c "import asyncio; from src.database.migrate_user_api_keys import upgrade; asyncio.run(upgrade())"

   # Downgrade (drop table)
   uv run python -c "import asyncio; from src.database.migrate_user_api_keys import downgrade; asyncio.run(downgrade())"
   ```

### Alembic (Alternative)

Alembic is also available for traditional migration management:

```bash
# Create a new migration
uv run alembic revision --autogenerate -m "Description of changes"

# Apply migrations
uv run alembic upgrade head

# Rollback migration
uv run alembic downgrade -1

# View migration history
uv run alembic history

# Check current version
uv run alembic current
```

**Note**: Use custom migration scripts for project-specific migrations and Alembic for auto-generated schema changes.

## API Documentation

Interactive API documentation is available when the service is running:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Error Handling

The service returns standard HTTP error codes with detailed messages:

| Code | Description | Example |
|------|-------------|---------|
| 200 | Success | Request completed successfully |
| 201 | Created | Task created successfully |
| 204 | No Content | Task deleted successfully |
| 400 | Bad Request | Invalid request data |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | User doesn't own the resource |
| 404 | Not Found | Task not found |
| 422 | Validation Error | Pydantic validation failed |
| 500 | Internal Server Error | Database or server error |

**Example Error Response**:
```json
{
  "detail": "Task not found or you don't have permission to access it"
}
```

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | - | PostgreSQL connection string (asyncpg format) |
| `SESSION_HASH_SECRET` | Yes | - | Secret for hashing session tokens (must match auth-server) |
| `AUTH_SERVER_URL` | No | `http://localhost:8080` | Auth server URL for integration tests |
| `SERVICE_AUTH_TOKEN` | Yes | - | Service-to-service authentication token (must match ai-agent) |
| `ENVIRONMENT` | No | `development` | Environment (development/staging/production) |
| `CORS_ORIGINS` | No | `http://localhost:3000` | CORS allowed origins (comma-separated) |
| `SQLALCHEMY_POOL_SIZE` | No | `10` | Number of connections to keep open |
| `SQLALCHEMY_POOL_OVERFLOW` | No | `20` | Additional connections above pool_size |
| `SQLALCHEMY_POOL_TIMEOUT` | No | `30` | Seconds to wait for available connection |
| `SQLALCHEMY_POOL_RECYCLE` | No | `3600` | Seconds before recycling connections |
| `SQLALCHEMY_ECHO` | No | `false` | Log all SQL queries (true/false) |
| `REDIS_URL` | No | `redis://localhost:6379/0` | Redis connection URL for rate limiting |
| `ENCRYPTION_KEY` | Yes | - | Fernet encryption key for API key storage |

### Connection Pooling

Production settings for SQLAlchemy connection pool:

```python
pool_size=10         # Persistent connections
max_overflow=20      # Additional connections when pool exhausted
pool_timeout=30      # Wait time for connection (seconds)
pool_recycle=3600    # Recycle connections after 1 hour
```

## Testing

### Run All Tests

```bash
# Run full test suite
uv run pytest

# Run with coverage report
uv run pytest --cov=src --cov-report=html

# Run specific test suites
uv run pytest tests/unit/ -v          # Unit tests
uv run pytest tests/integration/ -v  # Integration tests
uv run pytest tests/contract/ -v     # API contract tests
```

### Linting and Type Checking

```bash
# Run ruff linter
uv run ruff check src/ tests/

# Run mypy type checker
uv run mypy src/

# Format code with ruff
uv run ruff format src/ tests/
```

## Deployment

### Docker Deployment (Future)

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install uv && uv sync --frozen
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### Production Checklist

- [ ] Set `ENV=production`
- [ ] Use strong `SERVICE_AUTH_TOKEN` (32+ characters)
- [ ] Configure proper `ALLOWED_ORIGINS` (no wildcards)
- [ ] Enable HTTPS/TLS
- [ ] Set up monitoring and logging (Sentry, DataDog, etc.)
- [ ] Use managed PostgreSQL (Neon/RDS/Cloud SQL)
- [ ] Configure health checks
- [ ] Set up auto-scaling
- [ ] Enable database backups
- [ ] Configure rate limiting

## Troubleshooting

### Database Connection Issues

**Error**: `asyncpg connection errors`

**Solution**:
- Ensure `DATABASE_URL` uses `postgresql+asyncpg://` prefix
- Use `ssl=require` (not `sslmode=require`) for asyncpg
- Verify database credentials and network connectivity
- Check firewall rules for PostgreSQL port (5432)

### Authentication Errors

**Error**: `401 Unauthorized`

**Solution**:
- Verify session token exists in `user_sessions` table
- Check token hasn't expired (`expiresAt` column)
- Ensure correct `Authorization: Bearer <token>` format
- For service auth, verify `X-Service-Auth` and `X-User-ID` headers

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

## Contributing

This service is part of the todo-app project following Spec-Driven Development (SDD) methodology.

**Development workflow**:
1. Review specifications in `specs/003-fastapi-rest-api/`
2. Follow task breakdown in `tasks.md`
3. Write tests first (TDD: RED → GREEN → REFACTOR)
4. Implement changes with proper error handling
5. Update documentation
6. Run test suite: `uv run pytest -v`
7. Create PR for review

## License

[Your License Here]

## Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Database ORM: [SQLAlchemy](https://www.sqlalchemy.org/)
- Database: [Neon Serverless PostgreSQL](https://neon.tech/)
- Package Management: [uv](https://github.com/astral-sh/uv)
- Authentication: [better-auth](https://www.better-auth.com/)
