---
name: vercel-serverless-deployment
description: Expert knowledge for deploying Node.js/TypeScript serverless functions on Vercel with better-auth, Express, and Prisma. Includes lazy initialization patterns, ES module configuration, error handling, and troubleshooting. Use when deploying to Vercel, fixing FUNCTION_INVOCATION_FAILED errors, configuring ES modules, or setting up better-auth on serverless platforms.
license: MIT
metadata:
  version: 1.0.0
  author: Claude Code
  category: engineering
  domain: deployment
  updated: 2025-12-15
  python-tools: check-lazy-init.py, validate-esm-imports.py, analyze-module-deps.py
  tech-stack: Vercel, Node.js, TypeScript, Express, better-auth, Prisma, Resend
---

# Vercel Serverless Deployment Skill

## Purpose

This skill provides comprehensive guidance for deploying Node.js/TypeScript serverless functions on Vercel, with specific expertise in resolving common cold-start issues, module loading problems, and configuration challenges. It's particularly valuable for applications using better-auth, Express, Prisma ORM, and external services like Resend.

The skill emerged from real-world deployment challenges where standard Express applications failed on Vercel due to module-level initialization triggering before serverless handlers could execute. It documents proven patterns for lazy initialization, ES module configuration, and error handling that ensure successful deployments.

Whether you're experiencing `FUNCTION_INVOCATION_FAILED` errors, `ERR_MODULE_NOT_FOUND` issues, or need to configure better-auth for serverless environments, this skill provides battle-tested solutions.

## Core Patterns

### 1. Lazy Initialization with Proxy Pattern

**Problem**: Module-level code executes before serverless handler runs, causing crashes when environment variables are missing or database connections fail.

**Solution**: Use JavaScript Proxy objects to defer initialization until first access.

**Example - Environment Variables**:
```typescript
// ❌ WRONG - Crashes on module load
export const env = validateEnv(); // Executes immediately

// ✅ CORRECT - Lazy validation
let _env: Env | null = null;
export const env = new Proxy({} as Env, {
  get(target, prop) {
    if (!_env) {
      _env = validateEnv(); // Only runs when accessed
    }
    return _env[prop as keyof Env];
  }
});
```

**Example - Prisma Client**:
```typescript
// ❌ WRONG - Instantiates on module load
export const prisma = new PrismaClient();

// ✅ CORRECT - Lazy instantiation
let _prisma: PrismaClient | undefined;

function getPrismaClient(): PrismaClient {
  if (_prisma) return _prisma;
  if (global.prisma) {
    _prisma = global.prisma;
    return _prisma;
  }

  _prisma = new PrismaClient({
    log: ['query', 'info', 'warn', 'error'],
  });

  if (process.env.NODE_ENV !== 'production') {
    global.prisma = _prisma;
  }

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

**Example - External Service Clients (Resend)**:
```typescript
// ❌ WRONG - Instantiates on module load
export const resend = new Resend(process.env.RESEND_API_KEY);

// ✅ CORRECT - Lazy instantiation with Proxy
let _resend: Resend | null = null;

function getResend() {
  if (!_resend) {
    _resend = new Resend(env.RESEND_API_KEY);
  }
  return _resend;
}

export const resend = new Proxy({} as Resend, {
  get(target, prop) {
    return getResend()[prop as keyof Resend];
  }
});
```

### 2. App Factory Pattern

**Problem**: Express app initialized at module level executes all middleware and configuration before handler runs.

**Solution**: Wrap app creation in a factory function with caching for warm starts.

```typescript
// ❌ WRONG - App created on module load
const app = express();
app.use(middleware);
export default app;

// ✅ CORRECT - Factory pattern with caching
let _app: express.Express | null = null;
let _auth: ReturnType<typeof betterAuth> | null = null;

function createApp() {
  if (_app) return _app; // Return cached for warm starts

  const app = express();
  app.set('trust proxy', true);

  // Debug logging
  app.use((req, res, next) => {
    console.log(`[Auth Server] ${req.method} ${req.url}`);
    next();
  });

  // Initialize better-auth
  const auth = betterAuth(getAuthConfig());
  _auth = auth;

  // Configure middleware and routes
  app.use(cors({ /* ... */ }));
  app.use(helmet({ /* ... */ }));
  app.all('/api/auth/*', toNodeHandler(auth));

  _app = app;
  return app;
}

export const auth = {
  get instance() {
    if (!_auth) createApp();
    return _auth!;
  }
};

export { createApp };

