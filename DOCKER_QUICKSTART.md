# Quick Start - Momentum Microservices (Docker)

Get all 5 microservices running with a single command.

## Prerequisites

- Docker 24.0+
- Docker Compose 2.20+
- 8GB+ RAM available
- Ports available: 3000, 3002, 5432, 8000, 8001, 8002

## 1. Create Environment File

### Option A: Automated Setup (Recommended)

```bash
# From project root
cd /path/to/todo-app

# Run auto-generation script
./scripts/generate-secrets.sh
```

This script will:
- Generate 3 unique cryptographic secrets (BETTER_AUTH_SECRET, JWT_SECRET, SERVICE_AUTH_TOKEN)
- Generate Fernet encryption key for API key storage
- Create `.env` file from template
- Prompt for API keys (Resend, Gemini)
- Validate all secrets are unique

**You'll be prompted for:**
- Resend API Key: https://resend.com/api-keys (free tier: 100 emails/day)
- Gemini API Key: https://aistudio.google.com/app/apikey (free tier available)

### Option B: Manual Setup

```bash
# From project root
cd /path/to/todo-app

# Copy example
cp .env.example .env

# Generate secrets (run 3 times for 3 different secrets)
openssl rand -base64 32  # For BETTER_AUTH_SECRET
openssl rand -base64 32  # For JWT_SECRET
openssl rand -base64 32  # For SERVICE_AUTH_TOKEN

# Generate Fernet key for encryption
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

**Edit `.env` and set:**
```bash
# Required secrets (must all be different!)
BETTER_AUTH_SECRET=your_generated_secret_1
JWT_SECRET=your_generated_secret_2
SERVICE_AUTH_TOKEN=your_generated_secret_3
ENCRYPTION_KEY=your_fernet_encryption_key

# Required API keys
RESEND_API_KEY=re_your_resend_api_key
AGENT_GEMINI_API_KEY=your_gemini_api_key
```

## 2. Start All Services

```bash
# Build and start everything
docker-compose up --build

# Or run in background
docker-compose up -d

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f frontend
docker-compose logs -f backend
```

## 3. Verify Services

**Check all containers are running:**
```bash
docker-compose ps
```

Expected output:
```
NAME                    STATUS    PORTS
momentum-frontend       Up        0.0.0.0:3000->3000/tcp
momentum-auth-server    Up        0.0.0.0:3002->3002/tcp
momentum-backend-api    Up        0.0.0.0:8000->8000/tcp
momentum-mcp-server     Up        0.0.0.0:8001->8001/tcp
momentum-ai-agent       Up        0.0.0.0:8002->8002/tcp
momentum-postgres       Up        0.0.0.0:5432->5432/tcp
```

**Test health endpoints:**
```bash
# Auth server
curl http://localhost:3002/health

# Backend API
curl http://localhost:8000/health

# AI Agent
curl http://localhost:8002/health

# Frontend (should return HTML)
curl http://localhost:3000
```

## 4. Access the Application

**Open in browser:**
- **Application**: http://localhost:3000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **AI Agent Docs**: http://localhost:8002/docs

**First-time setup:**
1. Go to http://localhost:3000
2. Click "Sign Up"
3. Enter email and password
4. Check email for verification link (or check logs if RESEND_API_KEY not set)
5. Verify email and log in
6. Start creating tasks with natural language!

## 5. Test Task Creation

**Via frontend (recommended):**
1. Open http://localhost:3000
2. Type: "Add urgent task for tomorrow: Review project proposal"
3. AI agent creates the task automatically

**Via API (direct):**
```bash
# Get auth token first (sign up/login via frontend)
TOKEN="your_jwt_token"

# Create task via backend API
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Review proposal",
    "description": "Review client project proposal",
    "completed": false
  }'
```

## 6. Stop Services

```bash
# Stop all containers
docker-compose down

# Stop and remove volumes (⚠️ deletes database data)
docker-compose down -v

