'use client';

/**
 * Auth Context Provider
 *
 * Manages authentication state and token initialization.
 * Ensures components wait for token initialization before making API calls.
 */

import { createContext, useContext, useEffect, useState, useRef, ReactNode } from 'react';
import { getAccessToken, refreshAccessToken, clearAccessToken } from '@/lib/jwt-auth-client';

interface AuthContextType {
  isInitialized: boolean;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType>({
  isInitialized: false,
  isAuthenticated: false,
});

export function useAuth() {
  return useContext(AuthContext);
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isInitialized, setIsInitialized] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const hasInitialized = useRef(false);

  useEffect(() => {
    // Prevent duplicate initialization in development (React StrictMode)
    if (hasInitialized.current) {
      return;
    }
    hasInitialized.current = true;

    const initializeAuth = async () => {
      try {
        const accessToken = getAccessToken();

        // If no access token, try to refresh (user might have refresh token cookie)
        if (!accessToken) {
          console.log('[AuthContext] No access token found, attempting refresh...');
          try {
            await refreshAccessToken();
            console.log('[AuthContext] Token refreshed successfully on app init');
            setIsAuthenticated(true);
          } catch (error) {
            console.log('[AuthContext] No valid refresh token available');
            setIsAuthenticated(false);
          }
        } else {
          // If access token exists, check if it's expired
          try {
            const parts = accessToken.split('.');
            if (parts.length !== 3) {
              console.log('[AuthContext] Invalid token format, clearing...');
              clearAccessToken();
              setIsAuthenticated(false);
            } else {
              const payload = JSON.parse(atob(parts[1]));

              // Check if token is expired
              if (payload.exp && payload.exp * 1000 < Date.now()) {
                console.log('[AuthContext] Access token expired, refreshing...');
                try {
                  await refreshAccessToken();
                  console.log('[AuthContext] Token refreshed successfully');
                  setIsAuthenticated(true);
                } catch (error) {
                  console.log('[AuthContext] Failed to refresh expired token');
                  clearAccessToken();
                  setIsAuthenticated(false);
                }
              } else {
                console.log('[AuthContext] Access token is valid');
                setIsAuthenticated(true);
              }
            }
          } catch (error) {
            console.error('[AuthContext] Error checking token expiration:', error);
            clearAccessToken();
            setIsAuthenticated(false);
          }
        }
      } catch (error) {
        console.error('[AuthContext] Error initializing auth:', error);
        setIsAuthenticated(false);
      } finally {
        setIsInitialized(true);
      }
    };

    initializeAuth();
  }, []);

  return (
    <AuthContext.Provider value={{ isInitialized, isAuthenticated }}>
      {children}
    </AuthContext.Provider>
  );
}
