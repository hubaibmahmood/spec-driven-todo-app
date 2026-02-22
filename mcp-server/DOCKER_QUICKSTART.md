# MCP Server - Docker Quick Start (5 Minutes)

Get the MCP Server running in Docker in under 5 minutes.

## Prerequisites

- Docker and Docker Compose installed
- Backend service running (see `../backend/DOCKER_QUICKSTART.md`)

## Step 1: Environment Setup

```bash
cd mcp-server

# Create .env file
cp .env.example .env

# Generate secure service token
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Edit .env and add the token:
nano .env
```

**Required .env content**:
```env
SERVICE_AUTH_TOKEN=<paste-generated-token>
FASTAPI_BASE_URL=http://backend:8000
MCP_LOG_LEVEL=INFO
```

**IMPORTANT**: The same token must be in `../backend/.env`!

## Step 2: Build and Run

### Option A: Docker Compose (Recommended)

```bash
# Start MCP server + backend
docker-compose up --build

# Or run in background
docker-compose up -d
```

### Option B: Standalone Docker

```bash
# Create network (if not exists)
docker network create todo-network

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

## Step 3: Verify

```bash
# Check logs
docker logs -f mcp-server

# Expected output:
# INFO - Starting todo-mcp-server
# INFO - Registered tool: list_tasks
# INFO - Registered tool: create_task
# ...

# Check health status
docker inspect mcp-server --format='{{.State.Health.Status}}'
# Should return: healthy

# Test container networking
docker exec mcp-server ping backend -c 2
# Should successfully ping backend service
```

## Orchestrate Full Stack

```bash
# Start all services (backend, mcp-server, auth-server)
cd /Users/mac/Documents/PIAIC/speckit plus/todo-app

# Create shared network
docker network create todo-network

# Start backend
cd backend
docker-compose up -d

# Start MCP server
cd ../mcp-server
docker-compose up -d

# Verify all services
docker ps

# Expected output:
# CONTAINER ID   IMAGE              STATUS                   PORTS
# ...            todo-backend       Up (healthy)            0.0.0.0:8000->8000/tcp
# ...            todo-mcp-server    Up (healthy)            0.0.0.0:3000->3000/tcp
```

## Troubleshooting

### Issue 1: Container Won't Start

```bash
# Check logs for error messages
docker logs mcp-server

# Common fix: Missing environment variables
# Solution: Verify .env has SERVICE_AUTH_TOKEN and FASTAPI_BASE_URL
```

### Issue 2: Cannot Connect to Backend

```bash
# Verify backend is running
docker ps | grep backend

# Check network connectivity
docker exec mcp-server ping backend

# Fix: Ensure both containers on todo-network
docker network inspect todo-network
```

### Issue 3: Port 3000 Already in Use

```bash
# Use different port
docker run -p 3001:3000 todo-mcp-server

# Or stop conflicting service
lsof -ti:3000 | xargs kill
```

### Issue 4: Health Check Failing

```bash
# Check process inside container
docker exec mcp-server ps aux | grep python

# Restart container
docker restart mcp-server
```

## Development Workflow

```bash
# View logs
docker logs -f mcp-server

# Rebuild after code changes
docker-compose up --build

# Run tests inside container
docker exec mcp-server uv run pytest

# Stop services
docker-compose down

# Clean up (removes containers and images)
docker-compose down --rmi all
```

## Next Steps

- **Production deployment**: See `DOCKER_README.md` for Railway/Render setup
- **Security hardening**: Review security checklist in `DOCKER_README.md`
- **Monitoring**: Set up log aggregation and metrics (see Monitoring section)
- **Claude Desktop integration**: See `CLAUDE_DESKTOP_SETUP.md` for AI assistant setup

## Quick Reference

| Command | Description |
|---------|-------------|
| `docker-compose up --build` | Build and start all services |
| `docker logs -f mcp-server` | View real-time logs |
| `docker exec mcp-server <cmd>` | Run command inside container |
| `docker stats mcp-server` | Monitor CPU/memory usage |
| `docker restart mcp-server` | Restart container |
| `docker-compose down` | Stop all services |

## Help

If you encounter issues not covered here:
1. Check `DOCKER_README.md` for detailed troubleshooting
2. Review logs: `docker logs mcp-server`
3. Verify environment variables: `docker exec mcp-server env`
4. Check network: `docker network inspect todo-network`
