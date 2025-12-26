# Momentum - AI-Powered Task Management Platform

A production-ready, full-stack task management application with natural language AI integration, built using **Spec-Driven Development (SDD)** methodology. This project demonstrates modern microservices architecture with FastAPI backend, Next.js frontend, AI agent service, and dedicated authentication microservice.

## Architecture Overview

Momentum is built as a modern microservices architecture with five core services:

```
┌─────────────┐
│  Frontend   │ (Next.js 16 - Port 3000)
│  Dashboard  │ • Task Management UI
└──────┬──────┘ • AI Chat Interface
       │        • Real-time Updates
       ├─────────────────┬─────────────────┬──────────────┐
       │                 │                 │              │
┌──────▼──────┐  ┌──────▼──────┐  ┌──────▼──────┐ ┌────▼─────┐
│   Backend   │  │  AI Agent   │  │ Auth Server │ │   MCP    │
│     API     │  │   Service   │  │   Service   │ │  Server  │
└─────────────┘  └─────────────┘  └─────────────┘ └──────────┘
   Port 8000        Port 8002        Port 3002      Port 8001
       │                 │                 │              │
       └─────────────────┴─────────────────┴──────────────┘
                            │
                   ┌────────▼────────┐
                   │   PostgreSQL    │
                   │ (Neon Serverless)│
                   └─────────────────┘
```

- **Frontend** (Next.js 16) - Modern dashboard with real-time updates and AI chat interface
- **Backend API** (FastAPI) - RESTful API with task management and API key encryption
- **AI Agent** (FastAPI + Gemini) - Natural language task management via conversational AI
- **Auth Server** (Node.js/better-auth) - Email/password authentication and session management
- **MCP Server** (Python/FastMCP) - Tool integration layer for AI agent capabilities

All services share a single PostgreSQL database (Neon serverless) for data consistency and simplified deployment.

## Features

### 🤖 AI-Powered Task Management
- **Natural Language Interface** - Manage tasks through conversational AI using Gemini 2.5 Flash
- **Intelligent Parsing** - Understands dates, priorities, and context ("add urgent task for tomorrow")
- **Multi-Turn Conversations** - Maintains context across chat sessions with smart token management
- **Real-Time Feedback** - Instant UI updates showing operation status (success/failure indicators)
- **User-Specific API Keys** - Encrypted Gemini API key storage per user with Fernet encryption
- **Timezone-Aware** - Automatically interprets dates/times in user's local timezone

### 🎯 Task Management
- **Complete CRUD Operations** - Create, read, update, delete tasks via UI or natural language
- **Priority Levels** - URGENT, HIGH, MEDIUM, LOW priority support
- **Due Dates & Deadlines** - Task scheduling with timezone awareness
- **Real-Time Updates** - Dashboard cards update instantly without page refresh
- **Event-Driven Architecture** - Custom events sync UI across all components
- **User Isolation** - Each user can only access their own tasks

### 🔐 Authentication & Security
- **Email/Password Authentication** - Secure registration and login with bcrypt hashing
- **Email Verification** - Mandatory verification using Resend email service
- **Session Management** - Multiple concurrent sessions with device tracking
- **Password Recovery** - Secure password reset flow via email
- **Service-to-Service Auth** - X-Service-Auth header pattern for microservices
- **API Key Encryption** - Fernet encryption for user API keys at rest

### 💻 Modern Frontend
- **Next.js 16 App Router** - Server Components and optimized rendering
- **Responsive Design** - Mobile-first approach with Tailwind CSS 4
- **Floating Chat Widget** - Collapsible AI chat panel for natural language task management
- **Processing Indicators** - Shows "Processing..." while AI agent works
- **Conversation History** - Persistent chat sessions across page navigation
- **Error Handling** - Clear error messages with warning icons

### ⚡ Performance & Infrastructure
- **Async Operations** - Non-blocking database queries with SQLAlchemy async
- **Connection Pooling** - Optimized database connection management
- **Rate Limiting** - User-based rate limits with Redis
- **Custom Migrations** - Python-based database migration scripts
- **CORS Configuration** - Proper cross-origin support for microservices

