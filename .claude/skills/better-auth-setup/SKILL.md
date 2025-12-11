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
│  (React)    │       │  (Node.js)   │       │ (Neon/Other)│
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
- **Database**: Shared PostgreSQL (Neon/Supabase/Railway/Local)

## Core Patterns

### Pattern 1: Auth Server Configuration

**Template**: `templates/auth-server/src/auth/auth.config.ts.template`

**Purpose**: Configure better-auth with database adapter, session settings, and authentication methods.

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

**Key Placeholders**:
- `{{DATABASE_PROVIDER}}` - postgresql, mysql, sqlite
- `{{EMAIL_VERIFICATION_REQUIRED}}` - true or false
- `{{SESSION_EXPIRATION}}` - In seconds (e.g., 604800 = 7 days)
- `{{CORS_ORIGINS}}` - Array of allowed origins

### Pattern 2: FastAPI JWT Validation

**Template**: `templates/fastapi/{{BACKEND_SRC_DIR}}/auth/dependencies.py.template`

**Purpose**: Validate session tokens from auth server in FastAPI endpoints.

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

**Key Placeholders**:
- `{{VALIDATION_METHOD}}` - "database" or "jwt"
- `{{AUTH_SERVER_URL}}` - URL of auth server
- `{{BACKEND_SRC_DIR}}` - e.g., "src", "app", "api"
- `{{DATABASE_IMPORT_PATH}}` - Adjusted to project structure

**Conditional Blocks**:
- `{{#VALIDATION_METHOD_DATABASE}}...{{/VALIDATION_METHOD_DATABASE}}`
- `{{#VALIDATION_METHOD_JWT}}...{{/VALIDATION_METHOD_JWT}}`

### Pattern 3: Route Ordering (Critical!)

**Template**: `templates/auth-server/src/app.ts.template`

**Purpose**: Ensure custom routes are registered BEFORE better-auth catch-all handler.

```typescript
// IMPORTANT: Custom routes MUST come BEFORE better-auth catch-all

// ✅ CORRECT ORDER
app.use('/api/auth', authRoutes);           // Custom routes FIRST
app.all('/api/auth/*', toNodeHandler(auth)); // better-auth AFTER

// ❌ WRONG ORDER (causes 404s)
app.all('/api/auth/*', toNodeHandler(auth)); // Catch-all captures everything
app.use('/api/auth', authRoutes);           // Never reached!
```

**Why This Matters**: Express processes middleware in order. If better-auth's catch-all (`/api/auth/*`) comes first, it captures ALL routes and custom endpoints never execute.

### Pattern 4: Database Schema Sync

**Critical**: Prisma and Alembic must use compatible types!

| Field | Prisma | Alembic | Issue |
|-------|--------|---------|-------|
| `ip_address` | `String @db.Text` | `sa.Text` | ✅ Compatible |
| `ip_address` | `String` | `postgresql.INET` | ❌ Type mismatch! |
| `password` | `String @map("password_hash")` | `sa.String("password_hash")` | ✅ Compatible |

**Solution**: Use `scripts/sync-schemas.sh` to detect and fix mismatches.

## Templates

All templates use `{{PLACEHOLDER}}` syntax and are located in `templates/` directory.

### Template Structure

Templates are organized by component:

```
templates/
├── auth-server/          # Node.js auth server files
│   ├── src/
│   │   ├── auth/         # Authentication config
│   │   ├── config/       # Environment config
│   │   └── database/     # Database client
│   ├── prisma/           # Prisma schema
│   ├── package.json.template
│   ├── tsconfig.json.template
│   └── vercel.json.template
├── fastapi/              # FastAPI integration files
│   ├── {{BACKEND_SRC_DIR}}/
│   │   ├── auth/         # Auth dependencies
│   │   └── database/     # Migration templates
│   └── requirements.txt.template
├── docker/               # Docker compose files
└── docs/                 # Documentation templates
```

### Template Categories

**Auth Server** (~15 files):
- Core configuration (auth.config.ts, env.ts)
- Express app setup (app.ts, routes.ts)
- Database (prisma schema, client)
- Deployment (vercel.json, package.json)
- Environment (.env.example)

