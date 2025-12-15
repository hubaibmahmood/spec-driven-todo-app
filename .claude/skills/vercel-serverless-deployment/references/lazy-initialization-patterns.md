# Lazy Initialization Patterns for Serverless

## Overview

Lazy initialization is a design pattern where object creation or resource initialization is deferred until the first time it's needed. In serverless environments like Vercel, this pattern is **critical** because module-level code executes during cold starts, before the handler function runs.

## Why Lazy Initialization Matters

### The Problem

When deploying to Vercel, your code goes through these phases:

1. **Module Load Phase** - All imports are resolved, module-level code executes
2. **Handler Registration** - Your handler function is registered
3. **Request Phase** - Handler executes when requests arrive

During the **Module Load Phase**, if your code tries to:
- Access environment variables that aren't set yet
- Connect to databases
- Validate configuration
- Make API calls
- Initialize service clients

The function will **crash before it can even handle requests**, resulting in `FUNCTION_INVOCATION_FAILED`.

### The Solution

Defer all initialization until the **Request Phase** when:
- Environment variables are guaranteed to be available
- The handler has started executing
- You can catch and report errors properly

## Pattern 1: Proxy Pattern for Singletons

The Proxy pattern lets you create an object that looks and behaves like the real thing, but only creates the actual instance when first accessed.

### Template

```typescript
let _instance: RealType | null = null;

function getInstance(): RealType {
  if (_instance) return _instance;

  // Actual initialization happens here
  _instance = new RealType(/* config */);

  return _instance;
}

export const instance = new Proxy({} as RealType, {
  get(target, prop) {
    const obj = getInstance();
    const value = obj[prop as keyof RealType];

    // Bind methods to preserve 'this' context
    if (typeof value === 'function') {
      return value.bind(obj);
    }

    return value;
  }
});
```

### Example: Environment Variables

```typescript
// src/config/env.ts

interface Env {
  DATABASE_URL: string;
  BETTER_AUTH_SECRET: string;
  RESEND_API_KEY: string;
  EMAIL_FROM: string;
  FRONTEND_URL: string;
  NODE_ENV: 'development' | 'production' | 'test';
}

function validateEnv(): Env {
  const requiredEnvVars = [
    'DATABASE_URL',
    'BETTER_AUTH_SECRET',
    'RESEND_API_KEY',
    'EMAIL_FROM',
    'FRONTEND_URL'
  ];

  const missingEnvVars = requiredEnvVars.filter(
    envVar => !process.env[envVar]
  );

  if (missingEnvVars.length > 0) {
    throw new Error(
      `Missing required environment variables: ${missingEnvVars.join(', ')}\n` +
      'Configure these in your Vercel project settings.'
    );
  }

  return {
    DATABASE_URL: process.env.DATABASE_URL!,
    BETTER_AUTH_SECRET: process.env.BETTER_AUTH_SECRET!,
    RESEND_API_KEY: process.env.RESEND_API_KEY!,
    EMAIL_FROM: process.env.EMAIL_FROM!,
    FRONTEND_URL: process.env.FRONTEND_URL!,
    NODE_ENV: (process.env.NODE_ENV as any) || 'development',
  };
}

// ❌ WRONG - Validates on module load
// export const env = validateEnv();

// ✅ CORRECT - Validates on first access
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

### Example: Prisma Client

```typescript
// src/database/client.ts

import { PrismaClient } from '@prisma/client';

// Extend global type for development caching
declare global {
  var prisma: PrismaClient | undefined;
}

let _prisma: PrismaClient | undefined;

function getPrismaClient(): PrismaClient {
  if (_prisma) {
    return _prisma;
  }

  // Reuse existing client in development (hot reload)
  if (global.prisma) {
    _prisma = global.prisma;
    return _prisma;
  }

  // Create new client
  _prisma = new PrismaClient({
    log: process.env.NODE_ENV === 'development'
      ? ['query', 'info', 'warn', 'error']
      : ['error'],
  });

  // Cache in development
  if (process.env.NODE_ENV !== 'production') {
    global.prisma = _prisma;
  }

  return _prisma;
}

// ❌ WRONG - Connects on module load
// export const prisma = new PrismaClient();