export default function getApp() {
  return createApp();
}
```

### 3. Serverless Handler Pattern

**Problem**: Vercel needs a default export function that handles requests, not an Express app instance.

**Solution**: Create an async handler that lazily loads the app and forwards requests.

```typescript
// api/index.ts - Vercel serverless function entry point
import type { VercelRequest, VercelResponse } from '@vercel/node';
import type { Express } from 'express';

console.log('[API] Module loading started');

let cachedApp: Express | null = null;

async function getApp(): Promise<Express> {
  console.log('[API] getApp called, cached:', !!cachedApp);
  if (cachedApp) return cachedApp;

  try {
    console.log('[API] Attempting dynamic import of ../dist/app.js');
    const { default: getApp } = await import('../dist/app.js');
    console.log('[API] Import successful, calling getApp()');
    cachedApp = getApp();
    console.log('[API] App instance created successfully');
    return cachedApp;
  } catch (error) {
    console.error('[API] Error during app initialization:', error);

    // Provide helpful error messages for configuration issues
    if (error instanceof Error && error.message.includes('Missing required environment variables')) {
      const enhancedError = new Error(
        `Configuration Error: ${error.message}\n\n` +
        'Please configure these environment variables in Vercel:\n' +
        '- DATABASE_URL\n' +
        '- BETTER_AUTH_SECRET\n' +
        '- RESEND_API_KEY\n' +
        '- EMAIL_FROM\n' +
        '- FRONTEND_URL\n\n' +
        'Visit: https://vercel.com/docs/projects/environment-variables'
      );
      enhancedError.name = 'ConfigurationError';
      throw enhancedError;
    }
    throw error;
  }
}

console.log('[API] Module loading completed');

export default async function handler(req: VercelRequest, res: VercelResponse) {
  try {
    const app = await getApp();
    return app(req, res);
  } catch (error) {
    console.error('Serverless function error:', error);

    if (error instanceof Error) {
      if (error.name === 'ConfigurationError') {
        return res.status(500).json({
          error: 'Configuration Error',
          message: error.message,
        });
      }
      return res.status(500).json({
        error: 'Internal Server Error',
        message: error.message,
        stack: process.env.NODE_ENV === 'development' ? error.stack : undefined
      });
    }

    return res.status(500).json({
      error: 'Internal Server Error',
      message: 'An unknown error occurred'
    });
  }
}
```

### 4. ES Module Configuration

**Problem**: TypeScript imports without `.js` extensions cause `ERR_MODULE_NOT_FOUND` errors when compiled to ES modules.

**Solution**: Configure TypeScript for NodeNext module resolution and add `.js` extensions to all relative imports.

**tsconfig.json**:
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "skipLibCheck": true
  }
}
```

**Import Examples**:
```typescript
// ❌ WRONG - Missing .js extension
import { env } from './config/env';
import { prisma } from '../database/client';

// ✅ CORRECT - Include .js extension (even for .ts files)
import { env } from './config/env.js';
import { prisma } from '../database/client.js';
```

**Helmet ES Module Fix**:
```typescript
// ❌ WRONG - Default import doesn't work with NodeNext
import helmet from 'helmet';

// ✅ CORRECT - Namespace import with fallback
import * as helmetModule from 'helmet';
const helmet = (helmetModule as any).default || helmetModule;
```

### 5. Better-Auth Configuration

**Problem**: Better-auth baseURL must match the public-facing URL structure, including proxy paths.

**Solution**: Configure baseURL to include the full path where better-auth is mounted.

