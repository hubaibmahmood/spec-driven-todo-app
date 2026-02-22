# Docker Quick Start - Frontend

Get the Momentum frontend running in Docker in under 5 minutes.

## Prerequisites

- Docker and Docker Compose installed
- Backend and auth-server services running (or accessible)

## Quick Start

### Step 1: Environment Setup

Create `.env` file in `frontend/` directory:

```bash
# Copy example environment file
cp .env.example .env
```

**Edit `.env` with your configuration:**

```env
# Auth Service URL (use service name for Docker network)
NEXT_PUBLIC_AUTH_URL="http://auth-server:8080"

# Backend API URL (use service name for Docker network)
NEXT_PUBLIC_API_URL="http://backend:8000"

# ChatKit Domain Key
NEXT_PUBLIC_DOMAIN_KEY="local-dev"

# Google Analytics (optional)
NEXT_PUBLIC_GA_MEASUREMENT_ID=""
```

### Step 2: Build and Run

**Option A: Docker Compose (Recommended)**

```bash
# Create shared network if it doesn't exist
docker network create todo-network

# Build and run frontend
docker-compose up --build

# Access application
# http://localhost:3000
```

**Option B: Standalone Docker**

```bash
# Build image
docker build -t momentum-frontend:latest \
  --build-arg NEXT_PUBLIC_AUTH_URL=http://auth-server:8080 \
  --build-arg NEXT_PUBLIC_API_URL=http://backend:8000 \
  --build-arg NEXT_PUBLIC_DOMAIN_KEY=local-dev \
  .

# Run container
docker run -d \
  --name momentum-frontend \
  --network todo-network \
  -p 3000:3000 \
  momentum-frontend:latest

# Access application
# http://localhost:3000
```

### Step 3: Verify

Check container health:

```bash
# View logs
docker logs -f momentum-frontend

# Check health status
docker ps | grep momentum-frontend

# Test endpoint
curl http://localhost:3000
```

## Full Microservices Stack

Run all services together:

```bash
# 1. Create shared network
docker network create todo-network

# 2. Start backend services
cd backend
docker-compose up -d
cd ..

# 3. Start auth server
cd auth-server
docker-compose up -d
cd ..

# 4. Start frontend
cd frontend
docker-compose up -d
cd ..

# 5. Verify all services
docker ps | grep momentum

# Expected output:
# momentum-frontend  (port 3000)
# momentum-backend   (port 8000)
# momentum-auth-server (port 8080)
```

## Common Issues

### Issue: "Cannot connect to backend/auth service"

**Solution:** Ensure services are running and on the same network:

```bash
# Check if services are running
docker ps | grep momentum

# Check network connectivity
docker network inspect todo-network

# Restart services if needed
docker-compose restart
```

### Issue: "Environment variables not available"

**Solution:** Rebuild with build arguments:

```bash
# Rebuild with no cache
docker-compose build --no-cache

# Or pass build args explicitly
docker build --build-arg NEXT_PUBLIC_API_URL=http://backend:8000 .
```

### Issue: "Port 3000 already in use"

**Solution:** Stop existing process or use different port:

```bash
# Find process using port 3000
lsof -ti:3000 | xargs kill -9

# Or use custom port in docker-compose.yml
ports:
  - "3001:3000"
```

### Issue: "Image size too large (> 500MB)"

**Solution:** Verify standalone output is enabled in `next.config.ts`:

```typescript
const nextConfig: NextConfig = {
  output: "standalone",  // Required for optimized images
};
```

Then rebuild:

```bash
docker-compose build --no-cache
```

## Development Workflow

### Watch Logs
```bash
docker logs -f momentum-frontend
```

### Rebuild After Code Changes
```bash
# Code changes require rebuild (standalone output is not hot-reloadable)
docker-compose up --build
```

### Stop and Remove
```bash
# Stop container
docker-compose down

# Remove image
docker rmi momentum-frontend:latest
```

### Clean Up
```bash
# Remove all containers and images
docker-compose down --rmi all --volumes
```

## Next Steps

- Read full documentation: [DOCKER_README.md](./DOCKER_README.md)
- Configure production deployment: Vercel or Railway
- Set up monitoring and observability
- Integrate with CI/CD pipeline

## Resource Links

- [Next.js Standalone Output](https://nextjs.org/docs/app/api-reference/next-config-js/output)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Momentum Architecture Overview](../README.md)
