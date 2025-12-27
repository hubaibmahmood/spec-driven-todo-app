"use client";

import { useState, useEffect, Suspense } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Lock, Eye, EyeOff, Loader2, ArrowRight, ArrowLeft, ShieldCheck, AlertCircle, CheckCircle2 } from "lucide-react";
import { authClient } from "@/lib/auth-client";
import { validatePassword, validateTokenFormat, type PasswordValidation } from "@/lib/validation/password";

// Loading fallback component
function ResetPasswordLoading() {
  return (
    <div className="p-8 pt-0 flex items-center justify-center min-h-[400px]">
      <div className="text-center">
        <Loader2 className="w-8 h-8 text-indigo-600 animate-spin mx-auto mb-3" />
        <p className="text-sm text-slate-500">Loading...</p>
      </div>
    </div>
  );
}

// Main form component that uses useSearchParams
function ResetPasswordForm() {
  const searchParams = useSearchParams();
  const router = useRouter();

  // Token state
  const [token, setToken] = useState<string | null>(null);
  const [tokenError, setTokenError] = useState<string | null>(null);
  const [isTokenValidating, setIsTokenValidating] = useState(true);

  // Form state
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Validation state
  const [passwordValidation, setPasswordValidation] = useState<PasswordValidation | null>(null);
  const [passwordsMatch, setPasswordsMatch] = useState(true);

  // Extract and validate token on mount
  useEffect(() => {
    const tokenParam = searchParams.get('token');

    if (!tokenParam) {
      setTokenError('No reset token provided. Redirecting to forgot password...');
      setIsTokenValidating(false);
      // Auto-redirect after 3 seconds
      setTimeout(() => router.push('/forgot-password'), 3000);
      return;
    }

    // Basic token validation - just check it exists and has reasonable length
    // Server will do the real validation
    if (tokenParam.length < 10) {
      setTokenError('Invalid reset link format. Please request a new password reset.');
      setIsTokenValidating(false);
      return;
    }

    setToken(tokenParam);
    setIsTokenValidating(false);
  }, [searchParams, router]);

  // Real-time password validation
  useEffect(() => {
    if (newPassword.length > 0) {
      setPasswordValidation(validatePassword(newPassword));
    } else {
      setPasswordValidation(null);
    }
  }, [newPassword]);

  // Password match validation
  useEffect(() => {
    if (confirmPassword.length > 0) {
      setPasswordsMatch(newPassword === confirmPassword);
    } else {
      setPasswordsMatch(true);
    }
  }, [newPassword, confirmPassword]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!passwordValidation?.isValid) {
      setError("Please fix password validation errors");
      return;
    }

    if (!passwordsMatch) {
      setError("Passwords do not match");
      return;
    }

    setIsLoading(true);
    setError(null);

    await authClient.resetPassword(
      {
        newPassword,
        token: token!,
      },
      {
        onRequest: () => {
          setIsLoading(true);
        },
        onSuccess: async () => {
          // Check if user is logged in and sign out for security
          const session = await authClient.getSession();
          if (session) {
            await authClient.signOut();
          }

          setIsLoading(false);
          // Redirect to login with success message
          router.push('/login?reset=success');
        },
        onError: (ctx) => {
          setIsLoading(false);

          // Handle specific error cases
          if (ctx.error.message?.includes('expired')) {
            setError('This reset link has expired. Reset links are valid for 1 hour.');
          } else if (ctx.error.message?.includes('invalid') || ctx.error.message?.includes('not found')) {
            setError('This reset link is invalid. Please request a new password reset.');
          } else if (ctx.error.message?.includes('password')) {
            setError('Password does not meet security requirements.');
          } else if (!navigator.onLine) {
            setError('No internet connection. Please check your connection and try again.');
          } else {
            setError('Failed to reset password. Please try again.');
          }
        },
      }
    );
  };

  // Loading state while validating token
  if (isTokenValidating) {
    return (
      <div className="p-8 pt-0 flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <Loader2 className="w-8 h-8 text-indigo-600 animate-spin mx-auto mb-3" />
          <p className="text-sm text-slate-500">Validating reset link...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 pt-0">
      {/* Header with shield icon for security emphasis */}
      <div className="text-center mb-8 animate-in fade-in slide-in-from-top-4 duration-500">
        <div className="inline-flex items-center justify-center w-14 h-14 rounded-full bg-indigo-100 mb-4">
          <ShieldCheck className="w-7 h-7 text-indigo-600" />
        </div>
        <h2 className="text-2xl font-bold text-slate-900 mb-2">
          Set New Password
        </h2>
        <p className="text-slate-500 text-sm max-w-sm mx-auto leading-relaxed">
          Create a strong password to secure your account
        </p>
      </div>

      {/* Token error with auto-redirect message */}
      {tokenError && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl animate-in fade-in slide-in-from-top-2 duration-300" role="alert" aria-live="assertive">
          <div className="flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 mt-0.5 flex-shrink-0" aria-hidden="true" />
            <div className="flex-1">
              <p className="text-sm text-red-600 leading-relaxed mb-2">
                {tokenError}
              </p>
              {!tokenError.includes('Redirecting') && (
                <Link
                  href="/forgot-password"
                  className="text-sm font-medium text-red-700 hover:text-red-800 underline"
                >
                  Request New Reset Link →
                </Link>
              )}
            </div>
          </div>
        </div>
      )}

      {/* API error message */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl animate-in fade-in slide-in-from-top-2 duration-300" role="alert" aria-live="assertive">
          <div className="flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 mt-0.5 flex-shrink-0" aria-hidden="true" />
            <div className="flex-1">
              <p className="text-sm text-red-600 leading-relaxed mb-2">
                {error}
              </p>
              {(error.includes('expired') || error.includes('invalid')) && (
                <Link
                  href="/forgot-password"
                  className="text-sm font-medium text-red-700 hover:text-red-800 underline"
                >
                  Request New Reset Link →
                </Link>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Form - only show if token is valid */}
      {token && !tokenError && (
        <form onSubmit={handleSubmit} className="space-y-5 animate-in fade-in slide-in-from-bottom-4 duration-500 delay-100">
          {/* New Password Input */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              New Password
            </label>
            <div className="relative group">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 transition-colors group-focus-within:text-indigo-500" />
              <input
                type={showPassword ? "text" : "password"}
                required
                value={newPassword}
                onChange={(e) => {
                  setNewPassword(e.target.value);
                  setError(null);
                }}
                disabled={isLoading}
                className="w-full pl-10 pr-10 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent focus:bg-white transition-all disabled:opacity-60 disabled:cursor-not-allowed"
                placeholder="••••••••"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 focus:outline-none transition-colors"
                aria-label={showPassword ? "Hide password" : "Show password"}
              >
                {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
              </button>
            </div>

            {/* Password requirements - elegant grid layout */}
            {newPassword.length > 0 && passwordValidation && (
              <div className="mt-3 p-3 bg-slate-50 rounded-lg border border-slate-200">
                <p className="text-xs font-medium text-slate-600 mb-2">Password must contain:</p>
                <div className="grid grid-cols-2 gap-2">
                  <PasswordRequirement
                    met={newPassword.length >= 8}
                    text="8+ characters"
                  />
                  <PasswordRequirement
                    met={/[A-Z]/.test(newPassword)}
                    text="Uppercase letter"
                  />
                  <PasswordRequirement
                    met={/[a-z]/.test(newPassword)}
                    text="Lowercase letter"
                  />
                  <PasswordRequirement
                    met={/[0-9]/.test(newPassword)}
                    text="Number"
                  />
                  <PasswordRequirement
                    met={/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(newPassword)}
                    text="Special character"
                  />
                </div>
              </div>
            )}
          </div>

          {/* Confirm Password Input */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Confirm Password
            </label>
            <div className="relative group">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 transition-colors group-focus-within:text-indigo-500" />
              <input
                type={showConfirmPassword ? "text" : "password"}
                required
                value={confirmPassword}
                onChange={(e) => {
                  setConfirmPassword(e.target.value);
                  setError(null);
                }}
                disabled={isLoading}
                className={`w-full pl-10 pr-10 py-3 bg-slate-50 border rounded-xl text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:border-transparent focus:bg-white transition-all disabled:opacity-60 disabled:cursor-not-allowed ${
                  !passwordsMatch && confirmPassword.length > 0
                    ? 'border-red-300 focus:ring-red-500'
                    : 'border-slate-200 focus:ring-indigo-500'
                }`}
                placeholder="••••••••"
              />
              <button
                type="button"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 focus:outline-none transition-colors"
                aria-label={showConfirmPassword ? "Hide password" : "Show password"}
              >
                {showConfirmPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
              </button>
            </div>

            {/* Password match indicator */}
            {confirmPassword.length > 0 && (
              <div className="mt-2">
                {passwordsMatch ? (
                  <div className="flex items-center gap-2 text-emerald-600">
                    <CheckCircle2 className="w-4 h-4" />
                    <p className="text-xs font-medium">Passwords match</p>
                  </div>
                ) : (
                  <div className="flex items-center gap-2 text-red-600">
                    <AlertCircle className="w-4 h-4" />
                    <p className="text-xs font-medium">Passwords do not match</p>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Submit button */}
          <button
            type="submit"
            disabled={
              isLoading ||
              !passwordValidation?.isValid ||
              !passwordsMatch ||
              confirmPassword.length === 0
            }
            aria-busy={isLoading}
            className="w-full flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-700 active:bg-indigo-800 text-white font-medium py-3 rounded-xl transition-all shadow-lg shadow-indigo-200/50 hover:shadow-xl hover:shadow-indigo-300/50 disabled:opacity-60 disabled:cursor-not-allowed disabled:shadow-none disabled:hover:bg-indigo-600 group"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                <span>Resetting password...</span>
              </>
            ) : (
              <>
                <span>Reset Password</span>
                <ArrowRight className="w-5 h-5 transition-transform group-hover:translate-x-0.5" />
              </>
            )}
          </button>
        </form>
      )}

      {/* Back to login link */}
      <div className="mt-8 text-center animate-in fade-in duration-500 delay-200">
        <Link
          href="/login"
          className="inline-flex items-center gap-2 text-sm text-slate-600 hover:text-indigo-600 transition-colors group"
        >
          <ArrowLeft className="w-4 h-4 transition-transform group-hover:-translate-x-0.5" />
          <span>Back to Login</span>
        </Link>
      </div>

      {/* Subtle decorative element */}
      <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-slate-200 to-transparent opacity-50" />
    </div>
  );
}

// Password requirement indicator component
function PasswordRequirement({ met, text }: { met: boolean; text: string }) {
  return (
    <div className="flex items-center gap-1.5">
      <div className={`w-1.5 h-1.5 rounded-full transition-colors ${
        met ? 'bg-emerald-500' : 'bg-slate-300'
      }`} />
      <span className={`text-xs transition-colors ${
        met ? 'text-emerald-700 font-medium' : 'text-slate-500'
      }`}>
        {text}
      </span>
    </div>
  );
}

// Default export with Suspense boundary
export default function ResetPasswordPage() {
  return (
    <Suspense fallback={<ResetPasswordLoading />}>
      <ResetPasswordForm />
    </Suspense>
  );
}
