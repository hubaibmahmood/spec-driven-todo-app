# Docker Setup for Momentum Frontend

Production-ready Docker configuration for the Next.js 16 App Router frontend application with standalone output optimization.

## Quick Start

```bash
# 1. Create .env file with required variables
cp .env.example .env

# 2. Build and run with Docker Compose
docker-compose up --build

# 3. Access frontend
# http://localhost:3000
```

## Architecture

### Multi-Stage Build

```
┌─────────────────────────────────────────────────────────────┐
│                     Stage 1: Dependencies                    │
│  node:20-alpine                                             │
│  - Install libc6-compat for Alpine compatibility           │
│  - Copy package.json and package-lock.json                 │
│  - Run npm ci (clean install from lockfile)                │
│  Output: /app/node_modules (all dependencies)              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Stage 2: Builder                        │
│  node:20-alpine                                             │
│  - Copy node_modules from deps stage                        │
│  - Copy application source code                             │
│  - Set NEXT_PUBLIC_* build arguments as ENV vars           │
│  - Run npm run build (creates .next/standalone output)     │
│  Output: .next/standalone (optimized server bundle)        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  Stage 3: Runner (Production)                │
│  node:20-alpine                                             │
│  - Create non-root user (nextjs, UID 1001)                 │
│  - Copy .next/standalone, .next/static, public/ from build │
│  - Expose port 3000                                         │
│  - Health check every 30s                                   │
│  - Start server: node server.js                            │
│  Final Image Size: ~150-200MB (vs ~1GB without standalone) │
└─────────────────────────────────────────────────────────────┘
```

**Benefits:**
- 75% reduction in image size (standalone output)
- Faster deployments (smaller image = faster push/pull)
- Better layer caching (dependencies separate from code)
- Enhanced security (non-root user, minimal attack surface)

## Configuration

### Environment Variables

Next.js has two types of environment variables:

#### 1. Public Variables (NEXT_PUBLIC_*)
**Available:** Client-side JavaScript
**Bundled:** At build time
**Docker Handling:** Build arguments (ARG) → ENV

```dockerfile
# Build-time arguments
ARG NEXT_PUBLIC_AUTH_URL
ARG NEXT_PUBLIC_API_URL
ARG NEXT_PUBLIC_DOMAIN_KEY
ARG NEXT_PUBLIC_GA_MEASUREMENT_ID

# Set as environment variables for build
ENV NEXT_PUBLIC_AUTH_URL=$NEXT_PUBLIC_AUTH_URL
# These values are embedded in the JavaScript bundle during build
```

**Required Variables:**

| Variable | Description | Example |
|----------|-------------|---------|
| `NEXT_PUBLIC_AUTH_URL` | Better-auth server URL | `http://auth-server:8080` |
| `NEXT_PUBLIC_API_URL` | FastAPI backend URL | `http://backend:8000` |
| `NEXT_PUBLIC_DOMAIN_KEY` | OpenAI ChatKit domain key | `local-dev` |
| `NEXT_PUBLIC_GA_MEASUREMENT_ID` | Google Analytics ID (optional) | `G-XXXXXXXXXX` |

#### 2. Server-Only Variables
This application uses only public variables. All server-side logic is handled by external microservices (backend, auth-server).

### Docker Compose Configuration

```yaml
services:
  frontend:
    build:
      args:
        # Public vars passed as build arguments
        NEXT_PUBLIC_AUTH_URL: ${NEXT_PUBLIC_AUTH_URL:-http://auth-server:8080}
        NEXT_PUBLIC_API_URL: ${NEXT_PUBLIC_API_URL:-http://backend:8000}
        NEXT_PUBLIC_DOMAIN_KEY: ${NEXT_PUBLIC_DOMAIN_KEY:-local-dev}
```

**Default Values:**
- Auth URL: `http://auth-server:8080` (Docker service name)
- API URL: `http://backend:8000` (Docker service name)
- Domain Key: `local-dev` (development mode)

## Standalone Output

### What is Standalone Output?

Next.js standalone mode creates a self-contained server bundle with only the files needed for production.

**Enabled in `next.config.ts`:**
```typescript
const nextConfig: NextConfig = {
  output: "standalone",  // Drastically reduces image size
};
```

**Without Standalone:**
- Full node_modules (~500MB)
- Dev dependencies included
- Total image: ~1GB

**With Standalone:**
- Minimal dependencies (~50MB)
- Only production files
- Total image: ~150-200MB

### Directory Structure After Build

```
.next/
├── standalone/           # Self-contained server bundle
│   ├── node_modules/     # Only required dependencies
│   ├── server.js         # Entry point
│   └── ...
├── static/               # Static assets (JS, CSS)
└── ...
```

**Dockerfile copies:**
```dockerfile
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public
```

## Security Features

### 1. Non-Root User Execution
```dockerfile
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

USER nextjs  # Run as nextjs user, not root
```

**Why:** Limits blast radius if container is compromised.

### 2. Minimal Base Image
```dockerfile
FROM node:20-alpine AS runner
```

**Benefits:**
- Smaller attack surface (~40MB base vs ~900MB for full node image)
- Fewer vulnerabilities
- Faster deployments

### 3. .dockerignore
Prevents sensitive files from being copied into the image:
- `.env`, `.env.local` (secrets)
- `node_modules` (rebuilds from lockfile)
- `.git` (source control history)
- Test files and documentation

### 4. Health Checks
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s \
  CMD node -e "require('http').get('http://localhost:3000/api/health', ...)"
```

**Benefits:**
- Docker monitors container health
- Automatic restart if unhealthy
- Load balancer integration

## Deployment

### Local Development

```bash
# 1. Create todo-network (shared with backend services)
docker network create todo-network

