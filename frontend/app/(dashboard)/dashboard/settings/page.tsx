'use client';

import { useState, useEffect } from 'react';
import { Settings as SettingsIcon, Save, Trash2 } from 'lucide-react';
import { ApiKeyInput } from '@/components/settings/ApiKeyInput';
import { ApiKeyStatus } from '@/components/settings/ApiKeyStatus';
import { TestConnectionButton } from '@/components/settings/TestConnectionButton';
import { useApiKey } from '@/lib/hooks/useApiKey';
import { useSession } from '@/lib/auth-client';

export default function SettingsPage() {
  const { data: session } = useSession();
  const {
    status,
    loading,
    error: apiError,
    testStatus,
    fetchStatus,
    saveApiKey: saveApiKeyAction,
    testConnection: testConnectionAction,
    deleteApiKey: deleteApiKeyAction,
    clearError,
  } = useApiKey();

  const [apiKey, setApiKey] = useState('');
  const [notification, setNotification] = useState<{
    type: 'success' | 'error';
    message: string;
  } | null>(null);

  // Fetch API key status on mount
  useEffect(() => {
    if (session?.session?.token) {
      fetchStatus();
    }
  }, [session?.session?.token, fetchStatus]);

  const handleSave = async () => {
    if (!apiKey.trim()) {
      setNotification({
        type: 'error',
        message: 'Please enter an API key',
      });
      setTimeout(() => setNotification(null), 5000);
      return;
    }

    clearError();

    try {
      await saveApiKeyAction(apiKey);

      setNotification({
        type: 'success',
        message: 'API key saved successfully',
      });

      setApiKey('');
      setTimeout(() => setNotification(null), 5000);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to save API key';
      setNotification({
        type: 'error',
        message: errorMessage,
      });
      setTimeout(() => setNotification(null), 5000);
    }
  };

  const handleTestConnection = async () => {
    const keyToTest = apiKey.trim() || '';

    if (!keyToTest && !status.configured) {
      setNotification({
        type: 'error',
        message: 'Please enter an API key first',
      });
      setTimeout(() => setNotification(null), 5000);
      return;
    }

    clearError();

    try {
      // Test with entered key or fetch from backend if already saved
      await testConnectionAction(keyToTest);

      setNotification({
        type: 'success',
        message: testStatus.message || 'API key is valid and working',
      });

      setTimeout(() => setNotification(null), 5000);
    } catch (err) {
      const errorMessage = testStatus.message || (err instanceof Error ? err.message : 'Connection test failed');
      setNotification({
        type: 'error',
        message: errorMessage,
      });
      setTimeout(() => setNotification(null), 5000);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to remove your API key? AI features will be disabled.')) {
      return;
    }

    clearError();

    try {
      await deleteApiKeyAction();

      setNotification({
        type: 'success',
        message: 'API key removed successfully',
      });

      setTimeout(() => setNotification(null), 5000);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to remove API key';
      setNotification({
        type: 'error',
        message: errorMessage,
      });
      setTimeout(() => setNotification(null), 5000);
    }
  };

  return (
    <>
      {/* Page Header */}
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 rounded-lg bg-indigo-600">
            <SettingsIcon size={20} className="text-white" strokeWidth={2} />
          </div>
          <h1 className="text-2xl font-bold text-slate-900">
            Settings
          </h1>
        </div>
        <p className="text-slate-700">
          Manage your application preferences and API configuration
        </p>
      </div>

      {/* Notification */}
      {notification && (
        <div
          className={`
            mb-6 p-4 rounded-lg border-2 animate-in slide-in-from-top-2 fade-in duration-300
            ${
              notification.type === 'success'
                ? 'bg-emerald-50 border-emerald-300 text-emerald-900'
                : 'bg-red-50 border-red-300 text-red-900'
            }
          `}
        >
          <p className="text-sm font-semibold">{notification.message}</p>
        </div>
      )}

      {/* Main Content */}
      <div className="space-y-6">
        {/* API Key Management Section */}
        <section className="bg-white rounded-lg border-2 border-slate-200 shadow-sm overflow-hidden">
          <div className="border-b-2 border-slate-200 bg-slate-50 px-6 py-4">
            <h2 className="text-lg font-bold text-slate-900">
              API Key Management
            </h2>
            <p className="text-sm text-slate-700 mt-1">
              Configure your Gemini API key for AI-powered features
            </p>
          </div>

          <div className="p-6 space-y-6">
            {/* Status Card */}
            <ApiKeyStatus
              configured={status.configured}
              maskedKey={status.maskedKey}
              validationStatus={status.validationStatus}
              lastValidatedAt={status.lastValidatedAt}
            />

            {/* API Key Input */}
            <div className="space-y-4">
              <ApiKeyInput
                value={apiKey}
                onChange={setApiKey}
                error={apiError || ''}
              />

              {/* Action Buttons */}
              <div className="flex flex-wrap gap-3 pt-2">
                <button
                  type="button"
                  onClick={handleSave}
                  disabled={loading || !apiKey}
                  className={`
                    flex items-center gap-2 px-5 py-2.5 rounded-lg
                    font-medium text-sm transition-all
                    ${
                      loading || !apiKey
                        ? 'bg-slate-100 text-slate-400 cursor-not-allowed'
                        : 'bg-indigo-600 hover:bg-indigo-700 text-white shadow-sm active:scale-95'
                    }
                  `}
                >
                  <Save size={18} strokeWidth={2} />
                  <span>{loading ? 'Saving...' : 'Save API Key'}</span>
                </button>

                <TestConnectionButton
                  onClick={handleTestConnection}
                  loading={testStatus.testing}
                  disabled={!apiKey && !status.configured}
                />

                {status.configured && (
                  <button
                    type="button"
                    onClick={handleDelete}
                    disabled={loading}
                    className="
                      flex items-center gap-2 px-5 py-2.5 rounded-lg
                      font-medium text-sm
                      border border-red-200
                      bg-white
                      text-red-600
                      hover:bg-red-50
                      hover:border-red-300
                      transition-all
                      active:scale-95
                      disabled:opacity-50 disabled:cursor-not-allowed
                    "
                  >
                    <Trash2 size={18} strokeWidth={2} />
                    <span>Remove Key</span>
                  </button>
                )}
              </div>
            </div>

            {/* Help Text */}
            <div className="pt-4 border-t border-slate-200">
              <p className="text-sm text-slate-700">
                <strong className="font-bold">Note:</strong> Your API key is encrypted and stored securely.
                It will only be used for AI-powered features within this application.{' '}
                <a
                  href="https://aistudio.google.com/apikey"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-indigo-600 hover:text-indigo-800 underline font-semibold"
                >
                  Get your API key →
                </a>
              </p>
            </div>
          </div>
        </section>
      </div>
    </>
  );
}