// ✅ CORRECT - Connects on first query
export const prisma = new Proxy({} as PrismaClient, {
  get(target, prop) {
    const client = getPrismaClient();
    const value = client[prop as keyof PrismaClient];

    // Bind methods to maintain context
    if (typeof value === 'function') {
      return value.bind(client);
    }

    return value;
  }
});
```

### Example: External Service (Resend)

```typescript
// src/utils/resend.ts

import { Resend } from 'resend';
import { env } from '../config/env.js';

let _resend: Resend | null = null;

function getResend(): Resend {
  if (!_resend) {
    _resend = new Resend(env.RESEND_API_KEY);
  }
  return _resend;
}

// ❌ WRONG - Instantiates on module load
// export const resend = new Resend(process.env.RESEND_API_KEY);

// ✅ CORRECT - Instantiates on first use
export const resend = new Proxy({} as Resend, {
  get(target, prop) {
    return getResend()[prop as keyof Resend];
  }
});
```

## Pattern 2: Factory Functions

Factory functions create and return instances. They're useful when you need more control over initialization or when Proxy isn't appropriate.

### Template

```typescript
let _instance: Type | null = null;

export function getInstance(): Type {
  if (_instance) return _instance;

  // Initialization logic
  _instance = createInstance();

  return _instance;
}

// Optional: Export factory for custom initialization
export function createInstance(config?: Config): Type {
  const instance = new Type(config);
  // Additional setup
  return instance;
}
```

### Example: Express App

```typescript
// src/app.ts

import express from 'express';
import { betterAuth } from 'better-auth';
import { toNodeHandler } from 'better-auth/node';
import { getAuthConfig } from './auth/auth.config.js';

let _app: express.Express | null = null;
let _auth: ReturnType<typeof betterAuth> | null = null;

export function createApp(): express.Express {
  // Return cached instance for warm starts
  if (_app) return _app;

  const app = express();
  app.set('trust proxy', true);

  // Initialize better-auth
  const auth = betterAuth(getAuthConfig());
  _auth = auth;

  // Middleware
  app.use(cors(/* config */));
  app.use(helmet(/* config */));

  // Routes
  app.all('/api/auth/*', toNodeHandler(auth));
  app.get('/health', healthCheckHandler);

  // Error handlers
  app.use(notFoundHandler);
  app.use(errorHandler);

  _app = app;
  return app;
}

// Export auth instance accessor
export const auth = {
  get instance() {
    if (!_auth) {
      createApp(); // Initialize app if needed
    }
    return _auth!;
  }
};

// Default export for easy consumption
export default function getApp() {
  return createApp();
}
```

### Example: Auth Configuration

```typescript
// src/auth/auth.config.ts

import { prismaAdapter } from 'better-auth/adapters/prisma';
import { prisma } from '../database/client.js';
import { resend } from '../utils/resend.js';
import { env } from '../config/env.js';

// ❌ WRONG - Configuration object created on module load
// export const authConfig = {
//   database: prismaAdapter(prisma, { provider: 'postgresql' }),
//   secret: env.BETTER_AUTH_SECRET,
//   // ... rest of config
// };

// ✅ CORRECT - Configuration created when called
export function getAuthConfig() {
  return {
    database: prismaAdapter(prisma, { provider: 'postgresql' }),
    secret: env.BETTER_AUTH_SECRET,
    baseURL: `${env.FRONTEND_URL}/api/auth`,

    session: {
      expiresIn: 7 * 24 * 60 * 60,
      updateAge: 24 * 60 * 60,
      cookieCache: { enabled: true, maxAge: 5 * 60 },
    },

    emailAndPassword: {
      enabled: true,
      requireEmailVerification: true,
      sendResetPassword: async ({ user, url, token }) => {
        // Send email using lazy-loaded resend client
        await resend.emails.send({
          from: env.EMAIL_FROM,
          to: user.email,
          subject: 'Reset your password',
          html: `<p>Click <a href="${url}">here</a> to reset your password.</p>`,
        });
      },
    },

    emailVerification: {
      sendVerificationEmail: async ({ user, url, token }) => {
        await resend.emails.send({
          from: env.EMAIL_FROM,
          to: user.email,
          subject: 'Verify your email',
          html: `<p>Click <a href="${url}">here</a> to verify your email.</p>`,
        });
      },
    },
  };
}
```

## Pattern 3: Memoization for Computed Values

Use memoization to cache expensive computations that should only run once.

```typescript
let _computed: ComputedType | null = null;

