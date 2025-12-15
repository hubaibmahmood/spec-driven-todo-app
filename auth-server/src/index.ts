import 'dotenv/config';
import { env } from './config/env.js';
import getApp from './app.js';

async function startServer() {
  try {
    // Get the Express app instance
    const app = getApp();

    const server = app.listen(env.PORT, () => {
      console.log(`🚀 Auth server running on port ${env.PORT}`);
      console.log(`   Environment: ${env.NODE_ENV}`);
      console.log(`   Health check: http://localhost:${env.PORT}/health`);
      console.log(`   Auth endpoints: http://localhost:${env.PORT}/api/auth`);
      console.log(`   Access via frontend: ${env.FRONTEND_URL}/api/auth`);
      console.log(`   📧 Email from: ${env.EMAIL_FROM}`);
      console.log(`   📧 Resend API key: ${env.RESEND_API_KEY ? '✓ Set' : '✗ Missing'}`);
    });

    // Graceful shutdown
    process.on('SIGTERM', () => {
      console.log('SIGTERM received, shutting down gracefully');
      server.close(() => {
        console.log('Process terminated');
      });
    });

    process.on('SIGINT', () => {
      console.log('SIGINT received, shutting down gracefully');
      server.close(() => {
        console.log('Process terminated');
      });
    });
  } catch (error) {
    console.error('Failed to start server:', error);
    process.exit(1);
  }
}

startServer();