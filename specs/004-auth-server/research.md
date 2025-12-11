# Research: Better Auth Server for FastAPI Integration

**Feature**: 004-auth-server
**Phase**: 0 (Outline & Research)
**Date**: 2025-12-10
**Status**: Complete

## Overview

This document consolidates research findings for implementing a better-auth authentication server that integrates with FastAPI using a microservices architecture.

## Research Questions Resolved

### 1. How does better-auth integrate with FastAPI?

**Decision**: Separate microservices architecture

**Architecture Pattern**:
```
┌─────────────┐      ┌──────────────────┐      ┌─────────────────┐
│  Frontend   │─────▶│   Auth Server    │      │  API Server     │
│  (Browser)  │      │   (Node.js/      │      │  (FastAPI/      │
│             │      │   better-auth)   │      │   Python)       │
└─────────────┘      └──────────────────┘      └─────────────────┘
                              │                          │
                              │                          │
                              └──────────┬───────────────┘
                                         │
                                         ▼
                              ┌─────────────────────┐
                              │   PostgreSQL        │
                              │   (Neon Serverless) │
                              └─────────────────────┘
```

**Request Flow**:
1. User signs up/in via frontend → Auth Server `/api/auth/signup` or `/api/auth/signin`
2. Auth Server validates credentials, creates session in database
3. Auth Server returns httpOnly cookie (`better-auth.session_token`)
4. Frontend makes API requests to FastAPI with `Authorization: Bearer <token>` header
5. FastAPI extracts token, queries database to validate session and get user ID
6. FastAPI allows/denies request based on validation

**Rationale**:
- better-auth is Node.js-first with extensive TypeScript support
- FastAPI excels at Python-based business logic and AI/ML integration
- Separation of concerns: auth logic isolated from application logic
- Independent scaling: auth server can scale separately based on authentication load

**Alternatives Considered**:
- **Monolithic FastAPI with Python auth libs** (FastAPI-Users, Authlib): Less mature ecosystem, missing features like built-in OAuth providers, session management complexity
- **Auth0/Clerk third-party**: Higher cost, vendor lock-in, less customization

**References**:
- better-auth documentation: https://www.better-auth.com/docs
- better-auth GitHub: https://github.com/better-auth/better-auth (10k+ stars)
- FastAPI Security: https://fastapi.tiangolo.com/tutorial/security/

---

### 2. What session validation strategy should be used?

**Decision**: Database lookup for session validation

**Implementation**:
```python
# FastAPI dependency (backend/src/auth/dependencies.py)
async def get_current_user(
    token: str = Depends(get_bearer_token),
    db: AsyncSession = Depends(get_db)
):
    # Query user_sessions table
    result = await db.execute(
        select(Session, User)
        .join(User, Session.user_id == User.id)
        .where(Session.token == token)
        .where(Session.expires_at > datetime.utcnow())
    )
    session, user = result.one_or_none() or (None, None)

    if not session or not user:
        raise HTTPException(401, "Invalid or expired session")

    return user
```

**Rationale**:
- **Real-time session revocation**: Can invalidate sessions immediately (logout, security breach)
- **Audit trail**: Database tracks all active sessions with device/location info
- **Multi-session management**: Users can view and revoke individual sessions
- **Performance acceptable**: ~50ms latency overhead (Neon serverless has connection pooling)

**Alternatives Considered**:
- **JWT validation without database**: Lower latency (~5ms), but cannot revoke sessions in real-time. User must wait for token expiration.
- **Hybrid approach** (JWT with revocation list): Adds complexity; cache invalidation challenges

**Tradeoffs**:
- ✅ Security: Real-time revocation
- ✅ Transparency: Session audit trail
- ❌ Latency: +50ms per request
- ❌ Database load: One query per authenticated request (mitigated by connection pooling)

**References**:
- Session management best practices: https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html
- Better-auth session docs: https://www.better-auth.com/docs/concepts/sessions

---

### 3. How to coordinate database schemas between Prisma (Node.js) and Alembic (Python)?

**Decision**: Prisma-first schema definition with manual Alembic synchronization

**Process**:
1. Define schema in Prisma (auth-server/prisma/schema.prisma)
2. Run `npx prisma db push` to apply to database
3. Manually create matching Alembic migration in FastAPI
4. Run diagnostic script to validate schema sync