```typescript
// getAuthConfig() function
export function getAuthConfig() {
  return {
    database: prismaAdapter(prisma, { provider: "postgresql" }),
    secret: env.BETTER_AUTH_SECRET,

    // ✅ CRITICAL: Include /api/auth in baseURL if proxy routes there
    baseURL: process.env.NODE_ENV === 'production'
      ? `${process.env.FRONTEND_URL}/api/auth`
      : `${env.FRONTEND_URL}/api/auth`,

    trustedOrigins: env.CORS_ORIGINS.split(',').map((origin: string) => origin.trim()),

    session: {
      expiresIn: 7 * 24 * 60 * 60,
      updateAge: 24 * 60 * 60,
      cookieCache: { enabled: true, maxAge: 5 * 60 },
    },

    emailAndPassword: {
      enabled: true,
      requireEmailVerification: true,
      minPasswordLength: 8,
      sendResetPassword: async ({ user, url, token }: any) => {
        console.log('[Email] Sending password reset email to:', user.email);

        try {
          // Save token to database
          await prisma.verification.create({
            data: {
              identifier: user.email,
              value: token,
              expiresAt: new Date(Date.now() + 60 * 60 * 1000),
            },
          });

          // Log in development
          if (process.env.NODE_ENV === 'development') {
            console.log('\n=================================');
            console.log('🔐 PASSWORD RESET LINK');
            console.log('Link:', url);
            console.log('=================================\n');
          }

          // Send email
          const result = await resend.emails.send({
            from: env.EMAIL_FROM,
            to: user.email,
            subject: 'Reset your password',
            html: `<p>Click <a href="${url}">here</a> to reset your password.</p>`,
          });

          console.log('[Email] Password reset email sent successfully:', result);
        } catch (error) {
          console.error('[Email] Failed to send password reset email:', error);
        }
      },
    },

    emailVerification: {
      sendVerificationEmail: async ({ user, url, token }: any) => {
        console.log('[Email] Sending verification email to:', user.email);

        try {
          await prisma.verification.create({
            data: {
              identifier: user.email,
              value: token,
              expiresAt: new Date(Date.now() + 15 * 60 * 1000),
            },
          });

          if (process.env.NODE_ENV === 'development') {
            console.log('\n=================================');
            console.log('📧 EMAIL VERIFICATION LINK');
            console.log('Link:', url);
            console.log('=================================\n');
          }

          const result = await resend.emails.send({
            from: env.EMAIL_FROM,
            to: user.email,
            subject: 'Verify your email',
            html: `<p>Click <a href="${url}">here</a> to verify your email.</p>`,
          });

          console.log('[Email] Verification email sent successfully:', result);
        } catch (error) {
          console.error('[Email] Failed to send verification email:', error);
        }
      },
      sendOnSignUp: true,
    },

    advanced: {
      disableOriginCheck: process.env.NODE_ENV === 'development',
    },
  };
}
```

## Workflows

### Workflow 1: Deploy New Auth Server to Vercel

**Goal**: Deploy a Node.js/TypeScript auth server with better-auth and Prisma to Vercel serverless.

**Steps**:

1. **Configure TypeScript for ES Modules**
   - Set `"module": "NodeNext"` and `"moduleResolution": "NodeNext"` in `tsconfig.json`
   - Add `.js` extensions to all relative imports in `.ts` files
   - Fix any namespace imports (like helmet) that need special handling

2. **Implement Lazy Initialization**
   - Convert environment validation to Proxy pattern
   - Convert Prisma client to Proxy pattern
   - Convert external service clients (Resend, etc.) to Proxy pattern
   - Wrap app creation in factory function with caching

3. **Create Serverless Handler**
   - Create `api/index.ts` with async handler function
   - Import compiled app from `../dist/app.js`
   - Add comprehensive error handling and logging
   - Cache app instance for warm starts

4. **Configure Vercel**
   - Create/verify `vercel.json` with build command and rewrites
   - Set all required environment variables in Vercel dashboard
   - Add `@vercel/node` to devDependencies

5. **Deploy and Test**
   - Run `vercel --prod` or push to connected Git branch
   - Check deployment logs for initialization errors
   - Test health endpoint: `https://your-app.vercel.app/health`
   - Test auth endpoints: `https://your-app.vercel.app/api/auth/sign-up/email`

**Expected Output**: Successful deployment with working auth endpoints and no `FUNCTION_INVOCATION_FAILED` errors.

**Time Estimate**: 30-60 minutes for first deployment, 10-15 minutes for updates.

**Example Commands**:
```bash
# Install dependencies
npm install --save-dev @vercel/node

# Test build locally
npm run build

# Test locally
npm start

# Deploy to Vercel
vercel --prod
```

### Workflow 2: Fix FUNCTION_INVOCATION_FAILED Error

**Goal**: Diagnose and fix serverless function crashes on Vercel.

**Steps**:

1. **Check Deployment Logs**
   - Go to Vercel dashboard → Deployments → Latest deployment → Function logs
   - Look for error messages before the crash
   - Common causes: missing env vars, module not found, initialization errors

2. **Verify Environment Variables**
   - Check all required variables are set in Vercel dashboard
   - Verify variable names match exactly (case-sensitive)
   - Test locally with same env vars

3. **Check Module Imports**
   - Ensure serverless handler imports from `/dist` (compiled code)
   - Verify all relative imports have `.js` extensions
   - Check for module-level code execution

4. **Identify Initialization Issues**
   - Search for code that runs at module load time
   - Look for: `const x = someFunction()` at top level
   - Look for: `new SomeClass()` at module level
   - Look for: database queries, API calls, file operations

5. **Apply Lazy Initialization**
   - Convert constants to Proxy objects
   - Wrap initialization in functions
   - Use factory pattern for app creation
   - Cache instances for warm starts

