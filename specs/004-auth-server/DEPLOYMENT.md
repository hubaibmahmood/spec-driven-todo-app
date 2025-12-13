# Deployment Checklist: Auth Server + FastAPI Backend

**Feature**: 004-auth-server
**Purpose**: Pre-deployment validation checklist for production readiness

---

## Pre-Deployment Checklist

### 1. Code Readiness

#### Auth Server (Node.js/TypeScript)
- [ ] All TypeScript files compile without errors (`npm run build`)
- [ ] No console errors or warnings in production build
- [ ] Environment validation working (`src/config/env.ts`)
- [ ] Prisma schema matches production database
- [ ] All dependencies in `package.json` have locked versions
- [ ] `.gitignore` excludes `.env`, `node_modules`, `dist/`

#### FastAPI Backend (Python)
- [ ] All type checks pass (`mypy src/`)
- [ ] All linting passes (`ruff check`)
- [ ] All tests pass (`pytest`)
- [ ] Requirements.txt up to date
- [ ] Database migrations applied
- [ ] `.gitignore` excludes `.env`, `__pycache__`, `*.pyc`

---

### 2. Database Setup (Neon PostgreSQL)

- [ ] Production database created in Neon
- [ ] Connection string obtained and secured
- [ ] Connection pooling configured (default: 100 connections)
- [ ] Database schema pushed via Prisma (`npx prisma db push`)
- [ ] Prisma client generated (`npx prisma generate`)
- [ ] Database accessible from both auth server and API server
- [ ] SSL mode enabled (`?sslmode=require`)
- [ ] Test query successful from both services

**Connection String Format**:
```
postgresql://user:password@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require
```

---

### 3. Environment Variables

#### Auth Server (Vercel)

**Required**:
- [ ] `DATABASE_URL` - PostgreSQL connection string
- [ ] `JWT_SECRET` - 32+ character random string
- [ ] `NODE_ENV` - Set to `production`
- [ ] `CORS_ORIGINS` - Comma-separated frontend URLs
- [ ] `FRONTEND_URL` - Primary frontend URL

**Email Service (Resend)**:
- [ ] `RESEND_API_KEY` - API key from resend.com
- [ ] `EMAIL_FROM` - Verified sender email

**OAuth (Optional - Phase 9)**:
- [ ] `GOOGLE_CLIENT_ID` - Google OAuth client ID
- [ ] `GOOGLE_CLIENT_SECRET` - Google OAuth client secret
- [ ] `GOOGLE_REDIRECT_URI` - OAuth callback URL

#### FastAPI Backend (Render)

**Required**:
- [ ] `DATABASE_URL` - PostgreSQL connection string (with `postgresql+asyncpg://`)
- [ ] `AUTH_SERVER_URL` - Auth server production URL
- [ ] `CORS_ORIGINS` - Comma-separated allowed origins
- [ ] `FRONTEND_ORIGIN` - Frontend URL for CORS
- [ ] `ENVIRONMENT` - Set to `production`

**Validation Script**:
```bash
# Auth server
cd auth-server
node -e "require('./dist/config/env.js')" && echo "✅ Env vars valid"

# API server
cd backend
python -c "from src.config import settings; print('✅ Env vars valid')"
```

---

### 4. Auth Server Deployment (Vercel)

#### Pre-Flight Checks
- [ ] `vercel.json` exists with catch-all rewrite
- [ ] `api/index.ts` exports Express app
- [ ] `package.json` has `vercel-build` script
- [ ] `tsconfig.json` configured for ESM output
- [ ] Prisma schema compatible with Neon PostgreSQL

#### Deployment Steps
```bash
cd auth-server
npm install -g vercel  # If not installed
vercel login
vercel --prod
```

#### Post-Deployment Validation
- [ ] Health endpoint responds: `curl https://your-auth.vercel.app/health`
- [ ] Database connection confirmed in health response
- [ ] Signup endpoint works: `POST /api/auth/signup`
- [ ] Signin endpoint works: `POST /api/auth/signin`
- [ ] Email verification sends (check Resend dashboard)
- [ ] Password reset works: `POST /api/auth/forgot-password`
- [ ] CORS headers present in responses
- [ ] Cookies set with secure flags in production

**Expected Health Response**:
```json
{
  "status": "ok",
  "timestamp": "2025-01-10T12:00:00.000Z",
  "database": "connected"
}
```

---

### 5. FastAPI Backend Deployment (Render)

