/**
 * React hook for API key state management.
 * Handles loading, error, and success states for API key operations.
 */

import { useState, useCallback } from 'react';
import {
  getCurrentApiKey,
  saveApiKey as saveApiKeyApi,
  testApiKey as testApiKeyApi,
  deleteApiKey as deleteApiKeyApi,
} from '@/lib/api/apiKeys';

interface ApiKeyStatus {
  configured: boolean;
  provider?: string | null;
  maskedKey?: string | null;
  validationStatus?: string | null;
  lastValidatedAt?: string | null;
  createdAt?: string | null;
  updatedAt?: string | null;
}

interface UseApiKeyReturn {
  // State
  status: ApiKeyStatus;
  loading: boolean;
  error: string | null;
  testStatus: {
    testing: boolean;
    result: 'success' | 'failure' | null;
    message: string | null;
  };

  // Actions
  fetchStatus: () => Promise<void>;
  saveApiKey: (apiKey: string) => Promise<void>;
  testConnection: (apiKey: string) => Promise<void>;
  deleteApiKey: () => Promise<void>;
  clearError: () => void;
}

export function useApiKey(): UseApiKeyReturn {
  const [status, setStatus] = useState<ApiKeyStatus>({
    configured: false,
    provider: null,
    maskedKey: null,
    validationStatus: null,
    lastValidatedAt: null,
    createdAt: null,
    updatedAt: null,
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [testStatus, setTestStatus] = useState<{
    testing: boolean;
    result: 'success' | 'failure' | null;
    message: string | null;
  }>({
    testing: false,
    result: null,
    message: null,
  });

  /**
   * Fetch current API key status.
   */
  const fetchStatus = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await getCurrentApiKey();

      setStatus({
        configured: data.configured,
        provider: data.provider,
        maskedKey: data.masked_key,
        validationStatus: data.validation_status,
        lastValidatedAt: data.last_validated_at,
        createdAt: data.created_at,
        updatedAt: data.updated_at,
      });
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to fetch API key status';
      setError(message);
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Save or update API key.
   *
   * Since the backend now auto-validates the key on save, we fetch the
   * updated status to get the validation result and timestamp.
   */
  const saveApiKey = useCallback(async (apiKey: string) => {
    setLoading(true);
    setError(null);

    try {
      await saveApiKeyApi(apiKey);

      // Fetch the updated status from backend to get validation result
      // The backend auto-validates on save, so this will have validation_status='success'
      // and the correct last_validated_at timestamp
      const statusData = await getCurrentApiKey();

      setStatus({
        configured: statusData.configured,
        provider: statusData.provider,
        maskedKey: statusData.masked_key,
        validationStatus: statusData.validation_status,
        lastValidatedAt: statusData.last_validated_at,
        createdAt: statusData.created_at,
        updatedAt: statusData.updated_at,
      });
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to save API key';
      setError(message);
      throw err; // Re-throw so caller can handle
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Test API key connectivity.
   */
  const testConnection = useCallback(async (apiKey: string) => {
    setTestStatus({
      testing: true,
      result: null,
      message: null,
    });
    setError(null);

    try {
      const data = await testApiKeyApi(apiKey);

      const result = data.validation_status === 'success' ? 'success' : 'failure';

      setTestStatus({
        testing: false,
        result,
        message: data.message,
      });

      // Update status with validation result
      setStatus(prev => ({
        ...prev,
        validationStatus: data.validation_status,
        lastValidatedAt: new Date().toISOString(),
      }));
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to test API key';

      setTestStatus({
        testing: false,
        result: 'failure',
        message,
      });

      setError(message);
      throw err; // Re-throw so caller can handle
    }
  }, []);

  /**
   * Delete API key.
   */
  const deleteApiKey = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      await deleteApiKeyApi();

      // Reset status after successful delete
      setStatus({
        configured: false,
        provider: null,
        maskedKey: null,
        validationStatus: null,
        lastValidatedAt: null,
        createdAt: null,
        updatedAt: null,
      });

      // Reset test status
      setTestStatus({
        testing: false,
        result: null,
        message: null,
      });
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to delete API key';
      setError(message);
      throw err; // Re-throw so caller can handle
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Clear error state.
   */
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    status,
    loading,
    error,
    testStatus,
    fetchStatus,
    saveApiKey,
    testConnection,
    deleteApiKey,
    clearError,
  };
}
