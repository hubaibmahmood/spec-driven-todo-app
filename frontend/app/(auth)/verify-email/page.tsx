"use client";

import { useState, Suspense } from "react";
import Link from "next/link";
import { Mail, CheckCircle, AlertCircle, CheckSquare } from "lucide-react";
import { useSearchParams } from "next/navigation";

function VerifyEmailContent() {
  const searchParams = useSearchParams();
  const email = searchParams.get("email");
  const [resendStatus, setResendStatus] = useState<"idle" | "sending" | "sent" | "error">("idle");

  const handleResendEmail = async () => {
    if (!email) return;

    setResendStatus("sending");
    try {
      // TODO: Implement resend verification email endpoint
      // For now, just simulate success
      await new Promise(resolve => setTimeout(resolve, 1000));
      setResendStatus("sent");
      setTimeout(() => setResendStatus("idle"), 3000);
    } catch (error) {
      setResendStatus("error");
      setTimeout(() => setResendStatus("idle"), 3000);
    }
  };

  return (
    <div className="min-h-screen font-sans text-slate-900 selection:bg-indigo-100 selection:text-indigo-700 overflow-x-hidden bg-gradient-to-br from-slate-50 via-white to-indigo-50/30">
      {/* Background Decor */}
      <div className="fixed inset-0 -z-10 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1200px] h-[800px] bg-gradient-to-br from-indigo-100/40 to-purple-100/40 rounded-[100%] blur-3xl"></div>
        <div className="absolute bottom-0 left-0 w-[800px] h-[600px] bg-gradient-to-tr from-blue-100/30 to-indigo-100/30 rounded-[100%] blur-3xl"></div>
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-[0.15] brightness-100 contrast-150"></div>
      </div>

      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 bg-white/80 backdrop-blur-md border-b border-slate-100 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
          <Link
            href="/"
            className="flex items-center gap-2.5 text-slate-900 font-bold text-2xl cursor-pointer"
          >
            <div className="bg-gradient-to-br from-indigo-600 to-indigo-700 text-white p-2 rounded-xl shadow-lg shadow-indigo-500/20">
              <CheckSquare className="w-5 h-5" />
            </div>
            <span className="tracking-tight">Momentum</span>
          </Link>
          <div className="flex items-center gap-4 sm:gap-8">
            <Link
              href="/login"
              className="text-sm font-semibold text-slate-600 hover:text-indigo-600 transition-colors"
            >
              Back to Login
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-28 pb-12 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
        <div className="text-center max-w-3xl mx-auto relative z-10">
          {/* Icon */}
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-indigo-500 to-indigo-600 rounded-2xl shadow-xl shadow-indigo-500/30 mb-6 mx-auto">
            <Mail className="w-8 h-8 text-white" />
          </div>

          {/* Title */}
          <h1 className="text-3xl sm:text-4xl md:text-5xl font-extrabold tracking-tight text-slate-900 mb-4 leading-tight">
            Check Your Email
          </h1>

          {/* Description */}
          <p className="text-base sm:text-lg text-slate-600 mb-8 leading-relaxed max-w-2xl mx-auto">
            {email ? (
              <>
                We've sent a verification link to{" "}
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-purple-600 font-bold">{email}</span>
              </>
            ) : (
              "We've sent a verification link to your email address"
            )}
          </p>

          {/* Instructions Card */}
          <div className="bg-white rounded-2xl border border-slate-200 shadow-lg p-6 mb-6 text-left max-w-2xl mx-auto">
            <h2 className="text-lg font-bold text-slate-900 mb-4 flex items-center">
              <div className="w-8 h-8 bg-indigo-100 rounded-lg flex items-center justify-center mr-2">
                <CheckCircle className="w-4 h-4 text-indigo-600" />
              </div>
              Next Steps:
            </h2>
            <div className="space-y-3">
              <div className="flex items-start gap-3">
                <div className="w-6 h-6 bg-indigo-600 text-white rounded-full flex items-center justify-center font-bold text-xs flex-shrink-0 mt-0.5">1</div>
                <p className="text-sm text-slate-700 leading-relaxed">Open your email inbox</p>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-6 h-6 bg-indigo-600 text-white rounded-full flex items-center justify-center font-bold text-xs flex-shrink-0 mt-0.5">2</div>
                <p className="text-sm text-slate-700 leading-relaxed">Click the verification link in the email</p>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-6 h-6 bg-indigo-600 text-white rounded-full flex items-center justify-center font-bold text-xs flex-shrink-0 mt-0.5">3</div>
                <p className="text-sm text-slate-700 leading-relaxed">You'll be redirected to the login page</p>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-6 h-6 bg-indigo-600 text-white rounded-full flex items-center justify-center font-bold text-xs flex-shrink-0 mt-0.5">4</div>
                <p className="text-sm text-slate-700 leading-relaxed">Sign in with your credentials</p>
              </div>
            </div>
          </div>

          {/* Resend Email */}
          <div className="mb-6">
            <p className="text-sm text-slate-600 mb-3 font-medium">
              Didn't receive the email?
            </p>
            <button
              onClick={handleResendEmail}
              disabled={resendStatus === "sending" || resendStatus === "sent"}
              className="px-6 py-2.5 bg-white hover:bg-indigo-50 text-indigo-600 font-semibold rounded-xl text-sm border-2 border-indigo-600 transition-all shadow-md hover:shadow-lg hover:-translate-y-0.5 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:translate-y-0"
            >
              {resendStatus === "sending" && "Sending..."}
              {resendStatus === "sent" && "✓ Email sent!"}
              {resendStatus === "error" && "Failed to send"}
              {resendStatus === "idle" && "Resend verification email"}
            </button>
          </div>

          {/* Warning */}
          <div className="bg-amber-50 border-2 border-amber-200 rounded-xl p-4 mb-6 max-w-2xl mx-auto">
            <div className="flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-amber-600 mt-0.5 flex-shrink-0" />
              <p className="text-sm text-slate-700 text-left leading-relaxed">
                <span className="font-semibold text-slate-900">Heads up!</span> The verification link will expire in 15 minutes.
                Check your spam folder if you don't see the email.
              </p>
            </div>
          </div>

          {/* Back to Login */}
          <Link
            href="/login"
            className="inline-flex items-center text-sm text-slate-600 hover:text-indigo-600 font-semibold transition-colors gap-1"
          >
            ← Back to login
          </Link>
        </div>
      </section>
    </div>
  );
}

