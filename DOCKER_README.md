# Momentum - Dockerized Microservices Architecture

Complete Docker orchestration for all 5 microservices with a single command.

## Overview

This Docker setup provides production-ready containerization for the entire Momentum application stack:

- **Frontend**: Next.js 16 + React 19 + TypeScript
- **Auth Server**: Node.js + Express + better-auth
- **Backend API**: FastAPI + SQLAlchemy + PostgreSQL
- **MCP Server**: Python + FastMCP (Model Context Protocol)
- **AI Agent**: Python + Gemini 2.5 Flash
- **Database**: PostgreSQL 16 (shared by all services)

## Quick Start

**TL;DR:**
```bash
cp .env.example .env
# Edit .env with your API keys
docker-compose up --build
```

Access: http://localhost:3000

## Architecture

```
                    ┌─────────────────┐
                    │   Frontend      │
                    │   Next.js       │
                    │   Port: 3000    │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ Auth Server  │    │  Backend API │    │  AI Agent    │
│ better-auth  │    │  FastAPI     │    │  Gemini      │
│ Port: 3002   │    │  Port: 8000  │    │  Port: 8002  │
└──────┬───────┘    └──────┬───────┘    └──────┬───────┘
       │                   │                   │
       │         ┌─────────┴─────────┐        │
       │         │                   │        │
       ▼         ▼                   ▼        ▼
┌─────────────────────┐        ┌──────────────────┐
│  PostgreSQL DB      │        │  MCP Server      │
│  Port: 5432         │        │  Port: 8001      │
└─────────────────────┘        └──────────────────┘
```

## Service Details

### Frontend (Port 3000)
- **Framework**: Next.js 16 with App Router
- **Runtime**: Node.js 20 Alpine
- **Image Size**: ~150-200MB (standalone build)
- **Health Check**: `GET http://localhost:3000`
- **Dependencies**: auth-server, backend, ai-agent

### Auth Server (Port 3002)
- **Framework**: Express.js + TypeScript
- **Authentication**: better-auth (email + password)
- **Runtime**: Node.js 20 Alpine
- **Image Size**: ~150-200MB
- **Health Check**: `GET http://localhost:3002/health`
- **Dependencies**: PostgreSQL

### Backend API (Port 8000)
- **Framework**: FastAPI + SQLAlchemy 2.0
- **Runtime**: Python 3.12 Alpine with uv
- **Image Size**: ~200MB
- **Health Check**: `GET http://localhost:8000/health`
- **Dependencies**: PostgreSQL
- **API Docs**: http://localhost:8000/docs

### MCP Server (Port 8001)
- **Framework**: FastMCP (Model Context Protocol)
- **Runtime**: Python 3.12 Alpine with uv
- **Image Size**: ~180MB
- **Health Check**: Process check (pgrep)
- **Dependencies**: Backend API
- **Purpose**: Tool calling layer for AI agent

### AI Agent (Port 8002)
- **Framework**: FastAPI + Gemini 2.5 Flash
- **Runtime**: Python 3.12 Alpine with uv
- **Image Size**: ~200MB
- **Health Check**: `GET http://localhost:8002/health`
- **Dependencies**: PostgreSQL, Backend API, MCP Server
- **API Docs**: http://localhost:8002/docs

### PostgreSQL (Port 5432)
- **Version**: PostgreSQL 16 Alpine
- **Image Size**: ~250MB
- **Storage**: Named volume `momentum-postgres-data`
- **Health Check**: `pg_isready`

## Environment Variables

### Required Secrets

Generate with `openssl rand -base64 32`:

```bash
BETTER_AUTH_SECRET=<32+ characters>
JWT_SECRET=<32+ characters>
SERVICE_AUTH_TOKEN=<32+ characters>
```

### Required API Keys

```bash
RESEND_API_KEY=re_xxxxx           # From resend.com
AGENT_GEMINI_API_KEY=AIzaSyXXXXX  # From Google AI Studio
```

### Database Configuration

For Docker Compose (auto-configured):
```bash
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=momentum
```

For production (use Neon/managed PostgreSQL):
```bash
DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require
```

### CORS & URLs

```bash
FRONTEND_URL=http://localhost:3000
BETTER_AUTH_URL=http://localhost:3002
CORS_ORIGINS=http://localhost:3000

# Frontend build-time variables
NEXT_PUBLIC_AUTH_URL=http://localhost:3002/api/auth
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_AI_AGENT_URL=http://localhost:8002
```

See `.env.example` for complete list.

## Usage

### Start All Services