**Critical Type Mappings** (Prisma → PostgreSQL → SQLAlchemy):
```typescript
// Prisma schema.prisma
model User {
  id            String    @id @default(cuid())
  email         String    @unique
  emailVerified Boolean   @default(false)
  password      String?
  name          String?
  image         String?
  createdAt     DateTime  @default(now())
  updatedAt     DateTime  @updatedAt
}

model Session {
  id         String   @id @default(cuid())
  userId     String
  token      String   @unique
  expiresAt  DateTime
  ipAddress  String?     // ⚠️ Use String, NOT ip_address type
  userAgent  String?
  createdAt  DateTime @default(now())
  updatedAt  DateTime @updatedAt

  user User @relation(fields: [userId], references: [id], onDelete: Cascade)
}
```

```python
# Alembic migration (backend/src/database/migrations/versions/001_auth_tables.py)
def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('email', sa.String(), unique=True, nullable=False),
        sa.Column('email_verified', sa.Boolean(), default=False),
        sa.Column('password', sa.String(), nullable=True),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('image', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), onupdate=datetime.utcnow),
    )

    op.create_table(
        'user_sessions',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('user_id', sa.String(), sa.ForeignKey('users.id', ondelete='CASCADE')),
        sa.Column('token', sa.String(), unique=True, nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('ip_address', sa.Text(), nullable=True),  # ⚠️ Use sa.Text, NOT INET
        sa.Column('user_agent', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), onupdate=datetime.utcnow),
    )
```

**Common Schema Mismatch Issues**:

| Issue | Prisma | Alembic | Solution |
|-------|--------|---------|----------|
| IP address type | `String?` → `text` | `INET` (default) | Use `sa.Text()` or `sa.String()` |
| Boolean defaults | `@default(false)` | `server_default=False` (wrong) | Use `default=False` (Python-side) |
| Timestamps | `@default(now())` | `server_default=func.now()` | Use `default=datetime.utcnow` |
| Field naming | `emailVerified` | `email_verified` | Prisma uses `@map("email_verified")` for snake_case |

**Validation Process**:
```bash
# Compare schemas
diff <(npx prisma db pull && cat prisma/schema.prisma) \
     <(alembic upgrade head && alembic current)

# Or use diagnostic script (from better-auth-fastapi-agent)
bash .claude/skills/better-auth-setup/scripts/sync-schemas.sh --auto-fix
```

**Rationale**:
- Prisma provides excellent developer experience for auth server
- SQLAlchemy/Alembic is standard for Python FastAPI apps
- Manual sync ensures both services use identical schema
- Diagnostic automation prevents drift

**Alternatives Considered**:
- **Single ORM (Prisma or SQLAlchemy)**: Requires both services to use same language
- **Schema-first approach** (SQL DDL): Loses ORM type safety and migrations

**References**:
- Prisma migrations: https://www.prisma.io/docs/concepts/components/prisma-migrate
- Alembic tutorial: https://alembic.sqlalchemy.org/en/latest/tutorial.html
- Better-auth Prisma adapter: https://www.better-auth.com/docs/integrations/prisma

---

### 4. What are best practices for ESM/CommonJS compatibility in better-auth?

**Decision**: Use pure ESM module system

**Configuration**:
```json
// auth-server/package.json
{
  "type": "module",  // ⚠️ CRITICAL: Enables ESM
  "engines": {
    "node": ">=20.0.0"
  }
}

// auth-server/tsconfig.json
{
  "compilerOptions": {
    "module": "ESNext",           // ⚠️ Use ESNext for native ESM
    "moduleResolution": "node",
    "target": "ES2022",
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true
  }
}
```

**Import Syntax**:
```typescript
// ✅ Correct ESM imports
import express from 'express';
import { betterAuth } from 'better-auth';
import { PrismaClient } from '@prisma/client';

// ❌ Avoid CommonJS
const express = require('express');  // Error: ERR_REQUIRE_ESM
```

**Rationale**:
- better-auth v1.x is ESM-only (no CommonJS support)
- Node.js 20+ has stable ESM support
- Prevents `ERR_REQUIRE_ESM` errors