# 2. Start backend and auth services first
cd ../backend && docker-compose up -d
cd ../auth-server && docker-compose up -d

# 3. Start frontend
cd ../frontend
docker-compose up --build

# 4. Access application
# http://localhost:3000
```

### Production Deployment (Vercel)

This frontend is designed for Vercel deployment (not Docker in production):

```bash
# Deploy to Vercel
vercel --prod

# Set environment variables in Vercel dashboard:
# NEXT_PUBLIC_AUTH_URL = https://auth.yourdomain.com
# NEXT_PUBLIC_API_URL = https://api.yourdomain.com
# NEXT_PUBLIC_DOMAIN_KEY = your-chatkit-domain-key
# NEXT_PUBLIC_GA_MEASUREMENT_ID = G-XXXXXXXXXX
```

**Docker Usage:**
- **Local Development:** Full microservices stack with Docker Compose
- **Production:** Vercel (optimized for Next.js serverless)

### Standalone Docker Production (Alternative)

If deploying frontend via Docker (Railway, Render, etc.):

```bash
# Build with production environment variables
docker build -t momentum-frontend:latest \
  --build-arg NEXT_PUBLIC_AUTH_URL=https://auth.yourdomain.com \
  --build-arg NEXT_PUBLIC_API_URL=https://api.yourdomain.com \
  --build-arg NEXT_PUBLIC_DOMAIN_KEY=your-key \
  --build-arg NEXT_PUBLIC_GA_MEASUREMENT_ID=G-XXXXXXXXXX \
  .

# Run container
docker run -d \
  --name momentum-frontend \
  -p 3000:3000 \
  momentum-frontend:latest
```

**Railway/Render Configuration:**
- Build command: `docker build -t frontend .`
- Start command: `docker run -p 3000:3000 frontend`
- Environment variables: Set in platform dashboard

## Troubleshooting

### Issue: Image size > 500MB
**Solution:** Ensure `output: "standalone"` is in `next.config.ts`. Rebuild:
```bash
docker-compose build --no-cache
```

### Issue: Environment variables not available in browser
**Symptom:** `process.env.NEXT_PUBLIC_API_URL` is undefined

**Solution:** NEXT_PUBLIC_* vars must be passed as build arguments:
```bash
docker build --build-arg NEXT_PUBLIC_API_URL=http://backend:8000 .
```

### Issue: Connection refused to backend/auth services
**Symptom:** `fetch('http://backend:8000')` fails

**Solutions:**
1. Ensure `todo-network` exists:
   ```bash
   docker network create todo-network
   ```

2. Verify backend/auth services are running:
   ```bash
   docker ps | grep momentum
   ```

3. Check service names in docker-compose.yml match environment variables:
   ```yaml
   NEXT_PUBLIC_API_URL: http://backend:8000  # Service name, not localhost
   ```

### Issue: 404 errors for static files
**Symptom:** Images, CSS, or JS files not loading

**Solution:** Ensure `public/` and `.next/static/` are copied in Dockerfile:
```dockerfile
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
COPY --from=builder --chown=nextjs:nodejs /app/public ./public
```

### Issue: Health check failing
**Symptom:** Container marked as unhealthy

**Solution:** Add health check endpoint to Next.js:
```typescript
// app/api/health/route.ts
export async function GET() {
  return Response.json({ status: 'ok' }, { status: 200 });
}
```

## Performance Optimization

### Build Time Optimization
- **Layer Caching:** Dependencies installed in separate stage (cached if package.json unchanged)
- **npm ci:** Faster than `npm install` (uses lockfile, no version resolution)

### Runtime Optimization
- **Standalone Output:** Only required files in production image
- **Alpine Base:** Lightweight OS (40MB vs 900MB)
- **Non-Root User:** Minimal permissions

### Image Size Comparison

| Configuration | Image Size | Build Time |
|---------------|------------|------------|
| Standard Next.js (node:20) | ~1GB | 3-5 min |
| Alpine (node:20-alpine) | ~500MB | 2-3 min |
| Alpine + Standalone | **~150-200MB** | **1-2 min** |

## Monitoring

### Container Health
```bash
# Check health status
docker inspect --format='{{.State.Health.Status}}' momentum-frontend

# View health check logs
docker inspect --format='{{range .State.Health.Log}}{{.Output}}{{end}}' momentum-frontend
```

### Application Logs
```bash
# Stream logs
docker logs -f momentum-frontend

# Last 100 lines
docker logs --tail 100 momentum-frontend
```

### Resource Usage
```bash
# Container stats (CPU, memory, network)
docker stats momentum-frontend
```

## Resources

- [Next.js Standalone Output](https://nextjs.org/docs/app/api-reference/next-config-js/output)
- [Docker Multi-Stage Builds](https://docs.docker.com/build/building/multi-stage/)
- [Alpine Linux Security](https://alpinelinux.org/about/)
- [Better-auth Documentation](https://www.better-auth.com/docs)

## Summary

This Docker configuration provides:
- ✅ Production-ready multi-stage builds
- ✅ Standalone output optimization (75% size reduction)
- ✅ Security hardening (non-root user, Alpine base)
- ✅ Health checks for monitoring
- ✅ Microservices integration (backend, auth-server)
- ✅ Environment variable management (public vs server-only)
- ✅ Comprehensive troubleshooting guide

**Image Size:** ~150-200MB
**Build Time:** ~1-2 minutes
**Security:** Non-root user, minimal attack surface
**Deployment:** Local development (Docker) + Production (Vercel recommended)
