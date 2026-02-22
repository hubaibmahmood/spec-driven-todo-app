# Docker Setup for Backend Service

Production-ready Docker configuration for the FastAPI backend connecting to managed Neon PostgreSQL.

## What's Included

- **Multi-stage Dockerfile**: Optimized for production with minimal image size
- **docker-compose.yml**: Backend service with hot reload for development
- **entrypoint.sh**: Automated Alembic migrations on startup
- **.dockerignore**: Comprehensive exclusions for clean builds

## Architecture

```
┌─────────────────────────────────────────────────┐
│  Backend Service (Port 8000)                    │
│  - FastAPI application                          │
│  - Alembic migrations (auto-run on startup)     │
│  - Health checks at /health                     │
│  - Prometheus metrics at /metrics               │
└─────────────────────────────────────────────────┘
              │
              ▼
    ┌──────────────────────┐
    │   Neon PostgreSQL    │
    │   (Managed Service)  │
    │   Cloud Database     │
    └──────────────────────┘
```

## Quick Start

### Development Mode (with Docker Compose)

```bash
# Create .env file from example
cp .env.example .env
# Edit .env and add your Neon DATABASE_URL and secrets

# Start backend service
docker-compose up --build

# Start in detached mode
docker-compose up -d --build

# View logs
docker-compose logs -f backend

# Stop service
docker-compose down
```

**Access Points**:
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health
- Metrics: http://localhost:8000/metrics

### Production Build (Standalone)

```bash
# Build the Docker image
docker build -t todo-backend:latest .

# Run with Neon database (using .env file)
docker run -d \
  --name todo-backend \
  -p 8000:8000 \
  --env-file .env \
  todo-backend:latest

# Or with environment variables directly
docker run -d \
  --name todo-backend \
  -p 8000:8000 \
  -e DATABASE_URL="postgresql+asyncpg://user:pass@neon-host/todo_db" \
  -e SESSION_HASH_SECRET="your-session-secret" \
  -e SERVICE_AUTH_TOKEN="your-service-token" \
  -e ENCRYPTION_KEY="your-encryption-key" \
  -e ENVIRONMENT="production" \
  -e CORS_ORIGINS="https://yourdomain.com" \
  todo-backend:latest
```

## Configuration

### Environment Variables

All configuration is done via environment variables. See `.env.example` for full reference.

**Required Variables**:
```bash
DATABASE_URL=postgresql+asyncpg://user:password@neon-host/database
SESSION_HASH_SECRET=your-secret-key
SERVICE_AUTH_TOKEN=your-service-token
ENCRYPTION_KEY=your-fernet-encryption-key
```

**Optional Variables**:
```bash
ENVIRONMENT=production
CORS_ORIGINS=https://yourdomain.com
SQLALCHEMY_POOL_SIZE=10
SQLALCHEMY_POOL_OVERFLOW=20
AUTH_SERVER_URL=https://auth.yourdomain.com
```

### Generating Secrets

```bash
# Session hash secret (HMAC-SHA256)
openssl rand -hex 32

# Service auth token
openssl rand -hex 32

# Fernet encryption key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

## Docker Compose Configuration

### Single Service Setup

The `docker-compose.yml` contains only the backend service since we use managed Neon PostgreSQL.

**Why use docker-compose for a single service?**
- Simpler development workflow (`docker-compose up` vs long `docker run` commands)
- Pre-configured volume mounts for hot reload
- Easy to manage environment variables via `.env` file
- Will be extended with other microservices later

### Features Included

- **Hot reload**: Source code mounted as volume for live changes
- **Environment file**: Loads variables from `.env`
- **Auto-restart**: Container restarts on failure
- **Alembic migrations**: Run automatically on startup

### Future: Full-Stack Orchestration

Once all microservices are dockerized, we'll create `docker-compose.fullstack.yml`:
```yaml
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"

  auth-server:
    build: ./auth-server
    ports:
      - "8080:8080"

  ai-agent:
    build: ./ai-agent
    ports:
      - "8001:8001"

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
```

## Dockerfile Details

### Multi-Stage Build

**Stage 1: Builder**
- Installs build dependencies (gcc, g++, libpq-dev)
- Installs Python packages
- Creates isolated build environment

**Stage 2: Runtime**
- Minimal base image (python:3.12-slim)
- Copies only compiled packages from builder
- Runs as non-root user (appuser, UID 1000)
- Includes health check for container orchestration

### Security Features

✅ Non-root user (appuser)
✅ Minimal base image (~150MB vs ~900MB for full Python image)
✅ No hardcoded secrets
✅ Health checks for monitoring
✅ Comprehensive .dockerignore
✅ Separate build and runtime stages

## Database Migrations

Migrations run automatically on container startup via `entrypoint.sh`:

```bash
# Entrypoint sequence:
1. Run Alembic migrations (alembic upgrade head)
2. Start Uvicorn with 4 workers
```

**Manual Migration Execution**:
```bash
# Run migrations inside running container
docker-compose exec backend alembic upgrade head

