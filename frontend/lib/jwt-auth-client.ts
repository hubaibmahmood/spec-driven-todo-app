/**
 * JWT-enhanced authentication client for hybrid authentication.
 *
 * This client wraps the auth server's JWT endpoints and provides:
 * - Access token storage in localStorage
 * - Automatic token refresh
 * - Seamless integration with existing better-auth session system
 */

const JWT_STORAGE_KEY = 'jwt_access_token';

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
  // Development: connect directly to local auth server
  if (process.env.NODE_ENV === 'development') {
    return "http://localhost:8080";
  }

  // Production: use frontend URL (proxied by Netlify to auth server)
  return process.env.NEXT_PUBLIC_AUTH_URL || "https://momentum.intevia.cc";
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
 * Sign in with email and password, receive JWT tokens
 */
export async function jwtSignIn(data: SignInData): Promise<JWTAuthResponse> {
  const response = await fetch(`${BASE_URL}/api/auth/jwt/sign-in`, {
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

  // Store access token in localStorage
  storeAccessToken(result.accessToken);

  return result;
}

/**
 * Sign up with email, password, and optional name, receive JWT tokens
 */
export async function jwtSignUp(data: SignUpData): Promise<JWTAuthResponse> {
  const response = await fetch(`${BASE_URL}/api/auth/jwt/sign-up`, {
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

  // Store access token in localStorage
  storeAccessToken(result.accessToken);

  return result;
}

/**
 * Sign out - clear access token and notify server
 */
export async function jwtSignOut(): Promise<void> {
  const accessToken = getAccessToken();

  if (accessToken) {
    try {
      // Call backend logout endpoint (will be implemented in Phase 5)
      await fetch(`${BASE_URL}/api/auth/logout`, {
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

  // Clear access token from localStorage
  clearAccessToken();
}

/**
 * Get current user from access token (client-side only, no verification)
 * For actual verification, make API request to backend
 */
export function getCurrentUserFromToken(): User | null {
  const token = getAccessToken();

  if (!token) {
    return null;
  }

  try {
    // Decode JWT payload (not verifying signature - that's backend's job)
    const parts = token.split('.');
    if (parts.length !== 3) {
      return null;
    }

    const payload = JSON.parse(atob(parts[1]));

    // Check if token is expired
    if (payload.exp && payload.exp * 1000 < Date.now()) {
      clearAccessToken();
      return null;
    }

    // Note: We only have user_id in the token
    // Full user info should be fetched from backend if needed
    return {
      id: payload.sub,
      email: '', // Not stored in token for security
      name: null,
      image: null,
      emailVerified: false,
    };
  } catch (error) {
    console.error('Failed to decode token:', error);
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
