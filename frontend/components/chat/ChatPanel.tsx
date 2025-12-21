// Chat panel component using OpenAI ChatKit React SDK
// Spec: 009-frontend-chat-integration - User Story 2 (T039-T045, T050)

'use client';

import React, { useEffect, useCallback } from 'react';
import { ChatKit, useChatKit } from '@openai/chatkit-react';
import { useSession } from '@/lib/auth-client';
import { getUserTimezone } from '@/lib/utils/timezone';

interface ChatPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function ChatPanel({ isOpen, onClose }: ChatPanelProps) {
  const { data: session } = useSession();
  const sessionToken = session?.session?.token;
  const isAuthenticated = !!sessionToken;

  // Custom fetch function to add authentication headers
  const authenticatedFetch = useCallback(
    async (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
      const headers = new Headers(init?.headers);

      // Add authentication header
      if (sessionToken) {
        headers.set('Authorization', `Bearer ${sessionToken}`);
      }

      // Add timezone header
      const timezone = getUserTimezone();
      headers.set('X-Timezone', timezone);

      return fetch(input, {
        ...init,
        headers,
      });
    },
    [sessionToken]
  );

  // Initialize ChatKit with authentication
  const { control } = useChatKit({
    api: {
      url: `${process.env.NEXT_PUBLIC_API_URL || ''}/api/chat`,
      domainKey: process.env.NEXT_PUBLIC_DOMAIN_KEY || 'local-dev',
      fetch: authenticatedFetch,
    },
    header: {
      enabled: true,
      title: {
        text: 'AI Assistant',
      },
      rightAction: {
        icon: 'close' as any,
        onClick: onClose,
      },
    },
    composer: {
      placeholder: 'Type a message to create or manage tasks...',
    },
    startScreen: {
      greeting: 'How can I help you manage your tasks?',
      prompts: [
        {
          label: 'Add a task',
          prompt: 'Add a new task',
          icon: 'plus' as any,
        },
        {
          label: 'List my tasks',
          prompt: 'Show me all my tasks',
          icon: 'list' as any,
        },
        {
          label: 'Update a task',
          prompt: 'Update an existing task',
          icon: 'edit' as any,
        },
      ],
    },
    threadItemActions: {
      feedback: true,
      retry: true,
    },
  });

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
  if (!isAuthenticated) {
    return (
      <div
        className="fixed right-0 top-0 z-40 flex h-screen w-full flex-col bg-white shadow-xl transition-transform duration-300 md:w-96"
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

  // Render ChatKit component
  return (
    <div
      className="fixed right-0 top-0 z-40 h-screen w-full bg-white shadow-xl transition-transform duration-300 md:w-96"
      role="dialog"
      aria-label="Chat panel"
    >
      <ChatKit control={control} className="h-full w-full" />
    </div>
  );
}