**FastAPI Integration** (~8 files):
- Auth middleware (dependencies.py)
- Models (Pydantic schemas)
- Database migrations (Alembic templates)
- Requirements (python dependencies)

**Docker** (3 files):
- docker-compose.yml (production)
- docker-compose.dev.yml (development)
- nginx.conf (reverse proxy)

**Documentation** (4 files):
- README.md (overview and quick start)
- API_DOCUMENTATION.md (endpoint reference)
- TROUBLESHOOTING.md (common issues)
- SETUP.md (development guide)

### Key Placeholders

**Path Placeholders** (adapt to project structure):
- `{{AUTH_SERVER_DIR}}` - Auth server directory (e.g., "auth-server", "auth", "services/auth")
- `{{BACKEND_DIR}}` - Backend directory (e.g., "backend", "api", "app")
- `{{BACKEND_SRC_DIR}}` - Backend source dir (e.g., "src", "app", "api")
- `{{PRISMA_SCHEMA_PATH}}` - Path to Prisma schema
- `{{ALEMBIC_MIGRATIONS_PATH}}` - Path to Alembic migrations

**Configuration Placeholders**:
- `{{DATABASE_PROVIDER}}` - postgresql, mysql, sqlite
- `{{EMAIL_VERIFICATION_REQUIRED}}` - true or false
- `{{SESSION_EXPIRATION}}` - In seconds
- `{{SESSION_EXPIRATION_DAYS}}` - In days (for documentation)
- `{{CORS_ORIGINS}}` - JSON array of allowed origins
- `{{DEPLOYMENT_TARGET}}` - vercel, railway, docker

**Feature Toggles** (conditional blocks):
- `{{#OAUTH_ENABLED}}...{{/OAUTH_ENABLED}}`
- `{{#GOOGLE_OAUTH}}...{{/GOOGLE_OAUTH}}`
- `{{#GITHUB_OAUTH}}...{{/GITHUB_OAUTH}}`
- `{{#MAGIC_LINK_ENABLED}}...{{/MAGIC_LINK_ENABLED}}`
- `{{#TWO_FACTOR_ENABLED}}...{{/TWO_FACTOR_ENABLED}}`
- `{{#VALIDATION_METHOD_DATABASE}}...{{/VALIDATION_METHOD_DATABASE}}`
- `{{#VALIDATION_METHOD_JWT}}...{{/VALIDATION_METHOD_JWT}}`

### Template Usage Pattern

**Step 1: Discover Project Structure**
```bash
# Orchestrator discovers these paths dynamically
BACKEND_DIR=$(find . -maxdepth 1 -type d -name "backend" -o -name "api" -o -name "app")
AUTH_SERVER_DIR="auth-server"  # Or ask user
```

**Step 2: Read Template**
```typescript
const template = await read('templates/fastapi/{{BACKEND_SRC_DIR}}/auth/dependencies.py.template');
```

**Step 3: Replace Placeholders**
```typescript
const generated = template
  .replace(/\{\{DATABASE_PROVIDER\}\}/g, 'postgresql')
  .replace(/\{\{BACKEND_SRC_DIR\}\}/g, 'src')
  .replace(/\{\{VALIDATION_METHOD\}\}/g, 'database')
  // Handle conditional blocks
  .replace(/\{\{#VALIDATION_METHOD_DATABASE\}\}[\s\S]*?\{\{\/VALIDATION_METHOD_DATABASE\}\}/g, (match) => {
    // Include content if validation method is database
    return match.replace(/\{\{#VALIDATION_METHOD_DATABASE\}\}|\{\{\/VALIDATION_METHOD_DATABASE\}\}/g, '');
  });
```

**Step 4: Write to Destination**
```typescript
await write(`${BACKEND_DIR}/src/auth/dependencies.py`, generated);
```

## Common Issues & Solutions

See `diagnostics/COMMON_ISSUES.md` for detailed guides on each issue.

### Issue 1: ESM/CommonJS Error

**Error**: `ERR_REQUIRE_ESM when importing better-auth/node`

**Cause**: Missing ESM configuration in Node.js project.

**Solution**: Add `"type": "module"` to package.json in auth server directory.

**Details**: See `diagnostics/COMMON_ISSUES.md#issue-1`

---

### Issue 2: 404 on Auth Endpoints

**Error**: `POST /api/auth/signup → 404 Not Found`

