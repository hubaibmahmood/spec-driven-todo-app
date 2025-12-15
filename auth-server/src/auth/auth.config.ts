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
    // BaseURL should point to the frontend URL because auth requests are proxied
    // Frontend proxies /api/auth/* to this auth server (via Netlify redirects)
    // Cookies are set for the frontend domain, enabling same-origin authentication
    baseURL: `${env.FRONTEND_URL}/api/auth`,

    // Trusted origins for CORS (where requests can come from)
    trustedOrigins: env.CORS_ORIGINS.split(",").map((origin: string) =>
      origin.trim(),
    ),

    // Session settings with custom schema to match FastAPI expectations
    session: {
      expiresIn: 7 * 24 * 60 * 60, // 7 days
      updateAge: 24 * 60 * 60, // 24 hours
      cookieCache: {
        enabled: true,
        maxAge: 5 * 60, // 5 minutes
      },
    },

    // Cookie configuration for same-origin requests (via proxy)
    // Since auth requests are proxied through frontend domain, cookies are first-party
    cookies: {
      sessionToken: {
        name: "better-auth.session_token",
        options: {
          httpOnly: true,
          sameSite: "lax", // Safe for same-origin cookies
          secure: process.env.NODE_ENV === "production", // true in production (HTTPS required)
          path: "/",
        },
      },
    },

    // Email and password authentication (this is a core config, not a plugin import)
    emailAndPassword: {
      enabled: true,
      requireEmailVerification: true,
      minPasswordLength: 8,
      sendResetPassword: async ({
        user,
        url,
        token,
      }: {
        user: any;
        url: string;
        token: string;
      }) => {
        try {
          // Manually save the reset token to the database with type 'reset-password'
          const expiresAt = new Date(
            Date.now() + resetPasswordTokenExpiresIn * 1000,
          );
          await prisma.verification.create({
            data: {
              identifier: user.email,
              value: token,
              userId: user.id,
              expiresAt: expiresAt,
              type: "reset-password",
            },
          });

          // In development, log the reset link to console
          if (process.env.NODE_ENV === "development") {
            console.log("\n=================================");
            console.log("🔐 PASSWORD RESET LINK");
            console.log("=================================");
            console.log("To:", user.email);
            console.log("Link:", url);
            console.log("=================================\n");
          }

          const result = await resend.emails.send({
            from: env.EMAIL_FROM,
            to: user.email,
            subject: "Reset your password",
            html: `
              <!DOCTYPE html>
              <html lang="en">
              <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Reset Your Password</title>
              </head>
              <body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #f3f4f6;">
                <table role="presentation" style="width: 100%; border-collapse: collapse; background-color: #f3f4f6; padding: 40px 0;">
                  <tr>
                    <td align="center" style="padding: 0;">
                      <!-- Main Container -->
                      <table role="presentation" style="width: 600px; max-width: 100%; border-collapse: collapse; background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);">

                        <!-- Header -->
                        <tr>
                          <td style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 40px 30px; text-align: center; border-radius: 8px 8px 0 0;">
                            <div style="width: 64px; height: 64px; margin: 0 auto 16px; background-color: rgba(255, 255, 255, 0.2); border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                                <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
                              </svg>
                            </div>
                            <h1 style="margin: 0; color: #ffffff; font-size: 28px; font-weight: 700; letter-spacing: -0.5px;">
                              Reset Your Password
                            </h1>
                          </td>
                        </tr>

                        <!-- Content -->
                        <tr>
                          <td style="padding: 40px;">
                            <p style="margin: 0 0 16px; color: #111827; font-size: 16px; line-height: 1.6;">
                              Hi ${user.name || "there"},
                            </p>
                            <p style="margin: 0 0 24px; color: #4b5563; font-size: 16px; line-height: 1.6;">
                              We received a request to reset the password for your account. Click the button below to create a new password.
                            </p>

                            <!-- CTA Button -->
                            <table role="presentation" style="width: 100%; border-collapse: collapse; margin: 32px 0;">
                              <tr>
                                <td align="center">
                                  <a href="${url}" style="display: inline-block; padding: 16px 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #ffffff; text-decoration: none; border-radius: 6px; font-weight: 600; font-size: 16px; box-shadow: 0 4px 6px rgba(102, 126, 234, 0.4); transition: all 0.3s ease;">
                                    Reset Password
                                  </a>
                                </td>
                              </tr>
                            </table>

                            <!-- Alternative Link -->
                            <p style="margin: 24px 0 0; color: #6b7280; font-size: 14px; line-height: 1.6;">
                              Or copy and paste this link into your browser:
                            </p>
                            <p style="margin: 8px 0 0; padding: 12px; background-color: #f9fafb; border: 1px solid #e5e7eb; border-radius: 4px; word-break: break-all; font-size: 13px; color: #4b5563;">
                              ${url}
                            </p>

                            <!-- Expiration Notice -->
                            <table role="presentation" style="width: 100%; border-collapse: collapse; margin: 32px 0 0; padding: 16px; background-color: #fef3c7; border-left: 4px solid #f59e0b; border-radius: 4px;">
                              <tr>
                                <td>
                                  <p style="margin: 0; color: #92400e; font-size: 14px; line-height: 1.5;">
                                    ⏰ <strong>This link will expire in 1 hour</strong> for security reasons.
                                  </p>
                                </td>
                              </tr>
                            </table>

                            <!-- Security Notice -->
                            <table role="presentation" style="width: 100%; border-collapse: collapse; margin: 24px 0 0; padding: 16px; background-color: #fee2e2; border-left: 4px solid #ef4444; border-radius: 4px;">
                              <tr>
                                <td>
                                  <p style="margin: 0 0 8px; color: #991b1b; font-size: 14px; line-height: 1.5; font-weight: 600;">
                                    ⚠️ Security Alert
                                  </p>
                                  <p style="margin: 0; color: #991b1b; font-size: 13px; line-height: 1.5;">
                                    If you didn't request a password reset, please ignore this email. Your password will remain unchanged. Consider securing your account if you didn't make this request.
                                  </p>
                                </td>
                              </tr>
                            </table>
                          </td>
                        </tr>

                        <!-- Footer -->
                        <tr>
                          <td style="padding: 32px 40px; border-top: 1px solid #e5e7eb; background-color: #f9fafb; border-radius: 0 0 8px 8px;">
                            <p style="margin: 0 0 8px; color: #6b7280; font-size: 12px; line-height: 1.5; text-align: center;">
                              This is an automated email. Please do not reply to this message.
                            </p>
                            <p style="margin: 0; color: #9ca3af; font-size: 12px; line-height: 1.5; text-align: center;">
                              © ${new Date().getFullYear()} Todo App. All rights reserved.
                            </p>
                          </td>
                        </tr>

                      </table>
                    </td>
                  </tr>
                </table>
              </body>
              </html>
            `,
          });
        } catch (error) {
          console.error("[Email] Failed to send password reset email:", error);
          if (error instanceof Error) {
            console.error("[Email] Error details:", error.message);
          }
        }
      },
      resetPasswordTokenExpiresIn,
    },

    // Social providers
    socialProviders: {}, // No social providers needed for now

    // Email service configuration (top-level config for email sending)
    emailVerification: {
      sendVerificationEmail: async ({
        user,
        url,
        token,
      }: {
        user: any;
        url: string;
        token: string;
      }) => {
        try {
          // Manually save the verification token to the database
          const expiresAt = new Date(
            Date.now() + emailVerificationTokenExpiresIn * 1000,
          );
          await prisma.verification.create({
            data: {
              identifier: user.email,
              value: token,
              userId: user.id,
              expiresAt: expiresAt,
              type: "email-verification",
            },
          });

          // Replace the default callbackURL with our custom one
          // better-auth adds a default callbackURL=/, so we need to replace it
          const callbackUrl = `${env.FRONTEND_URL}/email-verified?verified=true`;
          const urlObj = new URL(url);
          urlObj.searchParams.set("callbackURL", callbackUrl);
          const verificationUrl = urlObj.toString();

          // In development, log the verification link to console
          if (process.env.NODE_ENV === "development") {
            console.log("\n=================================");
            console.log("📧 EMAIL VERIFICATION LINK");
            console.log("=================================");
            console.log("To:", user.email);
            console.log("Link:", verificationUrl);
            console.log("=================================\n");
          }

          const result = await resend.emails.send({
            from: env.EMAIL_FROM,
            to: user.email,
            subject: "Verify your email address",
            html: `
              <!DOCTYPE html>
              <html lang="en">
              <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Verify Your Email</title>
              </head>
              <body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #f3f4f6;">
                <table role="presentation" style="width: 100%; border-collapse: collapse; background-color: #f3f4f6; padding: 40px 0;">
                  <tr>
                    <td align="center" style="padding: 0;">
                      <!-- Main Container -->
                      <table role="presentation" style="width: 600px; max-width: 100%; border-collapse: collapse; background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);">

                        <!-- Header -->
                        <tr>
                          <td style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 40px 30px; text-align: center; border-radius: 8px 8px 0 0;">
                            <div style="width: 64px; height: 64px; margin: 0 auto 16px; background-color: rgba(255, 255, 255, 0.2); border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
                                <polyline points="22,6 12,13 2,6"></polyline>
                              </svg>
                            </div>
                            <h1 style="margin: 0; color: #ffffff; font-size: 28px; font-weight: 700; letter-spacing: -0.5px;">
                              Verify Your Email
                            </h1>
                          </td>
                        </tr>

                        <!-- Content -->
                        <tr>
                          <td style="padding: 40px;">
                            <p style="margin: 0 0 16px; color: #111827; font-size: 16px; line-height: 1.6;">
                              Hi ${user.name || "there"},
                            </p>
                            <p style="margin: 0 0 24px; color: #4b5563; font-size: 16px; line-height: 1.6;">
                              Thank you for creating an account! To get started, please verify your email address by clicking the button below.
                            </p>

                            <!-- CTA Button -->
                            <table role="presentation" style="width: 100%; border-collapse: collapse; margin: 32px 0;">
                              <tr>
                                <td align="center">
                                  <a href="${verificationUrl}" style="display: inline-block; padding: 16px 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #ffffff; text-decoration: none; border-radius: 6px; font-weight: 600; font-size: 16px; box-shadow: 0 4px 6px rgba(102, 126, 234, 0.4); transition: all 0.3s ease;">
                                    Verify Email Address
                                  </a>
                                </td>
                              </tr>
                            </table>

                            <!-- Alternative Link -->
                            <p style="margin: 24px 0 0; color: #6b7280; font-size: 14px; line-height: 1.6;">
                              Or copy and paste this link into your browser:
                            </p>
                            <p style="margin: 8px 0 0; padding: 12px; background-color: #f9fafb; border: 1px solid #e5e7eb; border-radius: 4px; word-break: break-all; font-size: 13px; color: #4b5563;">
                              ${verificationUrl}
                            </p>

                            <!-- Expiration Notice -->
                            <table role="presentation" style="width: 100%; border-collapse: collapse; margin: 32px 0 0; padding: 16px; background-color: #fef3c7; border-left: 4px solid #f59e0b; border-radius: 4px;">
                              <tr>
                                <td>
                                  <p style="margin: 0; color: #92400e; font-size: 14px; line-height: 1.5;">
                                    ⏰ <strong>This link will expire in 15 minutes</strong> for security reasons.
                                  </p>
                                </td>
                              </tr>
                            </table>

                            <!-- Security Notice -->
                            <p style="margin: 24px 0 0; padding: 16px; background-color: #f3f4f6; border-radius: 4px; color: #6b7280; font-size: 13px; line-height: 1.6;">
                              If you didn't create an account, you can safely ignore this email. No account will be created without verification.
                            </p>
                          </td>
                        </tr>

                        <!-- Footer -->
                        <tr>
                          <td style="padding: 32px 40px; border-top: 1px solid #e5e7eb; background-color: #f9fafb; border-radius: 0 0 8px 8px;">
                            <p style="margin: 0 0 8px; color: #6b7280; font-size: 12px; line-height: 1.5; text-align: center;">
                              This is an automated email. Please do not reply to this message.
                            </p>
                            <p style="margin: 0; color: #9ca3af; font-size: 12px; line-height: 1.5; text-align: center;">
                              © ${new Date().getFullYear()} Todo App. All rights reserved.
                            </p>
                          </td>
                        </tr>

                      </table>
                    </td>
                  </tr>
                </table>
              </body>
              </html>
            `,
          });
        } catch (error) {
          console.error("[Email] Failed to send verification email:", error);
          // Don't throw - better-auth will handle it, but log for debugging
          if (error instanceof Error) {
            console.error("[Email] Error details:", error.message);
          }
        }
      },
      sendOnSignUp: true,
      emailVerificationTokenExpiresIn,
    },
    advanced: {
      // Disable origin check in development to allow cross-origin requests from Next.js frontend
      // In production, this should be removed/commented to enable CSRF protection
      disableOriginCheck: process.env.NODE_ENV === "development",
    },
  };
}