**Common Pitfalls**:
| Error | Cause | Solution |
|-------|-------|----------|
| `ERR_REQUIRE_ESM` | Missing `"type": "module"` | Add to package.json |
| `Cannot use import outside module` | No `"type": "module"` | Add to package.json |
| `Directory import` | Import from directory not file | Use explicit file paths with `.js` extension |
| `Unknown file extension .ts` | Running TS files directly | Use `tsx` or compile first |

**References**:
- Node.js ESM documentation: https://nodejs.org/api/esm.html
- Better-auth setup guide: https://www.better-auth.com/docs/installation

---

### 5. How to handle CORS for cross-origin authentication?

**Decision**: Configure CORS with `SameSite=none` for production, `lax` for development

**Auth Server CORS** (Node.js/Express):
```typescript
// auth-server/src/app.ts
import cors from 'cors';

app.use(cors({
  origin: process.env.CORS_ORIGINS?.split(',') || ['http://localhost:3000'],
  credentials: true,  // ⚠️ CRITICAL: Allow cookies
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization'],
}));

// better-auth config
export const auth = betterAuth({
  // ...
  session: {
    cookieCache: {
      enabled: true,
      maxAge: 5 * 60, // 5 minutes
    },
  },
  advanced: {
    defaultCookieAttributes: {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: process.env.NODE_ENV === 'production' ? 'none' : 'lax',  // ⚠️ CRITICAL
      path: '/',
      domain: process.env.COOKIE_DOMAIN,  // e.g., '.yourdomain.com' for subdomains
    },
  },
});
```

**FastAPI CORS** (Python):
```python
# backend/src/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,  # ⚠️ CRITICAL: Allow cookies
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Frontend Configuration**:
```typescript
// Frontend API calls
fetch('https://api.yourdomain.com/protected', {
  credentials: 'include',  // ⚠️ CRITICAL: Send cookies
  headers: {
    'Authorization': `Bearer ${sessionToken}`,
    'Content-Type': 'application/json',
  },
});
```

**SameSite Policy**:
| Environment | SameSite | Secure | Reason |
|-------------|----------|--------|--------|
| Development (`localhost`) | `lax` | `false` | Same-site requests, HTTP allowed |
| Production (cross-domain) | `none` | `true` | Cross-site requests require Secure flag |

**Rationale**:
- `SameSite=none` required for cross-origin cookie sharing (auth server ≠ frontend domain)
- `Secure` flag mandatory when `SameSite=none` (requires HTTPS)
- `credentials: true` allows cookies to be sent cross-origin

**Common Issues**:
| Error | Cause | Solution |
|-------|-------|----------|
| Cookie not set | `credentials: 'include'` missing | Add to fetch options |
| `SameSite=None` requires Secure | Production without HTTPS | Enable HTTPS or use `lax` |
| CORS policy block | Origin not in `allow_origins` | Add frontend URL to CORS_ORIGINS |

**References**:
- MDN SameSite cookies: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie/SameSite
- CORS guide: https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS

---

### 6. What email service should be used for verification and password reset?

**Decision**: Resend for email delivery

**Configuration**:
```typescript
// auth-server/src/auth/auth.config.ts
import { Resend } from 'resend';

const resend = new Resend(process.env.RESEND_API_KEY);

