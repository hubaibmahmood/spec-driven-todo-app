import 'dotenv/config';
import { env } from './config/env';
import app from './app';

async function startServer() {
  try {
    const server = app.listen(env.PORT, () => {
      console.log(`🚀 Auth server running on port ${env.PORT}`);
      console.log(`   Environment: ${env.NODE_ENV}`);
      console.log(`   Health check: http://localhost:${env.PORT}/health`);
      console.log(`   Auth endpoints: http://localhost:${env.PORT}/api/auth`);
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