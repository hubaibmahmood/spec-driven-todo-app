# Vercel Serverless Deployment Checklist

Complete guide for deploying Node.js/TypeScript serverless functions to Vercel, specifically for auth servers using better-auth, Express, and Prisma.

## Pre-Deployment Checklist

### 1. Project Structure

- [ ] Project uses TypeScript 5.x or later
- [ ] `tsconfig.json` configured for ES modules
- [ ] Build output goes to `/dist` directory
- [ ] Source files in `/src` directory
- [ ] Serverless handler in `/api` directory
- [ ] Prisma schema defined (if using database)

**Verify:**
```bash
ls -la
# Should see:
# - tsconfig.json
# - package.json
# - api/index.ts
# - src/
# - prisma/ (if using database)
```

### 2. TypeScript Configuration

**File:** `tsconfig.json`

- [ ] `"module": "NodeNext"`
- [ ] `"moduleResolution": "NodeNext"`
- [ ] `"target": "ES2022"` or later
- [ ] `"outDir": "./dist"`
- [ ] `"rootDir": "./src"`
- [ ] `"esModuleInterop": true`
- [ ] `"skipLibCheck": true`

**Example:**
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "outDir": "./dist",
    "rootDir": "./src",
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

**Test:**
```bash
npm run build
# Should compile without errors
# Check dist/ has .js files
```

### 3. ES Module Imports

- [ ] All relative imports have `.js` extensions
- [ ] Import paths are case-sensitive correct
- [ ] No circular dependencies
- [ ] Special packages (helmet, etc.) use correct import syntax

**Check:**
```bash
# Use validation script
python .claude/skills/vercel-serverless-deployment/scripts/validate-esm-imports.py src/

# Should output: "All ES module imports are correctly formatted!"
```

**Common Fixes:**
```typescript
// ❌ WRONG
import { env } from './config/env';
import { prisma } from '../database/client';

// ✅ CORRECT
import { env } from './config/env.js';
import { prisma } from '../database/client.js';

// Special: helmet
import * as helmetModule from 'helmet';
const helmet = (helmetModule as any).default || helmetModule;
```

### 4. Lazy Initialization

- [ ] No module-level `new ClassName()` instantiation
- [ ] No module-level function calls assigned to constants
- [ ] No direct `process.env` access at module level
- [ ] Environment validation wrapped in function
- [ ] Database client uses Proxy pattern
- [ ] External service clients use Proxy pattern
- [ ] App creation wrapped in factory function
- [ ] Instances cached for warm starts

**Check:**
```bash
# Use lazy init checker
python .claude/skills/vercel-serverless-deployment/scripts/check-lazy-init.py src/

# Should output: "No module-level initialization issues found!"
```

**Required Patterns:**

**Environment Variables:**
```typescript
// src/config/env.ts
let _env: Env | null = null;

export const env = new Proxy({} as Env, {
  get(target, prop) {
    if (!_env) {
      _env = validateEnv();
    }
    return _env[prop as keyof Env];
  }
});
```

**Prisma Client:**
```typescript
// src/database/client.ts
let _prisma: PrismaClient | undefined;

function getPrismaClient(): PrismaClient {
  if (_prisma) return _prisma;
  _prisma = new PrismaClient();
  return _prisma;
}

export const prisma = new Proxy({} as PrismaClient, {
  get(target, prop) {
    const client = getPrismaClient();
    const value = client[prop as keyof PrismaClient];
    if (typeof value === 'function') {
      return value.bind(client);
    }
    return value;
  }
});
```

**Express App:**
```typescript
// src/app.ts
let _app: express.Express | null = null;

export function createApp(): express.Express {
  if (_app) return _app;

  const app = express();
  // ... setup

  _app = app;
  return app;
}

export default function getApp() {
  return createApp();
}
```

### 5. Serverless Handler

**File:** `api/index.ts`

