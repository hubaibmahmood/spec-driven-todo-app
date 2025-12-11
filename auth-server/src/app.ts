import express from 'express';
import cors from 'cors';
import { betterAuth } from 'better-auth';
import { toNodeHandler } from 'better-auth/node';
import { authConfig } from './auth/auth.config';
import { env } from './config/env';

// Import custom routes
import { getCurrentUser, getUserSessions, revokeSession } from './auth/routes';

export const app = express();

// Middleware
app.set('trust proxy', true);

// Initialize better-auth
export const auth = betterAuth(authConfig);


// Configure CORS

app.use(cors({

  origin: env.CORS_ORIGINS.split(',').map(origin => origin.trim()),

  credentials: true,

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

// Add a fallback route for non-auth paths that don't match other routes
app.get('*', (req, res) => {
  res.status(404).json({
    error: 'Not Found',
    message: 'Endpoint not found',
  });
});

export default app;