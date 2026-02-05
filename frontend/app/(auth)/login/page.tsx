"use client";

import { useState, useEffect, Suspense } from "react";
import Link from "next/link";
import { Mail, Lock, ArrowRight, Loader2, Eye, EyeOff, CheckCircle2 } from "lucide-react";
import { jwtSignIn } from "@/lib/jwt-auth-client";
import { useRouter, useSearchParams } from "next/navigation";

// Loading fallback component
function LoginLoading() {
  return (
    <div className="p-8 pt-0 flex items-center justify-center min-h-[400px]">
      <div className="text-center">
        <Loader2 className="w-8 h-8 text-indigo-600 animate-spin mx-auto mb-3" />
        <p className="text-sm text-slate-500">Loading...</p>
      </div>
    </div>
  );
}

// Main login form component that uses useSearchParams
function LoginForm() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const router = useRouter();
  const searchParams = useSearchParams();

  // Check for password reset success message
  useEffect(() => {
    if (searchParams.get('reset') === 'success') {
      setSuccessMessage('Your password has been reset successfully! Please log in with your new password.');
    }
  }, [searchParams]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      // Use JWT authentication
      await jwtSignIn({ email, password });
      // Sign-in successful, redirect to dashboard
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.message || "Failed to sign in");
      setIsLoading(false);
    }
  };

  return (
    <div className="p-8 pt-0">
      <h2 className="text-2xl font-bold text-slate-900 text-center mb-2">
        Welcome back
      </h2>
      <p className="text-slate-500 text-center mb-8 text-sm">
        Enter your details to access your workspace
      </p>

      {successMessage && (
        <div className="mb-6 p-4 bg-gradient-to-r from-emerald-50 to-teal-50 border border-emerald-200 rounded-xl animate-in fade-in slide-in-from-top-2 duration-300">
          <div className="flex items-start gap-3">
            <CheckCircle2 className="w-5 h-5 text-emerald-600 mt-0.5 flex-shrink-0" />
            <div>
              <p className="text-sm font-medium text-emerald-900 mb-1">Password Reset Complete</p>
              <p className="text-sm text-emerald-700 leading-relaxed">
                {successMessage}
              </p>
            </div>
          </div>
        </div>
      )}

      {error && (
        <div className="mb-4 p-3 text-sm text-red-500 bg-red-50 rounded-lg border border-red-200 text-center">
            {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Email Address</label>
          <div className="relative">
            <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-colors"
              placeholder="john@example.com"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Password</label>
          <div className="relative">
            <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
            <input
              type={showPassword ? "text" : "password"}
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full pl-10 pr-10 py-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-colors"
              placeholder="••••••••"
            />
            <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 focus:outline-none"
                aria-label={showPassword ? "Hide password" : "Show password"}
            >
                {showPassword ? (
                    <EyeOff className="w-5 h-5" />
                ) : (
                    <Eye className="w-5 h-5" />
                )}
            </button>
          </div>
          <div className="text-right mt-1">
            <Link
              href="/forgot-password"
              className="text-sm text-indigo-600 hover:text-indigo-500 transition-colors"
            >
              Forgot Password?
            </Link>
          </div>
        </div>

        <button
          type="submit"
          disabled={isLoading}
          className="w-full flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2.5 rounded-lg transition-all shadow-sm shadow-indigo-200 mt-6 disabled:opacity-70 disabled:cursor-not-allowed"
        >
          {isLoading ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : (
            <>
              Sign In
              <ArrowRight className="w-5 h-5" />
            </>
          )}
        </button>
      </form>

      <div className="mt-6 text-center">
        <p className="text-sm text-slate-600">
          Don&apos;t have an account?{" "}
          <Link
            href="/register"
            className="font-medium text-indigo-600 hover:text-indigo-500 transition-colors"
          >
            Sign up
          </Link>
        </p>
      </div>
    </div>
  );
}

// Default export with Suspense boundary
export default function LoginPage() {
  return (
    <Suspense fallback={<LoginLoading />}>
      <LoginForm />
    </Suspense>
  );
}