- [ ] Uses `@vercel/node` types
- [ ] Imports from `/dist` not `/src`
- [ ] Has async handler function
- [ ] Caches app instance
- [ ] Has error handling
- [ ] Logs initialization steps
- [ ] Provides helpful error messages

**Template:**
```typescript
import type { VercelRequest, VercelResponse } from '@vercel/node';
import type { Express } from 'express';

let cachedApp: Express | null = null;

async function getApp(): Promise<Express> {
  if (cachedApp) return cachedApp;

  try {
    const { default: getApp } = await import('../dist/app.js');
    cachedApp = getApp();
    return cachedApp;
  } catch (error) {
    console.error('[API] Error:', error);

    if (error instanceof Error &&
        error.message.includes('Missing required environment variables')) {
      const enhancedError = new Error(
        `Configuration Error: ${error.message}\n\n` +
        'Please configure environment variables in Vercel dashboard.'
      );
      enhancedError.name = 'ConfigurationError';
      throw enhancedError;
    }

    throw error;
  }
}

export default async function handler(
  req: VercelRequest,
  res: VercelResponse
) {
  try {
    const app = await getApp();
    return app(req, res);
  } catch (error) {
    console.error('Handler error:', error);

    if (error instanceof Error) {
      return res.status(500).json({
        error: error.name === 'ConfigurationError'
          ? 'Configuration Error'
          : 'Internal Server Error',
        message: error.message,
      });
    }

    return res.status(500).json({
      error: 'Internal Server Error',
      message: 'An unknown error occurred'
    });
  }
}
```

### 6. Vercel Configuration

**File:** `vercel.json`

- [ ] Specifies build command
- [ ] Routes all requests to `/api`
- [ ] Uses correct Node.js runtime

**Template:**
```json
{
  "version": 2,
  "buildCommand": "npm run vercel-build",
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/api"
    }
  ]
}
```

### 7. Build Scripts

**File:** `package.json`

- [ ] `build` script compiles TypeScript
- [ ] `vercel-build` script includes Prisma steps
- [ ] `start` script for local testing
- [ ] `dev` script for development

**Template:**
```json
{
  "scripts": {
    "dev": "tsx watch src/index.ts",
    "build": "tsc",
    "start": "node dist/index.js",
    "vercel-build": "prisma generate && prisma migrate deploy && npm run build"
  }
}
```

### 8. Dependencies

**Required:**
- [ ] `@vercel/node` in devDependencies
- [ ] TypeScript in devDependencies
- [ ] All production dependencies in `dependencies`

**Check:**
```bash
npm list @vercel/node
npm list typescript

# Verify all deps are installed
npm ci
```

### 9. Environment Variables Documentation

- [ ] All required variables documented
- [ ] Example values provided (not secrets!)
- [ ] Instructions for obtaining values
- [ ] Development vs Production differences noted

**Create:** `.env.example`
```bash
# Database
DATABASE_URL="postgresql://user:password@host:5432/database"

# Better-Auth
BETTER_AUTH_SECRET="generate-with-openssl-rand-base64-32"

# Email Service
RESEND_API_KEY="re_..."
EMAIL_FROM="noreply@yourdomain.com"

# URLs
FRONTEND_URL="http://localhost:3000"
CORS_ORIGINS="http://localhost:3000,http://localhost:8000"

# Environment
NODE_ENV="development"
PORT="8080"
```

**Create:** `DEPLOYMENT.md` or `README.md` section
Document each variable:
- What it's for
- How to obtain it
- Format/constraints
- Development vs Production values

## Deployment Steps

### Step 1: Local Validation

- [ ] Clean build
```bash
rm -rf dist node_modules/.cache
npm ci
npm run build
```

- [ ] Local server starts
```bash
npm start
# Should start without errors
```

- [ ] Health endpoint works
```bash
curl http://localhost:8080/health
# Should return { status: "ok" }
```

