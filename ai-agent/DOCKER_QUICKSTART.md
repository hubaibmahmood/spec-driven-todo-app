# AI Agent - Docker Quick Start

Get the AI Agent microservice running in Docker in under 5 minutes.

## Prerequisites

- Docker and Docker Compose installed
- Neon PostgreSQL database URL
- Gemini API key

## Step 1: Set Environment Variables

Create `.env` file in `ai-agent/` directory:

```bash
DATABASE_URL=postgresql+asyncpg://user:pass@host.neon.tech/db?ssl=require
AGENT_GEMINI_API_KEY=your_gemini_api_key_here
SERVICE_AUTH_TOKEN=your-service-auth-token
JWT_SECRET=dev-jwt-secret-min-32-chars-change-in-production-please
BACKEND_URL=http://backend:8000
AGENT_MCP_SERVER_URL=http://mcp-server:8001/mcp
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

## Step 2: Build and Run

```bash
# Navigate to ai-agent directory
cd ai-agent/

# Build and start with docker-compose
docker-compose up -d --build

# Or build and run manually
docker build -t ai-agent:latest .
docker run -d --name ai-agent --env-file .env -p 8002:8002 ai-agent:latest
```

## Step 3: Verify

```bash
# Check health
curl http://localhost:8002/health
# Expected: {"status": "healthy", "service": "ai-agent"}

# View logs
docker logs -f ai-agent
```

## Alternative: Run Without Docker Compose

```bash
# Create shared network (if not exists)
docker network create todo-network

# Run ai-agent
docker run -d \
  --name ai-agent \
  --network todo-network \
  --env-file .env \
  -p 8002:8002 \
  ai-agent:latest
```

## Common Issues

### Database Connection Failed

**Solution**: Verify `DATABASE_URL` uses `ssl=require` (not `sslmode=require`):
```bash
DATABASE_URL=postgresql+asyncpg://user:pass@host/db?ssl=require
```

### Migration Errors

**Solution**: Check database is accessible and schema is initialized:
```bash
docker exec -it ai-agent bash
uv run alembic current
uv run alembic upgrade head
```

### Port Conflict

**Solution**: Change external port mapping:
```bash
docker run -d --name ai-agent --env-file .env -p 8003:8002 ai-agent:latest
```

### Service Authentication Failed

**Solution**: Ensure `SERVICE_AUTH_TOKEN` matches backend/.env:
```bash
# Both files must have identical token
SERVICE_AUTH_TOKEN=abc123
```

## Development Mode

For hot reload during development:

```bash
docker-compose up -d
# Edits to src/ and alembic/ will be reflected inside container
```

## Stop and Clean Up

```bash
# Stop service
docker-compose down

# Remove container
docker rm -f ai-agent

# Remove image
docker rmi ai-agent:latest
```

## Next Steps

- See [DOCKER_README.md](./DOCKER_README.md) for comprehensive documentation
- Configure production deployment on Railway/Render
- Set up monitoring and logging

---

**Need Help?** Check the [main README](./README.md) or [troubleshooting guide](./DOCKER_README.md#troubleshooting).
