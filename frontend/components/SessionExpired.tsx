'use client';

/**
 * SessionExpired Component
 *
 * Displays a user-friendly message when the session expires and all token refresh attempts fail.
 * Provides a clear call-to-action to log in again.
 */

import { useRouter } from 'next/navigation';
import { AlertCircle } from 'lucide-react';
import { clearAccessToken, clearUserInfo } from '@/lib/jwt-auth-client';

interface SessionExpiredProps {
  message?: string;
  onDismiss?: () => void;
  autoRedirect?: boolean;
}

export function SessionExpired({
  message = 'Your session has expired. Please log in again to continue.',
  onDismiss,
  autoRedirect = false,
}: SessionExpiredProps) {
  const router = useRouter();

  const handleLogin = () => {
    // Clear any stale tokens
    clearAccessToken();
    clearUserInfo();

    // Redirect to login page
    router.push('/login');
  };

  // Auto-redirect to login if enabled
  if (autoRedirect) {
    handleLogin();
    return null;
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="max-w-md w-full mx-4 bg-white dark:bg-gray-800 rounded-lg shadow-xl p-6">
        {/* Icon */}
        <div className="flex items-center justify-center w-12 h-12 mx-auto mb-4 rounded-full bg-red-100 dark:bg-red-900/20">
          <AlertCircle className="w-6 h-6 text-red-600 dark:text-red-400" />
        </div>

        {/* Title */}
        <h2 className="text-xl font-semibold text-center text-gray-900 dark:text-gray-100 mb-2">
          Session Expired
        </h2>

        {/* Message */}
        <p className="text-center text-gray-600 dark:text-gray-400 mb-6">
          {message}
        </p>

        {/* Actions */}
        <div className="flex gap-3">
          {onDismiss && (
            <button
              onClick={onDismiss}
              className="flex-1 px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
            >
              Dismiss
            </button>
          )}
          <button
            onClick={handleLogin}
            className="flex-1 px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Log In
          </button>
        </div>
      </div>
    </div>
  );
}

/**
 * Hook to show session expired modal
 */
export function useSessionExpired() {
  const router = useRouter();

  const showSessionExpired = (autoRedirect = false) => {
    if (autoRedirect) {
      clearAccessToken();
      clearUserInfo();
      router.push('/login');
    } else {
      // For controlled display, parent component should manage state
      // This is a utility function for auto-redirect case
      clearAccessToken();
      clearUserInfo();
      router.push('/login');
    }
  };

  return { showSessionExpired };
}
