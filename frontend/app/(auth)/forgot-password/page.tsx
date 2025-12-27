"use client";

import { useState } from "react";
import Link from "next/link";
import { Mail, ArrowRight, Loader2, ArrowLeft, CheckCircle2 } from "lucide-react";
import { authClient } from "@/lib/auth-client";
import { checkRateLimit, recordAttempt } from "@/lib/validation/rate-limit";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    setSuccessMessage(null);

    // Client-side rate limiting check
    const rateCheck = checkRateLimit(email);
    if (!rateCheck.allowed) {
      const minutes = Math.floor(rateCheck.remainingTime! / 60);
      const seconds = rateCheck.remainingTime! % 60;
      const timeString = minutes > 0
        ? `${minutes} minute${minutes > 1 ? 's' : ''} and ${seconds} second${seconds !== 1 ? 's' : ''}`
        : `${seconds} second${seconds !== 1 ? 's' : ''}`;

      setError(
        `Too many attempts. Please check your email or wait ${timeString} before trying again.`
      );
      setIsLoading(false);
      return;
    }

    // Call the password reset endpoint directly
    // Use the auth server base URL (configured in auth-client.ts)
    const baseURL = process.env.NODE_ENV === 'development'
      ? 'http://localhost:8080/api/auth'
      : `${window.location.origin}/api/auth`;

    try {
      const response = await fetch(`${baseURL}/request-password-reset`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          redirectTo: `${window.location.origin}/reset-password`,
        }),
        credentials: 'include',
      });

      setIsLoading(false);

      if (response.ok) {
        setSuccessMessage(
          "If an account with that email exists, we've sent a password reset link. Please check your inbox and spam folder."
        );
        // Record attempt for rate limiting
        recordAttempt(email);
        // Clear email field on success
        setEmail("");
      } else if (response.status === 429) {
        setError("Too many attempts. Please check your email or wait 5 minutes before trying again.");
      } else if (response.status === 503) {
        setError("Email service is temporarily unavailable. Please try again in a few moments.");
      } else {
        const data = await response.json().catch(() => ({}));
        setError(data.message || "Something went wrong. Please try again.");
      }
    } catch (error) {
      setIsLoading(false);
      if (!navigator.onLine) {
        setError("No internet connection. Please check your connection and try again.");
      } else {
        setError("Something went wrong. Please try again.");
      }
    }
  };

  return (
    <div className="p-8 pt-0">
      {/* Header with subtle entrance animation */}
      <div className="text-center mb-8 animate-in fade-in slide-in-from-top-4 duration-500">
        <div className="inline-flex items-center justify-center w-14 h-14 rounded-full bg-indigo-100 mb-4">
          <Mail className="w-7 h-7 text-indigo-600" />
        </div>
        <h2 className="text-2xl font-bold text-slate-900 mb-2">
          Forgot your password?
        </h2>
        <p className="text-slate-500 text-sm max-w-sm mx-auto leading-relaxed">
          No worries! Enter your email address and we&apos;ll send you a link to reset your password.
        </p>
      </div>

      {/* Success message with check icon */}
      {successMessage && (
        <div className="mb-6 p-4 bg-gradient-to-r from-emerald-50 to-teal-50 border border-emerald-200 rounded-xl animate-in fade-in slide-in-from-top-2 duration-300" role="alert" aria-live="polite">
          <div className="flex items-start gap-3">
            <CheckCircle2 className="w-5 h-5 text-emerald-600 mt-0.5 flex-shrink-0" aria-hidden="true" />
            <div>
              <p className="text-sm font-medium text-emerald-900 mb-1">Email sent!</p>
              <p className="text-sm text-emerald-700 leading-relaxed">
                {successMessage}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Error message */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl animate-in fade-in slide-in-from-top-2 duration-300" role="alert" aria-live="assertive">
          <p className="text-sm text-red-600 leading-relaxed">
            {error}
          </p>
        </div>
      )}

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-5 animate-in fade-in slide-in-from-bottom-4 duration-500 delay-100">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">
            Email Address
          </label>
          <div className="relative group">
            <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 transition-colors group-focus-within:text-indigo-500" />
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={isLoading}
              className="w-full pl-10 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent focus:bg-white transition-all disabled:opacity-60 disabled:cursor-not-allowed"
              placeholder="john@example.com"
            />
          </div>
        </div>

        <button
          type="submit"
          disabled={isLoading || !email}
          aria-busy={isLoading}
          className="w-full flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-700 active:bg-indigo-800 text-white font-medium py-3 rounded-xl transition-all shadow-lg shadow-indigo-200/50 hover:shadow-xl hover:shadow-indigo-300/50 disabled:opacity-60 disabled:cursor-not-allowed disabled:shadow-none disabled:hover:bg-indigo-600 group"
        >
          {isLoading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              <span>Sending reset link...</span>
            </>
          ) : (
            <>
              <span>Send Reset Link</span>
              <ArrowRight className="w-5 h-5 transition-transform group-hover:translate-x-0.5" />
            </>
          )}
        </button>
      </form>

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
