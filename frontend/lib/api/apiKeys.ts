/**
 * API client for user API key management endpoints.
 * Handles communication with the backend /api/user-api-keys routes.
 */

import { httpClient } from '@/lib/http-client';

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
 * Get current user's API key status.
 */
export async function getCurrentApiKey(): Promise<ApiKeyStatusResponse> {
  try {
    return await httpClient.get<ApiKeyStatusResponse>(`${API_BASE_URL}/api/user-api-keys/current`);
  } catch (error: any) {
    if (error.status === 401) {
      throw new Error('Not authenticated. Please log in.');
    }
    throw new Error(error.message || 'Failed to fetch API key status');
  }
}

/**
 * Save or update user's API key.
 */
export async function saveApiKey(
  apiKey: string,
  provider: string = 'gemini'
): Promise<SaveApiKeyResponse> {
  try {
    return await httpClient.post<SaveApiKeyResponse>(
      `${API_BASE_URL}/api/user-api-keys`,
      {
        api_key: apiKey,
        provider,
      }
    );
  } catch (error: any) {
    throw new Error(error.message || 'Failed to save API key');
  }
}

/**
 * Test API key connectivity.
 *
 * Rate limit: 5 tests per hour per user.
 * If rate limit is exceeded, a 429 error will be thrown with a user-friendly message.
 */
export async function testApiKey(apiKey: string): Promise<TestApiKeyResponse> {
  try {
    return await httpClient.post<TestApiKeyResponse>(
      `${API_BASE_URL}/api/user-api-keys/test`,
      {
        api_key: apiKey,
      }
    );
  } catch (error: any) {
    // Handle rate limit (429) with the specific error message from backend
    if (error.status === 429) {
      throw new Error(error.message || 'Rate limit exceeded. Please try again later.');
    }
    throw new Error(error.message || 'Failed to test API key');
  }
}

/**
 * Delete user's API key.
 */
export async function deleteApiKey(): Promise<DeleteApiKeyResponse> {
  try {
    return await httpClient.delete<DeleteApiKeyResponse>(`${API_BASE_URL}/api/user-api-keys/current`);
  } catch (error: any) {
    if (error.status === 404) {
      throw new Error('No API key found to delete');
    }
    throw new Error(error.message || 'Failed to delete API key');
  }
}
