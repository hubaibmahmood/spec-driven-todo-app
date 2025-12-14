export class ApiError extends Error {
  constructor(public status: number, public message: string) {
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
}

async function request<T>(url: string, options: RequestOptions = {}): Promise<T> {
  const { params, headers, ...rest } = options;
  
  const queryString = params ? '?' + new URLSearchParams(params).toString() : '';
  const fullUrl = `${url}${queryString}`;

  const defaultHeaders: HeadersInit = {
    'Content-Type': 'application/json',
    ...headers,
  };

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
    try {
      if (contentType && contentType.includes("application/json")) {
        const errorData = await response.json();
        errorMessage = errorData.detail || errorData.message || errorMessage;
      } else {
        // If it's not JSON, capture raw text (e.g., HTML error page content)
        errorMessage = await response.text(); 
      }
    } catch (e: unknown) {
      errorMessage = `Failed to parse error response: ${e instanceof Error ? e.message : String(e)}`;
    }
    throw new ApiError(response.status, errorMessage);
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
}

export const httpClient = {
  get: <T>(url: string, options?: RequestOptions) => request<T>(url, { ...options, method: 'GET' }),
  post: <T>(url: string, body: unknown, options?: RequestOptions) => request<T>(url, { ...options, method: 'POST', body: JSON.stringify(body) }),
  put: <T>(url: string, body: unknown, options?: RequestOptions) => request<T>(url, { ...options, method: 'PUT', body: JSON.stringify(body) }),
  patch: <T>(url: string, body: unknown, options?: RequestOptions) => request<T>(url, { ...options, method: 'PATCH', body: JSON.stringify(body) }),
  delete: <T>(url: string, options?: RequestOptions) => request<T>(url, { ...options, method: 'DELETE' }),
};
