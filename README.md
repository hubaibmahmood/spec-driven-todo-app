# Momentum - Full-Stack Task Management Platform

A production-ready, full-stack task management application built using **Spec-Driven Development (SDD)** methodology. This project demonstrates modern web application architecture with FastAPI backend, Next.js frontend, and microservices authentication.

## Architecture Overview

Momentum is built as a modern microservices architecture with three core components:

- **Backend API** (Python/FastAPI) - RESTful API with PostgreSQL database, async operations
- **Auth Server** (Node.js/TypeScript) - Dedicated authentication microservice using better-auth
- **Frontend** (Next.js 16) - Modern dashboard with App Router, Server Components, and Tailwind CSS

All services share a single PostgreSQL database (Neon serverless) for data consistency and simplified deployment.

## Features

### Current Capabilities

#### Backend API (FastAPI)
- **RESTful Endpoints** - Complete CRUD operations for tasks
- **User Authentication** - Session-based auth with JWT tokens
- **Database Integration** - PostgreSQL with SQLAlchemy 2.0 async ORM
- **Rate Limiting** - User-based rate limiting (100 req/min read, 30 req/min write)
- **CORS Support** - Configured for cross-origin requests
- **Input Validation** - Pydantic models with comprehensive validation
- **Error Handling** - Structured error responses with proper HTTP status codes
- **Database Migrations** - Alembic for schema versioning
- **Task Filtering** - User-specific task isolation

#### Authentication Server (better-auth)
- **Email/Password Auth** - Secure registration and login with bcrypt hashing
- **Email Verification** - Mandatory verification using Resend email service
- **OAuth Integration** - Google sign-in support
- **Session Management** - Multiple concurrent sessions with device tracking
- **Password Recovery** - Secure password reset flow
- **JWT Tokens** - 15-minute access tokens, 7-day refresh tokens
- **Database-Driven** - Session validation against PostgreSQL

#### Frontend Dashboard (Next.js)
- **Modern UI** - Responsive design with Tailwind CSS 4
- **Authentication** - Sign-in/Sign-up forms integrated with auth server
- **Task Management** - Complete CRUD operations via API
- **Real-time Stats** - Dashboard with task statistics and completion rates
- **Search & Filter** - Filter by status (All/Active/Completed) with URL state
- **Priority & Due Dates** - Task priority levels and deadline tracking
- **Mobile Responsive** - Sidebar navigation with mobile toggle
- **Email Verification** - Full-width modern verification pages

## Quick Start

### Prerequisites

