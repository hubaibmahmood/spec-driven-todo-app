# Vercel Serverless Troubleshooting Guide

## Quick Diagnostic Steps

When a deployment fails or functions crash:

1. **Check Vercel Function Logs**
   - Dashboard → Project → Deployments → Click deployment → Functions tab
   - Look for the first error message before crash
   - Check timestamps to identify cold start vs warm start issues

2. **Verify Environment Variables**
   - Dashboard → Project → Settings → Environment Variables
   - Ensure all required variables are set
   - Check variable names are exact (case-sensitive)
   - Verify they're enabled for Production environment

3. **Test Build Locally**
   ```bash
   npm run build
   npm start
   # Test endpoints
   curl http://localhost:PORT/health
   ```

4. **Check Recent Commits**
   - What changed since last working deployment?
   - Did you modify imports, initialization, or configuration?

## Common Errors and Solutions

### Error: FUNCTION_INVOCATION_FAILED

**Symptoms:**
- Deployment succeeds but function crashes on first request
- Logs show no helpful error message
- Status: 500 Internal Server Error

**Common Causes:**

#### 1. Module-Level Initialization

**Diagnosis:**
```bash
# Check for module-level code execution
python .claude/skills/vercel-serverless-deployment/scripts/check-lazy-init.py src/
```

**Look for:**
- `export const x = functionCall()`
- `export const client = new Client()`
- `const app = express(); app.use(...)`
- Direct `process.env` access at module level

**Solution:** Apply lazy initialization patterns.

```typescript
// ❌ WRONG
export const env = validateEnv();

// ✅ CORRECT
let _env: Env | null = null;
export const env = new Proxy({} as Env, {
  get(target, prop) {
    if (!_env) _env = validateEnv();
    return _env[prop as keyof Env];
  }
});
```

#### 2. Missing Environment Variables

**Diagnosis:**
Check Vercel dashboard for all required variables:
- `DATABASE_URL`
- `BETTER_AUTH_SECRET`
- `RESEND_API_KEY`
- `EMAIL_FROM`
- `FRONTEND_URL`
- `CORS_ORIGINS`

