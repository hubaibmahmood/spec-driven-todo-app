'use client';

import React from 'react';
import { Sparkles } from 'lucide-react';

interface ChatToggleButtonProps {
  onClick: () => void;
  isOpen?: boolean;
}

export default function ChatToggleButton({ onClick, isOpen = false }: ChatToggleButtonProps) {
  if (isOpen) return null;

  return (
    <button
      onClick={onClick}
      aria-label="Open chat panel"
      aria-expanded={isOpen}
      title="Chat with AI assistant"
      className="fixed bottom-6 right-6 z-50 flex h-12 w-12 items-center justify-center rounded-full bg-indigo-600 text-white shadow-[0_4px_14px_rgba(99,102,241,0.4)] transition-all hover:bg-indigo-700 hover:scale-105 hover:shadow-[0_6px_20px_rgba(99,102,241,0.5)] focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
    >
      <Sparkles className="h-5 w-5" />
    </button>
  );
}
