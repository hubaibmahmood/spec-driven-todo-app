'use client';

import { useState } from 'react';
import { Eye, EyeOff } from 'lucide-react';

interface PasswordInputProps {
  id: string;
  label: string;
  value: string;
  onChange: (value: string) => void;
  error?: string;
  helperText?: string;
  placeholder?: string;
  required?: boolean;
  className?: string;
}

export function PasswordInput({
  id,
  label,
  value,
  onChange,
  error,
  helperText,
  placeholder = '',
  required = false,
  className = '',
}: PasswordInputProps) {
  const [showPassword, setShowPassword] = useState(false);

  return (
    <div className={`w-full ${className}`}>
      <label
        htmlFor={id}
        className="block text-sm font-semibold text-slate-900 mb-2"
      >
        {label}
        {required && <span className="text-red-500 ml-1">*</span>}
      </label>

      <div className="relative group">
        <input
          id={id}
          type={showPassword ? 'text' : 'password'}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          required={required}
          // Security attributes
          autoComplete="off"
          spellCheck="false"
          data-lpignore="true"
          data-1p-ignore="true"
          // Accessibility
          aria-label={label}
          aria-describedby={error ? `${id}-error` : helperText ? `${id}-hint` : undefined}
          aria-invalid={!!error}
          className={`
            w-full px-4 py-3 pr-12
            font-mono text-sm tracking-tight
            bg-white
            border-2 rounded-lg
            transition-all duration-200
            ${
              error
                ? 'border-red-400 focus:border-red-500 focus:ring-4 focus:ring-red-100'
                : 'border-slate-300 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-100'
            }
            placeholder:text-slate-400
            text-slate-900
            disabled:opacity-50 disabled:cursor-not-allowed
            hover:border-slate-400
          `}
        />

        <button
          type="button"
          onClick={() => setShowPassword(!showPassword)}
          aria-label={showPassword ? 'Hide password' : 'Show password'}
          aria-pressed={showPassword}
          className="
            absolute right-3 top-1/2 -translate-y-1/2
            p-2 rounded-md
            text-slate-500
            hover:text-slate-700
            hover:bg-slate-100
            transition-all duration-200
            focus:outline-none focus:ring-2 focus:ring-indigo-500
          "
        >
          {showPassword ? (
            <EyeOff size={18} aria-hidden="true" strokeWidth={2} />
          ) : (
            <Eye size={18} aria-hidden="true" strokeWidth={2} />
          )}
        </button>
      </div>

      {error && (
        <p
          id={`${id}-error`}
          className="mt-2 text-sm text-red-700 flex items-start gap-1.5"
          role="alert"
        >
          <span className="text-red-500 mt-0.5">⚠</span>
          <span>{error}</span>
        </p>
      )}

      {helperText && !error && (
        <p
          id={`${id}-hint`}
          className="mt-2 text-sm text-slate-600"
        >
          {helperText}
        </p>
      )}
    </div>
  );
}