**Cause**: Route ordering - better-auth catch-all registered before custom routes.

**Solution**: Ensure custom routes registered BEFORE `app.all('/api/auth/*', ...)`.

**Details**: See `diagnostics/COMMON_ISSUES.md#issue-2`

---

### Issue 3: Database Type Mismatch

**Error**: `column "ip_address" is of type inet but expression is of type text`

**Cause**: Prisma uses `String/Text` but Alembic uses `INET` type.

**Solution**: Run `scripts/sync-schemas.sh --auto-fix` to change INET to Text.

**Details**: See `diagnostics/COMMON_ISSUES.md#issue-3`

---

### Issue 4: Cross-Site Cookies Not Working

**Error**: Cookies not sent in cross-domain requests.

**Cause**: Incorrect `sameSite` or `secure` cookie attributes.

**Solution**: Set `sameSite: 'none'` and `secure: true` in production.

**Details**: See `diagnostics/COMMON_ISSUES.md#issue-4`

---

### Issue 5: Vercel 404 Errors

**Error**: 404 on all auth endpoints when deployed to Vercel.

**Cause**: Complex rewrite rules or incorrect Vercel configuration.

**Solution**: Use simplified single catch-all rewrite in vercel.json.

**Details**: See `diagnostics/COMMON_ISSUES.md#issue-5`

---

### Issue 6: Email Verification Not Working

**Error**: Emails not sent during signup.

**Cause**: Missing email service configuration (RESEND_API_KEY, EMAIL_FROM).

**Solution**: Configure email service environment variables.

**Details**: See `diagnostics/COMMON_ISSUES.md#issue-6`

## Scripts

### sync-schemas.sh

**Purpose**: Detect and fix type mismatches between Prisma and Alembic schemas.

**Usage**:
```bash
# Detect only
bash scripts/sync-schemas.sh

# Detect and auto-fix
bash scripts/sync-schemas.sh --auto-fix
```

**Environment Variables**:
- `PRISMA_SCHEMA` - Path to Prisma schema (default: auto-discovered)
- `ALEMBIC_MIGRATIONS` - Path to Alembic migrations dir (default: auto-discovered)

**What It Checks**:
1. `ip_address` type compatibility (INET vs Text)
2. Integer size mismatches (Int vs BigInteger)
3. Nullable field consistency

## Best Practices

### 1. Always Use Placeholders
- ❌ DON'T: Hardcode paths like `backend/src/auth/dependencies.py`
- ✅ DO: Use `{{BACKEND_DIR}}/{{BACKEND_SRC_DIR}}/auth/dependencies.py`

### 2. Discover Project Structure
- ❌ DON'T: Assume directory names
- ✅ DO: Discover with Glob/Bash and ask user if ambiguous

### 3. Adapt Imports
- ❌ DON'T: Hardcode `from src.database.postgres import ...`
- ✅ DO: Use `from {{BACKEND_SRC_DIR}}.database.{{DATABASE_MODULE}} import ...`

### 4. Use Conditional Blocks
- ❌ DON'T: Generate unused code
- ✅ DO: Use `{{#FEATURE_ENABLED}}...{{/FEATURE_ENABLED}}`

### 5. Document Assumptions
- ❌ DON'T: Leave configuration choices unexplained
- ✅ DO: Add comments explaining tradeoffs and decisions

## Integration with Orchestrator

This skill is designed to work with the `better-auth-fastapi-orchestrator` agent:

1. **Orchestrator discovers** project structure
2. **Orchestrator gathers** user configuration
3. **Skill provides** templates and patterns
4. **Orchestrator adapts** templates to project
5. **Skill provides** diagnostics and fixes

**Division of Responsibilities**:
- **Orchestrator**: Workflow, discovery, adaptation, user interaction
- **Skill**: Domain knowledge, templates, patterns, diagnostics

## Summary

This skill provides:
- ✅ **Reusable templates** with placeholder syntax
- ✅ **Adaptable patterns** that work with any project structure
- ✅ **Diagnostic tools** for common integration issues
- ✅ **Best practices** for better-auth + FastAPI integration
- ✅ **Production-ready** configurations and security settings

Use this skill through the orchestrator agent for systematic, reliable, and well-documented authentication implementation.