# Create new migration
docker-compose exec backend alembic revision --autogenerate -m "description"

# Rollback one migration
docker-compose exec backend alembic downgrade -1
```

## Health Checks

Docker health check hits `/health` endpoint every 30 seconds:

```bash
# Check container health status
docker ps  # Look for "healthy" status

# View health check logs
docker inspect todo-backend-api | grep -A 10 Health
```

## Monitoring

### Prometheus Metrics

Expose metrics at `/metrics` endpoint:

```bash
# Access metrics
curl http://localhost:8000/metrics
```

Integrate with Prometheus by adding to `prometheus.yml`:
```yaml
scrape_configs:
  - job_name: 'todo-backend'
    static_configs:
      - targets: ['backend:8000']
```

### Logs

```bash
# Follow logs for all services
docker-compose logs -f

# Follow backend logs only
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 backend
```

## Troubleshooting

### Container won't start

```bash
# Check logs
docker-compose logs backend

# Common issues:
# - DATABASE_URL incorrect: Check Neon connection string format
# - Neon database not accessible: Verify credentials and network access
# - Migration failed: Run manually with `docker-compose exec backend alembic upgrade head`
```

### Database connection failed

```bash
# Check DATABASE_URL in .env file
cat .env | grep DATABASE_URL

# Verify Neon connection format
# Correct: postgresql+asyncpg://user:pass@neon-host.neon.tech/todo_db
# Wrong: postgresql://user:pass@neon-host/todo_db (missing +asyncpg)

# Test connection from local machine
# (requires psql installed)
psql "postgresql://user:pass@neon-host.neon.tech/todo_db" -c "SELECT 1;"
```

### Hot reload not working

```bash
# Ensure volumes are mounted correctly
docker-compose config | grep -A 5 volumes

# Restart containers
docker-compose restart backend
```

### Permission denied errors

```bash
# Fix entrypoint.sh permissions
chmod +x entrypoint.sh

# Rebuild without cache
docker-compose build --no-cache backend
```

## Integration with Other Services

### Connecting to Auth Server

Update `docker-compose.yml` to include auth-server service:

```yaml
services:
  auth-server:
    build: ../auth-server
    ports:
      - "8080:8080"
    # ... auth server config

  backend:
    environment:
      AUTH_SERVER_URL: http://auth-server:8080
    depends_on:
      - auth-server
```

### Connecting to AI Agent

AI agent connects to backend via service-to-service auth:

```yaml
services:
  ai-agent:
    build: ../ai-agent
    environment:
      BACKEND_URL: http://backend:8000
      SERVICE_AUTH_TOKEN: ${SERVICE_AUTH_TOKEN}
    depends_on:
      - backend
```

## Production Deployment

### Render.com

Use existing `render.yaml` configuration. Docker setup is for local development.

### Railway

```bash
# Deploy with Railway CLI
railway up
```

Railway automatically detects Dockerfile and builds.

### AWS ECS / GCP Cloud Run

```bash
# Build and tag for container registry
docker build -t gcr.io/project-id/todo-backend:latest .
docker push gcr.io/project-id/todo-backend:latest

# Deploy to Cloud Run
gcloud run deploy todo-backend \
  --image gcr.io/project-id/todo-backend:latest \
  --platform managed \
  --region us-central1 \
  --set-env-vars DATABASE_URL=...,REDIS_URL=...
```

## Performance Tuning

### Worker Count

Uvicorn uses 4 workers by default. Adjust based on CPU cores:

```dockerfile
# In Dockerfile or entrypoint.sh
--workers $((2 * $(nproc) + 1))
```

### Database Connection Pooling

```bash
# For high-traffic applications
SQLALCHEMY_POOL_SIZE=20
SQLALCHEMY_POOL_OVERFLOW=40
SQLALCHEMY_POOL_RECYCLE=1800  # 30 minutes
```

### Connection Optimization

SQLAlchemy handles database connection pooling automatically. Adjust pool settings via environment variables if needed (SQLALCHEMY_POOL_SIZE, SQLALCHEMY_POOL_OVERFLOW).

## Development Workflow

```bash
# 1. Start services
docker-compose up -d

# 2. Make code changes (hot reload active)
# Edit files in src/

# 3. Check logs
docker-compose logs -f backend

# 4. Run tests inside container
docker-compose exec backend pytest

# 5. Stop services
docker-compose down
```

## Next Steps

- Dockerize auth-server microservice
- Dockerize ai-agent microservice
- Dockerize MCP server
- Dockerize frontend
- Create full-stack docker-compose.fullstack.yml

## Resources

- [Dockerfile Reference](https://docs.docker.com/engine/reference/builder/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/docker/)
- [Neon PostgreSQL Documentation](https://neon.tech/docs)
- [SQLAlchemy Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
