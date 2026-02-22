# Docker Deployment Guide - Momentum Auth Server

Production-ready Docker configuration for the Momentum authentication server (Node.js/TypeScript + Express + better-auth + Prisma).

## Architecture Overview

This is a **backend microservice** providing authentication services:
- **Framework**: Express.js with TypeScript
- **Authentication**: better-auth library with email verification
- **Database**: PostgreSQL (Neon in production, local PostgreSQL in Docker)
- **ORM**: Prisma with automatic migrations
- **Email**: Resend for verification emails
- **Security**: JWT tokens, helmet middleware, CORS

## Quick Start

### Prerequisites
- Docker 24.0+
- Docker Compose 2.20+
- `.env` file with required environment variables

### Environment Variables

Create `.env` file in `auth-server/` directory:

```bash
# Server Configuration
NODE_ENV=production
PORT=3002

# Database URL (use Docker service name in docker-compose)
DATABASE_URL=postgresql://postgres:postgres@db:5432/momentum

# better-auth Configuration
BETTER_AUTH_SECRET=your-32-character-secret-key-here
BETTER_AUTH_URL=http://localhost:3002

# Frontend URL for CORS
FRONTEND_URL=http://localhost:3000

# Email Configuration (Resend)
RESEND_API_KEY=re_your_resend_api_key
EMAIL_FROM=noreply@momentum.intevia.cc

# JWT Configuration
JWT_SECRET=your-jwt-secret-key-here
JWT_EXPIRES_IN=7d
```

### Build and Run

**Development with Docker Compose:**
```bash
# Build and start all services (auth-server + postgres)
docker-compose up --build

# Run in detached mode
docker-compose up -d

# View logs
docker-compose logs -f auth-server

# Stop services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

**Production Build:**
```bash
# Build image
docker build -t momentum-auth-server:latest .

# Run with environment variables
docker run -d \
  --name auth-server \
  -p 3002:3002 \
  --env-file .env \
  momentum-auth-server:latest
```

## Docker Configuration Details

### Multi-Stage Build

The Dockerfile uses three stages for optimization:

1. **deps** - Install all dependencies (including dev)
2. **builder** - Generate Prisma client and compile TypeScript
3. **runner** - Production runtime with minimal dependencies

**Image Size**: ~150-200MB (Alpine-based)

### Security Features

- ✅ Non-root user (`authserver` with UID 1001)
- ✅ Alpine Linux base image (minimal attack surface)
- ✅ Production dependencies only in final stage
- ✅ Health check endpoint configured
- ✅ Graceful shutdown handling (SIGTERM/SIGINT)

### Health Check

The container includes a health check that pings `/health` endpoint:
- Interval: 30 seconds
- Timeout: 10 seconds
- Start period: 40 seconds (allows migrations to complete)
- Retries: 3

Check health status:
```bash
docker inspect --format='{{.State.Health.Status}}' momentum-auth-server
```

## Database Migrations

Prisma migrations run automatically via `entrypoint.sh`:

1. Wait for PostgreSQL to be ready
2. Run `npx prisma migrate deploy`
3. Start auth server

**Manual migration** (if needed):
```bash
# Enter container
docker exec -it momentum-auth-server sh

# Run migrations
npx prisma migrate deploy

# Generate Prisma client
npx prisma generate
```

## Integration with Other Services

### With Frontend (Next.js)

**Port Configuration:**
- Frontend runs on: `http://localhost:3000`
- Auth-server runs on: `http://localhost:3002`
- Frontend connects to auth-server at: `http://localhost:3002/api/auth`

**Frontend environment variables:**
```bash
# Frontend .env.local
NEXT_PUBLIC_AUTH_URL=http://localhost:3002/api/auth
```

**Auth-server environment variables:**
```bash
# Auth-server .env
FRONTEND_URL=http://localhost:3000  # For CORS configuration
```

### With Backend API (FastAPI)

Both services share the same PostgreSQL database:

**Shared database:**
- Auth-server: Manages `user`, `session`, `account`, `verification` tables
- Backend API: Manages `tasks` table

**Service-to-service auth:**
- Backend validates JWTs issued by auth-server
- Use `X-Service-Auth` header for internal communication

