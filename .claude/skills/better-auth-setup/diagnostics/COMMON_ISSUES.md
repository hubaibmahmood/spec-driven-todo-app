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
Check auth server's `package.json` for missing `"type": "module"`:
```bash
# Replace {{AUTH_SERVER_DIR}} with your auth server directory
grep '"type"' {{AUTH_SERVER_DIR}}/package.json
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

### Auto-Fix (Orchestrator Should Execute)
```typescript
// Read package.json
const pkg = JSON.parse(await read('{{AUTH_SERVER_DIR}}/package.json'));

// Add type: module if missing
if (!pkg.type) {
  pkg.type = 'module';
  await write('{{AUTH_SERVER_DIR}}/package.json', JSON.stringify(pkg, null, 2));
}
```

### Verification
```bash
cd {{AUTH_SERVER_DIR}}
npm run dev
# Should start without ERR_REQUIRE_ESM
```

---

## Issue 2: Route Ordering

### Symptom
```
POST /api/auth/me → 404 Not Found
GET /api/auth/verify-token → 404 Not Found
```

### Root Cause
Custom routes registered AFTER better-auth catch-all handler.

Express processes middleware in order. If `app.all('/api/auth/*', ...)` comes before custom routes, it captures everything.

### Detection
Check route registration order in auth server's Express app:
```bash
# Look for route ordering in app.ts or main server file
grep -A 5 -B 5 "/api/auth" {{AUTH_SERVER_DIR}}/src/app.ts
```

### Solution

**Correct Order**:
```typescript
// ✅ Custom routes FIRST
app.use('/api/auth/me', getMeRoute);
app.use('/api/auth/verify-token', verifyTokenRoute);
app.use('/api/auth', customAuthRoutes);

// ✅ better-auth catch-all AFTER
app.all('/api/auth/*', toNodeHandler(auth));
```

**Incorrect Order**:
```typescript
// ❌ Catch-all FIRST (captures everything)
app.all('/api/auth/*', toNodeHandler(auth));

// ❌ Custom routes AFTER (never reached)
app.use('/api/auth', customAuthRoutes);
```

### Auto-Fix (Orchestrator Should Execute)
```typescript
// Read app.ts file
const appFile = await read('{{AUTH_SERVER_DIR}}/src/app.ts');

// Check if route ordering is incorrect
const catchAllIndex = appFile.indexOf("app.all('/api/auth/*'");
const customRoutesIndex = appFile.indexOf("app.use('/api/auth'");

if (catchAllIndex !== -1 && customRoutesIndex !== -1 && catchAllIndex < customRoutesIndex) {
  // Auto-fix: Reorder routes (move custom routes before catch-all)
  // Implementation depends on file structure
}
```

### Verification
```bash
# Test custom endpoint
curl http://localhost:3000/api/auth/me
# Should return 200 or 401, not 404
```

---

## Issue 3: Database Schema Sync

### Symptom
```
sqlalchemy.exc.ProgrammingError:
column "ip_address" is of type inet but expression is of type text
```

### Root Cause
Type mismatch between Prisma (auth server) and Alembic (FastAPI backend):
- Prisma uses `String` or `@db.Text`
- Alembic migration uses `postgresql.INET`

PostgreSQL's `INET` type expects IP addresses in a specific format, but better-auth stores them as plain text.

### Detection
```bash
# Check Prisma schema
grep "ip_address" {{PRISMA_SCHEMA_PATH}}

