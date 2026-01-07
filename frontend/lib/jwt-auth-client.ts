/**
 * JWT-enhanced authentication client for hybrid authentication.
 *
 * This client wraps the auth server's JWT endpoints and provides:
 * - Access token storage in localStorage
 * - Automatic token refresh
 * - Seamless integration with existing better-auth session system
 */

const JWT_STORAGE_KEY = 'jwt_access_token';
const USER_INFO_KEY = 'jwt_user_info';

interface User {
  id: string;
  email: string;
  name: string | null;
  image: string | null;
  emailVerified: boolean;
}

interface JWTAuthResponse {
  accessToken: string;
  user: User;
  message?: string;
}

interface SignInData {
  email: string;
  password: string;
}

interface SignUpData {
  email: string;
  password: string;
  name?: string;
}

function getAuthBaseURL(): string {
  // Always use same-origin requests to avoid cross-origin cookie issues
  // In development: Next.js proxies /api/auth-proxy/* to localhost:8080
  // In production: Frontend proxies auth requests to auth server
  if (typeof window !== 'undefined') {
    return window.location.origin;
  }

  // Server-side fallback
  return process.env.NODE_ENV === 'development'
    ? "http://localhost:3000"
    : (process.env.NEXT_PUBLIC_AUTH_URL || "https://momentum.intevia.cc");
}

const BASE_URL = getAuthBaseURL();

/**
 * Store JWT access token in localStorage
 */
export function storeAccessToken(token: string): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem(JWT_STORAGE_KEY, token);
  }
}

/**
 * Retrieve JWT access token from localStorage
 */
export function getAccessToken(): string | null {
  if (typeof window !== 'undefined') {
    return localStorage.getItem(JWT_STORAGE_KEY);
  }
  return null;
}

/**
 * Remove JWT access token from localStorage
 */
export function clearAccessToken(): void {
  if (typeof window !== 'undefined') {
    localStorage.removeItem(JWT_STORAGE_KEY);
  }
}

/**
 * Store user info in localStorage
 */
export function storeUserInfo(user: User): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem(USER_INFO_KEY, JSON.stringify(user));
  }
}

/**
 * Retrieve user info from localStorage
 */
export function getUserInfo(): User | null {
  if (typeof window !== 'undefined') {
    const userJson = localStorage.getItem(USER_INFO_KEY);
    if (userJson) {
      try {
        return JSON.parse(userJson);
      } catch {
        return null;
      }
    }
  }
  return null;
}

/**
 * Remove user info from localStorage
 */
export function clearUserInfo(): void {
  if (typeof window !== 'undefined') {
    localStorage.removeItem(USER_INFO_KEY);
  }
}

/**
 * Sign in with email and password, receive JWT tokens
 */
export async function jwtSignIn(data: SignInData): Promise<JWTAuthResponse> {
  const response = await fetch(`${BASE_URL}/api/auth-proxy/auth/jwt/sign-in`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include', // Include cookies for refresh token
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || 'Sign in failed');
  }

  const result: JWTAuthResponse = await response.json();

  // Store access token and user info in localStorage
  storeAccessToken(result.accessToken);
  storeUserInfo(result.user);

  return result;
}

/**
 * Sign up with email, password, and optional name, receive JWT tokens
 */
export async function jwtSignUp(data: SignUpData): Promise<JWTAuthResponse> {
  const response = await fetch(`${BASE_URL}/api/auth-proxy/auth/jwt/sign-up`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include', // Include cookies for refresh token
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || 'Sign up failed');
  }

  const result: JWTAuthResponse = await response.json();

  // Store access token and user info in localStorage
  storeAccessToken(result.accessToken);
  storeUserInfo(result.user);

  return result;
}

/**
 * Refresh the access token using the refresh token cookie
 */
export async function refreshAccessToken(): Promise<string> {
  const response = await fetch(`${BASE_URL}/api/auth-proxy/auth/refresh`, {
    method: 'POST',
    credentials: 'include', // Include httpOnly refresh token cookie
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || 'Token refresh failed');
  }

  const result = await response.json();
  const newAccessToken = result.access_token || result.accessToken;

  // Store new access token
  storeAccessToken(newAccessToken);

  return newAccessToken;
}

/**
 * Sign out - clear access token and notify server
 */
export async function jwtSignOut(): Promise<void> {
  const accessToken = getAccessToken();

  if (accessToken) {
    try {
      // Call backend logout endpoint to clear refresh token cookie
      await fetch(`${BASE_URL}/api/auth-proxy/auth/logout`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
        },
        credentials: 'include',
      });
    } catch (error) {
      console.error('Logout request failed:', error);
      // Continue with client-side cleanup even if server request fails
    }
  }

  // Clear access token and user info from localStorage
  clearAccessToken();
  clearUserInfo();
}

/**
 * Get current user from stored user info (client-side only, no verification)
 * User info is stored in localStorage during sign-in/sign-up
 * For actual verification, make API request to backend
 */
export function getCurrentUserFromToken(): User | null {
  const token = getAccessToken();
  const userInfo = getUserInfo();

  if (!token || !userInfo) {
    return null;
  }

  try {
    // Decode JWT payload to check expiration
    const parts = token.split('.');
    if (parts.length !== 3) {
      return null;
    }

    const payload = JSON.parse(atob(parts[1]));

    // Check if token is expired
    if (payload.exp && payload.exp * 1000 < Date.now()) {
      clearAccessToken();
      clearUserInfo();
      return null;
    }

    // Return stored user info
    return userInfo;
  } catch (error) {
    console.error('Failed to get user from token:', error);
    return null;
  }
}

/**
 * Check if user is authenticated (has valid access token)
 */
export function isAuthenticated(): boolean {
  const token = getAccessToken();
  if (!token) {
    return false;
  }

  try {
    const parts = token.split('.');
    if (parts.length !== 3) {
      return false;
    }

    const payload = JSON.parse(atob(parts[1]));

    // Check if token is expired
    if (payload.exp && payload.exp * 1000 < Date.now()) {
      clearAccessToken();
      return false;
    }

    return true;
  } catch (error) {
    return false;
  }
}