```bash
# Build and start (first time)
docker-compose up --build

# Start in background
docker-compose up -d

# Follow logs
docker-compose logs -f

# View specific service
docker-compose logs -f frontend
```

### Stop Services

```bash
# Stop containers (keeps data)
docker-compose down

# Stop and remove data (⚠️ deletes database)
docker-compose down -v
```

### Rebuild Single Service

```bash
docker-compose up -d --build frontend
docker-compose up -d --build backend
```

### View Service Status

```bash
docker-compose ps
docker-compose top
```

## Database Management

### Access PostgreSQL CLI

```bash
docker-compose exec db psql -U postgres -d momentum
```

### Common Queries

```sql
-- List all tables
\dt

-- View users
SELECT id, email, name, "emailVerified" FROM "user";

-- View tasks
SELECT id, user_id, title, completed FROM tasks;

-- View sessions
SELECT "userId", token, "expiresAt" FROM user_sessions;
```

### Run Migrations

**Auth Server (Prisma):**
```bash
# Auto-run on startup via entrypoint.sh

# Manual migration
docker-compose exec auth-server npx prisma migrate deploy
```

**Backend (Alembic):**
```bash
# Auto-run on startup via entrypoint.sh

# Manual migration
docker-compose exec backend alembic upgrade head
```

### Backup Database

```bash
# Dump to file
docker-compose exec db pg_dump -U postgres momentum > backup.sql

# Restore from file
docker-compose exec -T db psql -U postgres momentum < backup.sql
```

## Networking

All services communicate via the `momentum-network` bridge network. Service names resolve as hostnames:

- `db` → PostgreSQL
- `auth-server` → Auth service
- `backend` → Backend API
- `mcp-server` → MCP server
- `ai-agent` → AI agent service
- `frontend` → Next.js app

**Example: Backend connects to database:**
```
DATABASE_URL=postgresql://postgres:postgres@db:5432/momentum
                                             ^^
                                    Docker service name
```

## Health Checks

All services implement health checks for reliability:

### Check Individual Service

```bash
curl http://localhost:3002/health  # Auth server
curl http://localhost:8000/health  # Backend API
curl http://localhost:8002/health  # AI Agent
curl http://localhost:3000         # Frontend
```

### Check Container Health Status

```bash
docker inspect --format='{{.State.Health.Status}}' momentum-frontend
docker inspect --format='{{.State.Health.Status}}' momentum-backend-api
```

### Startup Dependencies

Services wait for their dependencies to be healthy:

1. **PostgreSQL** starts first
2. **Auth Server** waits for PostgreSQL
3. **Backend API** waits for PostgreSQL
4. **MCP Server** waits for Backend
5. **AI Agent** waits for PostgreSQL, Backend, MCP
6. **Frontend** waits for Auth, Backend, AI Agent

## Performance & Resource Usage

### Memory Requirements

| Service       | Memory (Idle) | Memory (Active) |
|---------------|---------------|-----------------|
| Frontend      | ~100MB        | ~200MB          |
| Auth Server   | ~100MB        | ~150MB          |
| Backend API   | ~80MB         | ~150MB          |
| MCP Server    | ~60MB         | ~100MB          |
| AI Agent      | ~100MB        | ~200MB          |
| PostgreSQL    | ~50MB         | ~100MB          |
| **Total**     | ~490MB        | ~900MB          |

### Startup Time

- **Cold start** (no cache): ~3-5 minutes
- **Warm start** (cached images): ~30-60 seconds
- **Database migrations**: +10-20 seconds

### Image Sizes

| Service       | Image Size |
|---------------|------------|
| Frontend      | ~180MB     |
| Auth Server   | ~150MB     |
| Backend API   | ~200MB     |
| MCP Server    | ~180MB     |
| AI Agent      | ~200MB     |
| PostgreSQL    | ~250MB     |
| **Total**     | ~1.1GB     |

## Troubleshooting

### Services won't start

**Check logs:**
```bash
docker-compose logs
```

**Common issues:**
1. Missing `.env` file → `cp .env.example .env`
2. Invalid secrets → Regenerate with `openssl rand -base64 32`
3. Ports in use → Stop conflicting services
4. Low memory → Increase Docker memory limit (8GB+ recommended)

### Database connection errors

**Reset database:**
```bash
docker-compose down -v
docker-compose up -d db
# Wait 10 seconds
docker-compose up
```

### Frontend build failures

**Clear build cache:**
```bash
docker-compose build --no-cache frontend
```

**Check build args:**
```bash
docker-compose config | grep NEXT_PUBLIC
```

