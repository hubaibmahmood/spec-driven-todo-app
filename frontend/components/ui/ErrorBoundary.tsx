'use client';

import React, { Component, ErrorInfo, ReactNode } from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

/**
 * Error Boundary component to catch and display React errors gracefully.
 *
 * Prevents the entire application from crashing when a component error occurs.
 * Shows a user-friendly error message with the option to retry.
 *
 * Usage:
 * ```tsx
 * <ErrorBoundary>
 *   <YourComponent />
 * </ErrorBoundary>
 * ```
 */
export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    // Update state so the next render will show the fallback UI
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    // Log error to console for debugging
    console.error('ErrorBoundary caught an error:', error, errorInfo);

    // You can also log the error to an error reporting service here
    // Example: logErrorToService(error, errorInfo);

    this.setState({
      error,
      errorInfo,
    });
  }

  handleReset = (): void => {
    // Reset error state and try to render children again
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
  };

  render(): ReactNode {
    if (this.state.hasError) {
      // Use custom fallback if provided
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default error UI
      return (
        <div className="min-h-screen flex items-center justify-center bg-slate-50 p-4">
          <div className="max-w-md w-full bg-white rounded-lg border-2 border-red-200 shadow-lg p-8">
            {/* Error Icon */}
            <div className="flex justify-center mb-4">
              <div className="p-3 rounded-full bg-red-100">
                <AlertTriangle size={32} className="text-red-600" strokeWidth={2} />
              </div>
            </div>

            {/* Error Title */}
            <h1 className="text-2xl font-bold text-slate-900 text-center mb-2">
              Oops! Something went wrong
            </h1>

            {/* Error Message */}
            <p className="text-slate-700 text-center mb-6">
              We encountered an unexpected error. Don&apos;t worry, your data is safe.
            </p>

            {/* Error Details (Development only) */}
            {process.env.NODE_ENV === 'development' && this.state.error && (
              <div className="mb-6 p-4 bg-slate-100 rounded border border-slate-300">
                <p className="text-xs font-mono text-red-600 break-all">
                  <strong>Error:</strong> {this.state.error.toString()}
                </p>
                {this.state.errorInfo && (
                  <details className="mt-2">
                    <summary className="text-xs font-semibold text-slate-700 cursor-pointer">
                      Stack Trace
                    </summary>
                    <pre className="text-xs text-slate-600 mt-2 overflow-auto max-h-48">
                      {this.state.errorInfo.componentStack}
                    </pre>
                  </details>
                )}
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-3">
              <button
                onClick={this.handleReset}
                className="
                  flex items-center justify-center gap-2 px-5 py-2.5 rounded-lg
                  font-medium text-sm
                  bg-indigo-600 hover:bg-indigo-700 text-white
                  shadow-sm active:scale-95
                  transition-all
                "
              >
                <RefreshCw size={18} strokeWidth={2} />
                <span>Try Again</span>
              </button>

              <button
                onClick={() => window.location.href = '/dashboard'}
                className="
                  flex items-center justify-center gap-2 px-5 py-2.5 rounded-lg
                  font-medium text-sm
                  border border-slate-300
                  bg-white hover:bg-slate-50
                  text-slate-700
                  transition-all
                  active:scale-95
                "
              >
                <span>Go to Dashboard</span>
              </button>
            </div>

            {/* Help Text */}
            <p className="text-xs text-slate-600 text-center mt-6">
              If this problem persists, please contact support or refresh the page.
            </p>
          </div>
        </div>
      );
    }

    // No error, render children normally
    return this.props.children;
  }
}

/**
 * Lightweight error boundary for inline use.
 * Shows a minimal error message without replacing the entire page.
 */
export function InlineErrorBoundary({
  children,
  fallback
}: ErrorBoundaryProps): ReactNode {
  return (
    <ErrorBoundary
      fallback={
        fallback || (
          <div className="p-4 bg-red-50 border-2 border-red-200 rounded-lg">
            <div className="flex items-center gap-2 text-red-900">
              <AlertTriangle size={20} strokeWidth={2} />
              <p className="text-sm font-semibold">
                An error occurred while loading this component
              </p>
            </div>
          </div>
        )
      }
    >
      {children}
    </ErrorBoundary>
  );
}
