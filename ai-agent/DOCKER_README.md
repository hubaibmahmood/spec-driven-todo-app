# AI Agent Microservice - Docker Deployment Guide

This guide explains how to build, run, and deploy the AI Agent microservice using Docker.

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Building the Image](#building-the-image)
- [Running with Docker Compose](#running-with-docker-compose)
- [Running Standalone](#running-standalone)
- [Configuration](#configuration)
- [Health Checks](#health-checks)
- [Troubleshooting](#troubleshooting)
- [Production Deployment](#production-deployment)

## 🚀 Quick Start

### Prerequisites

- Docker 20.10+ and Docker Compose 2.0+
- Neon PostgreSQL database URL
- Gemini API key from [Google AI Studio](https://ai.google.dev/)
- Service authentication token (shared with backend)
- Access to MCP server (running on port 8001)

### 1. Set Environment Variables

Create a `.env` file in the `ai-agent/` directory:

```bash
# Database (Neon PostgreSQL)
DATABASE_URL=postgresql+asyncpg://user:pass@host/db?ssl=require

# Service Authentication
SERVICE_AUTH_TOKEN=your-service-auth-token-change-this
JWT_SECRET=dev-jwt-secret-min-32-chars-change-in-production-please

# Backend URL
BACKEND_URL=http://backend:8000

# Gemini API Key
AGENT_GEMINI_API_KEY=your_gemini_api_key_here

# MCP Server
AGENT_MCP_SERVER_URL=http://mcp-server:8001/mcp

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

### 2. Build and Run

```bash
# Build the Docker image
docker build -t ai-agent:latest .

# Run with docker-compose
docker-compose up -d

# Or run standalone
docker run -d \
  --name ai-agent \
  --env-file .env \
  -p 8002:8002 \
  ai-agent:latest
```

### 3. Verify Health

```bash
curl http://localhost:8002/health
# Expected: {"status": "healthy", "service": "ai-agent"}
```

## 🏗️ Architecture

### Multi-Stage Dockerfile

The Dockerfile uses a **two-stage build** for optimal image size and security:

```
┌─────────────────────────────────────────────────────────────┐
│ Stage 1: Builder (python:3.12-slim)                         │
│ ─────────────────────────────────────────────────────────── │
│ • Install uv package manager                                │
│ • Copy pyproject.toml                                       │
│ • Run: uv sync --frozen --no-dev                            │
│ • Output: /app/.venv (virtual environment)                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Stage 2: Runtime (python:3.12-slim)                         │
│ ─────────────────────────────────────────────────────────── │
│ • Install runtime deps: libpq5, curl                        │
│ • Copy uv binary (for "uv run" commands)                    │
│ • Copy .venv from builder stage                             │
│ • Copy application code (src/, alembic/, alembic.ini)       │
│ • Copy entrypoint.sh                                        │
│ • Run as non-root user (appuser)                            │
│ • HEALTHCHECK: curl /health endpoint                        │
│ • ENTRYPOINT: ./entrypoint.sh                               │
└─────────────────────────────────────────────────────────────┘
```

**Benefits**:
- **Small image size**: Only runtime dependencies in final image (~200MB vs 1GB+)
- **Fast builds**: Dependency layer cached separately from application code
- **Security**: Runs as non-root user with minimal attack surface

### Entrypoint Flow

```bash
entrypoint.sh:
  1. Check for alembic.ini
  2. Run: uv run alembic upgrade head (database migrations)
  3. Start: uv run uvicorn ai_agent.main:app --workers 4 --port 8002
```

**Why uv in runtime?**
The entrypoint uses `uv run` commands to execute within the virtual environment context, ensuring all dependencies are available.

## 🔨 Building the Image

### Standard Build

```bash
cd ai-agent/
docker build -t ai-agent:latest .
```

### Build with Custom Tag

```bash
docker build -t ai-agent:v1.0.0 .
```

### Build with No Cache (force rebuild)

```bash
docker build --no-cache -t ai-agent:latest .
```

### View Build Stages

```bash
# Build and see both stages
docker build --target builder -t ai-agent-builder .
docker build -t ai-agent:latest .
```

### Check Image Size

```bash
docker images ai-agent
# Expected: ~200-300MB for production image
```

## 🐳 Running with Docker Compose

### Basic Usage

```bash
# Start service in background
docker-compose up -d

# View logs
docker-compose logs -f ai-agent

# Stop service
docker-compose down

# Rebuild and restart
docker-compose up -d --build
```

### Development Mode (Hot Reload)

The `docker-compose.yml` includes volume mounts for hot reload:

```yaml
volumes:
  - ./src:/app/src:ro        # Source code
  - ./alembic:/app/alembic:ro # Migrations
```

For production, comment out these volumes to use the baked-in code.

### Service Dependencies

The AI agent depends on:
- **Backend API** (port 8000) - for user API key retrieval
- **MCP Server** (port 8001) - for task management tools
- **Neon PostgreSQL** - for conversation/message persistence

Ensure these services are running and accessible.

## 🏃 Running Standalone

### With Environment File

```bash
docker run -d \
  --name ai-agent \
  --env-file .env \
  -p 8002:8002 \
  ai-agent:latest
```

### With Inline Environment Variables

```bash
docker run -d \
  --name ai-agent \
  -e DATABASE_URL="postgresql+asyncpg://user:pass@host/db" \
  -e AGENT_GEMINI_API_KEY="your-key" \
  -e SERVICE_AUTH_TOKEN="your-token" \
  -e BACKEND_URL="http://backend:8000" \
  -e AGENT_MCP_SERVER_URL="http://mcp-server:8001/mcp" \
  -p 8002:8002 \
  ai-agent:latest
```

### Connect to Existing Network

```bash
# Create shared network
docker network create todo-network

# Run ai-agent on the network
docker run -d \
  --name ai-agent \
  --network todo-network \
  --env-file .env \
  -p 8002:8002 \
  ai-agent:latest
```

Now the ai-agent can communicate with `backend:8000` and `mcp-server:8001` via Docker DNS.

## ⚙️ Configuration

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | Neon PostgreSQL connection string (asyncpg format) | `postgresql+asyncpg://user:pass@host/db?ssl=require` |
| `AGENT_GEMINI_API_KEY` | Gemini API key from Google AI Studio | `AIza...` |
| `SERVICE_AUTH_TOKEN` | Service-to-service auth token (must match backend) | `openssl rand -hex 32` |
| `JWT_SECRET` | JWT secret for user authentication (must match backend) | Min 32 characters |
| `BACKEND_URL` | FastAPI backend URL for API key retrieval | `http://backend:8000` |
| `AGENT_MCP_SERVER_URL` | MCP server endpoint URL | `http://mcp-server:8001/mcp` |

### Optional Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `ENV` | `development` | Environment (development/production) |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG/INFO/WARNING/ERROR) |
| `PORT` | `8002` | Application port (overridable for Railway/Render) |
| `CORS_ORIGINS` | `http://localhost:3000,http://localhost:3001` | Comma-separated CORS origins |
| `AGENT_TEMPERATURE` | `0.7` | AI model temperature (0.0-2.0) |
| `AGENT_TOKEN_BUDGET` | `800000` | Max tokens for conversation context |
| `AGENT_MCP_TIMEOUT` | `10` | MCP server timeout (seconds) |
| `AGENT_MCP_RETRY_ATTEMPTS` | `3` | Number of retry attempts for MCP calls |
| `AGENT_OPENAI_API_KEY` | - | Optional: OpenAI key for tracing/debugging |

### Database Connection Format

**Neon PostgreSQL** (asyncpg driver):
```bash
DATABASE_URL=postgresql+asyncpg://user:pass@host.neon.tech/db?ssl=require
```

**Important**: Use `ssl=require` (NOT `sslmode=require`) for asyncpg compatibility.

## 🏥 Health Checks

### Docker HEALTHCHECK

The Dockerfile includes an automated health check:

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8002/health || exit 1
```

**Parameters**:
- **interval**: Check every 30 seconds
- **timeout**: Wait 3 seconds for response
- **start-period**: Allow 10 seconds for migrations and startup
- **retries**: Mark unhealthy after 3 consecutive failures

### Manual Health Check

```bash
# Check container health status
docker ps --filter name=ai-agent

# Manual endpoint test
curl http://localhost:8002/health

# Expected response:
# {"status": "healthy", "service": "ai-agent"}
```

### Health Check Logs

```bash
# View health check results
docker inspect --format='{{json .State.Health}}' ai-agent | jq
```

## 🐛 Troubleshooting

### Container Won't Start

**Check logs**:
```bash
docker logs ai-agent
```

**Common issues**:
- **Migration failures**: Database URL incorrect or database unreachable
- **Missing environment variables**: Check .env file or docker-compose.yml
- **Port conflict**: Another service using port 8002

**Solution**: Fix environment variables and restart:
```bash
docker rm ai-agent
docker run -d --name ai-agent --env-file .env -p 8002:8002 ai-agent:latest
```

### Database Connection Errors

**Error**: `asyncpg connection errors`

**Solutions**:
1. Verify `DATABASE_URL` format uses `ssl=require` (not `sslmode=require`)
2. Check Neon database is accessible (test with psql or pgAdmin)
3. Ensure database credentials are correct
4. Verify network connectivity (if using Docker network)

### Migration Errors

**Error**: `Alembic migration fails`

**Solutions**:
```bash
# Enter container and manually run migrations
docker exec -it ai-agent bash
uv run alembic current
uv run alembic upgrade head

# If persistent, check database schema version
docker exec -it ai-agent bash -c "uv run alembic history"
```

### Service Authentication Failures

**Error**: `401 Unauthorized when calling backend`

**Solution**: Verify `SERVICE_AUTH_TOKEN` matches between ai-agent and backend:
```bash
# ai-agent/.env
SERVICE_AUTH_TOKEN=abc123

# backend/.env
SERVICE_AUTH_TOKEN=abc123  # Must be identical
```

### MCP Connection Failures

**Error**: `MCP server unreachable`

**Solutions**:
1. Verify MCP server is running: `curl http://localhost:8001/mcp`
2. Check network connectivity (if using Docker network)
3. Update `AGENT_MCP_SERVER_URL` to use Docker service name: `http://mcp-server:8001/mcp`

### Permission Denied Errors

**Error**: `PermissionError: [Errno 13] Permission denied`

**Cause**: Container runs as non-root user (appuser, UID 1000)

**Solution**: Ensure mounted volumes have correct permissions:
```bash
# Fix permissions on host
chown -R 1000:1000 ./src ./alembic
```

## 🚀 Production Deployment

### Railway / Render Deployment

1. **Push to GitHub**:
   ```bash
   git add Dockerfile entrypoint.sh .dockerignore docker-compose.yml
   git commit -m "Add Docker configuration for ai-agent"
   git push origin main
   ```

2. **Configure Railway/Render**:
   - Set build context: `ai-agent/`
   - Dockerfile path: `ai-agent/Dockerfile`
   - Port: `8002` (Railway/Render will override with `$PORT`)

3. **Environment Variables** (set in Railway/Render dashboard):
   ```
   DATABASE_URL=postgresql+asyncpg://...
   AGENT_GEMINI_API_KEY=...
   SERVICE_AUTH_TOKEN=...
   JWT_SECRET=...
   BACKEND_URL=https://backend-service-url.railway.app
   AGENT_MCP_SERVER_URL=https://mcp-server-url.railway.app/mcp
   CORS_ORIGINS=https://your-frontend-url.vercel.app
   ENV=production
   ```

### Security Checklist

Before deploying to production:

- [ ] Use strong `SERVICE_AUTH_TOKEN` (32+ characters): `openssl rand -hex 32`
- [ ] Use strong `JWT_SECRET` (32+ characters, must match backend)
- [ ] Set `ENV=production`
- [ ] Enable HTTPS/TLS for all endpoints
- [ ] Configure proper `CORS_ORIGINS` (no wildcards in production)
- [ ] Use managed PostgreSQL with SSL enabled (Neon with `ssl=require`)
- [ ] Set up monitoring and alerting
- [ ] Configure log aggregation (CloudWatch, Datadog, etc.)
- [ ] Enable auto-scaling if needed (Railway/Render support)

### Multi-Service Orchestration

If deploying all microservices together:

```yaml
# Full-stack docker-compose.yml
services:
  backend:
    image: backend:latest
    ports: ["8000:8000"]

  auth-server:
    image: auth-server:latest
    ports: ["3001:3001"]

  mcp-server:
    image: mcp-server:latest
    ports: ["8001:8001"]

  ai-agent:
    image: ai-agent:latest
    ports: ["8002:8002"]
    depends_on:
      - backend
      - mcp-server

  frontend:
    image: frontend:latest
    ports: ["3000:3000"]
    depends_on:
      - backend
      - auth-server
      - ai-agent
```

## 📊 Monitoring

### Container Metrics

```bash
# CPU and memory usage
docker stats ai-agent

# Logs with timestamps
docker logs -f --timestamps ai-agent

# Disk usage
docker system df
```

### Application Metrics

The service logs important metrics:
- Migration execution time
- Startup time
- Request processing time
- Token usage per conversation
- MCP tool call latency

**Example log output**:
```
🚀 Starting AI Agent microservice...
📦 Running database migrations...
✅ Starting Uvicorn server...
INFO: Started server process [1]
INFO: Waiting for application startup.
INFO: Application startup complete.
INFO: Uvicorn running on http://0.0.0.0:8002
```

## 🔧 Advanced Configuration

### Custom Entrypoint Arguments

Override default Uvicorn settings:

```bash
docker run -d \
  --name ai-agent \
  --env-file .env \
  -p 8002:8002 \
  ai-agent:latest \
  --entrypoint ""  # Disable entrypoint.sh
  uv run uvicorn ai_agent.main:app --workers 8 --port 8002
```

### Debug Mode

Run with interactive shell for debugging:

```bash
docker run -it --rm \
  --env-file .env \
  -p 8002:8002 \
  ai-agent:latest \
  /bin/bash
```

Inside container:
```bash
# Manually run migrations
uv run alembic upgrade head

# Start server manually
uv run uvicorn ai_agent.main:app --host 0.0.0.0 --port 8002 --reload
```

## 📚 Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [uv Package Manager](https://github.com/astral-sh/uv)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Neon PostgreSQL](https://neon.tech/docs)
- [Gemini API](https://ai.google.dev/gemini-api)
- [OpenAI Agents SDK](https://github.com/openai/openai-agents-python)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)

## 📝 Summary

**Key Files**:
- `Dockerfile` - Multi-stage production build
- `entrypoint.sh` - Migration + startup script
- `.dockerignore` - Build context exclusions
- `docker-compose.yml` - Local development setup

**Quick Commands**:
```bash
# Build
docker build -t ai-agent:latest .

# Run
docker-compose up -d

# Logs
docker logs -f ai-agent

# Health
curl http://localhost:8002/health

# Stop
docker-compose down
```

**Production Deployment**: Use Railway/Render with environment variables configured in dashboard.

---

**Need Help?** Open an issue or consult the main [AI Agent README](./README.md) for service-specific details.