### AI Agent not responding

**Check Gemini API key:**
```bash
docker-compose exec ai-agent env | grep GEMINI
```

**Test directly:**
```bash
curl -X POST http://localhost:8002/api/v1/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Test"}'
```

### Email verification not working

**Development mode (logs verification link):**
```bash
# In .env
NODE_ENV=development
```

**Check Resend API key:**
```bash
docker-compose logs auth-server | grep -i email
```

## Production Deployment

### Checklist

- [ ] Use managed PostgreSQL (Neon, AWS RDS, etc.)
- [ ] Set `NODE_ENV=production` and `ENV=production`
- [ ] Generate strong secrets (32+ characters)
- [ ] Configure CORS for production domain
- [ ] Enable SSL/TLS for all services
- [ ] Use HTTPS URLs for all `NEXT_PUBLIC_*` variables
- [ ] Set up monitoring and logging
- [ ] Configure backup strategy
- [ ] Set up CI/CD pipeline
- [ ] Enable rate limiting
- [ ] Configure firewall rules

### Environment Variables for Production

```bash
NODE_ENV=production
ENV=production

# Use managed database
DATABASE_URL=postgresql://user:pass@production-host:5432/db?sslmode=require

# Production URLs (HTTPS)
FRONTEND_URL=https://momentum.yourdomain.com
BETTER_AUTH_URL=https://auth.yourdomain.com
CORS_ORIGINS=https://momentum.yourdomain.com

# Frontend public URLs
NEXT_PUBLIC_AUTH_URL=https://auth.yourdomain.com/api/auth
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NEXT_PUBLIC_AI_AGENT_URL=https://ai.yourdomain.com
```

### Deployment Platforms

**Docker Compose on VPS:**
```bash
# SSH to server
ssh user@your-server

# Clone repo
git clone https://github.com/yourusername/momentum.git
cd momentum

# Set up .env
cp .env.example .env
nano .env  # Edit with production values

# Start services
docker-compose up -d

# Set up reverse proxy (Nginx/Traefik)
# Configure SSL certificates (Let's Encrypt)
```

**Kubernetes:**
- Convert docker-compose to Kubernetes manifests
- Use Helm charts for deployment
- Configure ingress for routing
- Set up persistent volumes for database

**Cloud Platforms:**
- AWS ECS/Fargate
- Google Cloud Run
- Azure Container Instances
- DigitalOcean App Platform

## Development Workflow

### Hot Reload

Most services support hot reload via volume mounts (in individual `docker-compose.yml` files).

**To enable development mode:**
1. Use service-specific `docker-compose.yml`
2. Mount source directories as volumes
3. Change `NODE_ENV=development`

### Testing

```bash
# Run tests in containers
docker-compose exec backend pytest
docker-compose exec frontend npm test
```

### Debugging

```bash
# Access container shell
docker-compose exec backend sh
docker-compose exec frontend sh

# View environment variables
docker-compose exec backend env

# Check network connectivity
docker-compose exec frontend ping backend
```

## Maintenance

### Update Dependencies

```bash
# Update base images
docker-compose pull

# Rebuild services
docker-compose up --build
```

### Clean Up

```bash
# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune

# Remove unused networks
docker network prune

# Complete cleanup (⚠️ removes everything)
docker system prune -a --volumes
```

### Logs Management

```bash
# Rotate logs
docker-compose logs --tail=1000 > logs-$(date +%Y%m%d).txt

# Clear container logs
truncate -s 0 $(docker inspect --format='{{.LogPath}}' momentum-frontend)
```

## Security Best Practices

### Implemented

- ✅ Non-root users in all containers
- ✅ Alpine base images (minimal attack surface)
- ✅ Multi-stage builds (production dependencies only)
- ✅ No hardcoded secrets
- ✅ Health checks for reliability
- ✅ Graceful shutdown handling
- ✅ `.dockerignore` files to exclude sensitive data

### Recommended

- Use secrets management (Docker Secrets, Vault)
- Enable TLS/SSL for all external communication
- Implement rate limiting
- Set up Web Application Firewall (WAF)
- Enable security scanning (Snyk, Trivy)
- Regular security updates
- Monitor for vulnerabilities

## References

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Microservices Architecture](https://microservices.io/)
- Individual service READMEs in each directory

## Support

For service-specific documentation, see:
- `frontend/DOCKER_README.md`
- `auth-server/DOCKER_README.md`
- `backend/DOCKER_README.md`
- `ai-agent/DOCKER_README.md`
- `mcp-server/DOCKER_README.md`
