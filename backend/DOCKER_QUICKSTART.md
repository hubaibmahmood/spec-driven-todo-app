# Backend Docker Quick Start

## 🚀 Start Development Environment

### Option A: Using docker-compose (Recommended for Development)

```bash
# Start backend with hot reload
docker-compose up --build

# Start in background
docker-compose up -d --build
```

### Option B: Using Dockerfile directly

```bash
# Build the image
docker build -t todo-backend .

# Run with .env file
docker run -d \
  --name todo-backend \
  -p 8000:8000 \
  --env-file .env \
  -v $(pwd)/src:/app/src \
  -v $(pwd)/alembic:/app/alembic \
  todo-backend
```

**Access:**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

## 🛑 Stop Services

```bash
# Stop containers
docker-compose down

# Stop and remove volumes (⚠️ deletes database data)
docker-compose down -v
```

## 📊 View Logs

```bash
# All services
docker-compose logs -f

# Backend only
docker-compose logs -f backend
```

## 🔧 Common Commands

```bash
# Rebuild after dependency changes
docker-compose build --no-cache backend

# Run migrations manually
docker-compose exec backend alembic upgrade head

# Run tests
docker-compose exec backend pytest

# Access backend shell
docker-compose exec backend bash

# Check container health
docker ps
```

## ⚙️ Environment Variables

Create `.env` file (copy from `.env.example`):

```env
# Required
DATABASE_URL=postgresql+asyncpg://user:pass@your-neon-endpoint.neon.tech/todo_db
SESSION_HASH_SECRET=your-session-secret
SERVICE_AUTH_TOKEN=your-service-token
ENCRYPTION_KEY=your-encryption-key

# Optional
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:3000
AUTH_SERVER_URL=http://localhost:8080
```

## 🔐 Production Secrets

Generate secrets for production:

```bash
# Session secret
openssl rand -hex 32

# Service token
openssl rand -hex 32

# Encryption key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

## 🐛 Troubleshooting

**Container won't start:**
```bash
docker-compose logs backend
```

**Permission denied:**
```bash
chmod +x entrypoint.sh
docker-compose build --no-cache
```

**Database connection failed:**
```bash
# Check DATABASE_URL in .env
cat .env | grep DATABASE_URL

# Verify Neon PostgreSQL is accessible
# Check your Neon dashboard for connection issues
```

## 📦 What's Included

✅ Multi-stage Dockerfile (optimized for production)
✅ Connects to Neon PostgreSQL (managed database)
✅ Automatic Alembic migrations on startup
✅ Health checks for monitoring
✅ Hot reload for development
✅ Non-root user for security
✅ Prometheus metrics at /metrics

## 📝 Note: Single Service Setup

Since backend connects to managed Neon PostgreSQL, `docker-compose.yml` currently has only one service.

**Why keep docker-compose?**
- Easier development workflow (`docker-compose up` vs long `docker run` commands)
- Pre-configured volume mounts for hot reload
- Will be extended with other microservices (auth-server, ai-agent, frontend)

Once all microservices are dockerized, we'll create `docker-compose.fullstack.yml` to orchestrate everything together.

## 🔄 Development Workflow

1. Start: `docker-compose up -d`
2. Edit code (hot reload active)
3. Check logs: `docker-compose logs -f backend`
4. Stop: `docker-compose down`

See `DOCKER_README.md` for full documentation.
