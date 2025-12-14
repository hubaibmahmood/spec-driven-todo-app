# FastAPI Backend - Render Deployment Guide

## Overview

This guide covers deploying the FastAPI Todo API backend to Render.com, a modern cloud platform with automatic deploys from Git.

## Prerequisites

- [x] Render account (sign up at https://render.com)
- [x] Neon PostgreSQL database (connection string from https://console.neon.tech)
- [x] GitHub repository with your code
- [ ] Redis instance (optional, for rate limiting - Render paid plan)

## Quick Start Deployment

### Option 1: Using Render Blueprint (Recommended)

The easiest way to deploy is using the `render.yaml` blueprint file.

1. **Push your code to GitHub** (if not already done)
   ```bash
   git add .
   git commit -m "Add Render deployment configuration"
   git push origin main
   ```

2. **Create New Blueprint Instance**
   - Go to https://dashboard.render.com/blueprints
   - Click **"New Blueprint Instance"**
   - Connect your GitHub repository
   - Select the repository containing your backend
   - Render will auto-detect `backend/render.yaml`
   - Click **"Apply"**

3. **Configure Environment Variables** (see below)

4. **Deploy** - Render will automatically build and deploy

### Option 2: Manual Web Service Creation

1. **Create New Web Service**
   - Go to https://dashboard.render.com
   - Click **"New +"** → **"Web Service"**
   - Connect your GitHub repository
   - Configure as follows:

   | Setting | Value |
   |---------|-------|
   | **Name** | `momentum-todo-api` (or your preferred name) |
   | **Region** | Choose closest to your users |
   | **Branch** | `main` |
   | **Root Directory** | `backend` |
   | **Runtime** | `Python 3` |
   | **Build Command** | `./build.sh` |
   | **Start Command** | `uvicorn src.api.main:app --host 0.0.0.0 --port $PORT` |
   | **Plan** | Free (or upgrade as needed) |

2. **Add Environment Variables** (see Environment Variables section)

3. **Create Web Service** - Render will build and deploy

## Environment Variables

Add these environment variables in Render Dashboard:

### Required Variables

| Variable | Value | Description |
|----------|-------|-------------|
| `DATABASE_URL` | `postgresql+asyncpg://user:pass@ep-xxx.neon.tech/db` | Neon PostgreSQL connection string |
| `SESSION_HASH_SECRET` | Generate with command below | Shared secret for session hashing |
| `ENVIRONMENT` | `production` | Application environment |
| `CORS_ORIGINS` | `https://your-frontend.netlify.app` | Allowed CORS origins (comma-separated) |

### Optional Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SQLALCHEMY_POOL_SIZE` | `5` | Database connection pool size |
| `SQLALCHEMY_POOL_OVERFLOW` | `10` | Max additional connections |
| `SQLALCHEMY_POOL_TIMEOUT` | `30` | Connection timeout in seconds |
| `SQLALCHEMY_POOL_RECYCLE` | `3600` | Connection recycle time |
| `SQLALCHEMY_ECHO` | `false` | Log SQL queries (debug only) |
| `REDIS_URL` | N/A | Redis connection URL (for rate limiting) |

### Generate SESSION_HASH_SECRET

```bash
openssl rand -hex 32
```

**IMPORTANT:** This secret must match the `SESSION_HASH_SECRET` in your auth-server!

## Deployment Steps

### 1. Prepare Database

Ensure your Neon PostgreSQL database is ready:

```bash
# Test connection locally
psql "postgresql://user:pass@ep-xxx.neon.tech/db"
```

### 2. Update CORS Origins

Update the `CORS_ORIGINS` environment variable with your production frontend URL:

```bash
# Example for Netlify frontend
CORS_ORIGINS=https://your-app.netlify.app,https://your-app.com
```

### 3. Configure Build Script

The `build.sh` script handles:
- Installing dependencies from `requirements.txt`
- Running Alembic migrations with `alembic upgrade head`

**Note:** The build script is already configured and executable.

### 4. Deploy

**Automatic Deployment (Recommended):**
- Push to your configured Git branch
- Render automatically builds and deploys
- Check build logs in Render dashboard

**Manual Deployment:**
- Go to Render Dashboard → Your Service
- Click **"Manual Deploy"** → **"Deploy latest commit"**

### 5. Verify Deployment

Test your deployed API:

```bash
# Health check
curl https://momentum-todo-api.onrender.com/health

# Expected response:
# {
#   "status": "healthy",
#   "timestamp": "2025-12-14T...",
#   "database": "connected"
# }
```

## Project Structure for Render

```
backend/
├── src/
│   ├── api/
│   │   ├── main.py           # FastAPI app entry point
│   │   ├── routers/          # API endpoints
│   │   └── schemas/          # Pydantic models
│   ├── models/
│   │   └── database.py       # SQLAlchemy models
│   ├── database/
│   │   ├── connection.py     # Database connection
│   │   └── repository.py     # Data access layer
│   ├── services/
│   │   └── auth_service.py   # Authentication logic
│   └── config.py             # App configuration
├── alembic/
│   ├── env.py                # Alembic environment
│   └── versions/             # Migration files
├── tests/                    # Test suite
├── requirements.txt          # Python dependencies
├── build.sh                  # Render build script
├── render.yaml               # Render blueprint
├── alembic.ini               # Alembic configuration
└── pyproject.toml            # Project metadata
```

## Database Migrations

### Automatic Migrations (During Build)

Migrations run automatically during Render builds via `build.sh`:

```bash
alembic upgrade head
```

### Manual Migration (If Needed)

You can run migrations manually using Render Shell:

1. Go to Render Dashboard → Your Service
2. Click **"Shell"** tab
3. Run:
   ```bash
   alembic upgrade head
   ```

### Create New Migration (Locally)

```bash
cd backend
alembic revision --autogenerate -m "Add new field to tasks"
git add alembic/versions/
git commit -m "Add migration: Add new field to tasks"
git push origin main  # Triggers automatic deployment
```

## Performance Optimization

### Connection Pooling

For Render free tier, optimize connection pool:

```bash
SQLALCHEMY_POOL_SIZE=5
SQLALCHEMY_POOL_OVERFLOW=10
SQLALCHEMY_POOL_RECYCLE=3600
```

Neon free tier allows ~95 concurrent connections.

### Cold Starts

Render free tier services spin down after 15 minutes of inactivity:
- First request after spin-down takes ~30 seconds
- Keep-alive services available on paid plans
- Use external monitoring (e.g., UptimeRobot) to prevent spin-down

## Monitoring & Logs

### View Logs

**In Render Dashboard:**
- Go to your service
- Click **"Logs"** tab
- Real-time logs appear here

**Via Render CLI:**
```bash
# Install Render CLI
brew install render  # macOS
# or
curl -L https://github.com/render-oss/cli/releases/latest/download/render-linux-amd64 -o render

# View logs
render logs -t <service-id>
```

### Health Check Endpoint

Render automatically monitors `/health`:
- 2xx response = healthy
- Non-2xx response = unhealthy (triggers restart)

## Common Issues & Solutions

### Issue: Build Failed - "Permission Denied: ./build.sh"

**Solution:**
```bash
chmod +x backend/build.sh
git add backend/build.sh
git commit -m "Make build.sh executable"
git push
```

### Issue: Database Connection Failed

**Solutions:**
1. Verify `DATABASE_URL` format: `postgresql+asyncpg://...`
2. Check Neon database is running in Neon dashboard
3. Ensure `?sslmode=require` is appended (if using SSL)

### Issue: CORS Errors from Frontend

**Solution:**
Update `CORS_ORIGINS` in Render dashboard:
```bash
# Format (no spaces after commas):
CORS_ORIGINS=https://app.netlify.app,https://app.com
```

### Issue: 500 Internal Server Error

**Debug:**
1. Check Render logs for error details
2. Verify all required environment variables are set
3. Test database connection in Render Shell:
   ```bash
   python -c "from src.config import settings; print(settings.DATABASE_URL)"
   ```

### Issue: Alembic Migration Failed

**Solution:**
```bash
# In Render Shell:
alembic current  # Check current revision
alembic history  # View migration history
alembic upgrade head --sql  # Preview SQL
alembic upgrade head  # Apply migrations
```

## Scaling & Upgrades

### Free Tier Limits

- **CPU:** Shared
- **RAM:** 512 MB
- **Bandwidth:** 100 GB/month
- **Build minutes:** 500/month
- **Disk:** Ephemeral
- **Spin down:** After 15 minutes inactivity

### Upgrade to Starter Plan ($7/month)

Benefits:
- Always-on (no spin down)
- 512 MB RAM
- Faster builds
- Custom domains

### Upgrade to Standard Plan ($25/month+)

Benefits:
- 2GB+ RAM
- Dedicated CPU
- Faster performance
- Auto-scaling
- Redis support

## CI/CD Integration

### Automatic Deployments

Enabled by default when using Git integration:

```yaml
# In render.yaml
autoDeploy: true
```

Push to main branch → Automatic deployment

### Deploy Hooks

Trigger deployments via webhook:

```bash
# Get deploy hook from Render Dashboard → Settings → Deploy Hook
curl -X POST https://api.render.com/deploy/srv-xxxxx?key=xxxxx
```

### Pre-Deploy Commands

Add in `render.yaml`:

```yaml
preDeployCommand: "python -m pytest tests/"  # Run tests before deploy
```

## Security Best Practices

- [x] Use environment variables for secrets (never commit `.env`)
- [x] Set `ENVIRONMENT=production` to disable debug mode
- [x] Restrict `CORS_ORIGINS` to your domains only
- [x] Use strong `SESSION_HASH_SECRET` (32+ characters)
- [x] Enable HTTPS (automatic on Render)
- [x] Use Neon SSL connections (`?sslmode=require`)
- [ ] Set up IP allowlisting in Neon (optional)
- [ ] Enable DDoS protection (Render paid plans)

## Custom Domain (Optional)

1. Go to Render Dashboard → Your Service → Settings
2. Click **"Add Custom Domain"**
3. Enter your domain (e.g., `api.yourdomain.com`)
4. Add DNS records as instructed by Render:
   ```
   Type: CNAME
   Name: api
   Value: momentum-todo-api.onrender.com
   ```
5. Wait for DNS propagation (~24 hours max)
6. Render auto-provisions SSL certificate

## Connecting Frontend to Backend

Update your frontend environment variables:

```bash
# Netlify/Vercel Frontend
VITE_API_URL=https://momentum-todo-api.onrender.com
VITE_AUTH_SERVER_URL=https://momentum-auth-server.vercel.app
```

Ensure both URLs are in the auth-server's `CORS_ORIGINS`.

## Rollback Deployment

If a deployment fails:

1. Go to Render Dashboard → Deployments
2. Find previous working deployment
3. Click **"..."** → **"Redeploy"**

## Backup & Disaster Recovery

### Database Backups

Neon automatically backs up your database:
- Point-in-time recovery available
- Backups retained per your Neon plan

### Service Snapshots

Render doesn't support direct snapshots, but you can:
- Use Git tags for version control
- Export database regularly
- Document environment variables

## Cost Optimization Tips

1. **Use Free Tier for Development**
   - Perfect for testing and low-traffic apps
   - Upgrade when needed

2. **Optimize Connection Pool**
   - Lower `POOL_SIZE` for free tier
   - Prevents exhausting Neon connections

3. **Monitor Usage**
   - Render Dashboard → Usage & Billing
   - Track bandwidth and build minutes

4. **Use Neon Autoscaling**
   - Neon automatically scales compute
   - Pay only for active time

## Support Resources

- **Render Documentation:** https://render.com/docs
- **Render Community:** https://community.render.com
- **FastAPI Documentation:** https://fastapi.tiangolo.com
- **SQLAlchemy Documentation:** https://docs.sqlalchemy.org
- **Alembic Documentation:** https://alembic.sqlalchemy.org

## Next Steps After Deployment

1. ✅ Test all API endpoints
2. ✅ Update frontend with production API URL
3. ✅ Configure custom domain (optional)
4. ✅ Set up monitoring/alerts
5. ✅ Enable auto-scaling (if using paid plan)
6. ✅ Document API with `/docs` (FastAPI automatic docs)

## Production Checklist

- [ ] All environment variables configured
- [ ] Database migrations applied successfully
- [ ] Health check endpoint responding
- [ ] CORS configured for production frontend
- [ ] Logs show no errors
- [ ] API accessible from frontend
- [ ] Authentication working end-to-end
- [ ] Custom domain configured (optional)
- [ ] SSL certificate active
- [ ] Monitoring set up

---

**Congratulations!** Your FastAPI backend is now deployed on Render. 🚀
