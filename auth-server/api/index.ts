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
    return res.status(500).json({
      error: 'Internal server error',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
}