6. **Test and Redeploy**
   - Build and test locally: `npm run build && npm start`
   - Deploy to Vercel: `vercel --prod`
   - Monitor function logs for successful initialization
   - Test endpoints

**Expected Output**: Function initializes successfully, no crashes, endpoints respond correctly.

**Time Estimate**: 15-45 minutes depending on complexity.

**Diagnostic Script**:
```bash
# Run the lazy initialization checker
python .claude/skills/vercel-serverless-deployment/scripts/check-lazy-init.py src/
```

### Workflow 3: Fix ERR_MODULE_NOT_FOUND Errors

**Goal**: Resolve ES module import errors in compiled TypeScript.

**Steps**:

1. **Update tsconfig.json**
   - Set `"module": "NodeNext"`
   - Set `"moduleResolution": "NodeNext"`
   - Verify `"outDir"` and `"rootDir"` are set correctly

2. **Add .js Extensions to Imports**
   - Update all relative imports: `'./file'` → `'./file.js'`
   - This applies even when importing `.ts` files
   - Example: `import { foo } from './utils.js'` (for `utils.ts`)

3. **Fix Special Import Cases**
   - **Helmet**: Use namespace import with fallback
   ```typescript
   import * as helmetModule from 'helmet';
   const helmet = (helmetModule as any).default || helmetModule;
   ```
   - **Other CJS modules**: May need similar treatment

4. **Verify Package.json**
   - Ensure `"type": "module"` is set for ES modules
   - Or use `.mjs` extension for module files

5. **Test Build**
   - Clean build: `rm -rf dist && npm run build`
   - Check compiled output in `/dist`
   - Run locally: `npm start`
   - Verify no import errors

**Expected Output**: Clean compilation, no ERR_MODULE_NOT_FOUND errors, app starts successfully.

**Time Estimate**: 15-30 minutes.

**Validation Script**:
```bash
# Validate all imports have .js extensions
python .claude/skills/vercel-serverless-deployment/scripts/validate-esm-imports.py src/
```

## Common Pitfalls

### ❌ Pitfall 1: Route Configuration Mismatch

**Problem**: Better-auth routes don't match frontend proxy configuration.

**Symptoms**: 404 errors on auth endpoints, verification links don't work.

**Solution**:
- Keep auth server routes consistent: `/api/auth/*`
- Set better-auth baseURL to match public-facing URL: `${FRONTEND_URL}/api/auth`
- Don't change routes when debugging other issues

**Example**:
```typescript
// Auth server routes
app.all('/api/auth/*', toNodeHandler(auth));

// Better-auth config
baseURL: `${FRONTEND_URL}/api/auth`

// Frontend proxy
if (servicePrefix === "auth") {
  targetHost = AUTH_SERVICE_URL;
  // If AUTH_SERVICE_URL already includes /api/auth, strip it from path
  if (targetHost.endsWith("/api/auth")) {
    newPathname = `/${urlParts.slice(2).join("/")}`;
  } else {
    newPathname = `/${urlParts.join("/")}`;
  }
}
```

### ❌ Pitfall 2: Importing TypeScript Source in Serverless Handler

**Problem**: Handler imports from `/src` instead of `/dist`.

**Symptoms**: Module not found, or TypeScript execution errors.

**Solution**: Always import from compiled output.

```typescript
// ❌ WRONG
import { default: getApp } from '../src/app';

// ✅ CORRECT
import { default: getApp } from '../dist/app.js';
```

### ❌ Pitfall 3: Missing Environment Variable Validation

**Problem**: App crashes with cryptic errors when env vars are missing.

**Symptoms**: `undefined` errors, connection failures, auth errors.

**Solution**: Validate early with helpful error messages.

```typescript
export function validateEnv(): Env {
  const requiredEnvVars = [
    'DATABASE_URL', 'BETTER_AUTH_SECRET', 'RESEND_API_KEY',
    'EMAIL_FROM', 'FRONTEND_URL'
  ];

  const missingEnvVars = requiredEnvVars.filter(envVar => !process.env[envVar]);

  if (missingEnvVars.length > 0) {
    const errorMessage = `❌ Missing required environment variables: ${missingEnvVars.join(', ')}`;
    console.error(errorMessage);
    console.error('Please configure these environment variables in your Vercel project settings.');
    console.error('Visit: https://vercel.com/docs/projects/environment-variables');
    throw new Error(errorMessage);
  }

  return {
    DATABASE_URL: process.env.DATABASE_URL!,
    // ... rest of env vars
  };
}
```

### ❌ Pitfall 4: Not Caching App Instance

**Problem**: App recreated on every request (cold start behavior on warm instances).

