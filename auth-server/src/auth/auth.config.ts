import { prismaAdapter } from "better-auth/adapters/prisma";
import { prisma } from "../database/client";
import { resend } from "../utils/resend";
import { env } from "../config/env";
import { boolean, string, date } from "zod";

export const authConfig = {
  database: prismaAdapter(prisma, {
    provider: "postgresql",
  }),
  secret: env.BETTER_AUTH_SECRET,
  baseURL: process.env.NODE_ENV === 'production'
    ? process.env.FRONTEND_URL
    : `http://localhost:${env.PORT}`,

  // Trusted origins for CORS (where requests can come from)
  trustedOrigins: env.CORS_ORIGINS.split(',').map(origin => origin.trim()),

  // Session settings with custom schema to match FastAPI expectations
  session: {
    expiresIn: 7 * 24 * 60 * 60, // 7 days
    updateAge: 24 * 60 * 60, // 24 hours
    cookieCache: {
      enabled: true,
      maxAge: 5 * 60, // 5 minutes
    },
  },

  // Email and password authentication (this is a core config, not a plugin import)
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: true,
    minPasswordLength: 8,
    sendResetPassword: async ({ user, url, token }: { user: any; url: string; token: string }) => {
      // Manually save the reset token to the database with type 'reset-password'
      const expiresAt = new Date(Date.now() + (authConfig.emailAndPassword.resetPasswordTokenExpiresIn || 3600) * 1000);
      await prisma.verification.create({
        data: {
          identifier: user.email,
          value: token,
          userId: user.id,
          expiresAt: expiresAt,
          type: "reset-password",
        },
      });

      await resend.emails.send({
        from: env.EMAIL_FROM,
        to: user.email,
        subject: "Reset your password",
        html: `
          <h2>Password Reset</h2>
          <p>You requested to reset your password. Click the link below to continue:</p>
          <a href="${url}">Reset Password</a>
          <p>This link will expire in 1 hour.</p>
          <p>If you didn't request this, please ignore this email.</p>
        `,
      });
    },
    resetPasswordTokenExpiresIn: 60 * 60, // 1 hour
  },

  // Social providers
  socialProviders: {}, // No social providers needed for now

  // Email service configuration (top-level config for email sending)
  emailVerification: {
    sendVerificationEmail: async ({ user, url, token }: { user: any; url: string; token: string }) => {
      // Manually save the verification token to the database
      const expiresAt = new Date(Date.now() + authConfig.emailVerification.emailVerificationTokenExpiresIn * 1000);
      await prisma.verification.create({
        data: {
          identifier: user.email,
          value: token,
          userId: user.id,
          expiresAt: expiresAt,
          type: "email-verification",
        },
      });

      await resend.emails.send({
        from: env.EMAIL_FROM,
        to: user.email,
        subject: "Verify your email address",
        html: `
          <h2>Email Verification</h2>
          <p>Please click the link below to verify your email address:</p>
          <a href="${url}">Verify Email</a>
          <p>This link will expire in 15 minutes.</p>
          <p>If you didn't request this, please ignore this email.</p>
        `,
      });
    },
    sendOnSignUp: true, // <--- Add this line
    emailVerificationTokenExpiresIn: 15 * 60, // 15 minutes
  },
  advanced: {
    // Disable origin check in development to allow cross-origin requests from Next.js frontend
    // In production, this should be removed/commented to enable CSRF protection
    disableOriginCheck: process.env.NODE_ENV === 'development',
  },
};