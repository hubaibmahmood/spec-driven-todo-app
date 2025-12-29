"use client";

import React, { useEffect } from "react";
import {
  CheckSquare,
  ArrowRight,
  Zap,
  Layers,
  BarChart3,
  Search,
  Bell,
  Plus,
  MoreVertical,
  LayoutDashboard,
  Settings,
  Clock,
  Calendar,
  AlertCircle,
  ChevronDown,
  MessageSquare,
  Shield,
  CheckCircle2,
  ListTodo,
  AlertTriangle,
} from "lucide-react";
import Link from "next/link";
import { useSession } from "@/lib/auth-client";
import { useRouter } from "next/navigation";
import type { Feature, CTAButtonProps } from "@/types/landing";

// Features Data - AI Assistant First
const FEATURES: readonly Feature[] = [
  {
    id: "ai-assistant",
    icon: MessageSquare,
    iconColor: "text-indigo-600",
    iconBgColor: "bg-indigo-50",
    title: "AI-Powered Assistant",
    description: "Get intelligent suggestions, automated task organization, and natural language task creation. Your personal productivity copilot."
  },
  {
    id: "dashboard",
    icon: LayoutDashboard,
    iconColor: "text-emerald-600",
    iconBgColor: "bg-emerald-50",
    title: "Visual Dashboard",
    description: "See your productivity at a glance with beautiful charts, real-time statistics, and organized task views that keep you focused."
  },
  {
    id: "realtime",
    icon: Zap,
    iconColor: "text-amber-600",
    iconBgColor: "bg-amber-50",
    title: "Real-Time Updates",
    description: "Changes sync instantly across all your devices. Work seamlessly from desktop, mobile, or tablet without missing a beat."
  },
  {
    id: "security",
    icon: Shield,
    iconColor: "text-blue-600",
    iconBgColor: "bg-blue-50",
    title: "Secure & Private",
    description: "Your data is encrypted and secure. Industry-standard authentication keeps your tasks and projects private and protected."
  }
] as const;

// CTAButton Component with Analytics
const CTAButton: React.FC<CTAButtonProps> = ({
  href,
  variant,
  location,
  children,
  className = ""
}) => {
  const handleClick = () => {
    if (typeof window !== 'undefined' && window.gtag) {
      window.gtag('event', 'cta_click', {
        event_category: 'Landing Page',
        event_label: location,
        value: 1
      });
    }
  };

  const baseStyles = variant === "primary"
    ? "bg-indigo-600 hover:bg-indigo-700 text-white shadow-xl shadow-indigo-500/30 hover:shadow-2xl"
    : "bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 hover:border-slate-300 shadow-sm";

  return (
    <Link
      href={href}
      onClick={handleClick}
      className={`px-8 py-4 font-bold rounded-2xl text-lg transition-all hover:-translate-y-1 flex items-center justify-center gap-2 ${baseStyles} ${className}`}
    >
      {children}
    </Link>
  );
};

// FeatureCard Component
const FeatureCard: React.FC<{ feature: Feature }> = ({ feature }) => {
  const Icon = feature.icon;

  return (
    <div className="bg-white p-8 rounded-2xl border border-slate-100 shadow-sm hover:shadow-lg transition-all duration-300 group relative overflow-hidden">
      {/* Subtle gradient background on hover */}
      <div className="absolute inset-0 bg-gradient-to-br from-indigo-50/0 via-purple-50/0 to-pink-50/0 group-hover:from-indigo-50/50 group-hover:via-purple-50/30 group-hover:to-pink-50/50 transition-all duration-500 opacity-0 group-hover:opacity-100"></div>

      <div className="relative z-10">
        <div className={`w-12 h-12 ${feature.iconBgColor} rounded-xl flex items-center justify-center ${feature.iconColor} mb-6 group-hover:scale-110 transition-transform duration-300`}>
          <Icon className="w-6 h-6" aria-hidden="true" />
        </div>
        <h3 className="text-xl font-bold text-slate-900 mb-3">
          {feature.title}
        </h3>
        <p className="text-slate-600 leading-relaxed">
          {feature.description}
        </p>
      </div>
    </div>
  );
};

