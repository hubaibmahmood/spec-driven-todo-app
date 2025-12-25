'use client';

import { CheckCircle2, XCircle, Info, Key } from 'lucide-react';

interface ApiKeyStatusProps {
  configured: boolean;
  maskedKey?: string | null;
  validationStatus?: string | null;
  lastValidatedAt?: string | null;
  className?: string;
}

export function ApiKeyStatus({
  configured,
  maskedKey,
  validationStatus,
  lastValidatedAt,
  className = '',
}: ApiKeyStatusProps) {
  const getStatusIcon = () => {
    if (!validationStatus) {
      return <Info size={20} className="text-slate-400" strokeWidth={2} />;
    }
    if (validationStatus === 'success') {
      return <CheckCircle2 size={20} className="text-emerald-500" strokeWidth={2} />;
    }
    return <XCircle size={20} className="text-red-500" strokeWidth={2} />;
  };

  const getStatusText = () => {
    if (!validationStatus) return 'Not tested';
    if (validationStatus === 'success') return 'Verified';
    return 'Failed';
  };

  const getStatusColor = () => {
    if (!validationStatus) return 'text-slate-700';
    if (validationStatus === 'success') return 'text-emerald-700';
    return 'text-red-700';
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return null;
    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

    if (diffInSeconds < 60) return 'Just now';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
    if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)}d ago`;

    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined,
    });
  };

  if (!configured) {
    return (
      <div className={`
        p-6 rounded-lg border-2 border-dashed border-slate-300
        bg-slate-50
        ${className}
      `}>
        <div className="flex items-start gap-3">
          <div className="p-2 rounded-lg bg-slate-200">
            <Key size={20} className="text-slate-600" strokeWidth={2} />
          </div>
          <div className="flex-1 min-w-0">
            <h3 className="text-sm font-semibold text-slate-900 mb-1">
              No API Key Configured
            </h3>
            <p className="text-sm text-slate-700">
              Add your Gemini API key to enable AI features
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`
      p-6 rounded-lg border-2 border-slate-200
      bg-white
      shadow-sm
      ${className}
    `}>
      <div className="space-y-4">
        {/* Status Header */}
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-start gap-3 flex-1 min-w-0">
            <div className="p-2 rounded-lg bg-indigo-100">
              <Key size={20} className="text-indigo-600" strokeWidth={2} />
            </div>
            <div className="flex-1 min-w-0">
              <h3 className="text-sm font-semibold text-slate-900 mb-1">
                API Key Configured
              </h3>
              {maskedKey && (
                <code className="text-sm font-mono text-slate-800 bg-slate-100 px-2 py-1 rounded">
                  {maskedKey}
                </code>
              )}
            </div>
          </div>

          {/* Validation Badge */}
          <div className={`
            flex items-center gap-2 px-3 py-1.5 rounded-full
            border-2 ${
              validationStatus === 'success'
                ? 'border-emerald-300 bg-emerald-50'
                : validationStatus === 'failure'
                ? 'border-red-300 bg-red-50'
                : 'border-slate-300 bg-slate-50'
            }
          `}>
            {getStatusIcon()}
            <span className={`text-xs font-semibold ${getStatusColor()}`}>
              {getStatusText()}
            </span>
          </div>
        </div>

        {/* Last Validated */}
        {lastValidatedAt && (
          <div className="pt-4 border-t border-slate-200">
            <p className="text-xs text-slate-700">
              Last tested <span className="font-semibold">{formatDate(lastValidatedAt)}</span>
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
