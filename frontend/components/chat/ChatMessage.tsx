// Chat message component with role-based styling and timestamp
// Spec: 009-frontend-chat-integration - User Story 2 (T034-T037)

'use client';

import React from 'react';
import { formatInTimeZone } from 'date-fns-tz';
import type { Message } from '@/types/chat';
import { getUserTimezone } from '@/lib/utils/timezone';

interface ChatMessageProps {
  message: Message;
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const { content, role, timestamp, metadata } = message;
  const isUser = role === 'user';
  const isAssistant = role === 'assistant';

  // Format timestamp in user's local timezone
  const userTimezone = getUserTimezone();
  const formattedTime = formatInTimeZone(
    timestamp,
    userTimezone,
    'MMM d, h:mm a' // e.g., "Dec 21, 2:30 PM"
  );

  // Determine if there's an error to display
  const hasError = metadata?.status === 'error';
  const errorMessage = metadata?.errorMessage;

  return (
    <div
      data-role={role}
      className={`mb-4 flex ${isUser ? 'justify-end' : 'justify-start'}`}
    >
      <div
        className={`max-w-[80%] rounded-lg px-4 py-2 ${
          isUser
            ? 'bg-blue-600 text-white'
            : hasError
            ? 'bg-red-50 text-red-900 border border-red-200'
            : 'bg-gray-100 text-gray-900'
        }`}
      >
        {/* Message content */}
        <div className="mb-1 whitespace-pre-wrap break-words text-sm">{content}</div>

        {/* Error message display (if operation failed) */}
        {hasError && errorMessage && (
          <div className="mt-2 flex items-start border-t border-red-200 pt-2 text-xs">
            <svg
              className="mr-1 mt-0.5 h-4 w-4 flex-shrink-0"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                clipRule="evenodd"
              />
            </svg>
            <span>{errorMessage}</span>
          </div>
        )}

        {/* Success indicator (if operation succeeded) */}
        {metadata?.status === 'success' && metadata.operation && (
          <div className="mt-2 flex items-center text-xs text-gray-600">
            <svg
              className="mr-1 h-4 w-4 text-green-600"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                clipRule="evenodd"
              />
            </svg>
            <span className="text-green-700">✓</span>
          </div>
        )}

        {/* Timestamp */}
        <div
          className={`mt-1 text-xs ${
            isUser ? 'text-blue-100' : hasError ? 'text-red-600' : 'text-gray-500'
          }`}
        >
          {formattedTime}
        </div>
      </div>
    </div>
  );
}
