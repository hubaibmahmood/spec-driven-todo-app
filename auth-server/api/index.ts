import type { VercelRequest, VercelResponse } from '@vercel/node';

// For Vercel serverless, we need to dynamically import the compiled app
// and handle each request individually
export default async function handler(req: VercelRequest, res: VercelResponse) {
  try {
    // Dynamically import the compiled Express app
    const { default: app } = await import('../dist/app.js');

    // Handle the request with the Express app
    return app(req, res);
  } catch (error) {
    console.error('Serverless function error:', error);

    // Check if this is an environment variable error
    if (error instanceof Error && error.message.includes('Missing required environment variables')) {
      return res.status(500).json({
        error: 'Configuration Error',
        message: error.message,
        hint: 'Please configure the required environment variables in your Vercel project settings.',
        docs: 'https://vercel.com/docs/projects/environment-variables'
      });
    }

    return res.status(500).json({
      error: 'Internal server error',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
}
