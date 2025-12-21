// Chat toggle button component
// Spec: 009-frontend-chat-integration - User Story 1

'use client';

import React from 'react';

interface ChatToggleButtonProps {
  onClick: () => void;
  isOpen?: boolean;
}

export default function ChatToggleButton({ onClick, isOpen = false }: ChatToggleButtonProps) {
  return (
    <button
      onClick={onClick}
      aria-label={isOpen ? 'Close chat panel' : 'Toggle chat panel'}
      className="fixed bottom-6 right-6 z-50 flex h-14 w-14 items-center justify-center rounded-full bg-blue-600 text-white shadow-lg transition-all hover:bg-blue-700 hover:scale-110 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 md:h-16 md:w-16"
      title="Chat with AI assistant"
    >
      {isOpen ? (
        // Close icon (X)
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="h-6 w-6"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={2}
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
        </svg>
      ) : (
        // Chat icon (message bubble)
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="h-6 w-6"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={2}
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
          />
        </svg>
      )}
    </button>
  );
}
