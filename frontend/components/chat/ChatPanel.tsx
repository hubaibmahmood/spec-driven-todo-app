// Chat panel component with custom backend integration
// Spec: 009-frontend-chat-integration - Phase 5 (User Story 3)

'use client';

import React, { useEffect } from 'react';
import { isAuthenticated } from '@/lib/jwt-auth-client';
import { MyAssistant } from './MyAssistant';

interface ChatPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function ChatPanel({ isOpen, onClose }: ChatPanelProps) {
  const userAuthenticated = isAuthenticated();

  // Handle ESC key to close panel
  useEffect(() => {
    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && isOpen) {
        onClose();
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => {
      document.removeEventListener('keydown', handleEscape);
    };
  }, [isOpen, onClose]);

  // Don't render if not open
  if (!isOpen) {
    return null;
  }

  // Show authentication error if not authenticated
  if (!userAuthenticated) {
    return (
      <div
        className="fixed bottom-6 right-6 z-40 flex h-[650px] w-[400px] flex-col overflow-hidden rounded-2xl border border-gray-300 bg-white shadow-[0_8px_30px_rgb(0,0,0,0.12)] transition-all duration-300"
        role="dialog"
        aria-label="Chat panel"
      >
        <div className="flex items-center justify-between border-b border-gray-200 bg-blue-600 p-4 text-white">
          <h2 className="text-lg font-semibold">AI Assistant</h2>
          <button
            onClick={onClose}
            className="rounded-full p-1 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-white"
            aria-label="Close chat panel"
          >
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
          </button>
        </div>

        <div className="mx-4 mt-4 rounded-lg bg-red-50 p-4 text-red-800" role="alert">
          <div className="flex items-start">
            <svg
              className="mr-3 h-5 w-5 flex-shrink-0"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                clipRule="evenodd"
              />
            </svg>
            <div>
              <h3 className="text-sm font-medium">Authentication Required</h3>
              <p className="mt-1 text-sm">Please log in to use the chat feature.</p>
              <button
                onClick={() => (window.location.href = '/login')}
                className="mt-3 rounded bg-red-600 px-4 py-2 text-sm text-white hover:bg-red-700"
              >
                Go to Login
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div
      className="fixed bottom-6 right-6 z-40 flex h-[650px] w-[400px] flex-col overflow-hidden rounded-2xl border border-gray-300 bg-white shadow-[0_8px_30px_rgb(0,0,0,0.12)] transition-all duration-300"
      role="dialog"
      aria-label="AI Assistant Chat Panel"
      aria-modal="true"
    >
      {/* Header */}
      <header className="flex items-center justify-between border-b border-gray-200 bg-blue-600 p-4 text-white">
        <h2 className="text-lg font-semibold">AI Assistant</h2>
        <button
          onClick={onClose}
          className="rounded-full p-1 transition-colors hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-blue-600"
          aria-label="Close chat panel"
        >
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
        </button>
      </header>

      {/* Main Content using assistant-ui */}
      <div className="flex-1 overflow-hidden">
        <MyAssistant />
      </div>
    </div>
  );
}
