'use client';

/**
 * TokenInitializer Component
 *
 * Validates and refreshes JWT access token on app initialization.
 * Ensures seamless authentication state when user returns to the app.
 */

import { useEffect, useRef } from 'react';
import { getAccessToken, refreshAccessToken, clearAccessToken } from '@/lib/jwt-auth-client';

export function TokenInitializer() {
  const hasInitialized = useRef(false);

  useEffect(() => {
    // Prevent duplicate initialization in development (React StrictMode)
    if (hasInitialized.current) {
      return;
    }
    hasInitialized.current = true;

    const initializeToken = async () => {
      try {
        const accessToken = getAccessToken();

        // If no access token, try to refresh (user might have refresh token cookie)
        if (!accessToken) {
          console.log('No access token found, attempting refresh...');
          try {
            await refreshAccessToken();
            console.log('Token refreshed successfully on app init');
          } catch (error) {
            console.log('No valid refresh token available');
            // This is fine - user is not authenticated
          }
          return;
        }

        // If access token exists, check if it's expired
        try {
          const parts = accessToken.split('.');
          if (parts.length !== 3) {
            // Invalid token format
            console.log('Invalid token format, clearing...');
            clearAccessToken();
            return;
          }

          const payload = JSON.parse(atob(parts[1]));

          // Check if token is expired
          if (payload.exp && payload.exp * 1000 < Date.now()) {
            console.log('Access token expired, refreshing...');
            try {
              await refreshAccessToken();
              console.log('Token refreshed successfully');
            } catch (error) {
              console.log('Failed to refresh expired token');
              clearAccessToken();
            }
          } else {
            console.log('Access token is valid');
          }
        } catch (error) {
          console.error('Error checking token expiration:', error);
          clearAccessToken();
        }
      } catch (error) {
        console.error('Error initializing token:', error);
      }
    };

    initializeToken();
  }, []);

  // This component doesn't render anything
  return null;
}