**Solution:**
1. Add missing variables in Vercel dashboard
2. Redeploy (changes don't auto-apply)
3. Ensure variables are enabled for Production

**Helpful Error Message:**
```typescript
if (missingEnvVars.length > 0) {
  const errorMessage =
    `❌ Missing required environment variables: ${missingEnvVars.join(', ')}\n` +
    'Configure these in Vercel project settings.\n' +
    'Visit: https://vercel.com/docs/projects/environment-variables';
  throw new Error(errorMessage);
}
```

#### 3. Importing from Source Instead of Dist

**Diagnosis:**
Check `api/index.ts`:
```typescript
// ❌ WRONG - Imports TypeScript source
import { default: getApp } from '../src/app';

// ✅ CORRECT - Imports compiled JavaScript
import { default: getApp } from '../dist/app.js';
```

**Solution:**
Update serverless handler to import from `/dist` directory.

#### 4. Database Connection Issues

**Diagnosis:**
- Check `DATABASE_URL` format is correct
- Verify database is accessible from Vercel IPs
- Check Prisma client is initialized lazily

**Solution:**
```typescript
// Lazy Prisma client
let _prisma: PrismaClient | undefined;

function getPrismaClient(): PrismaClient {
  if (_prisma) return _prisma;

  _prisma = new PrismaClient({
    log: ['error'],
  });

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

### Error: ERR_MODULE_NOT_FOUND

**Symptoms:**
```
Error [ERR_MODULE_NOT_FOUND]: Cannot find module '/path/to/module'
imported from /path/to/file.js
```

**Common Causes:**

#### 1. Missing .js Extensions

**Diagnosis:**
```bash
# Validate all imports have .js extensions
python .claude/skills/vercel-serverless-deployment/scripts/validate-esm-imports.py src/
```

**Solution:**
Add `.js` extension to all relative imports, even when importing `.ts` files.

```typescript
// ❌ WRONG
import { env } from './config/env';
import { prisma } from '../database/client';

// ✅ CORRECT
import { env } from './config/env.js';
import { prisma } from '../database/client.js';
```

#### 2. Incorrect Module Resolution

**Diagnosis:**
Check `tsconfig.json`:

```json
{
  "compilerOptions": {
    "module": "NodeNext",
    "moduleResolution": "NodeNext"
  }
}
```

**Solution:**
Set both `module` and `moduleResolution` to `"NodeNext"`.

#### 3. Import Path Case Sensitivity

**Diagnosis:**
- File: `myFile.ts`
- Import: `import { x } from './MyFile.js'` ❌

**Solution:**
Ensure import paths match file names exactly (case-sensitive).

### Error: 404 on Auth Endpoints

**Symptoms:**
- `POST /api/auth/sign-up/email` returns 404
- Verification links don't work
- Auth server deployed successfully but routes not found
- Function logs show `[Better Auth Handler]` message but still returns 404

**Common Causes:**

#### 0. Trailing Slash in FRONTEND_URL (MOST COMMON!)

**Diagnosis:**
Check if `FRONTEND_URL` environment variable has a trailing slash:

```bash
# ❌ WRONG - Has trailing slash
FRONTEND_URL=https://yourapp.vercel.app/

# ✅ CORRECT - No trailing slash
FRONTEND_URL=https://yourapp.vercel.app
```

**Why This Breaks:**
When better-auth constructs URLs, it concatenates:
```typescript
baseURL: `${env.FRONTEND_URL}/api/auth`

// With trailing slash: https://yourapp.vercel.app//api/auth (double slash!)
// Without trailing slash: https://yourapp.vercel.app/api/auth (correct!)
```

The double slash `//api/auth` breaks better-auth's internal routing logic, causing all auth endpoints to return 404 even though the handler is being called.

**Solution:**
1. Go to Vercel dashboard → Project → Settings → Environment Variables
2. Find `FRONTEND_URL` variable
3. Remove the trailing slash if present
4. Click Save
5. Redeploy the application

**This is the #1 cause of mysterious 404 errors where everything else looks correct!**

#### 1. Route Configuration Mismatch

**Diagnosis:**
Check these three places must align:

```typescript
// 1. Auth server routes (auth-server/src/app.ts)
app.all('/api/auth/*', toNodeHandler(auth));

// 2. Better-auth baseURL (auth-server/src/auth/auth.config.ts)
baseURL: `${env.FRONTEND_URL}/api/auth`

// 3. Frontend proxy (frontend/app/api/[...all]/route.ts)
if (servicePrefix === "auth") {
  targetHost = AUTH_SERVICE_URL;
  newPathname = `/${urlParts.join("/")}`;
}
```

**Solution:**
Keep routes consistent at `/api/auth/*` across all three locations.

#### 2. Environment Variable Mismatch

**Diagnosis:**
Check frontend env vars:
- `NEXT_PUBLIC_AUTH_URL` should point to deployed auth server
- Must NOT include `/api/auth` suffix (that's added by the proxy)

**Solution:**
```bash
# ❌ WRONG
NEXT_PUBLIC_AUTH_URL=https://auth-server.vercel.app/api/auth

# ✅ CORRECT
NEXT_PUBLIC_AUTH_URL=https://auth-server.vercel.app
```

#### 3. Proxy Routing Logic

**Diagnosis:**
Frontend proxy should check if `AUTH_SERVICE_URL` already includes `/api/auth`:

```typescript
if (servicePrefix === "auth") {
  targetHost = AUTH_SERVICE_URL;

  // Avoid duplicate /api/auth in path
  if (targetHost.endsWith("/api/auth")) {
    newPathname = `/${urlParts.slice(2).join("/")}`;
  } else {
    newPathname = `/${urlParts.join("/")}`;
  }
}
```

**Solution:**
Update proxy logic to handle both cases.

#### 4. Incorrect vercel.json Configuration

**Diagnosis:**
Check if `vercel.json` uses deprecated `routes` configuration:

```json
// ❌ DEPRECATED - May not work correctly
{
  "version": 2,
  "buildCommand": "npm run vercel-build",
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/api/index.ts"
    }
  ]
}
```

**Solution:**
Use `rewrites` instead and remove `buildCommand` (use `vercel-build` script in package.json instead):

```json
// ✅ CORRECT - Modern approach
{
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/api/index"
    }
  ]
}
```

**Why This Works:**
- `rewrites` is the modern, supported approach for Vercel routing
- Removing `buildCommand` from vercel.json allows Vercel to use the `vercel-build` script from package.json
- The destination should be `/api/index` (no file extension or `/api`)

**package.json should have:**
```json
{
  "scripts": {
    "vercel-build": "prisma migrate deploy && prisma generate && tsc"
  }
}
```

#### 5. Incorrect toNodeHandler Usage

**Diagnosis:**
Check if toNodeHandler is called with incorrect parameters:

```typescript
// ❌ WRONG - toNodeHandler doesn't accept 'next' parameter
app.all('/api/auth/*', (req, res, next) => {
  return toNodeHandler(auth)(req, res, next);
});
```

**Solution:**
toNodeHandler only accepts `req` and `res`:

```typescript
// ✅ CORRECT - Only req and res
app.all('/api/auth/*', (req, res) => {
  console.log(`[Better Auth Handler] ${req.method} ${req.url}`);
  return toNodeHandler(auth)(req, res);
});
```

Or even simpler:
```typescript
// ✅ BEST - Direct usage
app.all('/api/auth/*', toNodeHandler(auth));
```

### Error: CORS Issues

**Symptoms:**
- Browser console shows CORS errors
- Preflight OPTIONS requests fail
- `Access-Control-Allow-Origin` header missing

**Diagnosis:**
Check CORS configuration in auth server:

```typescript
app.use(cors({
  origin: env.CORS_ORIGINS.split(',').map(o => o.trim()),
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH'],
  allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With'],
}));
```

**Solution:**
1. Add frontend URL to `CORS_ORIGINS` environment variable
2. Ensure CORS middleware is before other middleware
3. Set `credentials: true` for cookie support
4. Redeploy auth server

**Environment Variable:**
```bash
CORS_ORIGINS=https://your-frontend.vercel.app,https://your-frontend.netlify.app
```

### Error: Helmet Compatibility Issues

**Symptoms:**
```
TypeError: helmet is not a function
```
or
```
error TS2349: This expression is not callable
```

**Diagnosis:**
Using NodeNext module resolution breaks default helmet import.

**Solution:**
Use namespace import with fallback:

```typescript
// ❌ WRONG
import helmet from 'helmet';

// ✅ CORRECT
import * as helmetModule from 'helmet';
const helmet = (helmetModule as any).default || helmetModule;

// Use normally
app.use(helmet({ /* config */ }));
```

### Error: Prisma Client Not Generated

**Symptoms:**
```
Cannot find module '@prisma/client'
```
or
```
PrismaClient is not a constructor
```

**Diagnosis:**
Prisma client not generated before build.

**Solution:**
Update `vercel.json` build command:

```json
{
  "buildCommand": "prisma generate && prisma migrate deploy && npm run build"
}
```

Or in `package.json`:
```json
{
  "scripts": {
    "vercel-build": "prisma generate && prisma migrate deploy && npm run build"
  }
}
```

### Error: Email Not Sending

**Symptoms:**
- No verification emails received
- No errors in logs
- Sign-up succeeds but user can't verify

**Diagnosis:**

1. **Check Resend API Key**
   ```bash
   # Verify in Vercel dashboard
   RESEND_API_KEY=re_...
   ```

2. **Check Email From Address**
   ```bash
   # Must be verified domain in Resend
   EMAIL_FROM=noreply@yourdomain.com
   ```

3. **Check Logs**
   Look for email sending in function logs:
   ```
   [Email] Sending verification email to: user@example.com
   [Email] Verification email sent successfully
   ```

**Solution:**

Add comprehensive logging:
```typescript
emailVerification: {
  sendVerificationEmail: async ({ user, url, token }) => {
    console.log('[Email] Sending verification email to:', user.email);

    try {
      // Save token
      await prisma.verification.create({ /* ... */ });

      // Development: Log link to console
      if (process.env.NODE_ENV === 'development') {
        console.log('\n=================================');
        console.log('📧 EMAIL VERIFICATION LINK');
        console.log('Link:', url);
        console.log('=================================\n');
      }

      // Send email
      const result = await resend.emails.send({
        from: env.EMAIL_FROM,
        to: user.email,
        subject: 'Verify your email',
        html: `<p>Click <a href="${url}">here</a> to verify.</p>`,
      });

      console.log('[Email] Email sent:', result);
    } catch (error) {
      console.error('[Email] Failed to send:', error);
      throw error; // Re-throw to surface the error
    }
  },
}
```

**Verify Resend Setup:**
1. Go to Resend dashboard
2. Check API key is valid
3. Verify sender domain
4. Check sending quota

## Debugging Workflows

### Workflow 1: Diagnose Cold Start Failure

**When:** Function crashes immediately on deployment

**Steps:**

1. **Get Error Details**
   ```bash
   # Check Vercel function logs
   # Dashboard → Deployment → Functions tab
   # Look for first error before crash
   ```

2. **Check Module Initialization**
   ```bash
   cd auth-server
   python ../claude/skills/vercel-serverless-deployment/scripts/check-lazy-init.py src/
   ```

3. **Verify Environment Variables**
   ```bash
   # In Vercel dashboard
   # Check all required variables are set
   # Verify they're enabled for Production
   ```

4. **Test Build Locally**
   ```bash
   rm -rf dist
   npm run build
   npm start

   # In another terminal
   curl http://localhost:8080/health
   ```

5. **Check Import Statements**
   ```bash
   python ../claude/skills/vercel-serverless-deployment/scripts/validate-esm-imports.py src/
   ```

6. **Apply Fixes**
   - Add lazy initialization where needed
   - Add missing environment variables
   - Fix import paths

7. **Redeploy and Monitor**
   ```bash
   git add .
   git commit -m "fix: Apply lazy initialization patterns"
   git push

   # Watch Vercel deployment
   # Check function logs immediately after deployment
   ```

### Workflow 2: Debug 404 Errors

**When:** Auth endpoints return 404

**Steps:**

1. **Trace the Request Path**
   ```
   Frontend Request:
   POST https://yourapp.vercel.app/api/auth/sign-up/email
      ↓
   Frontend Proxy:
   Receives: /api/auth/sign-up/email
   Extracts: ["api", "auth", "sign-up", "email"]
   Service: "auth"
      ↓
   Auth Server:
   Receives: /api/auth/sign-up/email
   Route: app.all('/api/auth/*', handler)
   ```

2. **Check Each Component**

   **Frontend Proxy:**
   ```typescript
   // Add debug logging
   console.log('[Proxy] Incoming:', {
     pathname: request.nextUrl.pathname,
     servicePrefix,
     targetHost,
     newPathname,
   });
   ```

   **Auth Server:**
   ```typescript
   // Add debug logging
   app.use((req, res, next) => {
     console.log(`[Auth Server] ${req.method} ${req.url}`);
     next();
   });
   ```

3. **Verify Configuration**
   ```bash
   # Frontend .env
   NEXT_PUBLIC_AUTH_URL=https://auth-server.vercel.app

   # Auth server routes
   app.all('/api/auth/*', toNodeHandler(auth));

   # Better-auth config
   baseURL: 'https://yourapp.vercel.app/api/auth'
   ```

4. **Test Directly**
   ```bash
   # Bypass proxy - test auth server directly
   curl -X POST https://auth-server.vercel.app/api/auth/sign-up/email \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","password":"password123"}'
   ```

5. **Fix Route Mismatch**
   - Align all routes to `/api/auth/*`
   - Update environment variables
   - Redeploy both frontend and auth server

### Workflow 3: Debug CORS Issues

**When:** Browser shows CORS errors

**Steps:**

1. **Check Browser Console**
   ```
   Access to fetch at 'https://auth-server.vercel.app/api/auth/sign-up/email'
   from origin 'https://yourapp.vercel.app' has been blocked by CORS policy
   ```

2. **Verify CORS Configuration**
   ```typescript
   // auth-server/src/app.ts
   app.use(cors({
     origin: env.CORS_ORIGINS.split(','),
     credentials: true,
     methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH'],
     allowedHeaders: ['Content-Type', 'Authorization'],
   }));
   ```

3. **Check Environment Variable**
   ```bash
   # In Vercel dashboard for auth-server
   CORS_ORIGINS=https://yourapp.vercel.app,https://yourapp.netlify.app
   ```

4. **Test OPTIONS Request**
   ```bash
   curl -X OPTIONS https://auth-server.vercel.app/api/auth/sign-up/email \
     -H "Origin: https://yourapp.vercel.app" \
     -H "Access-Control-Request-Method: POST" \
     -v

   # Should see:
   # Access-Control-Allow-Origin: https://yourapp.vercel.app
   # Access-Control-Allow-Methods: POST
   ```

5. **Fix CORS Configuration**
   - Add all frontend URLs to `CORS_ORIGINS`
   - Ensure CORS middleware is before other middleware
   - Redeploy auth server

## Prevention Checklist

Before deploying to Vercel:

### Critical (Check First!)
- [ ] ⚠️ **FRONTEND_URL has NO trailing slash** (e.g., `https://app.com` not `https://app.com/`)
- [ ] ⚠️ **CORS_ORIGINS have NO trailing slashes**
- [ ] ⚠️ **vercel.json uses `rewrites` not `routes`**
- [ ] ⚠️ **vercel.json has no `buildCommand` or `version` fields**
- [ ] ⚠️ **toNodeHandler called correctly** (no `next` parameter)

### Code Quality
- [ ] All module-level initialization converted to lazy patterns
- [ ] All relative imports have `.js` extensions
- [ ] `tsconfig.json` uses `"module": "NodeNext"`
- [ ] Serverless handler imports from `/dist` not `/src`
- [ ] App instance cached for warm starts
- [ ] Error handling catches and reports all failures
- [ ] Logging added for debugging (can be removed later)

### Environment & Configuration
- [ ] All environment variables documented
- [ ] Environment validation provides helpful error messages
- [ ] CORS configuration includes all origins
- [ ] Better-auth baseURL matches public URL (no double slashes!)

### Testing
- [ ] Local build succeeds: `npm run build`
- [ ] Local server starts: `npm start`
- [ ] Health endpoint responds: `curl localhost:PORT/health`
- [ ] Auth endpoints work locally

## Monitoring and Alerts

### Set Up Monitoring

1. **Vercel Analytics**
   - Enable in project settings
   - Monitor function duration
   - Track error rates

2. **Function Logs**
   - Regularly review deployment logs
   - Look for initialization errors
   - Monitor cold start times

3. **Uptime Monitoring**
   - Use external service (UptimeRobot, etc.)
   - Monitor `/health` endpoint
   - Alert on downtime

### Key Metrics

- **Cold Start Time**: Should be < 2 seconds
- **Warm Start Time**: Should be < 100ms
- **Error Rate**: Should be < 1%
- **Success Rate**: Should be > 99%

### Log Analysis

Look for patterns:
```bash
# Good cold start
[API] Module loading started
[API] getApp called, cached: false
[API] Attempting dynamic import
[API] Import successful
[API] App instance created successfully
[API] Module loading completed
[Auth Server] POST /api/auth/sign-up/email

# Bad cold start
[API] Module loading started
Error: Missing required environment variables: RESEND_API_KEY
FUNCTION_INVOCATION_FAILED
```

## Getting Help

If you're still stuck after trying these solutions:

1. **Check Error ID** in Vercel logs - Search Vercel docs for specific error
2. **Review Recent Changes** - What changed since it last worked?
3. **Test Minimal Example** - Remove complexity until it works
4. **Compare Working Example** - Check this skill's reference implementation
5. **Check Vercel Status** - https://www.vercel-status.com
6. **Community Support**:
   - Vercel Discord
   - Better-auth Discord
   - Stack Overflow with [vercel] [serverless] tags

## Summary

**Most Common Issues (in order of frequency):**
1. **Trailing slash in FRONTEND_URL** → Remove trailing slashes from ALL environment variables (MOST COMMON!)
2. **Deprecated vercel.json** → Use `rewrites` instead of `routes`
3. Module-level initialization → Use lazy patterns
4. Missing env variables → Check Vercel dashboard
5. Import errors → Add `.js` extensions
6. Route mismatches → Align all configurations
7. CORS errors → Update `CORS_ORIGINS`
8. Incorrect toNodeHandler usage → Don't pass `next` parameter

**Best Debugging Practice:**
1. Check function logs first
2. Test locally before deploying
3. Add logging during debugging
4. Fix one issue at a time
5. Verify fix before moving on