# Check Alembic migrations
grep "ip_address" {{ALEMBIC_MIGRATIONS_PATH}}/*.py
```

### Solution

**Option 1: Change Alembic to Text** (recommended):
```python
# In your Alembic migration file
sa.Column('ip_address', sa.Text, nullable=True)  # ✅ Compatible with Prisma
```

**Option 2: Change Prisma to INET** (not recommended):
```prisma
// In Prisma schema
ipAddress String? @map("ip_address") @db.Inet  // ⚠️ May cause issues with better-auth
```

### Auto-Fix (Use Script)
```bash
# Run the sync-schemas.sh script with auto-fix
bash .claude/skills/better-auth-setup/scripts/sync-schemas.sh --auto-fix
```

### Manual Fix
1. Find latest Alembic migration:
   ```bash
   ls -t {{ALEMBIC_MIGRATIONS_PATH}}/*.py | head -1
   ```

2. Edit migration file:
   ```python
   # Change from:
   sa.Column('ip_address', postgresql.INET, nullable=True)

   # To:
   sa.Column('ip_address', sa.Text, nullable=True)
   ```

3. Run migration:
   ```bash
   cd {{BACKEND_DIR}}
   alembic upgrade head
   ```

### Verification
```bash
# Check database schema
psql $DATABASE_URL -c "\d user_sessions"
# ip_address should be type 'text', not 'inet'
```

---

## Issue 4: Cross-Site Cookie Configuration

### Symptom
- Cookies not sent in cross-domain requests
- Browser console: "Cookie blocked due to SameSite policy"
- Auth works on same domain but fails cross-domain

### Root Cause
Incorrect `sameSite` or `secure` cookie attributes for production deployment.

For cross-domain setups (e.g., frontend at `app.example.com`, auth at `auth.example.com`):
- Cookies must have `sameSite: 'none'`
- Cookies must have `secure: true` (HTTPS only)

### Detection
Check auth server cookie configuration:
```bash
grep -A 10 "defaultCookieAttributes" {{AUTH_SERVER_DIR}}/src/auth/auth.config.ts
```

### Solution

**For Production (Cross-Domain)**:
```typescript
advanced: {
  defaultCookieAttributes: {
    httpOnly: true,
    secure: true,              // ✅ Required for SameSite=none
    sameSite: 'none',          // ✅ Required for cross-domain
    path: '/',
  },
}
```

**For Development (Same Domain)**:
```typescript
advanced: {
  defaultCookieAttributes: {
    httpOnly: true,
    secure: false,             // ✅ Can be false on localhost
    sameSite: 'lax',          // ✅ Lax is fine for same domain
    path: '/',
  },
}
```

**Dynamic (Recommended)**:
```typescript
advanced: {
  defaultCookieAttributes: {
    httpOnly: true,
    secure: env.nodeEnv === 'production',
    sameSite: env.nodeEnv === 'production' ? 'none' : 'lax',
    path: '/',
  },
}
```

### Auto-Fix (Orchestrator Should Execute)
```typescript
// Read auth.config.ts
const configFile = await read('{{AUTH_SERVER_DIR}}/src/auth/auth.config.ts');

// Check if sameSite is hardcoded
if (configFile.includes("sameSite: 'lax'") && !configFile.includes("env.nodeEnv")) {
  // Suggest fix: Use dynamic configuration based on environment
}
```

### Verification
```bash
# Start auth server
cd {{AUTH_SERVER_DIR}} && npm run dev

# Check Set-Cookie headers
curl -v http://localhost:3000/api/auth/session | grep "Set-Cookie"
```

---

## Issue 5: Vercel Deployment Config

### Symptom
- Auth endpoints work locally
- 404 errors on all auth endpoints when deployed to Vercel
- `/api/auth/signup` → 404

### Root Cause
Vercel requires specific routing configuration for dynamic routes.

Common mistakes:
- Multiple rewrite rules (confusing precedence)
- Missing catch-all rewrite
- Incorrect `dest` path in vercel.json

### Detection
Check if `vercel.json` exists and has correct structure:
```bash
cat {{AUTH_SERVER_DIR}}/vercel.json
```

### Solution

**Simplified Vercel Configuration** (recommended):
```json
{
  "version": 2,
  "builds": [
    {
      "src": "src/index.ts",
      "use": "@vercel/node"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/src/index.ts"
    }
  ]
}
```

**Alternative (Serverless Function)**:
```json
{
  "version": 2,
  "rewrites": [
    { "source": "/(.*)", "destination": "/api/index" }
  ]
}
```

With corresponding serverless function:
```typescript
// {{AUTH_SERVER_DIR}}/api/index.ts
import app from '../src/app';
export default app;
```

### Auto-Fix (Orchestrator Should Execute)
```typescript
// Check if vercel.json needs simplification
const vercelConfig = JSON.parse(await read('{{AUTH_SERVER_DIR}}/vercel.json'));

if (vercelConfig.routes && vercelConfig.routes.length > 1) {
  // Simplify to single catch-all
  vercelConfig.routes = [
    { src: "/(.*)", dest: "/src/index.ts" }
  ];
  await write('{{AUTH_SERVER_DIR}}/vercel.json', JSON.stringify(vercelConfig, null, 2));
}
```

### Verification
```bash
# Deploy to Vercel
vercel --prod

# Test endpoint
curl https://your-auth-server.vercel.app/api/auth/session
```

---

## Issue 6: Email Verification Flow

### Symptom
- Signup completes but no email sent
- Console shows no errors
- Email verification links don't arrive

### Root Cause
Missing or incorrect email service configuration.

better-auth requires email service setup for:
- Email verification during signup
- Password reset emails
- Magic link authentication

### Detection
Check environment variables:
```bash
grep -E "(EMAIL_|RESEND_)" {{AUTH_SERVER_DIR}}/.env
```

### Solution

**Step 1: Choose Email Service**

Popular options:
- **Resend** (recommended): https://resend.com
- **SendGrid**: https://sendgrid.com
- **Mailgun**: https://mailgun.com
- **AWS SES**: https://aws.amazon.com/ses

**Step 2: Configure Environment Variables**

For Resend:
```env
RESEND_API_KEY=re_123456789abcdef
EMAIL_FROM=noreply@yourdomain.com
```

For SendGrid:
```env
SENDGRID_API_KEY=SG.123456789abcdef
EMAIL_FROM=noreply@yourdomain.com
```

**Step 3: Update Auth Configuration**

```typescript
import { Resend } from 'resend';

const resend = new Resend(env.resendApiKey);

export const auth = betterAuth({
  // ... other config

  emailAndPassword: {
    enabled: true,
    requireEmailVerification: true,  // ✅ Enable verification

    async sendVerificationEmail({ user, url }) {
      await resend.emails.send({
        from: env.emailFrom,
        to: user.email,
        subject: 'Verify your email',
        html: `<p>Click <a href="${url}">here</a> to verify your email.</p>`,
      });
    },
  },
});
```

### Manual Fix Only
This issue requires manual configuration:

1. Sign up for email service
2. Get API keys
3. Add to `.env` file
4. Update auth configuration
5. Test email sending

### Verification
```bash
# Test signup with email verification
curl -X POST http://localhost:3000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123","name":"Test User"}'

# Check email inbox for verification link
```

---

## Summary

| Issue | Severity | Fix Complexity | Auto-Fix |
|-------|----------|----------------|----------|
| ESM/CommonJS | 🔴 High | Easy | ✅ Yes |
| Route Ordering | 🔴 High | Easy | ✅ Yes |
| Schema Sync | 🟠 Medium | Medium | ✅ Yes |
| Cross-Site Cookies | 🟠 Medium | Easy | ✅ Yes |
| Vercel Config | 🟡 Low | Easy | ✅ Yes |
| Email Verification | 🟡 Low | Medium | ⚠️ Manual |

## Troubleshooting Workflow

1. **Check logs** for error messages
2. **Match error** to one of the 6 common issues above
3. **Run detection** command for that issue
4. **Apply solution** (auto-fix if available)
5. **Verify fix** with verification command
6. **Repeat** if issue persists

## Prevention

Add these checks to your pre-commit hooks or CI/CD:

```bash
# Check ESM configuration
grep '"type": "module"' {{AUTH_SERVER_DIR}}/package.json

# Check route ordering
# (Custom script to verify route order)

# Check schema sync
bash .claude/skills/better-auth-setup/scripts/sync-schemas.sh

# Check Vercel config
# (Validate vercel.json structure)
```

## Getting Help

If you encounter an issue not covered here:

1. Check better-auth documentation: https://better-auth.com
2. Search GitHub issues: https://github.com/better-auth/better-auth/issues
3. Join Discord community: https://discord.gg/better-auth
4. Review diagnostic script output: `bash scripts/sync-schemas.sh`

## Contributing

Found a new common issue? Please document it following this format:
- Symptom (error message)
- Root Cause (technical explanation)
- Detection (how to identify)
- Solution (step-by-step fix)
- Auto-Fix (if possible)
- Verification (how to confirm fix)
