import { prismaAdapter } from "better-auth/adapters/prisma";
import { prisma } from "../database/client.js";
import { resend } from "../utils/resend.js";
import { env } from "../config/env.js";
import { boolean, string, date } from "zod";

// Lazy authConfig to prevent eager evaluation at module load
export function getAuthConfig() {
  const resetPasswordTokenExpiresIn = 60 * 60; // 1 hour
  const emailVerificationTokenExpiresIn = 15 * 60; // 15 minutes

  return {
    database: prismaAdapter(prisma, {
      provider: "postgresql",
    }),
    secret: env.BETTER_AUTH_SECRET,
    // BaseURL should include the full path where better-auth is publicly accessible
    // The frontend proxies /api/auth/* to the auth server
    baseURL: process.env.NODE_ENV === 'production'
      ? `${process.env.FRONTEND_URL}/api/auth`
      : `${env.FRONTEND_URL}/api/auth`,

    // Trusted origins for CORS (where requests can come from)
    trustedOrigins: env.CORS_ORIGINS.split(',').map((origin: string) => origin.trim()),

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
        console.log('[Email] Sending password reset email to:', user.email);

        try {
          // Manually save the reset token to the database with type 'reset-password'
          const expiresAt = new Date(Date.now() + resetPasswordTokenExpiresIn * 1000);
          await prisma.verification.create({
            data: {
              identifier: user.email,
              value: token,
              userId: user.id,
              expiresAt: expiresAt,
              type: "reset-password",
            },
          });

          console.log('[Email] Password reset token saved to database');
          console.log('[Email] Reset URL:', url);

          // In development, log the reset link to console
          if (process.env.NODE_ENV === 'development') {
            console.log('\n=================================');
            console.log('🔐 PASSWORD RESET LINK');
            console.log('=================================');
            console.log('To:', user.email);
            console.log('Link:', url);
            console.log('=================================\n');
          }

          const result = await resend.emails.send({
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

          console.log('[Email] Password reset email sent successfully:', result);
        } catch (error) {
          console.error('[Email] Failed to send password reset email:', error);
          if (error instanceof Error) {
            console.error('[Email] Error details:', error.message);
          }
        }
      },
      resetPasswordTokenExpiresIn,
    },

    // Social providers
    socialProviders: {}, // No social providers needed for now

    // Email service configuration (top-level config for email sending)
    emailVerification: {
      sendVerificationEmail: async ({ user, url, token }: { user: any; url: string; token: string }) => {
        console.log('[Email] Sending verification email to:', user.email);

        try {
          // Manually save the verification token to the database
          const expiresAt = new Date(Date.now() + emailVerificationTokenExpiresIn * 1000);
          await prisma.verification.create({
            data: {
              identifier: user.email,
              value: token,
              userId: user.id,
              expiresAt: expiresAt,
              type: "email-verification",
            },
          });

          console.log('[Email] Verification token saved to database');
          console.log('[Email] Verification URL:', url);

          // In development, log the verification link to console
          if (process.env.NODE_ENV === 'development') {
            console.log('\n=================================');
            console.log('📧 EMAIL VERIFICATION LINK');
            console.log('=================================');
            console.log('To:', user.email);
            console.log('Link:', url);
            console.log('=================================\n');
          }

          const result = await resend.emails.send({
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

          console.log('[Email] Verification email sent successfully:', result);
        } catch (error) {
          console.error('[Email] Failed to send verification email:', error);
          // Don't throw - better-auth will handle it, but log for debugging
          if (error instanceof Error) {
            console.error('[Email] Error details:', error.message);
          }
        }
      },
      sendOnSignUp: true,
      emailVerificationTokenExpiresIn,
    },
    advanced: {
      // Disable origin check in development to allow cross-origin requests from Next.js frontend
      // In production, this should be removed/commented to enable CSRF protection
      disableOriginCheck: process.env.NODE_ENV === 'development',
    },
  };
}