- [ ] Auth endpoints work (if applicable)
```bash
curl -X POST http://localhost:8080/api/auth/sign-up/email \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

- [ ] No module initialization errors in logs
- [ ] No import errors
- [ ] All features work as expected

### Step 2: Prepare Vercel Project

**Create Project (first time only):**

1. Go to https://vercel.com/dashboard
2. Click "Add New" → "Project"
3. Import your Git repository
4. Configure project:
   - Framework Preset: "Other"
   - Root Directory: `auth-server` (or your directory)
   - Build Command: `npm run vercel-build`
   - Output Directory: (leave blank)

**Or use Vercel CLI:**
```bash
npm install -g vercel
vercel login
vercel
# Follow prompts
```

### Step 3: Configure Environment Variables

**In Vercel Dashboard:**

1. Go to Project → Settings → Environment Variables
2. Add each variable:

**Production Variables:**

- [ ] `DATABASE_URL`
  - Your production database URL
  - Example: Neon, Supabase, etc.

- [ ] `BETTER_AUTH_SECRET`
  - Generate: `openssl rand -base64 32`
  - Store securely

- [ ] `RESEND_API_KEY`
  - From Resend dashboard
  - Format: `re_...`

- [ ] `EMAIL_FROM`
  - Verified sender email
  - Must be verified in Resend

- [ ] `FRONTEND_URL`
  - Your frontend URL
  - Example: `https://yourapp.vercel.app`

- [ ] `CORS_ORIGINS`
  - Comma-separated allowed origins
  - Example: `https://yourapp.vercel.app,https://yourapp.netlify.app`

- [ ] `NODE_ENV`
  - Set to: `production`

**Important:**
- Select "Production" environment for each variable
- Can also add to "Preview" and "Development" if needed
- Changes don't apply automatically - must redeploy

### Step 4: Deploy

**Via Git Push (Recommended):**
```bash
git add .
git commit -m "chore: Prepare for Vercel deployment"
git push

# Vercel auto-deploys on push
# Watch progress in Vercel dashboard
```

**Via Vercel CLI:**
```bash
vercel --prod

# Follow prompts
# Returns deployment URL
```

### Step 5: Post-Deployment Validation

**Check Deployment Status:**
- [ ] Build succeeded
- [ ] No build errors
- [ ] Functions deployed

**Check Function Logs:**
1. Go to Vercel Dashboard
2. Click deployment
3. Click "Functions" tab
4. Look for initialization messages
5. Verify no errors

**Test Endpoints:**

- [ ] Health endpoint
```bash
curl https://your-auth-server.vercel.app/health
# Should return: { status: "ok", timestamp: "...", database: "connected" }
```

- [ ] Auth endpoint (sign-up)
```bash
curl -X POST https://your-auth-server.vercel.app/api/auth/sign-up/email \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Password123!","name":"Test User"}'
# Should return user object or error message (not 404 or 500)
```

- [ ] Sign-in endpoint
```bash
curl -X POST https://your-auth-server.vercel.app/api/auth/sign-in/email \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Password123!"}'
```

**Monitor for Issues:**
- [ ] No cold start crashes
- [ ] Requests complete successfully
- [ ] Response times acceptable (< 2s cold start)
- [ ] No CORS errors in browser console

### Step 6: Frontend Integration

**Update Frontend Environment Variables:**

**In Frontend Project Settings:**

- [ ] `NEXT_PUBLIC_AUTH_URL`
  - Set to: `https://your-auth-server.vercel.app`
  - Do NOT include `/api/auth` suffix

**Redeploy Frontend:**
```bash
# Environment variables require redeploy
# Push to trigger deployment or:
vercel --prod

# Or trigger redeploy in dashboard
```

**Test Full Flow:**
- [ ] Frontend loads
- [ ] Sign-up form works
- [ ] Email verification sent
- [ ] Verification link works
- [ ] Sign-in works
- [ ] Sessions persist
- [ ] Protected routes work

## Troubleshooting After Deployment

### If Function Crashes:

1. **Check Logs Immediately**
   - Dashboard → Deployment → Functions
   - Look for error before crash