#### Pre-Flight Checks
- [ ] `render.yaml` configured (or manual Render settings)
- [ ] `requirements.txt` includes all dependencies
- [ ] Database models match Prisma schema
- [ ] CORS middleware configured with production origins
- [ ] `get_current_user` dependency validates tokens correctly

#### Deployment Steps (via Render Dashboard)
1. **Connect Repository**:
   - [ ] GitHub repo linked to Render
   - [ ] Correct branch selected (e.g., `main`)

2. **Configure Service**:
   - [ ] Service name: `todo-api`
   - [ ] Environment: Python 3.12
   - [ ] Build command: `pip install -r requirements.txt`
   - [ ] Start command: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`

3. **Set Environment Variables** (see section 3)

4. **Deploy**: Click "Create Web Service"

#### Post-Deployment Validation
- [ ] Health endpoint responds: `curl https://your-api.onrender.com/health`
- [ ] Protected endpoints require authentication (401 without token)
- [ ] Valid token from auth server grants access
- [ ] User isolation works (user A can't access user B's data)
- [ ] Token expiration handled correctly (401 for expired tokens)
- [ ] CORS allows requests from frontend domain

**Test Protected Endpoint**:
```bash
# Get token from auth server
TOKEN=$(curl -X POST https://your-auth.vercel.app/api/auth/signin \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password"}' \
  | jq -r '.session.token')

# Call protected endpoint
curl https://your-api.onrender.com/api/tasks \
  -H "Authorization: Bearer $TOKEN"
```

---

### 6. DNS and Domain Configuration

#### Auth Server
- [ ] Custom domain configured in Vercel (optional)
- [ ] SSL certificate auto-provisioned by Vercel
- [ ] DNS records propagated
- [ ] HTTPS working on custom domain

**Example DNS (Vercel)**:
```
Type: CNAME
Name: auth
Value: cname.vercel-dns.com
```

#### API Server
- [ ] Custom domain configured in Render (optional)
- [ ] SSL certificate auto-provisioned by Render
- [ ] DNS records propagated
- [ ] HTTPS working on custom domain

**Example DNS (Render)**:
```
Type: CNAME
Name: api
Value: your-service.onrender.com
```

#### Update Environment Variables After DNS
- [ ] Update `CORS_ORIGINS` with production domains
- [ ] Update `FRONTEND_URL` to production domain
- [ ] Update `GOOGLE_REDIRECT_URI` if using OAuth
- [ ] Redeploy both services after changes

---

### 7. Security Hardening

#### Auth Server
- [ ] Helmet middleware installed and configured
- [ ] Security headers present (CSP, HSTS, X-Frame-Options)
- [ ] HTTPS enforced (cookies secure flag set)
- [ ] SameSite cookie attribute set to `none` for production
- [ ] JWT secret is strong (32+ characters)
- [ ] Rate limiting configured (optional)
- [ ] No secrets in source code or logs

#### FastAPI Backend
- [ ] CORS origins restricted to known domains
- [ ] SQL injection protection (parameterized queries via ORM)
- [ ] Input validation on all endpoints
- [ ] No database credentials in source code
- [ ] Error messages don't leak sensitive info
- [ ] Security headers configured

#### Database
- [ ] SSL/TLS enabled for connections
- [ ] Database user has minimal required permissions
- [ ] Connection pooling configured correctly
- [ ] No public access to database

---

### 8. Monitoring and Observability

#### Auth Server (Vercel)
- [ ] Vercel Analytics enabled
- [ ] Error tracking configured (Sentry/LogRocket optional)
- [ ] Function logs accessible in Vercel dashboard
- [ ] Uptime monitoring configured

#### FastAPI Backend (Render)
- [ ] Render logs accessible
- [ ] Health check endpoint configured
- [ ] Error tracking configured (optional)
- [ ] Uptime monitoring configured (UptimeRobot/Pingdom optional)

#### Database (Neon)
- [ ] Connection count monitored
- [ ] Query performance tracked
- [ ] Storage usage monitored
- [ ] Backup strategy in place (Neon auto-backups)

---

### 9. Testing in Production

#### End-to-End Auth Flow
- [ ] **Sign Up**: User can register with email/password
- [ ] **Email Verification**: Verification email sent and link works
- [ ] **Sign In**: User can sign in after verification
- [ ] **Session Token**: Token included in response
- [ ] **Protected API**: Token works with FastAPI endpoints
- [ ] **Sign Out**: Token invalidated after signout
- [ ] **Token Expiration**: Expired tokens return 401