**Symptoms**: Slow response times, excessive database connections.

**Solution**: Cache app instance for warm starts.

```typescript
let cachedApp: Express | null = null;

async function getApp(): Promise<Express> {
  if (cachedApp) return cachedApp; // ✅ Return cached instance

  // Initialize app
  const { default: getApp } = await import('../dist/app.js');
  cachedApp = getApp();

  return cachedApp;
}
```

## Integration Examples

### Complete Auth Server Structure

```
auth-server/
├── api/
│   └── index.ts              # Vercel serverless handler
├── src/
│   ├── app.ts                # Express app with factory pattern
│   ├── index.ts              # Local dev server entry point
│   ├── auth/
│   │   ├── auth.config.ts    # getAuthConfig() function
│   │   └── routes.ts         # Custom auth routes
│   ├── config/
│   │   └── env.ts            # Lazy env validation with Proxy
│   ├── database/
│   │   └── client.ts         # Lazy Prisma client with Proxy
│   ├── middleware/
│   │   └── errorHandler.ts  # Error handling middleware
│   └── utils/
│       └── resend.ts         # Lazy Resend client with Proxy
├── dist/                     # Compiled output (gitignored)
├── prisma/
│   └── schema.prisma
├── package.json
├── tsconfig.json             # NodeNext configuration
└── vercel.json               # Vercel config
```

### vercel.json Configuration

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

### package.json Scripts

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

### Environment Variables Checklist

**Development (.env)**:
```bash
DATABASE_URL="postgresql://user:password@localhost:5432/dbname"
BETTER_AUTH_SECRET="your-secret-key-min-32-chars"
RESEND_API_KEY="re_..."
EMAIL_FROM="noreply@yourdomain.com"
FRONTEND_URL="http://localhost:3000"
CORS_ORIGINS="http://localhost:3000,http://localhost:8000"
NODE_ENV="development"
PORT="8080"
```

**Production (Vercel Dashboard)**:
- `DATABASE_URL` - Your production database URL (e.g., Neon, Supabase)
- `BETTER_AUTH_SECRET` - Generate with `openssl rand -base64 32`
- `RESEND_API_KEY` - From Resend dashboard
- `EMAIL_FROM` - Verified sender email
- `FRONTEND_URL` - Your frontend URL (e.g., `https://yourapp.vercel.app`)
- `CORS_ORIGINS` - Comma-separated allowed origins
- `NODE_ENV` - Set to `production`

## Success Metrics

- **Deployment Success Rate**: 100% successful deployments without `FUNCTION_INVOCATION_FAILED` errors
- **Cold Start Time**: < 2 seconds for function initialization
- **Error Rate**: 0% initialization errors, < 1% request errors
- **Development Experience**: Local development works identically to production
- **Debugging Time**: < 15 minutes to diagnose and fix deployment issues
- **Build Time**: < 2 minutes for full build and deployment

## Troubleshooting Guide

### Issue: Deployment succeeds but function crashes

**Check**:
1. Vercel function logs for error messages
2. Environment variables are all set
3. No module-level code execution
4. Imports are from `/dist` not `/src`

**Fix**: Apply lazy initialization patterns from this skill.

### Issue: ERR_MODULE_NOT_FOUND locally

**Check**:
1. `tsconfig.json` has `"module": "NodeNext"`
2. All relative imports have `.js` extensions
3. Build output exists in `/dist`

**Fix**: Add `.js` to imports and rebuild.

### Issue: 404 on auth endpoints

**Check**:
1. Better-auth baseURL configuration
2. Frontend proxy routing logic
3. Auth server route mounting path
4. Environment variable `NEXT_PUBLIC_AUTH_URL`

**Fix**: Align all configurations - see Pitfall 1.

### Issue: Emails not sending

**Check**:
1. `RESEND_API_KEY` is set correctly
2. `EMAIL_FROM` is verified in Resend
3. Function logs for email errors
4. Development mode console logs for verification links

**Fix**: Check Resend dashboard, verify domain, check error logs.

## Related Skills

- `better-auth-setup` - For initial better-auth configuration
- `database-integration` - For Prisma setup and migrations
- `fastapi-patterns` - For backend API integration

## References

- [Vercel Serverless Functions Documentation](https://vercel.com/docs/functions/serverless-functions)
- [Better-Auth Documentation](https://better-auth.com)
- [TypeScript ES Modules](https://www.typescriptlang.org/docs/handbook/esm-node.html)
- [Prisma with Serverless](https://www.prisma.io/docs/guides/deployment/deployment-guides/deploying-to-vercel)
- [Resend Email API](https://resend.com/docs)