export const auth = betterAuth({
  // ...
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: true,
    sendVerificationEmail: async ({ user, token, url }) => {
      await resend.emails.send({
        from: 'noreply@yourdomain.com',
        to: user.email,
        subject: 'Verify your email',
        html: `
          <p>Welcome! Please verify your email by clicking the link below:</p>
          <a href="${url}">Verify Email</a>
          <p>This link expires in 15 minutes.</p>
        `,
      });
    },
  },
  account: {
    accountLinking: {
      enabled: true,
      trustedProviders: ['google'],
    },
  },
  emailVerification: {
    sendOnSignUp: true,
    expiresIn: 15 * 60, // 15 minutes
    sendVerificationEmail: async ({ user, token, url }) => {
      // Same as above
    },
  },
});
```

**Environment Variables**:
```bash
# .env
RESEND_API_KEY=re_xxxxx
EMAIL_FROM=noreply@yourdomain.com
FRONTEND_URL=https://yourdomain.com
```

**Email Templates**:
1. **Email Verification**: 15-minute expiration, sent on signup
2. **Password Reset**: 1-hour expiration, sent on forgot password
3. **Welcome Email**: Optional, sent after email verification

**Rationale**:
- Resend is developer-friendly with simple API
- Generous free tier (3,000 emails/month)
- Better deliverability than SendGrid/SMTP
- Built-in templates and analytics

**Alternatives Considered**:
- **SendGrid**: More complex setup, higher cost
- **AWS SES**: Requires AWS account, more configuration
- **Nodemailer with SMTP**: Lower deliverability, spam issues

**Testing Strategy**:
```bash
# Development: Use email preview links (logged to console)
# Production: Test with real email address before going live
```

**References**:
- Resend documentation: https://resend.com/docs
- Better-auth email verification: https://www.better-auth.com/docs/plugins/email-verification

---

### 7. How to handle Vercel deployment for serverless functions?

**Decision**: Use simplified single-rewrite Vercel configuration

**Configuration**:
```json
// auth-server/vercel.json
{
  "version": 2,
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/api/index.js"
    }
  ],
  "env": {
    "DATABASE_URL": "@database-url",
    "JWT_SECRET": "@jwt-secret",
    "RESEND_API_KEY": "@resend-api-key"
  }
}

// auth-server/api/index.ts (Vercel entry point)
import app from '../src/app.js';

export default app;  // Export Express app as serverless function
```

**Package.json Scripts**:
```json
{
  "scripts": {
    "dev": "tsx watch src/index.ts",
    "build": "tsc",
    "vercel-build": "prisma generate && tsc",
    "start": "node dist/index.js"
  }
}
```

**Deployment Process**:
```bash
# 1. Install Vercel CLI
npm install -g vercel

# 2. Link project
vercel link

# 3. Set environment variables
vercel env add DATABASE_URL
vercel env add JWT_SECRET
vercel env add RESEND_API_KEY

# 4. Deploy
vercel --prod
```

**Rationale**:
- Single rewrite simplifies routing (all requests → /api/index.js)
- Avoids complex rewrites that cause 404 errors
- Supports custom routes before better-auth catch-all

**Common Pitfalls**:
| Issue | Cause | Solution |
|-------|-------|----------|
| 404 on auth endpoints | Multiple complex rewrites | Use single catch-all rewrite |
| Prisma not found | Missing `prisma generate` | Add to `vercel-build` script |
| Environment variables not loaded | Not set in Vercel | Use `vercel env add` |
| Cold start timeout | Function too large | Optimize bundle size, use edge functions |

**References**:
- Vercel Node.js deployment: https://vercel.com/docs/functions/runtimes/node-js
- Express on Vercel: https://vercel.com/guides/using-express-with-vercel

---

## Summary of Key Decisions

| Decision Area | Choice | Rationale |
|---------------|--------|-----------|
| **Architecture** | Microservices (Node.js auth + FastAPI backend) | Leverage language-specific strengths; better-auth is Node.js-first |
| **Session Strategy** | Database lookup | Real-time revocation, audit trail, multi-session management |
| **Schema Sync** | Prisma-first with manual Alembic | Prisma DX for auth; SQLAlchemy for FastAPI; manual sync prevents drift |
| **Module System** | Pure ESM | better-auth v1.x requires ESM; Node 20+ has stable support |
| **CORS Policy** | `SameSite=none` (prod), `lax` (dev) | Cross-origin cookie sharing for separate auth/API domains |
| **Email Service** | Resend | Developer-friendly API, good deliverability, generous free tier |
| **Auth Deployment** | Vercel Serverless | Simplified single-rewrite config; automatic scaling |
| **API Deployment** | Render | Python-friendly; auto-deploy from git; good for FastAPI |

---

## Next Steps (Phase 1)

With all research questions resolved, proceed to Phase 1:

1. **data-model.md**: Define User, Session, AuthToken entities with validation rules
2. **contracts/**: Generate OpenAPI specs for auth endpoints
3. **quickstart.md**: Create step-by-step setup instructions
4. **Update agent context**: Add Node.js, better-auth, Prisma to technology stack

---

**Phase 0 Complete** ✅
**Ready for Phase 1**: Data modeling and contract definition
