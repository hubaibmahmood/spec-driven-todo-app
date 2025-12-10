# FastAPI Development System

> Complete FastAPI backend development environment with intelligent agents and skills for Claude Code

## Overview

This system provides a comprehensive FastAPI development environment including:

- **1 Expert Agent**: Senior FastAPI backend engineer
- **4 Focused Skills**: API patterns, testing, database, security
- **4 Slash Commands**: Quick operations for common tasks
- **Production-ready patterns**: Clean architecture, async operations, comprehensive testing

## Contents

- [Quick Start](#quick-start)
- [System Architecture](#system-architecture)
- [Agent](#agent)
- [Skills](#skills)
- [Slash Commands](#slash-commands)
- [Workflows](#workflows)
- [Best Practices](#best-practices)

## Quick Start

### Using the System

1. **Ask for FastAPI development help** - The agent activates automatically:
   ```
   "Build a user authentication API with JWT"
   "Create a CRUD endpoint for products"
   "Help me set up PostgreSQL with async SQLAlchemy"
   ```

2. **Use slash commands** for quick operations:
   ```
   /fastapi-test       # Run tests with coverage
   /fastapi-format     # Format code
   /fastapi-check      # Type check and lint
   /fastapi-new-endpoint  # Scaffold new endpoint
   ```

3. **Skills activate automatically** when relevant:
   - Writing API code → `fastapi-patterns` skill activates
   - Writing tests → `python-testing` skill activates
   - Database work → `database-integration` skill activates
   - Security implementation → `security-best-practices` skill activates

## System Architecture

```
.claude/
├── agents/
│   └── fastapi-developer.md              # Main expert agent
│
├── skills/
│   ├── fastapi-patterns/                 # API design patterns
│   │   ├── SKILL.md
│   │   ├── API-DESIGN.md
│   │   ├── EXAMPLES.md
│   │   └── templates/
│   │       └── endpoint-template.py
│   │
│   ├── python-testing/                   # Testing with pytest
│   │   ├── SKILL.md
│   │   ├── PYTEST-GUIDE.md
│   │   └── scripts/
│   │       └── run-tests.sh
│   │
│   ├── database-integration/             # PostgreSQL & SQLAlchemy
│   │   ├── SKILL.md
│   │   ├── SQLALCHEMY.md
│   │   ├── ALEMBIC.md
│   │   └── examples/
│   │       └── migration-example.py
│   │
│   └── security-best-practices/          # Auth, CORS, validation
│       ├── SKILL.md
│       ├── JWT-AUTH.md
│       ├── CORS-MIDDLEWARE.md
│       └── VALIDATION.md
│
└── commands/
    ├── fastapi-test.md                   # Run tests
    ├── fastapi-format.md                 # Format code
    ├── fastapi-check.md                  # Type check & lint
    └── fastapi-new-endpoint.md           # Scaffold endpoint
```

## Agent

### fastapi-developer

**Expert Senior FastAPI Backend Engineer**

**Responsibilities:**
- Design and implement RESTful APIs
- Use async/await for all I/O
- Follow clean architecture (routers → services → repositories)
- Implement comprehensive testing
- Apply security best practices
- Integrate with PostgreSQL using async SQLAlchemy
- Create Alembic migrations

**Auto-loaded Skills:**
- `fastapi-patterns`
- `python-testing`
- `database-integration`
- `security-best-practices`

**When it activates:**
- Proactively activates for FastAPI development tasks
- API design and implementation
- Database integration
- Authentication and security
- Testing and deployment

## Skills

### 1. fastapi-patterns

**Purpose:** API design patterns, routing, middleware, dependency injection

**Covers:**
- RESTful API design conventions
- Endpoint naming and organization
- HTTP methods and status codes
- FastAPI project structure
- Dependency injection patterns
- Middleware implementation
- Router organization
- Response models and validation
- Error handling patterns

**Supporting Files:**
- `API-DESIGN.md` - Comprehensive API design guide
- `EXAMPLES.md` - Complete working examples
- `templates/endpoint-template.py` - Reusable CRUD template

### 2. python-testing

**Purpose:** Comprehensive testing with pytest

**Covers:**
- Unit testing with pytest
- Integration testing for FastAPI
- Async test patterns
- Fixtures and conftest.py
- Parametrized tests
- Mocking and patching
- Coverage analysis
- FastAPI TestClient usage

**Supporting Files:**
- `PYTEST-GUIDE.md` - Advanced pytest features
- `scripts/run-tests.sh` - Test runner script

### 3. database-integration

**Purpose:** PostgreSQL with SQLAlchemy 2.0 async

**Covers:**
- AsyncPG driver setup
- SQLAlchemy 2.0 async patterns
- Model creation with relationships
- Async CRUD operations
- Connection pooling
- Transaction management
- Alembic migrations
- Repository pattern

**Supporting Files:**
- `SQLALCHEMY.md` - Advanced query patterns
- `ALEMBIC.md` - Migration management
- `examples/migration-example.py` - Sample migration

### 4. security-best-practices

**Purpose:** Authentication, authorization, and API security

**Covers:**
- JWT authentication (access + refresh tokens)
- OAuth2 Password Flow
- Better-auth integration (Node.js collaboration)
- CORS configuration
- Security middleware
- Input validation with Pydantic
- Password hashing
- Rate limiting
- Environment variables and secrets

**Supporting Files:**
- `JWT-AUTH.md` - JWT implementation details
- `CORS-MIDDLEWARE.md` - CORS configuration
- `VALIDATION.md` - Input validation patterns

## Slash Commands

### `/fastapi-test`

Run tests with coverage reporting.

**What it does:**
- Runs pytest with coverage
- Shows test results
- Identifies failing tests
- Highlights low coverage areas
- Suggests improvements

**Usage:**
```
/fastapi-test
```

### `/fastapi-format`

Format code with ruff.

**What it does:**
- Checks code formatting
- Applies formatting fixes
- Reports changes made
- Ensures consistent code style

**Usage:**
```
/fastapi-format
```

### `/fastapi-check`

Type checking and linting.

**What it does:**
- Runs mypy for type checking
- Runs ruff for linting
- Reports errors and warnings
- Suggests fixes

**Usage:**
```
/fastapi-check
```

### `/fastapi-new-endpoint`

Scaffold a new CRUD endpoint.

**What it does:**
- Guides you through creating a new resource
- Generates model, schemas, repository, service, router
- Creates tests
- Follows clean architecture
- Uses endpoint template

**Usage:**
```
/fastapi-new-endpoint
```

## Workflows

### Creating a New Feature

1. **Ask the agent:**
   ```
   "Create a user authentication system with JWT"
   ```

2. **Agent workflow:**
   - ✅ Designs API endpoints (fastapi-patterns skill)
   - ✅ Creates database models (database-integration skill)
   - ✅ Implements authentication (security-best-practices skill)
   - ✅ Writes comprehensive tests (python-testing skill)
   - ✅ Runs tests and validates

3. **You verify:**
   ```
   /fastapi-test    # Run tests
   /fastapi-check   # Check quality
   ```

### Adding a CRUD Endpoint

1. **Use the scaffold command:**
   ```
   /fastapi-new-endpoint
   ```

2. **Follow the prompts:**
   - Provide resource name
   - Define fields and types
   - Specify relationships

3. **Agent generates:**
   - Model (`app/models/{resource}.py`)
   - Schemas (`app/schemas/{resource}.py`)
   - Repository (`app/repositories/{resource}_repository.py`)
   - Service (`app/services/{resource}_service.py`)
   - Router (`app/api/v1/endpoints/{resources}.py`)
   - Tests (`tests/test_{resources}.py`)

4. **Integration:**
   - Adds dependencies
   - Registers router
   - Creates migration

### Writing Tests

1. **Ask for test help:**
   ```
   "Write tests for the user service"
   "Improve test coverage for authentication"
   ```

2. **Agent uses python-testing skill:**
   - Creates pytest fixtures
   - Writes unit tests
   - Writes integration tests
   - Implements mocking
   - Achieves high coverage

3. **Run tests:**
   ```
   /fastapi-test
   ```

### Database Migration

1. **Ask for database help:**
   ```
   "Create a migration for adding a posts table"
   "Set up PostgreSQL with async SQLAlchemy"
   ```

2. **Agent uses database-integration skill:**
   - Creates SQLAlchemy models
   - Configures async session
   - Generates Alembic migration
   - Applies migration

3. **Verify:**
   ```bash
   alembic current
   alembic history
   ```

## Best Practices

### Clean Architecture

Follow the layered approach:

```
API Layer (Routers)
    ↓
Service Layer (Business Logic)
    ↓
Repository Layer (Database Access)
    ↓
Models (Database Tables)
```

**Key principles:**
- ✅ No business logic in routers
- ✅ No database queries in services (use repositories)
- ✅ Clear separation of concerns
- ✅ Dependency injection throughout

### Async Everywhere

```python
# ✅ Good: Async operations
@router.get("/users/{user_id}")
async def get_user(user_id: int, service: UserService = Depends()):
    return await service.get_user(user_id)

# ❌ Bad: Sync operations
@router.get("/users/{user_id}")
def get_user(user_id: int):
    return db.query(User).filter(User.id == user_id).first()
```

### Type Hints

```python
# ✅ Good: Full type hints
async def get_user(self, user_id: int) -> User | None:
    ...

# ❌ Bad: No type hints
async def get_user(self, user_id):
    ...
```

### Comprehensive Testing

- **Unit tests**: Test services and repositories
- **Integration tests**: Test API endpoints
- **Coverage target**: 80%+ overall, 100% for critical paths
- **Test naming**: Descriptive names explaining what and why

### Security

- ✅ JWT authentication on protected endpoints
- ✅ Input validation with Pydantic
- ✅ CORS configured for specific origins
- ✅ Secrets in environment variables
- ✅ Rate limiting on sensitive endpoints
- ✅ SQL injection prevention (use ORM)
- ✅ Error messages sanitized

## Technology Stack

- **Framework**: FastAPI 0.104+
- **Language**: Python 3.11+
- **Database**: PostgreSQL (async with asyncpg)
- **ORM**: SQLAlchemy 2.0 (async)
- **Migrations**: Alembic
- **Validation**: Pydantic v2
- **Testing**: pytest + pytest-asyncio
- **Caching**: Redis + arq
- **Authentication**: JWT (python-jose)
- **Password**: passlib + bcrypt
- **Code Quality**: ruff + mypy

## Project Structure

Recommended structure for FastAPI projects:

```
fastapi-app/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   │
│   ├── api/
│   │   ├── dependencies.py
│   │   └── v1/
│   │       ├── router.py
│   │       └── endpoints/
│   │
│   ├── models/             # SQLAlchemy models
│   ├── schemas/            # Pydantic models
│   ├── services/           # Business logic
│   ├── repositories/       # Data access
│   ├── core/               # Config, security
│   ├── db/                 # Database setup
│   └── middleware/         # Custom middleware
│
├── tests/
│   ├── conftest.py
│   ├── test_endpoints/
│   ├── test_services/
│   └── test_repositories/
│
├── alembic/                # Migrations
├── .env                    # Environment variables
├── requirements.txt        # Dependencies
├── Dockerfile              # Container
└── README.md               # Documentation
```

## Getting Started with a New Project

1. **Ask the agent to set up a new FastAPI project:**
   ```
   "Set up a new FastAPI project with PostgreSQL, authentication, and tests"
   ```

2. **Agent will create:**
   - Project structure
   - Database configuration
   - Authentication system
   - Initial tests
   - Docker setup
   - Environment configuration

3. **Start developing:**
   - Use `/fastapi-new-endpoint` for new features
   - Run `/fastapi-test` after changes
   - Check quality with `/fastapi-check`

## Support and Documentation

### Skill Documentation

Each skill has comprehensive reference documentation:
- `fastapi-patterns/API-DESIGN.md`
- `python-testing/PYTEST-GUIDE.md`
- `database-integration/SQLALCHEMY.md`
- `database-integration/ALEMBIC.md`
- `security-best-practices/JWT-AUTH.md`

### Examples

Working code examples available in:
- `fastapi-patterns/EXAMPLES.md`
- `fastapi-patterns/templates/endpoint-template.py`
- `database-integration/examples/migration-example.py`

### Asking Questions

Simply ask the agent:
- "How do I implement JWT authentication?"
- "What's the best way to structure my repositories?"
- "How do I write async tests?"
- "Show me how to create a migration"

The agent will reference the appropriate skills and provide guidance.

## Reusability

### Using in Other Projects

This system is fully reusable:

1. **Copy the `.claude/` directory** to any FastAPI project
2. **Agent and skills activate automatically**
3. **No configuration needed**

### Sharing with Team

Commit `.claude/` to your repository:
```bash
git add .claude/
git commit -m "Add FastAPI development system"
git push
```

Team members get the full system when they clone.

### Creating a Plugin (Advanced)

Package as a Claude Code plugin for organization-wide distribution:

```bash
# Create plugin structure
mkdir fastapi-dev-plugin
cp -r .claude/agents fastapi-dev-plugin/
cp -r .claude/skills fastapi-dev-plugin/
cp -r .claude/commands fastapi-dev-plugin/

# Create plugin manifest
# See Claude Code plugin documentation
```

## Summary

This FastAPI development system provides:

- ✅ **Intelligent Agent**: Expert FastAPI engineer
- ✅ **Comprehensive Skills**: API patterns, testing, database, security
- ✅ **Quick Commands**: Test, format, check, scaffold
- ✅ **Production Patterns**: Clean architecture, async, security
- ✅ **Reusable**: Copy to any project
- ✅ **Team-friendly**: Share via git
- ✅ **Well-documented**: Extensive reference materials

**Ready to build production-grade FastAPI applications with AI assistance!**

---

*Generated for Claude Code - FastAPI Development System v1.0*