- **Python 3.12+** - For backend API
- **Node.js 20+** - For auth server and frontend
- **PostgreSQL** - Neon serverless PostgreSQL (or local instance)
- **uv** - Python package manager ([install](https://github.com/astral-sh/uv))

### Full Stack Setup

#### 1. Clone Repository

```bash
git clone https://github.com/hubaibmahmood/momentum.git
cd momentum
```

#### 2. Database Setup

Create a Neon PostgreSQL database or use a local PostgreSQL instance:

```bash
# Set up your DATABASE_URL in .env files (see .env.example in each directory)
# Example: postgresql+asyncpg://user:password@host/database
```

#### 3. Backend API Setup

```bash
cd backend

# Create .env file (copy from .env.example and configure)
cp .env.example .env

# Install dependencies
uv sync

# Run database migrations
alembic upgrade head

# Start the FastAPI server
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

Backend API will be available at `http://localhost:8000`

#### 4. Auth Server Setup

```bash
cd auth-server

# Create .env file (copy from .env.example and configure)
cp .env.example .env

# Install dependencies
npm install

# Generate Prisma client
npx prisma generate

# Push database schema
npx prisma db push

# Start the auth server
npm run dev
```

Auth server will be available at `http://localhost:3001`

#### 5. Frontend Setup

```bash
cd frontend

# Create .env file (copy from .env.example and configure)
cp .env.example .env

# Install dependencies
npm install

# Start the Next.js development server
npm run dev
```

Frontend will be available at `http://localhost:3000`

### Environment Variables

Each component requires specific environment variables. See `.env.example` files in:
- `backend/.env.example` - Database URL, CORS origins, session secret
- `auth-server/.env.example` - Database URL, better-auth config, Resend API key, OAuth credentials
- `frontend/.env.example` - Backend API URL, Auth server URL

## Project Structure

```
momentum/
├── backend/                      # FastAPI REST API
│   ├── src/
│   │   ├── api/                 # API layer
│   │   │   ├── main.py         # FastAPI application
│   │   │   ├── routers/        # API route handlers
│   │   │   └── schemas/        # Pydantic models
│   │   ├── database/           # Database layer
│   │   │   ├── connection.py  # SQLAlchemy engine
│   │   │   └── models/        # ORM models
│   │   ├── services/           # Business logic
│   │   └── config.py           # Configuration settings
│   ├── alembic/                # Database migrations
│   ├── tests/                  # API tests
│   └── pyproject.toml          # Python dependencies
│
├── auth-server/                 # Authentication microservice
│   ├── src/
│   │   ├── auth/               # better-auth configuration
│   │   ├── config/             # Server configuration
│   │   └── index.ts            # Express server
│   ├── api/                    # Vercel serverless functions
│   ├── prisma/                 # Prisma schema for auth tables
│   └── package.json            # Node.js dependencies
│
├── frontend/                    # Next.js dashboard
│   ├── app/                    # Next.js App Router
│   │   ├── (auth)/            # Auth routes (sign-in, sign-up)
│   │   ├── dashboard/         # Protected dashboard routes
│   │   └── layout.tsx         # Root layout
│   ├── components/             # React components
│   ├── lib/                    # Utilities and API clients
│   ├── hooks/                  # Custom React hooks
│   └── package.json            # Node.js dependencies
│
├── specs/                       # Feature specifications (SDD)
│   ├── 003-fastapi-rest-api/   # Backend API specification
│   ├── 004-auth-server/        # Authentication service spec
│   └── 005-nextjs-dashboard-migration/  # Frontend dashboard spec
│
├── history/prompts/             # Development history (PHRs)
│   ├── constitution/           # Project principles
│   ├── 001-add-task/          # Feature development records
│   └── .../                   # Other feature histories
│
└── .specify/                    # SpecKit Plus framework
    ├── memory/                 # Constitution and guidelines
    └── templates/              # Spec templates
```

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

### Backend API
- **Framework**: FastAPI 0.104+
- **Language**: Python 3.12+
- **Database**: PostgreSQL (Neon serverless)
- **ORM**: SQLAlchemy 2.0+ (async)
- **Migrations**: Alembic 1.13+
- **Validation**: Pydantic 2.0+
- **Server**: Uvicorn (ASGI)
- **Rate Limiting**: SlowAPI with Redis
- **Testing**: pytest, pytest-asyncio, httpx
- **Type Checking**: mypy
- **Linting**: ruff

### Authentication Server
- **Framework**: Express.js
- **Language**: TypeScript 5.x
- **Runtime**: Node.js 20+
- **Auth Library**: better-auth 1.4+
- **Database ORM**: Prisma
- **Email Service**: Resend
- **Password Hashing**: bcrypt
- **Deployment**: Vercel serverless functions

### Frontend
- **Framework**: Next.js 16.0+ (App Router)
- **Language**: TypeScript 5.x
- **Runtime**: Node.js 20+
- **UI Library**: React 19.2+
- **Styling**: Tailwind CSS 4
- **Charts**: Recharts 3.5+
- **Icons**: Lucide React
- **State Management**: URL Search Params
- **Deployment**: Netlify

### Development Framework
- **Methodology**: [SpecKit Plus](https://github.com/panaversity/spec-kit-plus) - Spec-Driven Development
- **Version Control**: Git with feature branch workflow
- **Documentation**: Markdown specs with traceability
- **AI Assistant**: [Claude Code](https://claude.com/claude-code) for development

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

**Current Version**: 1.0.0 (Full-Stack Production Release)

### Completed Features

- ✅ **Backend API (FastAPI)** - RESTful API with PostgreSQL, authentication, rate limiting
- ✅ **Authentication Server** - better-auth microservice with email verification and OAuth
- ✅ **Frontend Dashboard** - Next.js 16 with modern UI, task management, and statistics
- ✅ **Database Integration** - SQLAlchemy async ORM with Alembic migrations
- ✅ **User Authentication** - JWT tokens, session management, password recovery
- ✅ **Task Management** - CRUD operations with priority levels and due dates
- ✅ **Cloud Deployment** - Production-ready deployment on Render, Vercel, and Netlify

### Development Methodology

This project demonstrates **Spec-Driven Development (SDD)** using SpecKit Plus:

- Every feature starts with a detailed specification
- Implementation follows TDD principles
- Full traceability from spec to code via PHRs (Prompt History Records)
- Architecture decisions documented in ADRs
- Clean separation between business requirements and technical implementation

---
