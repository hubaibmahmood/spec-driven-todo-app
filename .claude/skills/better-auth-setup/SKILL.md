---
name: better-auth-setup
description: Expert knowledge for implementing better-auth authentication in FastAPI applications with microservices architecture. Use when setting up authentication, troubleshooting auth issues, or need better-auth + FastAPI integration patterns. Includes templates, common issue solutions, and production-ready configurations.
---

# Better-Auth + FastAPI Setup Skill

This skill provides comprehensive knowledge for implementing better-auth authentication in FastAPI applications using a microservices architecture.

## Quick Start

### Architecture Overview

```
┌─────────────┐       ┌──────────────┐       ┌─────────────┐
│   Frontend  │──────▶│ Auth Server  │──────▶│  PostgreSQL │
│  (React)    │       │  (Node.js)   │       │   (Neon)    │
└─────────────┘       └──────────────┘       └─────────────┘
       │                                              ▲
       │              ┌──────────────┐               │
       └─────────────▶│  API Server  │───────────────┘
                      │  (FastAPI)   │
                      └──────────────┘
```

**Components:**
- **Auth Server**: Node.js + Express + better-auth (handles authentication)
- **API Server**: FastAPI (validates JWT tokens, manages business logic)
- **Database**: Shared PostgreSQL (Neon/Supabase/Railway)

## Core Patterns

### Pattern 1: Auth Server Configuration

**Location**: `auth-server/src/auth/auth.config.ts`

```typescript
import { betterAuth } from 'better-auth';
import { prismaAdapter } from 'better-auth/adapters/prisma';

export const auth = betterAuth({
  database: prismaAdapter(prisma, { provider: 'postgresql' }),

  emailAndPassword: {
    enabled: true,
    requireEmailVerification: false, // For testing
    minPasswordLength: 8,
  },

  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days
    cookieCache: { enabled: true, maxAge: 60 * 5 },
  },

  advanced: {
    defaultCookieAttributes: {
      sameSite: env.nodeEnv === 'production' ? 'none' : 'lax',
      secure: env.nodeEnv === 'production',
    },
  },

  trustedOrigins: env.corsOrigins,
});
```

### Pattern 2: FastAPI JWT Validation

**Location**: `backend/src/auth/dependencies.py`

**Database Lookup Method** (recommended for real-time revocation):
```python
async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> dict:
    token = credentials.credentials

    async with postgres_db.get_connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("""
                SELECT s.user_id, u.email, u.status, u.email_verified
                FROM user_sessions s
                JOIN users u ON s.user_id = u.id
                WHERE s.token = %s AND s.expires_at > NOW()
            """, (token,))

            row = await cur.fetchone()
            if not row:
                raise HTTPException(status_code=401, detail="Invalid session")

            return {
                "user_id": str(row["user_id"]),
                "email": row["email"],
            }
```

### Pattern 3: Route Ordering (Critical!)

**Location**: `auth-server/src/app.ts`

```typescript
// IMPORTANT: Custom routes MUST come BEFORE better-auth catch-all

// ✅ CORRECT ORDER
app.use('/api/auth', authRoutes);           // Custom routes FIRST
app.all('/api/auth/*', toNodeHandler(auth)); // better-auth AFTER

// ❌ WRONG ORDER (causes 404s)
app.all('/api/auth/*', toNodeHandler(auth)); // Catch-all captures everything
app.use('/api/auth', authRoutes);           // Never reached!
```

### Pattern 4: Database Schema Sync

**Critical**: Prisma and Alembic must use compatible types!

| Field | Prisma | Alembic | Issue |
|-------|--------|---------|-------|
| `ip_address` | `String @db.Text` | `sa.Text` | ✅ Compatible |
| `ip_address` | `String` | `postgresql.INET` | ❌ Type mismatch! |
| `password` | `String @map("password_hash")` | `sa.String("password_hash")` | ✅ Compatible |

**Solution**: Use `scripts/sync-schemas.sh` to detect and fix mismatches.

## Templates

All templates are in `templates/` directory with `{{PLACEHOLDER}}` syntax.

### Available Templates

