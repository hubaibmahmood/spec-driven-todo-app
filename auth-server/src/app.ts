import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import { betterAuth } from 'better-auth';
import { toNodeHandler } from 'better-auth/node';
import { authConfig } from './auth/auth.config';
import { env } from './config/env';
import { errorHandler, notFoundHandler } from './middleware/errorHandler';

// Import custom routes
import { getCurrentUser, getUserSessions, revokeSession } from './auth/routes';

export const app = express();

// Middleware
app.set('trust proxy', true);

// Initialize better-auth
export const auth = betterAuth(authConfig);

// CRITICAL: CORS must be configured BEFORE helmet to allow cross-origin requests
app.use(cors({
  origin: env.CORS_ORIGINS.split(',').map(origin => origin.trim()),
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



// Mount express json middleware - NOT GLOBAL
// app.use(express.json());
// app.use(express.urlencoded({ extended: true }));

// Add custom routes BEFORE better-auth's middleware
app.get('/api/auth/me', getCurrentUser);
app.get('/api/auth/sessions', getUserSessions);
app.delete('/api/auth/sessions/:sessionId', revokeSession);

// Add better-auth middleware - this must come after custom routes if they handle /api/auth paths
app.all('/api/auth/*', toNodeHandler(auth));

// Health check endpoint (T023)
app.get('/health', async (req, res) => {
  try {
    // Test database connection by importing and using the Prisma client directly
    // This ensures the database connection is working
    const { prisma } = await import('./database/client');

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

export default app;