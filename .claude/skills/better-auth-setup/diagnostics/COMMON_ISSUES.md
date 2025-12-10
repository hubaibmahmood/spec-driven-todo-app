# Common Issues & Solutions

This document covers all 6 common issues encountered when implementing better-auth + FastAPI authentication.

## Overview

| Issue | Symptom | Auto-Fix Available |
|-------|---------|-------------------|
| [1. ESM/CommonJS Compatibility](#issue-1-esmcommonjs-compatibility) | `ERR_REQUIRE_ESM` | ✅ Yes |
| [2. Route Ordering](#issue-2-route-ordering) | 404 on auth endpoints | ✅ Yes |
| [3. Database Schema Sync](#issue-3-database-schema-sync) | `column "ip_address" is of type inet` | ✅ Yes |
| [4. Cross-Site Cookies](#issue-4-cross-site-cookie-configuration) | Cookies not sent cross-domain | ✅ Yes |
| [5. Vercel Deployment](#issue-5-vercel-deployment-config) | 404 on Vercel | ✅ Yes |
| [6. Email Verification](#issue-6-email-verification-flow) | Emails not sent | ⚠️ Manual |

---

## Issue 1: ESM/CommonJS Compatibility

### Symptom
```
Error [ERR_REQUIRE_ESM]: require() of ES Module not supported
Cannot require better-auth/node
```

### Root Cause
better-auth is an ES Module but your Node.js project is configured for CommonJS.

### Detection
Check `auth-server/package.json` for missing `"type": "module"`:
```bash
grep '"type"' auth-server/package.json
```

### Solution

**Step 1**: Add to `package.json`:
```json
{
  "type": "module",
  "name": "auth-server",
  ...
}
```

**Step 2**: Verify `tsconfig.json`:
```json
{
  "compilerOptions": {
    "module": "ESNext",
    "moduleResolution": "node"
  }
}
```

**Step 3**: Add `.js` extensions to all imports:
```typescript
// ✅ Correct
import { auth } from './auth/auth.config.js';
import { env } from './config/env.js';

// ❌ Wrong
import { auth } from './auth/auth.config';
import { env } from './config/env';
```

### Auto-Fix
```bash
# Add "type": "module" to package.json
node -e "const pkg = require('./auth-server/package.json'); pkg.type = 'module'; require('fs').writeFileSync('./auth-server/package.json', JSON.stringify(pkg, null, 2));"
```

### Verification
```bash
cd auth-server
npm run dev
# Should start without ERR_REQUIRE_ESM
```

---

## Issue 2: Route Ordering

### Symptom
```
POST /api/auth/signup → 404 Not Found
POST /api/auth/signin → 404 Not Found
GET /api/auth/me → 404 Not Found
```

Custom endpoints return 404 even though better-auth built-in endpoints work.

### Root Cause
Express middleware order matters! If better-auth catch-all is registered before custom routes, it captures all `/api/auth/*` requests before they reach your custom handlers.

### Detection
Check route order in `auth-server/src/app.ts`:
```typescript
// ❌ WRONG ORDER (causes 404s)
app.all('/api/auth/*', toNodeHandler(auth));  // Catches everything first
app.use('/api/auth', authRoutes);             // Never reached!

// ✅ CORRECT ORDER
app.use('/api/auth', authRoutes);             // Custom routes first
app.all('/api/auth/*', toNodeHandler(auth));  // Catch-all last
```

### Solution

**Correct middleware order**:
```typescript
// Custom auth routes (MUST come first)
app.use('/api/auth', authRoutes);

// better-auth catch-all (MUST come last)
app.all('/api/auth/*', toNodeHandler(auth));
```

### Auto-Fix
Edit `auth-server/src/app.ts` and move custom routes before better-auth handler.

### Verification
```bash
curl -X POST http://localhost:3000/api/auth/me \
  -H "Authorization: Bearer your-token"
# Should return user info, not 404
```

---

## Issue 3: Database Schema Sync

### Symptom
```
Error related to IP address type mismatch (e.g., AddrParseError, INET type error)
```

Or:

```
sqlalchemy.exc.ProgrammingError: column "ip_address" is of type inet
but expression is of type text
```

### Root Cause
Database schema definitions (auth-server) and Alembic (backend) use different column types for the same field:

| Field | Schema Definition | Alembic | Issue |
|-------|-------------------|---------|-------|
| `ip_address` | `String` / `@db.Text` (Prisma) or TEXT (custom) | `postgresql.INET` | ❌ Type mismatch |
| `user_agent` | `String` / `@db.Text` (Prisma) or TEXT (custom) | `sa.Text` | ✅ Compatible |

PostgreSQL `INET` type is strict and requires valid IP addresses. Text-based field types (Prisma `String`, custom TEXT) accept any text.

### Detection
```bash
# Check Prisma schema
grep "ip_address" auth-server/prisma/schema.prisma

# Check Alembic migration
grep "ip_address" backend/src/database/migrations/*.py
```

### Solution

**Option A: Change Alembic to Text** (Recommended)
```python
# backend/src/database/migrations/001_create_auth_tables.py

# ❌ WRONG (causes mismatch)
sa.Column('ip_address', postgresql.INET, nullable=True)

# ✅ CORRECT (compatible with Prisma)
sa.Column('ip_address', sa.Text, nullable=True)
```

**Option B: Change Prisma to validate IPs** (Not recommended)
```prisma
// More complex - requires validation logic
```

### Auto-Fix
```bash
# Run sync-schemas.sh script
bash .claude/skills/better-auth-setup/scripts/sync-schemas.sh --auto-fix
```

### Verification
```bash
# Recreate database with correct types
cd backend
alembic downgrade base
alembic upgrade head

# OR use custom Python migration (for projects using custom migration scripts)
# python src/database/run_migration.py

# Test creation
curl -X POST http://localhost:3000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test1234"}'
# Should succeed without AddrParseError
```

---

## Issue 4: Cross-Site Cookie Configuration

### Symptom
- Frontend on `https://yourdomain.github.io` cannot authenticate with auth server on `https://auth.vercel.app`
- Cookies not sent with cross-origin requests
- Session appears valid on auth server but frontend receives 401

### Root Cause
Cross-site cookies require `SameSite=none` and `Secure=true` in production.

Default configuration (`SameSite=lax`) blocks cookies on cross-origin requests.

### Detection
Check cookie configuration in `auth-server/src/auth/auth.config.ts`:
```typescript
// ❌ WRONG (blocks cross-site cookies)
sameSite: 'lax'  // Only works for same-domain

// ✅ CORRECT (allows cross-site)
sameSite: env.nodeEnv === 'production' ? 'none' : 'lax'
```

### Solution

Update `auth-server/src/auth/auth.config.ts`:
```typescript
advanced: {
  useSecureCookies: env.nodeEnv === 'production',
  defaultCookieAttributes: {
    httpOnly: true,
    secure: env.nodeEnv === 'production',  // HTTPS required
    sameSite: env.nodeEnv === 'production' ? 'none' : 'lax',  // Critical!
    path: '/',
  },
}
```

**Important**:
- `SameSite=none` REQUIRES `Secure=true` (HTTPS only)
- In development (localhost), use `SameSite=lax`

### Auto-Fix
Edit auth.config.ts to set correct SameSite policy based on environment.

### Verification
```bash
# Test cross-origin request
curl -X POST https://your-auth-server.vercel.app/api/auth/signin \
  -H "Content-Type: application/json" \
  -H "Origin: https://yourdomain.github.io" \
  -d '{"email":"test@example.com","password":"Test1234"}' \
  -v
# Check Set-Cookie header includes: SameSite=none; Secure
```

---

## Issue 5: Vercel Deployment Config

### Symptom
```
404 - NOT_FOUND
All routes return 404 on Vercel
Health endpoint works but auth endpoints don't
```

### Root Cause
Complex `vercel.json` rewrite rules or missing entry point configuration.

### Detection
Check `auth-server/vercel.json` for multiple rewrites:
```json
{
  "rewrites": [
    { "source": "/api/auth/(.*)", "destination": "/api/auth.js" },
    { "source": "/health", "destination": "/api/health.js" },
    { "source": "/(.*)", "destination": "/api/index.js" }
  ]
}
```
Multiple specific rewrites can cause conflicts.

### Solution

**Simplify to single catch-all**:
```json
{
  "version": 2,
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/api/index.js"
    }
  ]
}
```

**Ensure `api/index.ts` exists**:
```typescript
// auth-server/api/index.ts
import app from '../src/app.js';

export default app;
```

### Auto-Fix
Replace vercel.json with simplified configuration.

### Verification
```bash
# Deploy to Vercel
vercel deploy

# Test endpoints
curl https://your-deployment.vercel.app/health
curl -X POST https://your-deployment.vercel.app/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test1234"}'
```

---

## Issue 6: Email Verification Flow

### Symptom
- `requireEmailVerification: true` but no emails sent
- Users can't verify their accounts
- "Email verification required" error

### Root Cause
Email service not configured while email verification is enabled.

### Detection
Check `auth-server/src/auth/auth.config.ts`:
```typescript
emailAndPassword: {
  enabled: true,
  requireEmailVerification: true,  // ⚠️ Requires email service
}
```

Check for email configuration:
```typescript
// Missing email configuration!
// No Resend, SendGrid, or SMTP setup
```

### Solution

**Option A: Configure Email Service** (Production)

1. Choose email provider (Resend, SendGrid, AWS SES)
2. Get API key
3. Add to better-auth config:

```typescript
import { Resend } from 'resend';

const resend = new Resend(env.resendApiKey);

export const auth = betterAuth({
  // ... other config

  emailAndPassword: {
    enabled: true,
    requireEmailVerification: true,
    sendVerificationEmail: async (email, verificationUrl) => {
      await resend.emails.send({
        from: 'noreply@yourdomain.com',
        to: email,
        subject: 'Verify your email',
        html: `<a href="${verificationUrl}">Verify Email</a>`,
      });
    },
  },
});
```

**Option B: Disable Verification** (Testing)

```typescript
emailAndPassword: {
  enabled: true,
  requireEmailVerification: false,  // Disabled for testing
}
```

### Manual Steps Required
1. Choose email provider
2. Create account and get API key
3. Add API key to `.env`
4. Implement `sendVerificationEmail` function
5. Test email delivery

### Verification
```bash
# Test signup
curl -X POST http://localhost:3000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test1234"}'

# Check email inbox for verification link
# Or check email service logs
```

---

## Diagnostic Checklist

Run through this checklist when debugging auth issues:

```
□ ESM Configuration
  □ "type": "module" in package.json?
  □ .js extensions on all imports?
  □ tsconfig.json module: "ESNext"?

□ Route Ordering
  □ Custom routes before better-auth catch-all?
  □ app.use('/api/auth', authRoutes) comes first?
  □ app.all('/api/auth/*', ...) comes last?

□ Database Schema
  □ Prisma and Alembic use compatible types?
  □ ip_address field uses Text, not INET?
  □ Nullable fields match?

□ Cookie Configuration
  □ SameSite=none for production cross-domain?
  □ Secure=true in production?
  □ CORS origins include frontend URL?

□ Deployment (Vercel)
  □ Single catch-all rewrite in vercel.json?
  □ api/index.ts entry point exists?
  □ All routes tested after deployment?

□ Email Verification
  □ Email service configured if required?
  □ Or verification disabled for testing?
  □ Verification emails being sent?
```

---

## Quick Fixes Summary

```bash
# Fix 1: Add ESM support
echo '{"type":"module",...}' > auth-server/package.json

# Fix 2: Reorder routes (manual edit required)
# Move custom routes before better-auth in app.ts

# Fix 3: Sync schemas
bash .claude/skills/better-auth-setup/scripts/sync-schemas.sh --auto-fix

# Fix 4: Fix cookie config (manual edit required)
# Set sameSite: 'none' in auth.config.ts

# Fix 5: Simplify Vercel config
echo '{"rewrites":[{"source":"/(.*)", "destination":"/api/index.js"}]}' > vercel.json

# Fix 6: Disable email verification (for testing)
# Set requireEmailVerification: false in auth.config.ts
```

---

## Getting Help

If you encounter an issue not covered here:

1. Check better-auth documentation: https://docs.better-auth.com
2. Search GitHub issues: https://github.com/better-auth/better-auth/issues
3. Check this skill's examples: `.claude/skills/better-auth-setup/examples/`
4. Run diagnostics: Use the better-auth-fastapi-agent's validation phase

## Contributing

Found a new issue? Document it here with:
- Symptom (error message)
- Root cause (why it happens)
- Solution (how to fix)
- Auto-fix (if possible)
- Verification (how to test)
