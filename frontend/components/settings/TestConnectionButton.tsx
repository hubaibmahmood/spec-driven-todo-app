'use client';

import { Loader2, Zap } from 'lucide-react';

interface TestConnectionButtonProps {
  onClick: () => void;
  loading: boolean;
  disabled?: boolean;
  className?: string;
}

export function TestConnectionButton({
  onClick,
  loading,
  disabled = false,
  className = '',
}: TestConnectionButtonProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled || loading}
      className={`
        group relative
        px-6 py-3 rounded-lg
        font-medium text-sm
        border-2
        transition-all duration-200
        ${
          disabled || loading
            ? 'bg-slate-100 border-slate-300 text-slate-500 cursor-not-allowed'
            : 'bg-white border-indigo-600 text-indigo-700 hover:bg-indigo-50 hover:shadow-sm active:scale-95'
        }
        ${className}
      `}
    >
      <span className="flex items-center gap-2">
        {loading ? (
          <>
            <Loader2 size={18} className="animate-spin" strokeWidth={2} />
            <span>Testing...</span>
          </>
        ) : (
          <>
            <Zap size={18} strokeWidth={2} className="group-hover:scale-110 transition-transform" />
            <span>Test Connection</span>
          </>
        )}
      </span>
    </button>
  );
}