2. **Verify Environment Variables**
   - Settings → Environment Variables
   - All required variables set?
   - Correct values?

3. **Check Recent Changes**
   - What changed since last working deploy?
   - Review commit diff

4. **Test Locally**
   - Does it work with production env vars locally?
   ```bash
   # Copy production vars to .env
   npm run build
   npm start
   ```

5. **Roll Back**
   - Dashboard → Deployments
   - Find last working deployment
   - Click "..." → "Promote to Production"

### If 404 Errors:

1. **Check Route Configuration**
   - Auth server routes at `/api/auth/*`?
   - Better-auth baseURL correct?
   - Frontend proxy routes correctly?

2. **Test Direct Access**
   ```bash
   # Bypass frontend, test auth server directly
   curl https://your-auth-server.vercel.app/api/auth/sign-up/email
   ```

3. **Check Proxy Logs**
   - Add debug logging to frontend proxy
   - Verify request routing

### If CORS Errors:

1. **Update CORS_ORIGINS**
   - Include all frontend URLs
   - Comma-separated
   - No trailing slashes

2. **Redeploy Auth Server**
   - Environment changes require redeploy

3. **Verify CORS Middleware**
   - Is it before other middleware?
   - Are credentials enabled?

## Maintenance Checklist

### After Every Deployment:

- [ ] Check function logs for errors
- [ ] Test health endpoint
- [ ] Test at least one auth flow
- [ ] Monitor error rates
- [ ] Check cold start times

### Weekly:

- [ ] Review function analytics
- [ ] Check error logs
- [ ] Verify email delivery
- [ ] Test all auth flows
- [ ] Check database connections

### Monthly:

- [ ] Update dependencies
- [ ] Review and rotate secrets
- [ ] Check Prisma client version
- [ ] Review CORS origins
- [ ] Audit environment variables

## Rollback Plan

If deployment fails:

1. **Immediate Rollback**
   ```bash
   # In Vercel dashboard
   # Deployments → Find last working → Promote to Production
   ```

2. **Fix Issues Locally**
   - Identify problem
   - Fix and test locally
   - Commit fix

3. **Redeploy**
   ```bash
   git push
   # Monitor deployment carefully
   ```

## Production Optimization

### After Initial Deployment:

- [ ] Remove debug logging (or only in development)
- [ ] Enable function analytics
- [ ] Set up monitoring/alerts
- [ ] Document deployment process
- [ ] Create runbook for common issues
- [ ] Set up staging environment

### Performance:

- [ ] Cold start time < 2s
- [ ] Warm start time < 100ms
- [ ] Database query optimization
- [ ] Connection pooling configured
- [ ] Prisma client properly cached

### Security:

- [ ] Rotate `BETTER_AUTH_SECRET` regularly
- [ ] Review CORS origins
- [ ] Check helmet configuration
- [ ] Audit environment variables
- [ ] Enable Vercel firewall rules
- [ ] Set up rate limiting

## Success Criteria

Your deployment is successful when:

- ✅ Build completes without errors
- ✅ Function starts without crashes
- ✅ Health endpoint responds 200
- ✅ Auth endpoints work (no 404/500)
- ✅ Email verification works
- ✅ Frontend integration works
- ✅ No CORS errors
- ✅ Cold start time < 2 seconds
- ✅ Error rate < 1%
- ✅ All environment variables set
- ✅ Database connections stable

## Reference

- [Vercel Serverless Functions Docs](https://vercel.com/docs/functions/serverless-functions)
- [Better-Auth Documentation](https://better-auth.com)
- [Prisma Serverless Guide](https://www.prisma.io/docs/guides/deployment/deployment-guides/deploying-to-vercel)
- [Troubleshooting Guide](./troubleshooting-guide.md)
- [Lazy Initialization Patterns](./lazy-initialization-patterns.md)

---

**Last Updated:** 2025-12-15
**Skill Version:** 1.0.0