const LandingPage: React.FC = () => {
  const { data: session, isPending } = useSession();
  const router = useRouter();

  // Redirect authenticated users to dashboard
  useEffect(() => {
    if (session && !isPending) {
      router.push("/dashboard");
    }
  }, [session, isPending, router]);

  // Show loading or nothing while redirecting
  if (isPending) return <div className="min-h-screen bg-white" />;
  if (session) return null; // Redirecting...

  return (
    <div className="min-h-screen bg-white font-sans text-slate-900 selection:bg-indigo-100 selection:text-indigo-700 overflow-x-hidden">
      {/* Enhanced Background with AI-inspired patterns */}
      <div className="fixed inset-0 -z-10 overflow-hidden pointer-events-none">
        {/* Gradient mesh background */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1200px] h-[800px] bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 rounded-[100%] blur-3xl opacity-60 mix-blend-multiply"></div>
        <div className="absolute top-[20%] right-0 w-[900px] h-[700px] bg-gradient-to-bl from-purple-50 via-indigo-50 to-blue-50 rounded-[100%] blur-3xl opacity-50 mix-blend-multiply"></div>

        {/* Subtle grid pattern */}
        <div className="absolute inset-0 bg-[linear-gradient(rgba(99,102,241,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(99,102,241,0.03)_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_80%_50%_at_50%_0%,#000_70%,transparent_110%)]"></div>

        {/* Grain texture */}
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-[0.015] brightness-100 contrast-150"></div>
      </div>

      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 bg-white/80 backdrop-blur-md border-b border-slate-100 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
          <div
            className="flex items-center gap-2.5 text-slate-900 font-bold text-2xl cursor-pointer"
            onClick={() => window.scrollTo(0, 0)}
          >
            <div className="bg-gradient-to-br from-indigo-600 to-indigo-700 text-white p-2 rounded-xl shadow-lg shadow-indigo-500/20">
              <CheckSquare className="w-5 h-5" />
            </div>
            <span className="tracking-tight">Momentum</span>
          </div>
          <div className="flex items-center gap-4 sm:gap-8">
            <Link
              href="/login"
              className="text-sm font-semibold text-slate-600 hover:text-indigo-600 transition-colors hidden sm:block"
            >
              Log in
            </Link>
            <CTAButton
              href="/register"
              variant="primary"
              location="nav"
              className="!px-5 !py-2.5 !text-sm !rounded-full"
            >
              Get Started <ArrowRight className="w-4 h-4" />
            </CTAButton>
          </div>
        </div>
      </nav>

      {/* Hero Section - AI-Focused */}
      <section className="pt-32 pb-16 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
        <div className="text-center max-w-4xl mx-auto relative z-10 mb-20">
          {/* Badge with enhanced styling */}
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-gradient-to-r from-indigo-50 to-purple-50 border border-indigo-100 text-indigo-600 text-xs font-bold uppercase tracking-wider mb-8 shadow-sm animate-pulse-slow">
            <span className="flex h-2 w-2 rounded-full bg-indigo-600 animate-pulse"></span>
            New V2.0 Available
          </div>

          {/* AI-Focused Headline with Gradient */}
          <h1 className="text-5xl sm:text-7xl font-extrabold tracking-tight text-slate-900 mb-8 leading-[1.1]">
            Organize your work with <br className="hidden sm:block" />
            <span className="relative inline-block">
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 animate-gradient-x">
                AI-powered assistance
              </span>
              {/* Subtle underline accent */}
              <div className="absolute -bottom-2 left-0 right-0 h-1 bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 rounded-full opacity-30"></div>
            </span>
          </h1>

          {/* Updated Subheadline */}
          <p className="text-xl text-slate-600 mb-10 leading-relaxed max-w-2xl mx-auto font-medium">
            Let AI help you manage tasks, prioritize smartly, and reach your goals faster.
            Simple enough for personal use, powerful enough for teams.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <CTAButton
              href="/register"
              variant="primary"
              location="hero"
              className="w-full sm:w-auto"
            >
              Get Started for Free
            </CTAButton>
            <CTAButton
              href="/login"
              variant="secondary"
              location="hero"
              className="w-full sm:w-auto"
            >
              Sign in
            </CTAButton>
          </div>
        </div>

        {/* Dashboard Preview - Enhanced with AI indicators */}
        <div className="relative mx-auto max-w-6xl perspective-2000 group">
          {/* Enhanced glow effect */}
          <div className="absolute -inset-4 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 rounded-[30px] blur-2xl opacity-20 group-hover:opacity-30 transition-opacity duration-700"></div>

          {/* Main Container */}
          <div className="relative bg-white rounded-xl border border-slate-200 shadow-2xl overflow-hidden transform rotate-x-6 group-hover:rotate-x-2 transition-transform duration-700 ease-out origin-top">
            {/* Window Controls */}
            <div className="h-10 bg-slate-50 border-b border-slate-200 flex items-center px-4 gap-2">
              <div className="flex gap-1.5">
                <div className="w-3 h-3 rounded-full bg-red-400 border border-red-500/20"></div>
                <div className="w-3 h-3 rounded-full bg-amber-400 border border-amber-500/20"></div>
                <div className="w-3 h-3 rounded-full bg-green-400 border border-green-500/20"></div>
              </div>
              <div className="flex-1 text-center text-xs font-medium text-slate-400 ml-[-50px]">
                Momentum Dashboard
              </div>
            </div>

            {/* Application Layout */}
            <div className="flex h-[750px] bg-slate-50 font-sans text-left overflow-hidden">
              {/* Sidebar */}
              <aside className="hidden md:flex flex-col w-64 bg-white border-r border-slate-200 flex-shrink-0">
                <div className="p-6 h-20 flex items-center">
                  <div className="flex items-center gap-2 text-indigo-600 font-bold text-xl">
                    <CheckSquare className="w-7 h-7" />
                    <span>Momentum</span>
                  </div>
                </div>

                <nav className="flex-1 px-4 space-y-1">
                  <div className="flex items-center gap-3 px-3 py-2.5 text-indigo-600 bg-indigo-50 rounded-lg font-medium text-sm">
                    <LayoutDashboard className="w-4 h-4" />
                    Dashboard
                  </div>
                  <div className="flex items-center gap-3 px-3 py-2.5 text-slate-600 hover:bg-slate-50 rounded-lg font-medium text-sm transition-colors">
                    <CheckSquare className="w-4 h-4" />
                    My Tasks
                  </div>
                  <div className="flex items-center gap-3 px-3 py-2.5 text-slate-600 hover:bg-slate-50 rounded-lg font-medium text-sm transition-colors">
                    <Settings className="w-4 h-4" />
                    Settings
                  </div>
                </nav>

                <div className="p-4 border-t border-slate-100">
                  <div className="flex items-center gap-3 p-2 rounded-lg hover:bg-slate-50 transition-colors cursor-pointer">
                    <div className="w-9 h-9 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-600 font-bold text-sm">
                      JD
                    </div>
                    <div className="flex-1 overflow-hidden">
                      <p className="text-sm font-medium text-slate-900 truncate">
                        John Doe
                      </p>
                      <p className="text-xs text-slate-500 truncate">
                        john@example.com
                      </p>
                    </div>
                  </div>
                </div>
              </aside>

              {/* Main Content */}
              <div className="flex-1 flex flex-col min-w-0 bg-slate-50/50">
                {/* Header */}
                <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-end px-8 flex-shrink-0">
                  <div className="flex items-center gap-4">
                    <div className="relative p-2 text-slate-400 hover:bg-slate-50 rounded-full transition-colors cursor-pointer">
                      <Bell className="w-5 h-5" />
                      <span className="absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full border border-white"></span>
                    </div>
                  </div>
                </header>

                {/* Main Body */}
                <main className="flex-1 p-8 space-y-6 overflow-y-auto no-scrollbar bg-gradient-to-br from-stone-50 via-white to-indigo-50/30">
                  {/* Welcome Section */}
                  <div>
                    <h2 className="text-3xl font-bold text-stone-900 mb-1">
                      Good morning, Hubaib Mehmood! 👋
                    </h2>
                    <p className="text-sm text-stone-500">
                      You have 1 task pending today
                    </p>
                  </div>

                  {/* Stats Grid */}
                  <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                    {/* Total Tasks */}
                    <div className="bg-white rounded-2xl p-5 shadow-sm border border-stone-100">
                      <div className="flex items-start justify-between mb-3">
                        <p className="text-sm text-stone-500">Total Tasks</p>
                        <div className="p-2.5 rounded-xl bg-indigo-100">
                          <LayoutDashboard className="w-5 h-5 text-indigo-600" />
                        </div>
                      </div>
                      <p className="text-4xl font-bold text-stone-900">7</p>
                    </div>

                    {/* Completed */}
                    <div className="bg-white rounded-2xl p-5 shadow-sm border border-stone-100">
                      <div className="flex items-start justify-between mb-3">
                        <p className="text-sm text-stone-500">Completed</p>
                        <div className="p-2.5 rounded-xl bg-emerald-100">
                          <CheckSquare className="w-5 h-5 text-emerald-600" />
                        </div>
                      </div>
                      <p className="text-4xl font-bold text-stone-900">2</p>
                    </div>

                    {/* Pending */}
                    <div className="bg-white rounded-2xl p-5 shadow-sm border border-stone-100">
                      <div className="flex items-start justify-between mb-3">
                        <p className="text-sm text-stone-500">Pending</p>
                        <div className="p-2.5 rounded-xl bg-amber-100">
                          <Clock className="w-5 h-5 text-amber-600" />
                        </div>
                      </div>
                      <p className="text-4xl font-bold text-stone-900">5</p>
                    </div>

                    {/* Overdue */}
                    <div className="bg-white rounded-2xl p-5 shadow-sm border border-stone-100">
                      <div className="flex items-start justify-between mb-3">
                        <p className="text-sm text-stone-500">Overdue</p>
                        <div className="p-2.5 rounded-xl bg-rose-100">
                          <AlertCircle className="w-5 h-5 text-rose-600" />
                        </div>
                      </div>
                      <p className="text-4xl font-bold text-stone-900">1</p>
                    </div>
                  </div>

                  {/* Main Content Grid - 2/3 + 1/3 layout */}
                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Left Column - Today's Tasks (2/3) */}
                    <div className="lg:col-span-2 space-y-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <h3 className="text-2xl font-bold text-stone-900">Today&apos;s Tasks</h3>
                          <p className="text-sm text-stone-500 mt-1">1 remaining</p>
                        </div>
                        <button className="px-4 py-2 bg-indigo-600 text-white rounded-xl text-sm font-semibold hover:bg-indigo-700 transition-all flex items-center gap-2">
                          View All <ArrowRight className="w-4 h-4" />
                        </button>
                      </div>

                      {/* Task Card */}
                      <div className="bg-white rounded-xl p-4 border border-stone-100 hover:shadow-md transition-all">
                        <div className="flex items-start gap-4">
                          <div className="w-5 h-5 rounded-full border-2 border-stone-300 mt-0.5 flex-shrink-0"></div>
                          <div className="flex-1 min-w-0">
                            <h4 className="font-semibold text-stone-900 text-base mb-1">
                              Buy clothes
                            </h4>
                            <p className="text-sm text-stone-500 mb-3">
                              shirt, suit, pant
                            </p>
                            <div className="flex items-center gap-3">
                              <span className="px-2.5 py-1 rounded-md text-xs font-medium bg-orange-50 text-orange-600 border border-orange-200">
                                High
                              </span>
                              <div className="flex items-center gap-1.5 text-sm text-stone-500">
                                <Clock className="w-3.5 h-3.5" />
                                <span>10:00 PM</span>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Right Column - Widgets (1/3) */}
                    <div className="space-y-6">
                      {/* Task Progress Widget */}
                      <div className="bg-white rounded-2xl p-6 border border-stone-100 shadow-sm">
                        <h3 className="text-lg font-bold text-stone-900 mb-6">Task Progress</h3>

                        <div className="flex items-center gap-6 mb-6">
                          {/* Circular Progress */}
                          <div className="relative w-28 h-28 flex-shrink-0">
                            <svg className="w-full h-full -rotate-90">
                              <circle
                                cx="56"
                                cy="56"
                                r="45"
                                stroke="#f5f5f4"
                                strokeWidth="10"
                                fill="none"
                              />
                              <circle
                                cx="56"
                                cy="56"
                                r="45"
                                stroke="#6366f1"
                                strokeWidth="10"
                                fill="none"
                                strokeDasharray="283"
                                strokeDashoffset="201"
                                strokeLinecap="round"
                              />
                            </svg>
                            <div className="absolute inset-0 flex items-center justify-center">
                              <span className="text-2xl font-bold text-stone-900">29%</span>
                            </div>
                          </div>
                        </div>

                        {/* Legend */}
                        <div className="space-y-3">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                              <div className="w-3 h-3 rounded-full bg-indigo-600"></div>
                              <span className="text-sm text-stone-600">Completed</span>
                            </div>
                            <span className="text-lg font-bold text-stone-900">2</span>
                          </div>
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                              <div className="w-3 h-3 rounded-full bg-stone-200"></div>
                              <span className="text-sm text-stone-600">Pending</span>
                            </div>
                            <span className="text-lg font-bold text-stone-900">5</span>
                          </div>
                        </div>
                      </div>

                      {/* Upcoming Tasks Widget */}
                      <div className="bg-white rounded-2xl p-6 border border-stone-100 shadow-sm">
                        <div className="flex items-center gap-2 mb-4">
                          <Calendar className="w-5 h-5 text-indigo-600" />
                          <h3 className="text-lg font-bold text-stone-900">Upcoming Tasks</h3>
                        </div>

                        <div className="space-y-3">
                          {/* Upcoming Task 1 */}
                          <div className="flex items-start gap-3 p-2 rounded-lg hover:bg-stone-50 transition-colors">
                            <div className="w-2 h-2 rounded-full bg-orange-500 mt-2 flex-shrink-0"></div>
                            <div className="flex-1 min-w-0">
                              <p className="text-sm font-medium text-stone-900 truncate mb-1">
                                Generate documentation for docu...
                              </p>
                              <p className="text-xs text-stone-500">
                                Tomorrow • 11:59 PM
                              </p>
                            </div>
                          </div>

                          {/* Upcoming Task 2 */}
                          <div className="flex items-start gap-3 p-2 rounded-lg hover:bg-stone-50 transition-colors">
                            <div className="w-2 h-2 rounded-full bg-rose-500 mt-2 flex-shrink-0"></div>
                            <div className="flex-1 min-w-0">
                              <p className="text-sm font-medium text-stone-900 truncate mb-1">
                                generate proper documentation for...
                              </p>
                              <p className="text-xs text-stone-500">
                                Tomorrow • 11:59 PM
                              </p>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </main>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section - NEW: 4 Features with AI First */}
      <section className="py-24 bg-slate-50 relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="text-center mb-16 max-w-2xl mx-auto">
            <h2 className="text-3xl md:text-4xl font-extrabold text-slate-900 mb-6">
              Designed for modern workflows
            </h2>
            <p className="text-slate-600 text-lg">
              Experience the future of task management with AI-powered intelligence,
              real-time collaboration, and enterprise-grade security.
            </p>
          </div>

          {/* Updated Grid: 4 columns on large screens */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {FEATURES.map((feature) => (
              <FeatureCard key={feature.id} feature={feature} />
            ))}
          </div>
        </div>
      </section>

      {/* Bottom CTA */}
      <section className="py-20 px-4">
        <div className="max-w-5xl mx-auto bg-slate-900 rounded-3xl p-12 md:p-20 text-center text-white relative overflow-hidden shadow-2xl">
          <div className="relative z-10">
            <h2 className="text-4xl md:text-5xl font-bold mb-6">
              Ready to get organized?
            </h2>
            <p className="text-slate-400 text-xl mb-10 max-w-xl mx-auto">
              Join thousands of users who have transformed their productivity with Momentum.
            </p>
            <CTAButton
              href="/register"
              variant="primary"
              location="bottom"
              className="!bg-white !text-slate-900 hover:!bg-indigo-50 inline-flex"
            >
              Get Started for Free
            </CTAButton>
          </div>

          {/* Abstract Background Shapes */}
          <div className="absolute top-0 left-0 w-64 h-64 bg-indigo-600/20 rounded-full blur-3xl -translate-x-1/2 -translate-y-1/2"></div>
          <div className="absolute bottom-0 right-0 w-64 h-64 bg-purple-600/20 rounded-full blur-3xl translate-x-1/2 translate-y-1/2"></div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-white border-t border-slate-200 pt-16 pb-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row justify-between items-center gap-8 mb-8">
            <div className="flex items-center gap-2 text-slate-900 font-bold text-xl">
              <div className="bg-indigo-600 text-white p-1.5 rounded-lg">
                <CheckSquare className="w-4 h-4" />
              </div>
              Momentum
            </div>
            <div className="flex gap-8 text-sm text-slate-500 font-medium">
              <a href="#" className="hover:text-indigo-600 transition-colors">
                Features
              </a>
              <a href="#" className="hover:text-indigo-600 transition-colors">
                Pricing
              </a>
              <a href="#" className="hover:text-indigo-600 transition-colors">
                About
              </a>
              <a href="#" className="hover:text-indigo-600 transition-colors">
                Contact
              </a>
            </div>
          </div>
          <div className="text-center md:text-left text-sm text-slate-400 border-t border-slate-100 pt-8">
            © 2025 Momentum Inc. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
