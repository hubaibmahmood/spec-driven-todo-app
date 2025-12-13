"use client";

import React from "react";
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
} from "lucide-react";
import Link from "next/link";

const LandingPage: React.FC = () => {
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
          <div
            className="flex items-center gap-2.5 text-slate-900 font-bold text-2xl cursor-pointer"
            onClick={() => window.scrollTo(0, 0)}
          >
            <div className="bg-gradient-to-br from-indigo-600 to-indigo-700 text-white p-2 rounded-xl shadow-lg shadow-indigo-500/20">
              <CheckSquare className="w-5 h-5" />
            </div>
            <span className="tracking-tight">TaskFlow</span>
          </div>
          <div className="flex items-center gap-4 sm:gap-8">
            <Link
              href="/login"
              className="text-sm font-semibold text-slate-600 hover:text-indigo-600 transition-colors hidden sm:block"
            >
              Log in
            </Link>
            <Link
              href="/register"
              className="px-5 py-2.5 bg-slate-900 text-white text-sm font-semibold rounded-full hover:bg-slate-800 transition-all hover:shadow-lg hover:-translate-y-0.5 active:translate-y-0 flex items-center gap-2"
            >
              Get Started <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-16 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
        <div className="text-center max-w-4xl mx-auto relative z-10 mb-20">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-50 border border-indigo-100 text-indigo-600 text-xs font-bold uppercase tracking-wider mb-8 shadow-sm">
            <span className="flex h-2 w-2 rounded-full bg-indigo-600 animate-pulse"></span>
            New V2.0 Available
          </div>

          <h1 className="text-5xl sm:text-7xl font-extrabold tracking-tight text-slate-900 mb-8 leading-[1.1]">
            Organize your work, <br className="hidden sm:block" />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600">
              amplify your impact.
            </span>
          </h1>

          <p className="text-xl text-slate-500 mb-10 leading-relaxed max-w-2xl mx-auto font-medium">
            TaskFlow helps you manage projects, track tasks, and reach new
            productivity peaks. Simple enough for personal use, powerful enough
            for teams.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              href="/register"
              className="w-full sm:w-auto px-8 py-4 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-2xl text-lg transition-all shadow-xl shadow-indigo-500/30 hover:shadow-2xl hover:-translate-y-1 flex items-center justify-center gap-2"
            >
              Get Started
            </Link>
            <Link
              href="/login"
              className="w-full sm:w-auto px-8 py-4 bg-white hover:bg-slate-50 text-slate-700 font-bold rounded-2xl text-lg border border-slate-200 transition-all hover:border-slate-300 flex items-center justify-center gap-2 shadow-sm"
            >
              Sign in
            </Link>
          </div>
        </div>

        {/* Dashboard Preview - Cleaned Up & Polished */}
        <div className="relative mx-auto max-w-6xl perspective-2000 group">
          {/* Glow Effect */}
          <div className="absolute -inset-4 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 rounded-[30px] blur-2xl opacity-20 group-hover:opacity-30 transition-opacity duration-700"></div>

          {/* Main Container with Tilt */}
          <div className="relative bg-white rounded-xl border border-slate-200 shadow-2xl overflow-hidden transform rotate-x-6 group-hover:rotate-x-2 transition-transform duration-700 ease-out origin-top">
            {/* Window Controls (Mac Style) */}
            <div className="h-10 bg-slate-50 border-b border-slate-200 flex items-center px-4 gap-2">
              <div className="flex gap-1.5">
                <div className="w-3 h-3 rounded-full bg-red-400 border border-red-500/20"></div>
                <div className="w-3 h-3 rounded-full bg-amber-400 border border-amber-500/20"></div>
                <div className="w-3 h-3 rounded-full bg-green-400 border border-green-500/20"></div>
              </div>
              <div className="flex-1 text-center text-xs font-medium text-slate-400 ml-[-50px]">
                TaskFlow Dashboard
              </div>
            </div>

            {/* Application Layout Replica */}
            <div className="flex h-[750px] bg-slate-50 font-sans text-left overflow-hidden">
              {/* Sidebar - Clean & Structured */}
              <aside className="hidden md:flex flex-col w-64 bg-white border-r border-slate-200 flex-shrink-0">
                <div className="p-6 h-20 flex items-center">
                  <div className="flex items-center gap-2 text-indigo-600 font-bold text-xl">
                    <CheckSquare className="w-7 h-7" />
                    <span>TaskFlow</span>
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

              {/* Main Content Area */}
              <div className="flex-1 flex flex-col min-w-0 bg-slate-50/50">
                {/* Header - Minimalist */}
                <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-end px-8 flex-shrink-0">
                  <div className="flex items-center gap-4">
                    <div className="relative p-2 text-slate-400 hover:bg-slate-50 rounded-full transition-colors cursor-pointer">
                      <Bell className="w-5 h-5" />
                      <span className="absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full border border-white"></span>
                    </div>
                  </div>
                </header>

                {/* Main Body - Content Area */}
                <main className="flex-1 p-8 space-y-8 overflow-y-auto no-scrollbar">
                  {/* Welcome Section */}
                  <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div>
                      <h1 className="text-2xl font-bold text-slate-900">
                        Good Morning, John
                      </h1>
                      <p className="text-slate-500 text-sm mt-1">
                        You have 4 pending tasks for today.
                      </p>
                    </div>
                    <button className="flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2.5 rounded-lg shadow-sm transition-all text-sm font-medium">
                      <Plus className="w-4 h-4" />
                      <span>New Task</span>
                    </button>
                  </div>

                  {/* Stats Grid - Cleaner Layout */}
                  <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                    {/* Stat Card 1 */}
                    <div className="bg-white p-5 rounded-xl shadow-[0_2px_10px_-4px_rgba(0,0,0,0.05)] border border-slate-100">
                      <div className="flex justify-between items-start">
                        <div>
                          <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                            Total Tasks
                          </p>
                          <h3 className="text-2xl font-bold text-slate-900 mt-1">
                            12
                          </h3>
                        </div>
                        <div className="p-2 bg-slate-50 rounded-lg text-slate-400">
                          <Layers className="w-4 h-4" />
                        </div>
                      </div>
                      <div className="mt-3 flex items-center text-xs text-slate-500 font-medium">
                        <span className="text-emerald-600 bg-emerald-50 px-1.5 py-0.5 rounded mr-2">
                          +2
                        </span>
                        from yesterday
                      </div>
                    </div>

                    {/* Stat Card 2 */}
                    <div className="bg-white p-5 rounded-xl shadow-[0_2px_10px_-4px_rgba(0,0,0,0.05)] border border-slate-100">
                      <div className="flex justify-between items-start">
                        <div>
                          <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                            Pending
                          </p>
                          <h3 className="text-2xl font-bold text-indigo-600 mt-1">
                            4
                          </h3>
                        </div>
                        <div className="p-2 bg-indigo-50 rounded-lg text-indigo-500">
                          <Clock className="w-4 h-4" />
                        </div>
                      </div>
                      <div className="mt-3 flex items-center text-xs text-slate-500 font-medium">
                        <span className="text-indigo-600 bg-indigo-50 px-1.5 py-0.5 rounded mr-2">
                          3 due
                        </span>
                        today
                      </div>
                    </div>

                    {/* Stat Card 3 */}
                    <div className="bg-white p-5 rounded-xl shadow-[0_2px_10px_-4px_rgba(0,0,0,0.05)] border border-slate-100">
                      <div className="flex justify-between items-start">
                        <div>
                          <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                            High Priority
                          </p>
                          <h3 className="text-2xl font-bold text-orange-600 mt-1">
                            3
                          </h3>
                        </div>
                        <div className="p-2 bg-orange-50 rounded-lg text-orange-500">
                          <AlertCircle className="w-4 h-4" />
                        </div>
                      </div>
                      <div className="mt-3 flex items-center text-xs text-slate-500 font-medium">
                        Action required
                      </div>
                    </div>

                    {/* Stat Card 4 - Completion (FIXED) */}
                    <div className="bg-white p-5 rounded-xl shadow-[0_2px_10px_-4px_rgba(0,0,0,0.05)] border border-slate-100 flex items-center gap-4">
                      <div className="relative w-16 h-16 flex-shrink-0">
                        <svg
                          className="w-full h-full transform -rotate-90"
                          viewBox="0 0 64 64"
                        >
                          <circle
                            cx="32"
                            cy="32"
                            r="28"
                            stroke="currentColor"
                            strokeWidth="6"
                            fill="transparent"
                            className="text-slate-100"
                          />
                          <circle
                            cx="32"
                            cy="32"
                            r="28"
                            stroke="currentColor"
                            strokeWidth="6"
                            fill="transparent"
                            strokeDasharray="175.9"
                            strokeDashoffset="58"
                            className="text-emerald-500"
                            strokeLinecap="round"
                          />
                        </svg>
                        <div className="absolute inset-0 flex items-center justify-center text-sm font-bold text-slate-800">
                          67%
                        </div>
                      </div>
                      <div className="flex flex-col justify-center min-w-0">
                        <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                          Completion
                        </p>
                        <p className="text-xs text-slate-500 mt-1 truncate">
                          Great progress!
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Filters & Search - Cleaner */}
                  <div className="flex items-center justify-between bg-white p-2 rounded-xl border border-slate-200 shadow-sm">
                    <div className="flex gap-1 bg-slate-100/80 p-1 rounded-lg">
                      <button className="px-3 py-1.5 text-xs font-medium rounded-md bg-white text-indigo-600 shadow-sm transition-all">
                        All Tasks
                      </button>
                      <button className="px-3 py-1.5 text-xs font-medium rounded-md text-slate-500 hover:bg-slate-200/50 transition-all">
                        Active
                      </button>
                      <button className="px-3 py-1.5 text-xs font-medium rounded-md text-slate-500 hover:bg-slate-200/50 transition-all">
                        Completed
                      </button>
                    </div>
                    <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 bg-slate-50 border border-slate-100 rounded-lg w-64">
                      <Search className="w-4 h-4 text-slate-400" />
                      <input
                        type="text"
                        placeholder="Search..."
                        className="bg-transparent border-none focus:outline-none text-sm w-full placeholder-slate-400 text-slate-700"
                        readOnly
                      />
                    </div>
                    <button className="sm:hidden p-2 text-slate-400">
                      <Search className="w-4 h-4" />
                    </button>
                  </div>

                  {/* Todo Items - Cleaner List */}
                  <div className="space-y-3">
                    <div className="flex items-center justify-between px-1">
                      <h3 className="text-sm font-semibold text-slate-900">
                        Today&apos;s Focus
                      </h3>
                      <button className="text-xs text-indigo-600 hover:text-indigo-700 font-medium flex items-center gap-1">
                        View All <ChevronDown className="w-3 h-3" />
                      </button>
                    </div>

                    {/* Item 1 */}
                    <div className="group bg-white rounded-xl border border-slate-200 p-4 hover:shadow-md transition-all cursor-pointer">
                      <div className="flex items-start gap-4">
                        <div className="mt-1 w-5 h-5 rounded-full border-2 border-slate-300 group-hover:border-indigo-500 transition-colors flex-shrink-0"></div>
                        <div className="flex-1 min-w-0">
                          <div className="flex justify-between items-start">
                            <h4 className="font-semibold text-slate-900 text-sm">
                              Review Project Requirements
                            </h4>
                            <div className="opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-slate-100 rounded text-slate-400">
                              <MoreVertical className="w-4 h-4" />
                            </div>
                          </div>
                          <p className="text-slate-500 text-xs mt-1 line-clamp-1">
                            Review the latest PRD updates and technical specs.
                          </p>
                          <div className="flex items-center gap-2 mt-3">
                            <span className="px-2 py-0.5 rounded-md text-[10px] font-bold uppercase tracking-wide bg-orange-50 text-orange-600 border border-orange-100">
                              High
                            </span>
                            <div className="flex items-center gap-1 text-[11px] text-slate-400 bg-slate-50 px-2 py-0.5 rounded-md border border-slate-100">
                              <Calendar className="w-3 h-3" /> Today
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Item 2 */}
                    <div className="group bg-white rounded-xl border border-slate-200 p-4 hover:shadow-md transition-all cursor-pointer">
                      <div className="flex items-start gap-4">
                        <div className="mt-1 w-5 h-5 rounded-full border-2 border-slate-300 group-hover:border-indigo-500 transition-colors flex-shrink-0"></div>
                        <div className="flex-1 min-w-0">
                          <div className="flex justify-between items-start">
                            <h4 className="font-semibold text-slate-900 text-sm">
                              Update Landing Page Design
                            </h4>
                            <div className="opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-slate-100 rounded text-slate-400">
                              <MoreVertical className="w-4 h-4" />
                            </div>
                          </div>
                          <p className="text-slate-500 text-xs mt-1 line-clamp-1">
                            Implement new dashboard preview and cleanup layout.
                          </p>
                          <div className="flex items-center gap-2 mt-3">
                            <span className="px-2 py-0.5 rounded-md text-[10px] font-bold uppercase tracking-wide bg-blue-50 text-blue-600 border border-blue-100">
                              Medium
                            </span>
                            <div className="flex items-center gap-1 text-[11px] text-slate-400 bg-slate-50 px-2 py-0.5 rounded-md border border-slate-100">
                              <Clock className="w-3 h-3" /> 2h left
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Item 3 (Completed) */}
                    <div className="group bg-white/60 rounded-xl border border-slate-100 p-4 transition-all">
                      <div className="flex items-start gap-4">
                        <div className="mt-1 w-5 h-5 rounded-full bg-emerald-500 border-2 border-emerald-500 flex items-center justify-center flex-shrink-0">
                          <CheckSquare className="w-3 h-3 text-white" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex justify-between items-start">
                            <h4 className="font-semibold text-slate-500 text-sm line-through">
                              Weekly Team Sync
                            </h4>
                          </div>
                          <p className="text-slate-400 text-xs mt-1 line-clamp-1">
                            Prepare slides for the engineering all-hands
                            meeting.
                          </p>
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

      {/* Features Grid */}
      <section className="py-24 bg-slate-50 relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="text-center mb-16 max-w-2xl mx-auto">
            <h2 className="text-3xl md:text-4xl font-extrabold text-slate-900 mb-6">
              Designed for modern workflows
            </h2>
            <p className="text-slate-500 text-lg">
              Stop juggling multiple tools. TaskFlow combines organization,
              analytics, and speed in one beautiful interface.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="bg-white p-8 rounded-2xl border border-slate-100 shadow-sm hover:shadow-lg transition-all duration-300 group">
              <div className="w-12 h-12 bg-indigo-50 rounded-xl flex items-center justify-center text-indigo-600 mb-6 group-hover:scale-110 transition-transform">
                <Layers className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-slate-900 mb-3">
                Smart Organization
              </h3>
              <p className="text-slate-500 leading-relaxed">
                Categorize with tags, prioritize with ease, and filter to focus
                on what matters right now.
              </p>
            </div>

            <div className="bg-white p-8 rounded-2xl border border-slate-100 shadow-sm hover:shadow-lg transition-all duration-300 group">
              <div className="w-12 h-12 bg-emerald-50 rounded-xl flex items-center justify-center text-emerald-600 mb-6 group-hover:scale-110 transition-transform">
                <BarChart3 className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-slate-900 mb-3">
                Instant Analytics
              </h3>
              <p className="text-slate-500 leading-relaxed">
                Visualize your progress. Know exactly how much you&apos;ve
                accomplished and what&apos;s left.
              </p>
            </div>

            <div className="bg-white p-8 rounded-2xl border border-slate-100 shadow-sm hover:shadow-lg transition-all duration-300 group">
              <div className="w-12 h-12 bg-amber-50 rounded-xl flex items-center justify-center text-amber-600 mb-6 group-hover:scale-110 transition-transform">
                <Zap className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-slate-900 mb-3">
                Lightning Fast
              </h3>
              <p className="text-slate-500 leading-relaxed">
                Built for speed. Instant interactions, zero lag, and a fluid
                experience on any device.
              </p>
            </div>
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
              Join thousands of users who have transformed their productivity
              with TaskFlow.
            </p>
            <Link
              href="/register"
              className="px-8 py-4 bg-white text-slate-900 font-bold rounded-xl hover:bg-indigo-50 transition-all transform hover:scale-105 inline-block"
            >
              Get Started for Free
            </Link>
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
              TaskFlow
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
            © 2024 TaskFlow Inc. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;