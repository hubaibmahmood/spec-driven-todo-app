/**
 * API client for user API key management endpoints.
 * Handles communication with the backend /api/user-api-keys routes.
 */

import { authClient } from '@/lib/auth-client';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface ApiKeyStatusResponse {
  configured: boolean;
  provider?: string | null;
  masked_key?: string | null;
  validation_status?: string | null;
  last_validated_at?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
}

interface SaveApiKeyResponse {
  success: boolean;
  message: string;
  masked_key: string;
}

interface TestApiKeyResponse {
  success: boolean;
  message: string;
  validation_status: string;
}

interface DeleteApiKeyResponse {
  success: boolean;
  message: string;
}

/**
 * Get authentication token from better-auth session.
 */
async function getAuthToken(): Promise<string | null> {
  try {
    const { data: session } = await authClient.getSession();
    return session?.session?.token || null;
  } catch (error) {
    console.error('Failed to get auth session:', error);
    return null;
  }
}

/**
 * Make an authenticated API request.
 */
async function authenticatedFetch(
  endpoint: string,
  options: RequestInit = {}
): Promise<Response> {
  const token = await getAuthToken();

  if (!token) {
    throw new Error('Not authenticated. Please log in.');
  }

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`,
    ...(options.headers as Record<string, string> || {}),
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
    credentials: 'include', // Include cookies for session
  });

  return response;
}

/**
 * Get current user's API key status.
 */
export async function getCurrentApiKey(): Promise<ApiKeyStatusResponse> {
  const response = await authenticatedFetch('/api/user-api-keys/current');

  if (!response.ok) {
    if (response.status === 401) {
      throw new Error('Not authenticated');
    }
    throw new Error('Failed to fetch API key status');
  }

  return response.json();
}

/**
 * Save or update user's API key.
 */
export async function saveApiKey(
  apiKey: string,
  provider: string = 'gemini'
): Promise<SaveApiKeyResponse> {
  const response = await authenticatedFetch('/api/user-api-keys', {
    method: 'POST',
    body: JSON.stringify({
      api_key: apiKey,
      provider,
    }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'Failed to save API key' }));
    throw new Error(errorData.detail || 'Failed to save API key');
  }

  return response.json();
}

/**
 * Test API key connectivity.
 *
 * Rate limit: 5 tests per hour per user.
 * If rate limit is exceeded, a 429 error will be thrown with a user-friendly message.
 */
export async function testApiKey(apiKey: string): Promise<TestApiKeyResponse> {
  const response = await authenticatedFetch('/api/user-api-keys/test', {
    method: 'POST',
    body: JSON.stringify({
      api_key: apiKey,
    }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'Failed to test API key' }));

    // Handle rate limit (429) with the specific error message from backend
    if (response.status === 429) {
      throw new Error(errorData.detail || 'Rate limit exceeded. Please try again later.');
    }

    throw new Error(errorData.detail || 'Failed to test API key');
  }

  return response.json();
}

/**
 * Delete user's API key.
 */
export async function deleteApiKey(): Promise<DeleteApiKeyResponse> {
  const response = await authenticatedFetch('/api/user-api-keys/current', {
    method: 'DELETE',
  });

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error('No API key found to delete');
    }
    const errorData = await response.json().catch(() => ({ detail: 'Failed to delete API key' }));
    throw new Error(errorData.detail || 'Failed to delete API key');
  }

  return response.json();
}