# Rebuild from scratch
docker-compose down -v && docker-compose up --build
```

## Service Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (Next.js)                   │
│                     http://localhost:3000                   │
└────────────┬────────────────────────────────────────────────┘
             │
             ├─────────────────────────────────────────────────┐
             │                                                 │
             ▼                                                 ▼
┌────────────────────────┐                    ┌────────────────────────┐
│   Auth Server          │                    │   AI Agent             │
│   (better-auth)        │                    │   (Gemini 2.5)         │
│   Port: 3002           │                    │   Port: 8002           │
└────────────┬───────────┘                    └────────────┬───────────┘
             │                                             │
             │                                             │
             │                 ┌───────────────────────────┘
             │                 │
             ▼                 ▼
┌────────────────────────────────────────┐
│         Backend API (FastAPI)          │
│         Port: 8000                     │
└────────────┬───────────────────────────┘
             │
             ├─────────────────┐
             │                 │
             ▼                 ▼
┌────────────────────┐    ┌────────────────────┐
│  PostgreSQL DB     │    │  MCP Server        │
│  Port: 5432        │    │  Port: 8001        │
└────────────────────┘    └────────────────────┘
```

## Port Reference

| Service       | Port | Purpose                          |
|---------------|------|----------------------------------|
| Frontend      | 3000 | Next.js web application          |
| Auth Server   | 3002 | Authentication (better-auth)     |
| Backend API   | 8000 | Task management REST API         |
| MCP Server    | 8001 | Model Context Protocol (tools)   |
| AI Agent      | 8002 | Natural language task interface  |
| PostgreSQL    | 5432 | Shared database                  |

## Troubleshooting

### Services won't start

**Check logs:**
```bash
docker-compose logs
```

**Common issues:**
1. Missing environment variables → Check `.env` file
2. Ports already in use → Stop conflicting services
3. Insufficient memory → Allocate more RAM to Docker

### Database connection errors

**Reset database:**
```bash
docker-compose down -v
docker-compose up -d db
# Wait 10 seconds for DB to initialize
docker-compose up
```

### Frontend can't connect to services

**Check network:**
```bash
docker network inspect momentum-network
```

**Verify service names resolve:**
```bash
docker exec momentum-frontend ping backend
docker exec momentum-frontend ping auth-server
```

### Email verification not working

**Check Resend configuration:**
```bash
docker-compose logs auth-server | grep -i email
```

**Development workaround:**
- Set `NODE_ENV=development` in `.env`
- Verification links will print to auth-server logs

### AI agent errors

**Check Gemini API key:**
```bash
docker-compose exec ai-agent env | grep GEMINI
```

**Test Gemini directly:**
```bash
curl -X POST http://localhost:8002/api/v1/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Create task: Test AI"}'
```

## Development Workflow

### Hot Reload

Individual services support hot reload via volume mounts (check each `docker-compose.yml`).

**Frontend hot reload:**
```bash
# Edit frontend/src files
# Changes automatically reflected (Next.js Fast Refresh)
```

**Backend hot reload:**
```bash
# Edit backend/src files
# Uvicorn auto-reloads on file changes
```

### Rebuild Single Service

```bash
# Rebuild and restart specific service
docker-compose up -d --build frontend

# View logs
docker-compose logs -f frontend
```

### Database Migrations

**Auth server (Prisma):**
```bash
# Auto-run on container start via entrypoint.sh

# Manual migration
docker-compose exec auth-server npx prisma migrate deploy
```

**Backend (Alembic):**
```bash
# Auto-run on container start via entrypoint.sh

# Manual migration
docker-compose exec backend alembic upgrade head
```

### Access Database

```bash
# PostgreSQL CLI
docker-compose exec db psql -U postgres -d momentum

# List tables
\dt

# Query users
SELECT email, name FROM "user";

# Query tasks
SELECT id, title, completed FROM tasks;
```

## Production Deployment

For production, consider:

1. **Use managed database** (Neon, AWS RDS, etc.)
2. **Set `NODE_ENV=production`**
3. **Use HTTPS** for all services
4. **Set strong secrets** (32+ characters)
5. **Configure CORS** properly
6. **Enable SSL/TLS** for database connections
7. **Use container orchestration** (Kubernetes, ECS, etc.)
8. **Set up monitoring** (health checks, logs, metrics)

## Clean Up

**Remove everything:**
```bash
# Stop and remove containers, networks, volumes
docker-compose down -v

# Remove images
docker-compose down --rmi all -v

# Prune system (⚠️ removes all unused Docker resources)
docker system prune -a --volumes
```

## Next Steps

- Explore API documentation: http://localhost:8000/docs
- Read individual service READMEs:
  - `frontend/DOCKER_README.md`
  - `auth-server/DOCKER_README.md`
  - `backend/DOCKER_README.md`
  - `ai-agent/DOCKER_README.md`
  - `mcp-server/DOCKER_README.md`
- Configure production deployment
- Set up CI/CD pipeline
- Enable monitoring and logging