export function getComputed(): ComputedType {
  if (_computed) return _computed;

  // Expensive computation
  _computed = expensiveOperation();

  return _computed;
}

// Usage
const result = getComputed(); // Runs computation
const result2 = getComputed(); // Returns cached value
```

## Anti-Patterns to Avoid

### ❌ Direct Module-Level Initialization

```typescript
// These will all cause crashes on Vercel:

export const env = validateEnv();
export const prisma = new PrismaClient();
export const resend = new Resend(process.env.RESEND_API_KEY);
export const config = loadConfig();

const app = express();
app.use(middleware);
export default app;
```

### ❌ Conditional but Still Eager

```typescript
// Still runs on module load, just conditionally
export const prisma = process.env.NODE_ENV === 'production'
  ? new PrismaClient({ log: ['error'] })
  : new PrismaClient({ log: ['query'] });
```

### ❌ Async Module-Level Code

```typescript
// Top-level await is not supported in serverless functions
const data = await fetchData();
export { data };
```

## Migration Checklist

When refactoring existing code for serverless:

- [ ] Identify all module-level constants that execute code
- [ ] Check for `new ClassName()` at module level
- [ ] Check for function calls assigned to constants
- [ ] Look for database client instantiations
- [ ] Look for API client instantiations
- [ ] Find environment variable accesses
- [ ] Identify configuration loading
- [ ] Check for file system operations at module level

For each item found:

- [ ] Wrap in lazy initialization (Proxy or factory function)
- [ ] Add caching for warm starts
- [ ] Ensure proper error handling
- [ ] Test locally with `npm start`
- [ ] Test build with `npm run build`
- [ ] Deploy and monitor logs

## Testing Lazy Initialization

### Local Testing

```bash
# Clear any cached instances
rm -rf dist node_modules/.cache

# Build
npm run build

# Start fresh
npm start

# Test endpoints
curl http://localhost:8080/health
curl -X POST http://localhost:8080/api/auth/sign-up/email
```

### Vercel Testing

```bash
# Check function logs in Vercel dashboard
# Look for initialization messages
# Verify no crashes during cold starts

# Test cold start behavior
# Wait 5 minutes (function timeout)
# Make request to trigger new cold start
# Check logs for initialization
```

### Automated Testing

```bash
# Use the provided diagnostic scripts
python .claude/skills/vercel-serverless-deployment/scripts/check-lazy-init.py src/

# Should output: "No module-level initialization issues found!"
```

## Performance Considerations

### Warm Start Optimization

Cache instances to reuse across invocations:

```typescript
let _instance: Type | null = null;

function getInstance(): Type {
  if (_instance) {
    console.log('[Warm Start] Reusing cached instance');
    return _instance;
  }

  console.log('[Cold Start] Creating new instance');
  _instance = new Type();
  return _instance;
}
```

### Cold Start Monitoring

Add logging to track initialization time:

```typescript
function getInstance(): Type {
  if (_instance) return _instance;

  const startTime = Date.now();
  _instance = new Type();
  const duration = Date.now() - startTime;

  console.log(`[Init] Instance created in ${duration}ms`);

  return _instance;
}
```

### Lazy Loading Heavy Dependencies

```typescript
// Don't import heavy dependencies at module level
// ❌ import { HeavyLibrary } from 'heavy-library';

// ✅ Import only when needed
async function useHeavyLibrary() {
  const { HeavyLibrary } = await import('heavy-library');
  return new HeavyLibrary();
}
```

## Summary

**Key Principles:**

1. **Never execute code at module level** - Wrap everything in functions
2. **Cache instances for warm starts** - Store in module-level variables
3. **Use Proxy for transparent lazy loading** - Appears as normal object
4. **Use factories for explicit control** - More obvious what's happening
5. **Validate environment on first access** - Not on module load
6. **Log initialization for debugging** - Track cold vs warm starts

**Benefits:**

- ✅ No crashes during Vercel deployment
- ✅ Proper error reporting when things go wrong
- ✅ Faster warm starts by reusing instances
- ✅ More testable code
- ✅ Works locally and in production

**Trade-offs:**

- Slightly more complex code
- First request is slower (cold start)
- Need to understand Proxy behavior
- Must remember to cache instances