**Auth Server** (15 files):
- `templates/auth-server/src/auth/auth.config.ts.template` - Core configuration
- `templates/auth-server/src/app.ts.template` - Express app with correct route ordering
- `templates/auth-server/src/auth/routes.ts.template` - Custom routes (/me, /verify-token)
- `templates/auth-server/prisma/schema.prisma.template` - Database schema
- `templates/auth-server/package.json.template` - With "type": "module"
- `templates/auth-server/tsconfig.json.template` - ESM configuration
- `templates/auth-server/vercel.json.template` - Simplified rewrites
- And 8 more...

**FastAPI Integration** (8 files):
- `templates/fastapi/src/auth/dependencies.py.template` - JWT validation
- `templates/fastapi/src/auth/models.py.template` - Pydantic models
- `templates/fastapi/src/database/migrations/001_create_auth_tables.py.template` - Alembic migration
- `templates/fastapi/requirements.txt.template` - Python dependencies
- And 4 more...

**Docker** (3 files):
- `templates/docker/docker-compose.yml.template`
- `templates/docker/docker-compose.dev.yml.template`
- `templates/docker/nginx.conf.template`

**Documentation** (4 files):
- `templates/docs/README.md.template`
- `templates/docs/API_DOCUMENTATION.md.template`
- `templates/docs/TROUBLESHOOTING.md.template`
- `templates/docs/SETUP.md.template`

### Template Usage

```typescript
// Read template
const template = await readFile('templates/auth-server/src/auth/auth.config.ts.template');

// Replace placeholders
const config = template
  .replace('{{DATABASE_PROVIDER}}', 'postgresql')
  .replace('{{EMAIL_VERIFICATION_REQUIRED}}', 'false')
  .replace('{{SESSION_EXPIRATION}}', '604800') // 7 days in seconds
  .replace('{{CORS_ORIGINS}}', JSON.stringify(['http://localhost:3000']));

// Write to destination
await writeFile('auth-server/src/auth/auth.config.ts', config);
```

## Common Issues & Solutions

See `diagnostics/` directory for detailed guides on each issue.

### Issue 1: ESM/CommonJS Error

**Error**: `ERR_REQUIRE_ESM when importing better-auth/node`

**Cause**: Missing ESM configuration

**Solution**: Add to `package.json`:
```json
{
  "type": "module"
}
```

**Details**: See `diagnostics/ESM_COMPATIBILITY.md`

---

### Issue 2: 404 on Auth Endpoints

**Error**: `POST /api/auth/signup → 404 Not Found`

**Cause**: Custom routes placed AFTER better-auth catch-all

**Solution**: Reorder routes (custom first, then better-auth)

**Details**: See `diagnostics/ROUTE_ORDERING.md`

---

### Issue 3: Database Type Mismatch

**Error**: `column "ip_address" is of type inet but expression is of type text`

**Cause**: Prisma uses `String` but Alembic uses `INET`

**Solution**: Change Alembic migration to `sa.Text`:
```python
sa.Column('ip_address', sa.Text, nullable=True)
```

**Details**: See `diagnostics/SCHEMA_SYNC.md`

---

### Issue 4: Cross-Site Cookie Issues

**Error**: Cookies not sent from GitHub Pages to Vercel auth server

**Cause**: Missing `SameSite=none` for cross-domain requests

**Solution**: Update auth.config.ts:
```typescript
sameSite: env.nodeEnv === 'production' ? 'none' : 'lax'
```

**Details**: See `diagnostics/COOKIE_CONFIGURATION.md`

---

### Issue 5: Vercel 404 Errors

**Error**: Routes return 404 on Vercel deployment

**Cause**: Complex rewrite rules

**Solution**: Simplify `vercel.json`:
```json
{
  "rewrites": [{ "source": "/(.*)", "destination": "/api/index.js" }]
}
```

**Details**: See `diagnostics/VERCEL_DEPLOYMENT.md`

---

### Issue 6: Email Verification Not Working

**Error**: Email verification required but no emails sent

**Cause**: Email service not configured

**Solution**: Either configure email service or disable verification:
```typescript
requireEmailVerification: false
```

**Details**: See `diagnostics/EMAIL_VERIFICATION.md`

## Configuration Options

### Database Providers

- **Neon Serverless** (Recommended)
  - Connection pooling built-in
  - Auto-scaling
  - Generous free tier

- **Supabase**
  - Built-in auth UI
  - Real-time subscriptions
  - Storage included

- **Railway**
  - Simple deployment
  - Auto-scaling
  - One-click PostgreSQL

- **Local PostgreSQL**
  - Development only
  - Use Docker Compose

### Auth Methods

