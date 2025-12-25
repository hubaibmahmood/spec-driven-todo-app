'use client';

import { PasswordInput } from '@/components/ui/PasswordInput';

interface ApiKeyInputProps {
  value: string;
  onChange: (value: string) => void;
  error?: string;
  className?: string;
}

export function ApiKeyInput({
  value,
  onChange,
  error,
  className = '',
}: ApiKeyInputProps) {
  return (
    <PasswordInput
      id="gemini-api-key"
      label="Gemini API Key"
      value={value}
      onChange={onChange}
      error={error}
      helperText="Enter your API key from Google AI Studio"
      placeholder="AIza..."
      required
      className={className}
    />
  );
}