## Quick Start

### Prerequisites

- **Python 3.12+** - For backend API, AI agent, and MCP server
- **Node.js 20+** - For auth server and frontend
- **PostgreSQL** - Neon serverless PostgreSQL recommended
- **Redis** - For rate limiting (optional)
- **uv** - Python package manager ([install](https://github.com/astral-sh/uv))
- **Gemini API Key** - From [Google AI Studio](https://ai.google.dev/)
- **Resend API Key** - From [resend.com](https://resend.com) for email verification

> **📚 Detailed Setup**: Each service has its own comprehensive README with detailed setup instructions:
> - [Backend API](./backend/README.md) - Port 8000
> - [AI Agent](./ai-agent/README.md) - Port 8002
> - [Auth Server](./auth-server/README.md) - Port 3002
> - [Frontend](./frontend/README.md) - Port 3000
> - [MCP Server](./mcp-server/README.md) - Port 8001

### Full Stack Setup

#### 1. Clone and Setup Database

```bash
git clone https://github.com/hubaibmahmood/momentum.git
cd momentum

# Create a Neon PostgreSQL database at https://neon.tech
# Note your DATABASE_URL - it will be used in all service .env files
```

#### 2. Start Services (in order)

**Backend API** (Port 8000)
```bash
cd backend
cp .env.example .env  # Configure DATABASE_URL and secrets
uv sync
uv run python -c "import asyncio; from src.database.migrations import init_db; asyncio.run(init_db())"
uv run uvicorn src.api.main:app --reload --port 8000
```

**Auth Server** (Port 3002)
```bash
cd auth-server
cp .env.example .env  # Configure DATABASE_URL, RESEND_API_KEY
npm install && npx prisma generate && npx prisma db push
npm run dev
```

**MCP Server** (Port 8001)
```bash
cd mcp-server
cp .env.example .env  # Configure SERVICE_AUTH_TOKEN
uv sync
uv run python -m src.server
```

**AI Agent** (Port 8002)
```bash
cd ai-agent
cp .env.example .env  # Configure AGENT_GEMINI_API_KEY, BACKEND_URL
uv sync
uv run alembic upgrade head
uv run uvicorn ai_agent.main:app --reload --port 8002
```

**Frontend** (Port 3000)
```bash
cd frontend
cp .env.local.example .env.local  # Configure API URLs
npm install
npm run dev
```

> **🔧 Service Order Matters**: Start services in the order shown above. AI Agent depends on Backend and MCP Server.

### Key Environment Variables

**Critical Shared Variables** (must match across services):
- `DATABASE_URL` - PostgreSQL connection string (all Python services)
- `SERVICE_AUTH_TOKEN` - Service-to-service auth token (backend ↔ ai-agent ↔ mcp-server)
- `SESSION_HASH_SECRET` - Session token hashing (backend ↔ auth-server)

**Service-Specific**:
- `AGENT_GEMINI_API_KEY` - Gemini API key (ai-agent)
- `RESEND_API_KEY` + `EMAIL_FROM` - Email service (auth-server)
- `ENCRYPTION_KEY` - Fernet key for API key encryption (backend)

> See individual `.env.example` files in each service directory for complete configuration details.


## Development Workflow

This project follows **Spec-Driven Development (SDD)** using [SpecKit Plus](https://github.com/panaversity/spec-kit-plus):

### Feature Development Lifecycle

1. **Specification** (`/sp.specify`)
   - Write business requirements in plain language
   - Define user stories and acceptance criteria
   - Document edge cases and constraints

2. **Planning** (`/sp.plan`)
   - Create technical architecture
   - Design data models and interfaces
   - Define implementation strategy

3. **Task Generation** (`/sp.tasks`)
   - Break down into atomic, testable tasks
   - Organize by user story and priority
   - Identify parallel execution opportunities

4. **Implementation** (`/sp.implement`)
   - Follow TDD: tests before implementation
   - Complete tasks phase by phase
   - Track progress in tasks.md

5. **Git Workflow** (`/sp.git.commit_pr`)
   - Commit with descriptive messages
   - Create pull requests with context
   - Merge to main after review

### Documentation Generated Per Feature

Each feature in `specs/<feature-name>/` includes:

- `spec.md` - Business requirements and user stories
- `plan.md` - Technical architecture and decisions
- `tasks.md` - Atomic implementation tasks
- `data-model.md` - Entity definitions and relationships
- `contracts/` - API interfaces and test contracts
- `research.md` - Technical investigation findings
- `quickstart.md` - Implementation guide

### Traceability

All development sessions are recorded as **Prompt History Records (PHRs)** in `history/prompts/`:

- Full prompt and response text
- Files modified and tests run
- Stage (spec/plan/tasks/implementation)
- Links to related artifacts

## Testing

### Backend API Tests

```bash
cd backend

# Run all tests with coverage
pytest --cov=src --cov-report=html

# Run specific test suites
pytest tests/unit/ -v           # Unit tests
pytest tests/integration/ -v    # Integration tests
pytest tests/contract/ -v       # Contract tests

# Linting and type checking
ruff check src/ tests/          # Run ruff linter
mypy src/                       # Run mypy type checker
```

### Auth Server Tests

```bash
cd auth-server

# Run tests
npm test

# Type checking
npx tsc --noEmit

# Linting
npm run lint
```

### Frontend Tests

```bash
cd frontend

# Run tests (when implemented)
npm test

# Type checking
npx tsc --noEmit

# Linting
npm run lint
```

## Tech Stack

### Backend Services

**Backend API** (Python/FastAPI)
- FastAPI 0.127.0+, SQLAlchemy 2.0 (async), Pydantic 2.0+
- Custom Python migrations, Fernet encryption
- Redis rate limiting, CORS middleware

**AI Agent** (Python/FastAPI + Gemini)
- OpenAI Agents SDK 0.6.4+, Gemini 2.5 Flash backend
- MCP 1.25.0+ (Model Context Protocol), tiktoken
- SQLModel + Alembic, timezone-aware parsing

**MCP Server** (Python/FastMCP)
- FastMCP (official MCP Python SDK), httpx (async client)
- Service-to-service authentication pattern

### Frontend & Auth

**Frontend** (TypeScript/Next.js)
- Next.js 16+ (App Router), React 18+, TypeScript 5.x
- Tailwind CSS 4, date-fns, better-auth client
- Real-time event-driven UI updates

**Auth Server** (TypeScript/Node.js)
- Express.js, better-auth 1.4+, Prisma ORM
- Resend email service, bcrypt hashing
- Vercel serverless deployment

### Infrastructure

- **Database**: Neon Serverless PostgreSQL (shared)
- **Cache**: Redis (rate limiting)
- **Package Managers**: uv (Python), npm (Node.js)
- **Development**: SpecKit Plus (Spec-Driven Development)
- **AI Tools**: Claude Code, Google AI Studio (Gemini)

## Architecture Decisions

Key architectural choices documented in feature specs:

### Full-Stack Architecture
- **Microservices Pattern** - Separate services for API, auth, and frontend
- **Shared Database** - PostgreSQL shared between FastAPI and auth server
- **Session-Based Auth** - JWT tokens stored in database, validated on each request
- **Cross-Origin** - CORS configured for frontend-backend communication
- **Rate Limiting** - User-based rate limiting with IP fallback
- **API-First Design** - RESTful API contracts drive frontend development

### Backend Decisions
- **Async SQLAlchemy** - Non-blocking database operations for high concurrency
- **Pydantic Validation** - Request/response validation with automatic OpenAPI docs
- **Alembic Migrations** - Version-controlled database schema changes
- **Repository Pattern** - Clean separation between API and data access layers
- **Error Handling** - Structured error responses with proper HTTP status codes

### Authentication Decisions
- **better-auth Library** - Production-ready auth with built-in security features
- **Email Verification** - Mandatory verification using Resend email service
- **Multiple Sessions** - Users can maintain sessions across multiple devices
- **OAuth Integration** - Google sign-in for streamlined user onboarding
- **Database-Driven Tokens** - Session validation against PostgreSQL (not cryptographic)

### Frontend Decisions
- **Next.js App Router** - Server Components for improved performance and SEO
- **URL State Management** - Search params for filter/search persistence and shareability
- **TypeScript Strict Mode** - Type safety across the entire application
- **Tailwind CSS 4** - Utility-first styling with modern CSS features
- **Client-Side API Calls** - Fetch API with proper error handling and loading states
- **Responsive Design** - Mobile-first approach with adaptive layouts

## API Documentation

Once the backend is running, you can access:

- **OpenAPI Docs**: `http://localhost:8000/docs` - Interactive API documentation
- **ReDoc**: `http://localhost:8000/redoc` - Alternative API documentation
- **Health Check**: `http://localhost:8000/health` - Service health status

### Key API Endpoints

```
POST   /api/tasks              - Create a new task
GET    /api/tasks              - Get all user tasks
GET    /api/tasks/{id}         - Get specific task
PATCH  /api/tasks/{id}         - Update task
DELETE /api/tasks/{id}         - Delete task
PATCH  /api/tasks/{id}/complete - Toggle task completion
```

All endpoints require authentication via `Authorization: Bearer <token>` header.

## Deployment

The application is designed for cloud deployment:

- **Backend**: Render.com (see `backend/DEPLOYMENT_RENDER.md`)
- **Auth Server**: Vercel serverless (see `auth-server/DEPLOYMENT.md`)
- **Frontend**: Netlify (see `frontend/DEPLOYMENT.md`)

Each component includes deployment configuration files and detailed deployment guides.

## Contributing

This project follows Spec-Driven Development. To contribute:

1. **Specify the feature** - Write a spec in `specs/<feature-name>/spec.md`
2. **Plan the implementation** - Create architecture plan
3. **Generate tasks** - Break down into atomic tasks
4. **Implement with TDD** - Tests first, then code
5. **Document decisions** - Update specs and create PHRs
6. **Submit PR** - Include spec, tests, and implementation

## License

This project is a demonstration of Spec-Driven Development methodology.

## Acknowledgments

- Built with [SpecKit Plus](https://github.com/panaversity/spec-kit-plus) - Spec-Driven Development framework
- Developed with [Claude Code](https://claude.com/claude-code) - AI-powered development assistant

## Project Status

**Current Version**: 2.0.0 (AI-Powered Production Release)

### Latest Updates (2025)

**🤖 AI Integration (Specs 007-010)**
- ✅ Natural language task management with Gemini 2.5 Flash
- ✅ Conversational AI with multi-turn context (800k token budget)
- ✅ MCP server integration for tool calling
- ✅ Per-user encrypted API key storage
- ✅ Real-time operation feedback in chat UI

**💬 Enhanced Frontend (Spec 009)**
- ✅ Floating chat widget with conversation history
- ✅ Real-time dashboard updates (no page refresh needed)
- ✅ Event-driven architecture for instant UI sync
- ✅ Processing indicators and error handling

**🔐 Security Improvements (Spec 010)**
- ✅ Service-to-service authentication pattern
- ✅ Fernet encryption for API keys at rest
- ✅ Rate limiting for test operations (5/hour per user)

### Core Features

- ✅ **Backend API** - FastAPI with async PostgreSQL, custom migrations, API key encryption
- ✅ **AI Agent Service** - Gemini-powered natural language task management
- ✅ **MCP Server** - Tool integration layer with service-to-service auth
- ✅ **Auth Server** - Email/password auth with email verification (no OAuth currently)
- ✅ **Frontend** - Next.js 16 with real-time updates and AI chat interface
- ✅ **Cloud Deployment** - Production-ready on Render, Vercel, and Netlify

### Development Methodology

This project demonstrates **Spec-Driven Development (SDD)** using SpecKit Plus:

- Every feature starts with a detailed specification
- Implementation follows TDD principles
- Full traceability from spec to code via PHRs (Prompt History Records)
- Architecture decisions documented in ADRs
- Clean separation between business requirements and technical implementation

---
