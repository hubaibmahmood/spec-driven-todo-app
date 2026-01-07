import { getAccessToken, refreshAccessToken, storeAccessToken } from './jwt-auth-client';

export class ApiError extends Error {
  constructor(public status: number, public message: string, public errorCode?: string) {
    super(message);
    this.name = 'ApiError';
  }
}

export class ApiRedirectError extends ApiError {
    constructor(public status: number, public message: string, public redirectUrl: string) {
        super(status, message);
        this.name = 'ApiRedirectError';
    }
}

interface RequestOptions extends RequestInit {
  params?: Record<string, string>;
  _retryCount?: number;
  _skipTokenRefresh?: boolean;
}

// Helper to delay for exponential backoff
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

// Helper to determine if error is retryable
function isRetryableError(status: number, errorCode?: string): boolean {
  // Network errors (500, 503) are retryable
  if (status >= 500) {
    return true;
  }
  // Auth errors (401, 403) are not retryable
  if (status === 401 || status === 403) {
    return false;
  }
  return false;
}

// Helper to determine if we should attempt token refresh
// Industry standard: Refresh on ANY 401 error (not just specific error codes)
function shouldRefreshToken(status: number, errorCode?: string): boolean {
  return status === 401;
}

async function request<T>(url: string, options: RequestOptions = {}): Promise<T> {
  const { params, headers, _retryCount = 0, _skipTokenRefresh = false, ...rest } = options;

  const queryString = params ? '?' + new URLSearchParams(params).toString() : '';
  const fullUrl = `${url}${queryString}`;

  // Proactive token validation and refresh (industry standard)
  let accessToken = getAccessToken();

  if (!_skipTokenRefresh && accessToken) {
    try {
      // Parse JWT to check expiration
      const parts = accessToken.split('.');
      if (parts.length === 3) {
        const payload = JSON.parse(atob(parts[1]));

        // Check if token is expired or will expire soon (60 second buffer)
        const expirationTime = payload.exp * 1000;
        const now = Date.now();
        const bufferTime = 60 * 1000; // 60 seconds

        if (expirationTime - now < bufferTime) {
          console.log('[http-client] Token expired or expiring soon, refreshing...');
          try {
            accessToken = await refreshAccessToken();
            console.log('[http-client] Token refreshed successfully');
          } catch (refreshError) {
            console.error('[http-client] Failed to refresh token:', refreshError);
            // Continue with expired token - will likely get 401 and trigger fallback
          }
        }
      }
    } catch (error) {
      console.error('[http-client] Error validating token:', error);
      // Continue with existing token
    }
  }

  const defaultHeaders: HeadersInit = {
    'Content-Type': 'application/json',
    ...(accessToken ? { 'Authorization': `Bearer ${accessToken}` } : {}),
    ...headers,
  };

  try {
    const response = await fetch(fullUrl, {
      headers: defaultHeaders,
      credentials: 'include',
      ...rest,
    });

    const finalUrl = response.url;
    const contentType = response.headers.get("content-type");

    // If the fetch eventually landed on an unauthorized HTML page (e.g., /login or /)
    // this indicates an unauthenticated access that was redirected.
    if ((finalUrl.includes('/login') || finalUrl === 'http://localhost:3000/') && contentType && contentType.includes('text/html')) {
        // Throw a specific error that the caller (page.tsx) can catch to redirect.
        // Redirect to /login explicitly, as that's the desired behavior for unauthenticated API access.
        throw new ApiRedirectError(response.status, "Redirected to unauthorized HTML page. Not authenticated.", "http://localhost:3000/login");
    }

    if (!response.ok) {
      let errorMessage = 'An error occurred';
      let errorCode: string | undefined;

      try {
        if (contentType && contentType.includes("application/json")) {
          const errorData = await response.json();
          errorMessage = errorData.detail?.message || errorData.detail || errorData.message || errorMessage;
          errorCode = errorData.detail?.error_code || errorData.error_code;
        } else {
          // If it's not JSON, capture raw text (e.g., HTML error page content)
          errorMessage = await response.text();
        }
      } catch (e: unknown) {
        errorMessage = `Failed to parse error response: ${e instanceof Error ? e.message : String(e)}`;
      }

      // Response Interceptor Logic:
      // 1. Check for 401 with token_expired error code
      if (!_skipTokenRefresh && shouldRefreshToken(response.status, errorCode)) {
        try {
          // Attempt to refresh the token
          await refreshAccessToken();

          // Retry the original request with the new token
          return request<T>(url, {
            ...options,
            _skipTokenRefresh: true, // Prevent infinite refresh loops
            _retryCount: 0, // Reset retry count for the new request
          });
        } catch (refreshError) {
          // If refresh fails, throw the original error
          // This will trigger logout or show session expired message
          throw new ApiError(response.status, errorMessage, errorCode);
        }
      }

      // 2. Check for retryable errors (network errors 500, 503)
      if (isRetryableError(response.status, errorCode) && _retryCount < 3) {
        // Exponential backoff: 1s, 2s, 4s
        const delayMs = Math.pow(2, _retryCount) * 1000;
        await delay(delayMs);

        // Retry the request
        return request<T>(url, {
          ...options,
          _retryCount: _retryCount + 1,
        });
      }

      // 3. Throw error if not retryable or max retries reached
      throw new ApiError(response.status, errorMessage, errorCode);
    }

    // Handle 204 No Content
    if (response.status === 204) {
      return {} as T;
    }

    // Only attempt to parse JSON if content type is JSON
    if (contentType && contentType.includes("application/json")) {
        return response.json();
    } else {
        // This should ideally not happen for successful API responses that expect JSON
        throw new Error(`Expected JSON response, but received ${contentType || 'no content type'}`);
    }
  } catch (error) {
    // Handle network errors (fetch failures)
    if (error instanceof ApiError || error instanceof ApiRedirectError) {
      throw error;
    }

    // Network error - retry with exponential backoff
    if (_retryCount < 3) {
      const delayMs = Math.pow(2, _retryCount) * 1000;
      await delay(delayMs);

      return request<T>(url, {
        ...options,
        _retryCount: _retryCount + 1,
      });
    }

    // Max retries reached
    throw new ApiError(0, error instanceof Error ? error.message : 'Network error occurred');
  }
}

export const httpClient = {
  get: <T>(url: string, options?: RequestOptions) => request<T>(url, { ...options, method: 'GET' }),
  post: <T>(url: string, body: unknown, options?: RequestOptions) => request<T>(url, { ...options, method: 'POST', body: JSON.stringify(body) }),
  put: <T>(url: string, body: unknown, options?: RequestOptions) => request<T>(url, { ...options, method: 'PUT', body: JSON.stringify(body) }),
  patch: <T>(url: string, body: unknown, options?: RequestOptions) => request<T>(url, { ...options, method: 'PATCH', body: JSON.stringify(body) }),
  delete: <T>(url: string, options?: RequestOptions) => request<T>(url, { ...options, method: 'DELETE' }),
};
