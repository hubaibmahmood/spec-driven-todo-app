"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Mail, Lock, User, ArrowRight, Loader2, Eye, EyeOff } from "lucide-react";
import { signUp } from "@/lib/auth-client";
import { useRouter } from "next/navigation";
import { validatePassword, type PasswordValidation } from "@/lib/validation/password";

export default function RegisterPage() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [passwordValidation, setPasswordValidation] = useState<PasswordValidation | null>(null);
  const router = useRouter();

  // Real-time password validation
  useEffect(() => {
    if (password.length > 0) {
      setPasswordValidation(validatePassword(password));
    } else {
      setPasswordValidation(null);
    }
  }, [password]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    await signUp.email({
      email,
      password,
      name,
      fetchOptions: {
        onSuccess: () => {
             // Redirect to verification pending page (no email in URL for security)
             router.push('/verify-email');
        },
        onError: (ctx) => {
             setError(ctx.error.message);
             setIsLoading(false);
        }
      }
    });
  };

  return (
    <div className="p-8 pt-0">
      <h2 className="text-2xl font-bold text-slate-900 text-center mb-2">
        Create an account
      </h2>
      <p className="text-slate-500 text-center mb-8 text-sm">
        Get started with your free account today
      </p>

      {error && (
        <div className="mb-4 p-3 text-sm text-red-500 bg-red-50 rounded-lg border border-red-200 text-center">
            {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Full Name</label>
          <div className="relative">
            <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
            <input
              type="text"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-colors"
              placeholder="John Doe"
            />
          </div>
        </div>

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

          {/* Password requirements - elegant grid layout */}
          {password.length > 0 && passwordValidation && (
            <div className="mt-3 p-3 bg-slate-50 rounded-lg border border-slate-200">
              <p className="text-xs font-medium text-slate-600 mb-2">Password must contain:</p>
              <div className="grid grid-cols-2 gap-2">
                <PasswordRequirement
                  met={password.length >= 8}
                  text="8+ characters"
                />
                <PasswordRequirement
                  met={/[A-Z]/.test(password)}
                  text="Uppercase letter"
                />
                <PasswordRequirement
                  met={/[a-z]/.test(password)}
                  text="Lowercase letter"
                />
                <PasswordRequirement
                  met={/[0-9]/.test(password)}
                  text="Number"
                />
                <PasswordRequirement
                  met={/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password)}
                  text="Special character"
                />
              </div>
            </div>
          )}
        </div>

        <button
          type="submit"
          disabled={isLoading || (password.length > 0 && !passwordValidation?.isValid)}
          className="w-full flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2.5 rounded-lg transition-all shadow-sm shadow-indigo-200 mt-6 disabled:opacity-70 disabled:cursor-not-allowed"
          aria-busy={isLoading}
        >
          {isLoading ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : (
            <>
              Create Account
              <ArrowRight className="w-5 h-5" />
            </>
          )}
        </button>
      </form>

      <div className="mt-6 text-center">
        <p className="text-sm text-slate-600">
          Already have an account?{" "}
          <Link
            href="/login"
            className="font-medium text-indigo-600 hover:text-indigo-500 transition-colors"
          >
            Sign in
          </Link>
        </p>
      </div>
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