export default function VerifyEmailPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen font-sans text-slate-900 selection:bg-indigo-100 selection:text-indigo-700 overflow-x-hidden bg-gradient-to-br from-slate-50 via-white to-indigo-50/30">
        <div className="fixed inset-0 -z-10 overflow-hidden pointer-events-none">
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1200px] h-[800px] bg-gradient-to-br from-indigo-100/40 to-purple-100/40 rounded-[100%] blur-3xl"></div>
          <div className="absolute bottom-0 left-0 w-[800px] h-[600px] bg-gradient-to-tr from-blue-100/30 to-indigo-100/30 rounded-[100%] blur-3xl"></div>
          <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-[0.15] brightness-100 contrast-150"></div>
        </div>
        <nav className="fixed top-0 left-0 right-0 bg-white/80 backdrop-blur-md border-b border-slate-100 z-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
            <Link
              href="/"
              className="flex items-center gap-2.5 text-slate-900 font-bold text-2xl cursor-pointer"
            >
              <div className="bg-gradient-to-br from-indigo-600 to-indigo-700 text-white p-2 rounded-xl shadow-lg shadow-indigo-500/20">
                <CheckSquare className="w-5 h-5" />
              </div>
              <span className="tracking-tight">Momentum</span>
            </Link>
            <div className="flex items-center gap-4 sm:gap-8">
              <Link
                href="/login"
                className="text-sm font-semibold text-slate-600 hover:text-indigo-600 transition-colors"
              >
                Back to Login
              </Link>
            </div>
          </div>
        </nav>
        <section className="pt-28 pb-12 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
          <div className="text-center max-w-3xl mx-auto relative z-10">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-indigo-500 to-indigo-600 rounded-2xl shadow-xl shadow-indigo-500/30 mb-6 mx-auto animate-pulse">
              <Mail className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-3xl sm:text-4xl md:text-5xl font-extrabold tracking-tight text-slate-900 mb-4 leading-tight">Loading...</h1>
          </div>
        </section>
      </div>
    }>
      <VerifyEmailContent />
    </Suspense>
  );
}