#### Password Reset Flow
- [ ] **Request Reset**: `POST /api/auth/forgot-password` sends email
- [ ] **Reset Email**: Email received with reset link
- [ ] **Reset Password**: `POST /api/auth/reset-password` updates password
- [ ] **Sign In**: New password works for signin

#### Error Scenarios
- [ ] Invalid credentials return 401
- [ ] Missing token returns 401
- [ ] Expired token returns 401
- [ ] Unverified email handled correctly
- [ ] Invalid email format rejected
- [ ] Weak password rejected

---

### 10. Performance Validation

#### Auth Server
- [ ] Cold start time acceptable (<3s on Vercel)
- [ ] Health check responds in <500ms
- [ ] Signup completes in <2s
- [ ] Signin completes in <1s
- [ ] Database queries optimized (indexes present)

#### FastAPI Backend
- [ ] Health check responds in <500ms
- [ ] Protected endpoint with token validation <1s
- [ ] Database connection pool not exhausted
- [ ] No N+1 query problems

#### Database
- [ ] Queries use indexes (check Neon query insights)
- [ ] Connection count within limits (free tier: 100)
- [ ] No long-running queries blocking resources

---

### 11. Rollback Plan

#### If Deployment Fails

**Auth Server (Vercel)**:
```bash
# Rollback to previous deployment
vercel rollback
```

**FastAPI Backend (Render)**:
- Use Render dashboard to redeploy previous commit
- Or rollback Git commit and trigger redeploy

#### If Database Migration Fails
- Neon provides point-in-time restore (up to 7 days on free tier)
- Restore to pre-migration snapshot
- Fix schema issues locally
- Test migration again

#### Emergency Contacts
- Database: Neon support (support@neon.tech)
- Auth Server: Vercel support
- API Server: Render support

---

### 12. Post-Deployment Documentation

- [ ] Update README.md with production URLs
- [ ] Document environment variables in team wiki
- [ ] Share deployment runbook with team
- [ ] Update API documentation with production endpoints
- [ ] Document rollback procedures
- [ ] Create incident response plan

---

### 13. Final Validation Checklist

- [ ] ✅ Auth server deployed and healthy
- [ ] ✅ API server deployed and healthy
- [ ] ✅ Database connected from both services
- [ ] ✅ End-to-end signup flow works
- [ ] ✅ End-to-end signin flow works
- [ ] ✅ Password reset flow works
- [ ] ✅ Protected API endpoints work with tokens
- [ ] ✅ CORS configured correctly
- [ ] ✅ Security headers present
- [ ] ✅ Monitoring enabled
- [ ] ✅ Team notified of deployment
- [ ] ✅ Documentation updated

---

## Production URLs Reference

After deployment, update these:

```bash
# Auth Server
PROD_AUTH_URL=https://auth.yourdomain.com
# or
PROD_AUTH_URL=https://your-project.vercel.app

# API Server
PROD_API_URL=https://api.yourdomain.com
# or
PROD_API_URL=https://your-service.onrender.com

# Frontend
PROD_FRONTEND_URL=https://yourdomain.com

# Database
NEON_DATABASE_URL=postgresql://user:pass@ep-xxx.neon.tech/neondb?sslmode=require
```

---

## Support and Troubleshooting

### Common Issues

**Issue: 401 Unauthorized on API endpoints**
- Verify token format: `Authorization: Bearer <token>`
- Check token hasn't expired (7 days)
- Verify auth server and API share same database

**Issue: CORS errors**
- Add frontend domain to `CORS_ORIGINS` in both services
- Redeploy after environment variable changes
- Clear browser cache

**Issue: Email verification not sending**
- Check `RESEND_API_KEY` is set
- Verify sender email in Resend dashboard
- Check Resend send logs for errors

**Issue: Database connection errors**
- Verify `DATABASE_URL` format correct for each service
- Auth server: `postgresql://...`
- API server: `postgresql+asyncpg://...`
- Check Neon connection limits not exceeded

---

## Deployment Complete!

Once all checkboxes are complete, your authentication system is production-ready:

- ✅ Secure authentication with better-auth
- ✅ Email/password registration and verification
- ✅ Password reset functionality
- ✅ Session-based authentication
- ✅ Protected FastAPI endpoints
- ✅ Production-grade security
- ✅ Monitoring and observability

**Next Steps**: Deploy frontend (Phase 005) or add optional features (Google OAuth - Phase 9)
