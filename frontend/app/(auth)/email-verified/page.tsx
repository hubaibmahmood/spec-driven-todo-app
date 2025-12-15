"use client";

import { useEffect, useState, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { CheckCircle, XCircle, Loader2, CheckSquare } from "lucide-react";
import Link from "next/link";

type VerificationStatus = "verifying" | "success" | "error" | "already-verified";

function EmailVerifiedContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [status, setStatus] = useState<VerificationStatus>("verifying");
  const [errorMessage, setErrorMessage] = useState<string>("");
  const [countdown, setCountdown] = useState(5);

  useEffect(() => {
    // Check if verification was successful from URL params
    const error = searchParams.get("error");
    const verified = searchParams.get("verified");

    if (error) {
      setStatus("error");
      setErrorMessage(error === "token-expired"
        ? "Verification link has expired. Please request a new one."
        : "Invalid or expired verification link."
      );
    } else if (verified === "true") {
      setStatus("success");
    } else if (verified === "already") {
      setStatus("already-verified");
    } else {
      // Simulate verification process if status not in URL
      setTimeout(() => {
        setStatus("success");
      }, 1500);
    }
  }, [searchParams]);

  useEffect(() => {
    // Countdown timer for successful verification
    if (status === "success" || status === "already-verified") {
      const timer = setInterval(() => {
        setCountdown((prev) => {
          if (prev <= 1) {
            clearInterval(timer);
            return 0;
          }
          return prev - 1;
        });
      }, 1000);

      return () => clearInterval(timer);
    }
  }, [status]);

  useEffect(() => {
    // Redirect when countdown reaches 0
    if ((status === "success" || status === "already-verified") && countdown === 0) {
      router.push("/login");
    }
  }, [countdown, status, router]);

  return (
    <div className="min-h-screen bg-white font-sans text-slate-900 selection:bg-indigo-100 selection:text-indigo-700 overflow-x-hidden">
      {/* Background Decor */}
      <div className="fixed inset-0 -z-10 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[600px] bg-indigo-50/50 rounded-[100%] blur-3xl opacity-50 mix-blend-multiply"></div>
        <div className="absolute top-[20%] right-0 w-[800px] h-[600px] bg-purple-50/50 rounded-[100%] blur-3xl opacity-50 mix-blend-multiply"></div>
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-10 brightness-100 contrast-150"></div>
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
              Go to Login
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-16 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
        <div className="text-center max-w-4xl mx-auto relative z-10">
          {/* Verifying State */}
          {status === "verifying" && (
            <>
              <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-blue-500 to-blue-600 rounded-3xl shadow-2xl shadow-blue-500/40 mb-10 mx-auto animate-pulse">
                <Loader2 className="w-10 h-10 text-white animate-spin" />
              </div>
              <h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold tracking-tight text-slate-900 mb-6 leading-[1.1]">
                Verifying Your Email
              </h1>
              <p className="text-lg sm:text-xl text-slate-600 leading-relaxed max-w-3xl mx-auto font-medium">
                Please wait while we verify your email address...
              </p>
            </>
          )}

          {/* Success State */}
          {status === "success" && (
            <>
              <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-3xl shadow-2xl shadow-emerald-500/40 mb-10 mx-auto">
                <CheckCircle className="w-10 h-10 text-white" />
              </div>
              <h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold tracking-tight text-slate-900 mb-6 leading-[1.1]">
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-600 to-green-600">
                  Email Verified!
                </span>
              </h1>
              <p className="text-lg sm:text-xl text-slate-600 mb-12 leading-relaxed max-w-3xl mx-auto font-medium">
                Your email address has been verified. You can now sign in to your account.
              </p>

              {/* Auto-redirect message */}
              <div className="bg-emerald-50 border-2 border-emerald-200 rounded-2xl p-5 mb-10 max-w-2xl mx-auto">
                <p className="text-base text-slate-700 leading-relaxed">
                  Redirecting to login page in{" "}
                  <span className="font-bold text-emerald-700 text-xl">{countdown}</span>{" "}
                  {countdown === 1 ? "second" : "seconds"}...
                </p>
              </div>

              {/* Manual login link */}
              <Link
                href="/login"
                className="inline-flex items-center justify-center px-7 py-3.5 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-2xl text-base transition-all shadow-xl shadow-indigo-500/30 hover:shadow-2xl hover:-translate-y-1"
              >
                Continue to Login
              </Link>
            </>
          )}

          {/* Already Verified State */}
          {status === "already-verified" && (
            <>
              <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-blue-500 to-blue-600 rounded-3xl shadow-2xl shadow-blue-500/40 mb-10 mx-auto">
                <CheckCircle className="w-10 h-10 text-white" />
              </div>
              <h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold tracking-tight text-slate-900 mb-6 leading-[1.1]">
                Already Verified
              </h1>
              <p className="text-lg sm:text-xl text-slate-600 mb-12 leading-relaxed max-w-3xl mx-auto font-medium">
                Your email address has already been verified. You can sign in to your account.
              </p>

              {/* Auto-redirect message */}
              <div className="bg-blue-50 border-2 border-blue-200 rounded-2xl p-5 mb-10 max-w-2xl mx-auto">
                <p className="text-base text-slate-700 leading-relaxed">
                  Redirecting to login page in{" "}
                  <span className="font-bold text-blue-700 text-xl">{countdown}</span>{" "}
                  {countdown === 1 ? "second" : "seconds"}...
                </p>
              </div>

              {/* Manual login link */}
              <Link
                href="/login"
                className="inline-flex items-center justify-center px-7 py-3.5 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-2xl text-base transition-all shadow-xl shadow-indigo-500/30 hover:shadow-2xl hover:-translate-y-1"
              >
                Continue to Login
              </Link>
            </>
          )}

          {/* Error State */}
          {status === "error" && (
            <>
              <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-red-500 to-red-600 rounded-3xl shadow-2xl shadow-red-500/40 mb-10 mx-auto">
                <XCircle className="w-10 h-10 text-white" />
              </div>
              <h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold tracking-tight text-slate-900 mb-6 leading-[1.1]">
                Verification Failed
              </h1>
              <p className="text-lg sm:text-xl text-slate-600 mb-12 leading-relaxed max-w-3xl mx-auto font-medium">
                {errorMessage || "We couldn't verify your email address. The link may be invalid or expired."}
              </p>

              {/* Error help */}
              <div className="bg-white rounded-3xl border border-slate-200 shadow-xl p-8 md:p-10 mb-10 text-left max-w-3xl mx-auto">
                <h2 className="text-xl font-bold text-slate-900 mb-6 flex items-center">
                  <div className="w-9 h-9 bg-red-100 rounded-xl flex items-center justify-center mr-3">
                    <XCircle className="w-5 h-5 text-red-600" />
                  </div>
                  What to do next:
                </h2>
                <div className="space-y-3.5">
                  <div className="flex items-start gap-3.5">
                    <div className="w-2 h-2 bg-slate-400 rounded-full mt-2 flex-shrink-0"></div>
                    <p className="text-base text-slate-700 leading-relaxed">Request a new verification email from the login page</p>
                  </div>
                  <div className="flex items-start gap-3.5">
                    <div className="w-2 h-2 bg-slate-400 rounded-full mt-2 flex-shrink-0"></div>
                    <p className="text-base text-slate-700 leading-relaxed">Check if the link has expired (15-minute limit)</p>
                  </div>
                  <div className="flex items-start gap-3.5">
                    <div className="w-2 h-2 bg-slate-400 rounded-full mt-2 flex-shrink-0"></div>
                    <p className="text-base text-slate-700 leading-relaxed">Make sure you're using the latest verification email</p>
                  </div>
                </div>
              </div>

              {/* Back to login */}
              <Link
                href="/login"
                className="inline-flex items-center justify-center px-7 py-3.5 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-2xl text-base transition-all shadow-xl shadow-indigo-500/30 hover:shadow-2xl hover:-translate-y-1"
              >
                Go to Login
              </Link>
            </>
          )}
        </div>
      </section>
    </div>
  );
}

export default function EmailVerifiedPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-white font-sans text-slate-900 selection:bg-indigo-100 selection:text-indigo-700 overflow-x-hidden">
        <div className="fixed inset-0 -z-10 overflow-hidden pointer-events-none">
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[600px] bg-indigo-50/50 rounded-[100%] blur-3xl opacity-50 mix-blend-multiply"></div>
          <div className="absolute top-[20%] right-0 w-[800px] h-[600px] bg-purple-50/50 rounded-[100%] blur-3xl opacity-50 mix-blend-multiply"></div>
          <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-10 brightness-100 contrast-150"></div>
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
                Go to Login
              </Link>
            </div>
          </div>
        </nav>
        <section className="pt-32 pb-16 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
          <div className="text-center max-w-4xl mx-auto relative z-10">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-blue-500 to-blue-600 rounded-3xl shadow-2xl shadow-blue-500/40 mb-10 mx-auto animate-pulse">
              <Loader2 className="w-10 h-10 text-white animate-spin" />
            </div>
            <h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold tracking-tight text-slate-900 mb-6 leading-[1.1]">Loading...</h1>
          </div>
        </section>
      </div>
    }>
      <EmailVerifiedContent />
    </Suspense>
  );
}
