import express from 'express';
import cors from 'cors';
import cookieParser from 'cookie-parser';
import * as helmetModule from 'helmet';
import { betterAuth } from 'better-auth';
import { toNodeHandler } from 'better-auth/node';
import { getAuthConfig } from './auth/auth.config.js';
import { env } from './config/env.js';
import { errorHandler, notFoundHandler } from './middleware/errorHandler.js';

// Workaround for helmet ES module compatibility
const helmet = (helmetModule as any).default || helmetModule;

// Import custom routes
import { getCurrentUser, getUserSessions, revokeSession } from './auth/routes.js';
import { jwtSignIn, jwtSignUp, jwtLogout, jwtRefresh } from './auth/jwt-auth.routes.js';

// Lazy initialization for serverless environments
let _app: express.Express | null = null;
let _auth: ReturnType<typeof betterAuth> | null = null;

function createApp() {
  if (_app) {
    return _app;
  }

  const app = express();

  // Middleware
  app.set('trust proxy', true);

  // Initialize better-auth
  const auth = betterAuth(getAuthConfig());
  _auth = auth;

  // CRITICAL: CORS must be configured BEFORE helmet to allow cross-origin requests
  app.use(cors({
    origin: env.CORS_ORIGINS.split(',').map((origin: string) => origin.trim()),
    credentials: true,
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH'],
    allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With'],
    exposedHeaders: ['Set-Cookie'],
    maxAge: 86400, // 24 hours
  }));

  // Security: Helmet middleware for security headers (AFTER CORS)
  app.use(helmet({
    contentSecurityPolicy: env.NODE_ENV === 'production' ? {
      directives: {
        defaultSrc: ["'self'"],
        styleSrc: ["'self'", "'unsafe-inline'"],
        scriptSrc: ["'self'"],
        imgSrc: ["'self'", 'data:', 'https:'],
      },
    } : false, // Disable CSP in development to avoid issues
    hsts: env.NODE_ENV === 'production' ? {
      maxAge: 31536000, // 1 year
      includeSubDomains: true,
      preload: true,
    } : false, // Disable HSTS in development (no HTTPS locally)
    frameguard: {
      action: 'deny',
    },
    referrerPolicy: {
      policy: 'strict-origin-when-cross-origin',
    },
    crossOriginResourcePolicy: { policy: "cross-origin" }, // Allow cross-origin requests
  }));

  // Cookie parser middleware - MUST be before routes that use req.cookies
  app.use(cookieParser());

  // Mount express json middleware - NOT GLOBAL
  // app.use(express.json());
  // app.use(express.urlencoded({ extended: true }));

  // Add custom routes BEFORE better-auth's middleware
  app.get('/api/auth/me', getCurrentUser);
  app.get('/api/auth/sessions', getUserSessions);
  app.delete('/api/auth/sessions/:sessionId', revokeSession);

  // JWT authentication endpoints (enhanced login/signup with JWT tokens)
  app.post('/api/auth/jwt/sign-in', express.json(), jwtSignIn);
  app.post('/api/auth/jwt/sign-up', express.json(), jwtSignUp);
  app.post('/api/auth/refresh', jwtRefresh); // No express.json() needed - reads from cookies
  app.post('/api/auth/logout', express.json(), jwtLogout);

  // Add better-auth middleware - this must come after custom routes if they handle /api/auth paths
  app.all('/api/auth/*', (req, res) => {
    return toNodeHandler(auth)(req, res);
  });

  // Health check endpoint (T023)
  app.get('/health', async (req, res) => {
    try {
      // Test database connection by importing and using the Prisma client directly
      // This ensures the database connection is working
      const { prisma } = await import('./database/client.js');

      // Perform a simple query to test the connection
      await prisma.$queryRaw`SELECT 1`;

      res.json({
        status: 'ok',
        timestamp: new Date().toISOString(),
        database: 'connected',
      });
    } catch (error) {
      console.error('Health check error:', error);
      res.status(503).json({
        status: 'error',
        timestamp: new Date().toISOString(),
        database: 'disconnected',
        error: error instanceof Error ? error.message : 'Unknown error',
      });
    }
  });

  // 404 handler for unmatched routes
  app.use(notFoundHandler);

  // Global error handler (must be last)
  app.use(errorHandler);

  _app = app;
  return app;
}

// Export the auth instance (lazy access via getter)
export const auth = {
  get instance() {
    if (!_auth) {
      createApp();
    }
    return _auth!;
  }
};

// Export createApp function for manual initialization
export { createApp };

// Default export returns the app instance (lazy - only initializes when called)
export default function getApp() {
  return createApp();
}
