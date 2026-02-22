# MCP Server - Docker Deployment Guide

Production-ready Docker configuration for the Todo MCP Server microservice.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Deployment Scenarios](#deployment-scenarios)
- [Security](#security)
- [Troubleshooting](#troubleshooting)
- [Monitoring](#monitoring)

## Overview

The MCP Server is containerized using a **multi-stage Docker build** optimized for:

- **Fast builds**: uv dependency manager (10-100x faster than pip)
- **Small images**: Multi-stage build excludes dev dependencies (~150-200MB final size)
- **Security**: Non-root user execution, minimal attack surface
- **Production-ready**: Health checks, proper signal handling, environment-based configuration

### Build Architecture

```
┌─────────────────────────────────────────┐
│ Stage 1: Builder (bookworm-slim)        │
│ - Install uv                             │
│ - Install production dependencies       │
│ - Create .venv with frozen lockfile     │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│ Stage 2: Runtime (python:3.12-slim)     │
│ - Copy .venv from builder               │
│ - Copy application source               │
│ - Create non-root user (mcpuser)        │
│ - Install uv runtime (for commands)     │
│ - Add health checks                     │
└─────────────────────────────────────────┘
```

## Architecture

### Microservices Integration

```
Claude Desktop / AI Assistant
        ↓
MCP Server (Docker Container)
        ↓ HTTP + Service Auth
Backend API (Docker Container)
        ↓
Neon PostgreSQL Database
```

### Network Communication

- **MCP Server** exposes port 3000 (HTTP transport for FastMCP)
- **Backend API** exposes port 8000 (FastAPI)
- Both services communicate via shared Docker network: `todo-network`
- Service-to-service authentication via `SERVICE_AUTH_TOKEN` header

## Prerequisites

- Docker 20.10+ and Docker Compose v2+
- Backend API running (see `../backend/DOCKER_README.md`)
- Environment variables configured (see Configuration section)

## Quick Start

### 1. Configure Environment

```bash
cd mcp-server

# Create .env from template
cp .env.example .env

# Generate secure service token (must match backend/.env)
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Edit .env and add:
# SERVICE_AUTH_TOKEN=<generated-token>
# FASTAPI_BASE_URL=http://backend:8000  # For Docker network
```

### 2. Build and Run

#### Option A: Docker Compose (Recommended)

```bash
# Build and start MCP server + backend
docker-compose up --build

# Or run in background
docker-compose up -d
```

#### Option B: Standalone Docker

```bash
# Build image
docker build -t todo-mcp-server .

# Run container
docker run -d \
  --name mcp-server \
  --network todo-network \
  -p 3000:3000 \
  --env-file .env \
  todo-mcp-server
```

### 3. Verify Deployment

```bash
# Check container logs
docker logs -f mcp-server

# Expected output:
# INFO - Starting todo-mcp-server
# INFO - Registered tool: list_tasks
# INFO - Registered tool: create_task
# INFO - Registered tool: mark_task_completed
# INFO - Registered tool: update_task
# INFO - Registered tool: delete_task

# Check health status
docker inspect mcp-server --format='{{.State.Health.Status}}'
# Should return: healthy
```

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SERVICE_AUTH_TOKEN` | ✅ | - | Service-to-service authentication token (must match backend) |
| `FASTAPI_BASE_URL` | ✅ | - | Backend API URL (`http://localhost:8000` for local, `http://backend:8000` for Docker) |
| `MCP_LOG_LEVEL` | ❌ | INFO | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `MCP_SERVER_PORT` | ❌ | 3000 | HTTP server port (overridden by `PORT` on Railway/Render) |
| `BACKEND_TIMEOUT` | ❌ | 30.0 | Backend request timeout in seconds |
| `BACKEND_MAX_RETRIES` | ❌ | 2 | Backend request retry attempts |

### Docker Network Setup

The MCP server requires a shared network to communicate with the backend:

```bash
# Create network (if not already created by backend)
docker network create todo-network

# Connect existing backend container
docker network connect todo-network todo-backend
```

## Deployment Scenarios

### Scenario 1: Local Development with Docker Compose

**Use Case**: Full-stack development with hot reload

```yaml
# docker-compose.yml (development override)
services:
  mcp-server:
    build:
      context: .
      dockerfile: Dockerfile
    volumes:
      - ./src:/app/src  # Hot reload source code
    environment:
      - MCP_LOG_LEVEL=DEBUG
```

```bash
# Start with development configuration
docker-compose up
```

### Scenario 2: Production Deployment (Railway/Render)

**Railway**:
1. Connect GitHub repository
2. Select `mcp-server` as root directory
3. Add environment variables in Railway dashboard
4. Railway auto-detects Dockerfile and deploys

**Render**:
1. Create new Web Service
2. Connect GitHub repository
3. Set Root Directory: `mcp-server`
4. Set Build Command: `docker build -t mcp-server .`
5. Set Start Command: `docker run -p 3000:3000 mcp-server`

### Scenario 3: Multi-Container Orchestration

**Stack**: Frontend + Backend + MCP Server + Auth Server

```bash
# Start all services
docker-compose -f docker-compose.fullstack.yml up

# Services communicate via todo-network
# - Frontend: http://localhost:3000
# - Backend: http://localhost:8000
# - MCP Server: http://localhost:3001
# - Auth Server: http://localhost:8080
```

## Security

### Security Features

#### 1. Non-Root User Execution
```dockerfile
# Create and use non-root user
RUN useradd -m -u 1000 mcpuser
USER mcpuser
```

**Why**: Limits container compromise damage. Even if attacker gains shell access, they run as unprivileged user.

#### 2. Minimal Base Image
```dockerfile
FROM python:3.12-slim  # 40MB vs 900MB full image
```

**Why**: Reduces attack surface by excluding unnecessary system packages.

#### 3. Multi-Stage Build
```dockerfile
FROM builder AS builder  # Install dependencies
FROM python:3.12-slim    # Runtime only
```

**Why**: Production image excludes build tools (gcc, make) that could be exploited.

#### 4. .dockerignore Exclusions
```
.env         # Secrets
.git/        # Source history
tests/       # Test data
*.md         # Documentation
```

**Why**: Prevents sensitive files from leaking into Docker images.

#### 5. Health Checks
```dockerfile
HEALTHCHECK CMD pgrep -f "python.*server" || exit 1
```

**Why**: Enables automatic container restart on process failure.

### Secret Management

**Never commit secrets to Git or Dockerfile!**

✅ **Recommended**:
```bash
# Use environment variables
docker run --env-file .env todo-mcp-server

# Or pass individual secrets
docker run -e SERVICE_AUTH_TOKEN=$TOKEN todo-mcp-server
```

❌ **Avoid**:
```dockerfile
# DO NOT hardcode secrets in Dockerfile
ENV SERVICE_AUTH_TOKEN=abc123
```

## Troubleshooting

### Issue 1: Container Fails to Start

**Symptom**: Container exits immediately after starting

**Diagnosis**:
```bash
docker logs mcp-server
```

**Common Causes**:
1. Missing `SERVICE_AUTH_TOKEN` environment variable
   - **Solution**: Verify `.env` file contains `SERVICE_AUTH_TOKEN`

2. Cannot connect to backend API
   - **Solution**: Ensure backend container is running and connected to `todo-network`
   - Check: `docker network inspect todo-network`

3. Port 3000 already in use
   - **Solution**: Change port mapping: `-p 3001:3000`

### Issue 2: "Connection Refused" to Backend

**Symptom**: Logs show `httpx.ConnectError: Connection refused`

**Solution**:
```bash
# Check if backend is reachable from MCP container
docker exec mcp-server ping backend

# Verify both services are on same network
docker network inspect todo-network
```

**Fix**: Update `FASTAPI_BASE_URL` to use service name:
```env
# .env
FASTAPI_BASE_URL=http://backend:8000  # Use 'backend' not 'localhost'
```

### Issue 3: Large Docker Image Size

**Symptom**: Image size > 500MB

**Diagnosis**:
```bash
docker images todo-mcp-server
```

**Solutions**:
1. Verify multi-stage build is working:
   ```bash
   docker history todo-mcp-server
   # Should show FROM python:3.12-slim (not builder stage)
   ```

2. Check .dockerignore excludes large files:
   ```bash
   cat .dockerignore | grep -E "tests|docs|.venv"
   ```

3. Clean up dangling images:
   ```bash
   docker image prune -a
   ```

### Issue 4: Health Check Failing

**Symptom**: `docker inspect` shows `unhealthy` status

**Diagnosis**:
```bash
docker inspect mcp-server --format='{{.State.Health}}'
```

**Solution**:
```bash
# Check if process is running inside container
docker exec mcp-server ps aux | grep python

# View health check logs
docker inspect mcp-server --format='{{range .State.Health.Log}}{{.Output}}{{end}}'
```

## Monitoring

### Container Logs

```bash
# View real-time logs
docker logs -f mcp-server

# View last 100 lines
docker logs --tail 100 mcp-server

# Filter by log level
docker logs mcp-server 2>&1 | grep ERROR
```

### Health Status

```bash
# Check health status
docker inspect mcp-server --format='{{.State.Health.Status}}'

# View detailed health check history
docker inspect mcp-server | jq '.[0].State.Health'
```

### Resource Usage

```bash
# Monitor CPU/Memory usage
docker stats mcp-server

# Example output:
# CONTAINER    CPU %   MEM USAGE / LIMIT   MEM %   NET I/O
# mcp-server   0.5%    50MiB / 1GiB        5%      1.2kB / 800B
```

### Performance Metrics

```bash
# View startup time
docker inspect mcp-server --format='{{.State.StartedAt}}'

# Check restart count (should be 0 for stable service)
docker inspect mcp-server --format='{{.RestartCount}}'
```

## Best Practices

### Development Workflow

1. **Use docker-compose for local development**
   ```bash
   docker-compose up  # Auto-rebuilds on code changes with volumes
   ```

2. **Run tests before building**
   ```bash
   uv run pytest  # Local testing
   docker build -t mcp-server-test .  # Container testing
   ```

3. **Use .env files for configuration**
   ```bash
   cp .env.example .env
   # Edit .env with local values
   docker-compose up  # Automatically loads .env
   ```

### Production Deployment

1. **Always use multi-stage builds** (already configured)
2. **Pin dependency versions** (pyproject.toml already pins major versions)
3. **Enable health checks** (already configured)
4. **Use non-root user** (already configured as `mcpuser`)
5. **Monitor logs and metrics** (see Monitoring section)

### Security Checklist

- [ ] No secrets in Dockerfile or docker-compose.yml
- [ ] `.env` file in `.gitignore`
- [ ] Service token matches backend configuration
- [ ] Container runs as non-root user (mcpuser)
- [ ] Health checks enabled
- [ ] Network isolation via `todo-network`

## Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [uv Package Manager](https://github.com/astral-sh/uv)
- [Multi-Stage Build Best Practices](https://docs.docker.com/build/building/multi-stage/)
