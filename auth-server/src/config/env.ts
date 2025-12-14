export interface Env {
  // Database
  DATABASE_URL: string;

  // Application
  NODE_ENV: 'development' | 'production' | 'test';
  PORT: number;

  // Auth
  BETTER_AUTH_SECRET: string;

  // CORS
  CORS_ORIGINS: string;

  // Email
  RESEND_API_KEY: string;
  EMAIL_FROM: string;

  // Frontend
  FRONTEND_URL: string;
}

export function validateEnv(): Env {
  const requiredEnvVars = [
    'DATABASE_URL',
    'BETTER_AUTH_SECRET',
    'RESEND_API_KEY',
    'EMAIL_FROM',
    'FRONTEND_URL'
  ];

  const missingEnvVars = requiredEnvVars.filter(envVar => !process.env[envVar]);

  if (missingEnvVars.length > 0) {
    const errorMessage = `❌ Missing required environment variables: ${missingEnvVars.join(', ')}`;
    console.error(errorMessage);
    throw new Error(errorMessage);
  }

  return {
    DATABASE_URL: process.env.DATABASE_URL!,
    NODE_ENV: (process.env.NODE_ENV as 'development' | 'production' | 'test') || 'development',
    PORT: parseInt(process.env.PORT || '8080', 10),
    BETTER_AUTH_SECRET: process.env.BETTER_AUTH_SECRET!,
    CORS_ORIGINS: process.env.CORS_ORIGINS || 'http://localhost:3000,http://localhost:8000',
    RESEND_API_KEY: process.env.RESEND_API_KEY!,
    EMAIL_FROM: process.env.EMAIL_FROM!,
    FRONTEND_URL: process.env.FRONTEND_URL!,
  };
}

export const env = validateEnv();