- **Email/Password** (Standard)
  - Best for most applications
  - Optional email verification

- **Google OAuth**
  - Quick signup
  - Requires Google Cloud Console setup

- **GitHub OAuth**
  - Developer-friendly
  - Requires GitHub OAuth App

- **Magic Links**
  - Passwordless
  - Email service required

### Session Validation

- **Database Lookup** (Recommended)
  - ✅ Real-time revocation
  - ✅ Audit trail
  - ❌ ~50ms added latency
  - ❌ Database load

- **JWT Validation**
  - ✅ Lower latency
  - ✅ Stateless
  - ❌ No real-time revocation
  - ❌ Tokens valid until expiry

### Deployment Targets

- **Vercel (Auth Server)**
  - Serverless
  - Automatic scaling
  - Edge network

- **Render (API Server)**
  - Python-friendly
  - Auto-deploy from git
  - Free tier available

- **Railway (Both)**
  - Full-stack platform
  - Simple configuration
  - One dashboard

- **Docker (Both)**
  - Self-hosted
  - Full control
  - Docker Compose included

## Best Practices

### 1. Security

- ✅ Use environment variables for secrets
- ✅ Enable HTTPS in production (`secure: true`)
- ✅ Set appropriate CORS origins
- ✅ Enable rate limiting (default: 10 requests/minute)
- ✅ Use strong password requirements (min 8 characters)

### 2. Session Management

- ✅ 7-day expiration (balance security/convenience)
- ✅ Daily refresh (`updateAge: 24 hours`)
- ✅ 5-minute cookie cache (reduce database load)
- ✅ Database session validation (real-time revocation)

### 3. Database

- ✅ Use connection pooling (Neon, Supabase)
- ✅ Sync Prisma and Alembic schemas
- ✅ Add indexes on `email`, `token`, `user_id`
- ✅ Use transactions for user creation

### 4. Error Handling

- ✅ Return appropriate status codes (401, 403, 400)
- ✅ Don't leak sensitive information in errors
- ✅ Log errors with correlation IDs
- ✅ Provide clear error messages to users

### 5. Testing

- ✅ Test signup/signin flows
- ✅ Test session expiration
- ✅ Test CORS from actual frontend URLs
- ✅ Test OAuth flows in production

## Advanced Topics

For detailed information, see:

- **Authentication Flow**: `patterns/AUTHENTICATION_FLOW.md`
- **Session Management**: `patterns/SESSION_MANAGEMENT.md`
- **Database Schema Sync**: `patterns/DATABASE_SYNC.md`
- **OAuth Integration**: `patterns/OAUTH_INTEGRATION.md`
- **Deployment Strategies**: `patterns/DEPLOYMENT.md`

## Scripts

Helper scripts in `scripts/` directory:

- **`sync-schemas.sh`**: Synchronize Prisma and Alembic schemas
- **`setup-dev.sh`**: Initial development environment setup
- **`health-check.sh`**: Validate deployment health

## Examples

Complete working examples in `examples/` directory:

- **`neon-vercel-example/`**: Neon + Vercel + Render deployment
- **`supabase-railway-example/`**: Supabase + Railway deployment
- **`local-docker-example/`**: Local development with Docker Compose

## Usage with Agents

This skill is designed to be used with the `better-auth-fastapi-agent`:

```
Agent: I need to implement better-auth authentication
Skill: [Provides templates, patterns, and solutions]
Agent: [Uses skill knowledge to generate code and solve issues]
```

The agent handles:
- Interactive configuration
- Code generation from templates
- Running diagnostics
- Creating PHRs and ADRs
- Workflow orchestration

The skill provides:
- Reusable knowledge base
- Production-ready templates
- Common issue solutions
- Best practices and patterns

## Portability

This skill is **project-independent** and can be used in any FastAPI project:

### Copy to New Project
```bash
cp -r .claude/skills/better-auth-setup /path/to/new-project/.claude/skills/
```

### Install Globally (System-Wide)
```bash
cp -r .claude/skills/better-auth-setup ~/.claude/skills/
```

### Share via Git
```bash
git clone https://github.com/yourusername/better-auth-setup-skill \
  .claude/skills/better-auth-setup
```

Once installed, any agent (or Claude directly) can reference this skill's knowledge!

## License

This skill is based on the working implementation of better-auth + FastAPI authentication in this project and follows MIT license principles for maximum reusability.