### Docker Network

Services communicate via `momentum-network` bridge network:
```yaml
networks:
  momentum-network:
    driver: bridge
```

**Service names resolve as hostnames:**
- `db` → PostgreSQL
- `auth-server` → Auth service
- `frontend` → Next.js app (if in same compose file)
- `api` → FastAPI backend (if in same compose file)

## Troubleshooting

### Container won't start

**Check logs:**
```bash
docker-compose logs auth-server
```

**Common issues:**
1. Missing environment variables → Check `.env` file
2. Database not ready → Increase health check start period
3. Port already in use → Change `PORT` in .env

### Database connection errors

**Verify database is running:**
```bash
docker-compose ps db
```

**Test connection:**
```bash
docker exec -it momentum-postgres psql -U postgres -d momentum -c "SELECT 1"
```

**Check DATABASE_URL format:**
```
postgresql://USER:PASSWORD@HOST:5432/DATABASE
```

### Prisma migration failures

**Reset database** (⚠️ deletes all data):
```bash
docker-compose down -v  # Remove volumes
docker-compose up --build  # Fresh start
```

**Run migrations manually:**
```bash
docker exec -it momentum-auth-server npx prisma migrate deploy
```

### Email verification not working

**Check Resend configuration:**
```bash
docker exec -it momentum-auth-server env | grep RESEND
```

**Test email sending:**
- Verify `RESEND_API_KEY` is valid
- Check `EMAIL_FROM` domain is verified in Resend dashboard
- Review auth-server logs for email sending errors

### CORS errors from frontend

**Update FRONTEND_URL:**
```bash
# In .env
FRONTEND_URL=http://localhost:3000
```

**Allow additional origins** (if needed):
- Edit `src/app.ts` to add origins to CORS configuration

## Production Deployment

### Environment Variables

**Security checklist:**
- ✅ Generate strong `BETTER_AUTH_SECRET` (32+ characters)
- ✅ Use separate `JWT_SECRET` from better-auth secret
- ✅ Set `NODE_ENV=production`
- ✅ Use production `DATABASE_URL` (Neon/managed PostgreSQL)
- ✅ Configure `BETTER_AUTH_URL` with production domain
- ✅ Set `FRONTEND_URL` to production frontend domain
- ✅ Verify `EMAIL_FROM` domain in Resend

### Deployment Platforms

**Render/Railway/Fly.io:**
```bash
# Build command
npm ci && npx prisma generate && npm run build

# Start command
npx prisma migrate deploy && node dist/index.js
```

**Docker deployment:**
```bash
# Build and tag
docker build -t registry.example.com/momentum-auth-server:v1.0.0 .

# Push to registry
docker push registry.example.com/momentum-auth-server:v1.0.0

# Deploy to production
docker run -d \
  --name auth-server \
  -p 3002:3002 \
  --env-file .env.production \
  --restart unless-stopped \
  registry.example.com/momentum-auth-server:v1.0.0
```

## Monitoring

### Health Check Endpoint

**HTTP GET `/health`** returns:
```json
{
  "status": "healthy",
  "timestamp": "2026-02-07T12:00:00.000Z",
  "uptime": 3600
}
```

### Container Metrics

```bash
# CPU/Memory usage
docker stats momentum-auth-server

# Logs (last 100 lines)
docker logs --tail 100 momentum-auth-server

# Follow logs in real-time
docker logs -f momentum-auth-server
```

## Development Workflow

### Local Development (without Docker)

```bash
# Install dependencies
npm install

# Generate Prisma client
npx prisma generate

# Run migrations
npx prisma migrate dev

# Start dev server with hot reload
npm run dev
```

### Hybrid Development (Docker DB, local server)

```bash
# Start only PostgreSQL
docker-compose up db

# Run auth-server locally
npm run dev
```

### Testing Database Changes

```bash
# Create migration
npx prisma migrate dev --name add_new_field

# Apply migration in Docker
docker exec -it momentum-auth-server npx prisma migrate deploy
```

## References

- [better-auth Documentation](https://www.better-auth.com/docs)
- [Prisma Documentation](https://www.prisma.io/docs)
- [Express.js Guide](https://expressjs.com/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
