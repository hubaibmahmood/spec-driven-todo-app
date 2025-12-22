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
  const isPending = metadata?.status === 'pending';
  const isGuidance = metadata?.status === 'guidance';
  const errorMessage = metadata?.errorMessage;
  const examples = metadata?.examples;

  return (
    <div
      data-role={role}
      className={`mb-4 flex ${isUser ? 'justify-end' : 'justify-start'}`}
      role="article"
      aria-label={`${isUser ? 'Your' : 'Assistant'} message from ${formattedTime}`}
    >
      <div
        className={`max-w-[80%] rounded-lg px-4 py-2 ${
          isUser
            ? 'bg-blue-600 text-white'
            : hasError
            ? 'bg-red-50 text-red-800 border border-red-300'
            : isPending
            ? 'bg-yellow-50 text-yellow-800 border border-yellow-300'
            : isGuidance
            ? 'bg-blue-50 text-blue-800 border border-blue-300'
            : 'bg-gray-100 text-gray-900'
        }`}
        role={isPending ? 'status' : undefined}
        aria-live={isPending ? 'polite' : undefined}
        aria-busy={isPending}
      >
        {/* Message content */}
        <div className="mb-1 whitespace-pre-wrap break-words text-sm">
          {isPending ? (
            <div className="flex items-center gap-2">
              <svg
                className="h-4 w-4 animate-spin text-yellow-600"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
              <span>{content}</span>
            </div>
          ) : (
            content
          )}
        </div>

        {/* Error message display (if operation failed) */}
        {hasError && errorMessage && (
          <div
            className="mt-2 flex items-start border-t border-red-200 pt-2 text-xs"
            role="alert"
            aria-live="assertive"
          >
            <svg
              className="mr-1 mt-0.5 h-4 w-4 flex-shrink-0 text-red-600"
              fill="currentColor"
              viewBox="0 0 20 20"
              aria-hidden="true"
            >
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                clipRule="evenodd"
              />
            </svg>
            <span>⚠️ {errorMessage}</span>
          </div>
        )}

        {/* Examples display (for guidance messages) */}
        {isGuidance && examples && examples.length > 0 && (
          <div className="mt-3 border-t border-blue-200 pt-3" role="region" aria-label="Examples">
            <div className="mb-2 text-xs font-semibold text-blue-800">Try these examples:</div>
            <ul className="space-y-2 text-xs" role="list">
              {examples.map((example, index) => (
                <li
                  key={index}
                  className="flex items-start rounded bg-white px-2 py-1.5 text-blue-700"
                >
                  <span className="mr-2 text-blue-400" aria-hidden="true">
                    •
                  </span>
                  <span className="italic">"{example}"</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Timestamp */}
        <time
          dateTime={timestamp.toISOString()}
          className={`mt-1 block text-xs ${
            isUser
              ? 'text-blue-100'
              : hasError
              ? 'text-red-700'
              : isGuidance
              ? 'text-blue-700'
              : 'text-gray-600'
          }`}
          aria-label={`Sent at ${formattedTime}`}
        >
          {formattedTime}
        </time>
      </div>
    </div>
  );
}
