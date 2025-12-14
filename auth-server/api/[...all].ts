import type { VercelRequest, VercelResponse } from '@vercel/node';
import type { Express } from 'express';

console.log('[API] Module loading started');

// Cache the app instance across warm starts
let cachedApp: Express | null = null;

// Lazy load and initialize the Express app
async function getApp(): Promise<Express> {
  console.log('[API] getApp called, cached:', !!cachedApp);

  if (cachedApp) {
    return cachedApp;
  }

  try {
    console.log('[API] Attempting dynamic import of ../dist/app.js');
    // Dynamically import the compiled Express app getter
    const { default: getApp } = await import('../dist/app.js');
    console.log('[API] Import successful, calling getApp()');

    // Call the function to get the app instance
    cachedApp = getApp();
    console.log('[API] App instance created successfully');
    return cachedApp;
  } catch (error) {
    console.error('[API] Error during app initialization:', error);

    // Re-throw with more context
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

// Serverless function handler
export default async function handler(req: VercelRequest, res: VercelResponse) {
  try {
    const app = await getApp();

    // Handle the request with the Express app
    return app(req, res);
  } catch (error) {
    console.error('Serverless function error:', error);

    // Return user-friendly error response
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
