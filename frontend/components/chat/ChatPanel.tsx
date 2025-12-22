// Chat panel component with custom backend integration
// Spec: 009-frontend-chat-integration - Phase 5 (User Story 3)

'use client';

import React, { useEffect, useCallback, useState, useRef } from 'react';
import { useSession } from '@/lib/auth-client';
import { getUserTimezone } from '@/lib/utils/timezone';
import { validateChatInput } from '@/lib/chat/input-validation';
import { fetchWithRetry } from '@/lib/chat/retry-logic';
import { detectDestructiveOperation } from '@/lib/chat/destructive-detection';
import type { Message } from '@/types/chat';
import ChatMessage from './ChatMessage';
import ConfirmationModal from './ConfirmationModal';
import { useTasks } from '@/hooks/useTasks';

interface ChatPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function ChatPanel({ isOpen, onClose }: ChatPanelProps) {
  const { data: session } = useSession();
  const sessionToken = session?.session?.token;
  const userId = session?.user?.id;
  const isAuthenticated = !!sessionToken;

  const [messages, setMessages] = useState<Message[]>([]);
  const [conversationId, setConversationId] = useState<number | null>(null);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasMore, setHasMore] = useState(false);
  const [offset, setOffset] = useState(0);
  const [sessionExpired, setSessionExpired] = useState(false);
  const [pendingMessage, setPendingMessage] = useState<string | null>(null); // Store message when session expires
  const [retryCount, setRetryCount] = useState(0);
  const [isRetrying, setIsRetrying] = useState(false);
  const [showConfirmation, setShowConfirmation] = useState(false);
  const [confirmationData, setConfirmationData] = useState<{
    message: string;
    confirmationMessage: string;
    estimatedAffected?: string;
  } | null>(null);
  const [isRateLimited, setIsRateLimited] = useState(false); // Show rate limit feedback
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);
  const { refreshTodos } = useTasks();
  const hasLoadedHistory = useRef(false);
  const shouldAutoScroll = useRef(true); // Track whether to auto-scroll
  const lastSendTimeRef = useRef<number>(0); // Track last send time for rate limiting
  const debounceTimerRef = useRef<NodeJS.Timeout | null>(null); // Debounce timer
  const rateLimitFeedbackTimerRef = useRef<NodeJS.Timeout | null>(null); // Feedback timer

  // Auto-scroll to bottom only when sending new messages (not when loading more)
  useEffect(() => {
    if (shouldAutoScroll.current) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
    // Reset to true after scrolling (or not scrolling)
    shouldAutoScroll.current = true;
  }, [messages]);

  // Handle session restoration after re-authentication
  useEffect(() => {
    if (isAuthenticated && sessionExpired) {
      // Session restored - clear expired flag
      setSessionExpired(false);

      // Retry pending message if exists
      if (pendingMessage) {
        const message = pendingMessage;
        setPendingMessage(null);
        handleSendMessage(message);
      }
    }
  }, [isAuthenticated, sessionExpired, pendingMessage]);

  // Load conversation history when panel opens
  useEffect(() => {
    const loadConversationHistory = async () => {
      if (!isOpen || !sessionToken || hasLoadedHistory.current) return;

      setIsLoadingHistory(true);
      try {
        const AI_AGENT_URL = process.env.NEXT_PUBLIC_AI_AGENT_URL || 'http://localhost:8002';
        const response = await fetch(`${AI_AGENT_URL}/api/conversations`, {
          headers: {
            'Authorization': `Bearer ${sessionToken}`,
          },
        });

        if (!response.ok) {
          console.error('Failed to load conversations');
          return;
        }

        const conversations = await response.json();

        // Load the most recent conversation if exists
        if (conversations && conversations.length > 0) {
          const latestConversation = conversations[0];
          setConversationId(latestConversation.id);

          // Fetch conversation messages with pagination (limit=5 for testing, offset=0)
          const detailResponse = await fetch(
            `${AI_AGENT_URL}/api/conversations/${latestConversation.id}?limit=5&offset=0`,
            {
              headers: {
                'Authorization': `Bearer ${sessionToken}`,
              },
            }
          );

          if (detailResponse.ok) {
            const conversationDetail = await detailResponse.json();
            const loadedMessages: Message[] = conversationDetail.messages.map((msg: any) => ({
              id: String(msg.id),
              conversationId: String(latestConversation.id),
              content: msg.content,
              role: msg.role,
              timestamp: new Date(msg.created_at),
            }));

            shouldAutoScroll.current = false; // Don't auto-scroll when loading history
            setMessages(loadedMessages);
            setHasMore(conversationDetail.has_more || false);
            setOffset(loadedMessages.length);
          }
        }

        hasLoadedHistory.current = true;
      } catch (err) {
        console.error('Failed to load conversation history:', err);
      } finally {
        setIsLoadingHistory(false);
      }
    };

    loadConversationHistory();
  }, [isOpen, sessionToken]);

  // Load more messages (pagination)
  const loadMoreMessages = useCallback(async () => {
    if (!conversationId || !sessionToken || isLoadingMore || !hasMore) return;

    setIsLoadingMore(true);

    try {
      const AI_AGENT_URL = process.env.NEXT_PUBLIC_AI_AGENT_URL || 'http://localhost:8002';

      // Save current scroll position before loading
      const container = messagesContainerRef.current;
      const scrollTopBefore = container?.scrollTop || 0;
      const scrollHeightBefore = container?.scrollHeight || 0;

      const response = await fetch(
        `${AI_AGENT_URL}/api/conversations/${conversationId}?limit=5&offset=${offset}`,
        {
          headers: {
            'Authorization': `Bearer ${sessionToken}`,
          },
        }
      );

      if (response.ok) {
        const conversationDetail = await response.json();
        const olderMessages: Message[] = conversationDetail.messages.map((msg: any) => ({
          id: String(msg.id),
          conversationId: String(conversationId),
          content: msg.content,
          role: msg.role,
          timestamp: new Date(msg.created_at),
        }));

        // Don't auto-scroll when loading more messages
        shouldAutoScroll.current = false;

        // Prepend older messages to maintain chronological order
        setMessages((prev) => [...olderMessages, ...prev]);
        setHasMore(conversationDetail.has_more || false);
        setOffset((prevOffset) => prevOffset + olderMessages.length);

        // Maintain scroll position after loading more messages
        setTimeout(() => {
          if (container) {
            const scrollHeightAfter = container.scrollHeight;
            const heightAdded = scrollHeightAfter - scrollHeightBefore;
            // Adjust scroll position by the height of content added
            container.scrollTop = scrollTopBefore + heightAdded;
          }
        }, 0);
      }
    } catch (err) {
      console.error('Failed to load more messages:', err);
    } finally {
      setIsLoadingMore(false);
    }
  }, [conversationId, sessionToken, offset, hasMore, isLoadingMore]);

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
      // Cleanup timers on unmount
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }
      if (rateLimitFeedbackTimerRef.current) {
        clearTimeout(rateLimitFeedbackTimerRef.current);
      }
    };
  }, [isOpen, onClose]);

  // Execute message send (internal function, bypasses confirmation)
  const executeSendMessage = useCallback(async (messageText: string) => {
    if (!sessionToken) return;

    const timezone = getUserTimezone();
    const tempUserMsgId = `temp-user-${Date.now()}`;
    const tempAssistantMsgId = `temp-assistant-${Date.now()}`;
    const tempProcessingMsgId = `temp-processing-${Date.now()}`;

    // Optimistic UI update - add user message immediately
    const userMessage: Message = {
      id: tempUserMsgId,
      conversationId: conversationId ? String(conversationId) : 'temp',
      content: messageText,
      role: 'user',
      timestamp: new Date(),
    };

    // Add processing indicator
    const processingMessage: Message = {
      id: tempProcessingMsgId,
      conversationId: conversationId ? String(conversationId) : 'temp',
      content: 'Processing your request...',
      role: 'assistant',
      timestamp: new Date(),
      metadata: {
        status: 'pending',
      },
    };

    setMessages((prev) => [...prev, userMessage, processingMessage]);
    setInputValue('');
    setIsLoading(true);
    setError(null);

    try {
      // Call AI agent chat endpoint with retry logic
      const AI_AGENT_URL = process.env.NEXT_PUBLIC_AI_AGENT_URL || 'http://localhost:8002';

      const data = await fetchWithRetry(
        async () => {
          const response = await fetch(`${AI_AGENT_URL}/api/chat`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${sessionToken}`,
              'X-Timezone': timezone,
            },
            body: JSON.stringify({
              message: messageText,
              conversation_id: conversationId, // null for first message
            }),
          });

          if (response.status === 401) {
            // Session expired - preserve state for retry after re-auth
            setSessionExpired(true);
            setPendingMessage(messageText);
            throw new Error('Session expired. Please log in again.');
          }

          if (!response.ok) {
            throw new Error(`Failed to send message: ${response.statusText}`);
          }

          return response.json();
        },
        {
          maxRetries: 3,
          initialDelay: 1000,
          maxDelay: 8000,
          backoffMultiplier: 2,
        }
      );

      // Save conversation ID from first response
      if (!conversationId && data.conversation_id) {
        setConversationId(data.conversation_id);
      }

      // Add assistant response
      const assistantMessage: Message = {
        id: tempAssistantMsgId,
        conversationId: String(data.conversation_id),
        content: data.assistant_message,
        role: 'assistant',
        timestamp: new Date(),
      };

      // Replace processing message with actual response
      setMessages((prev) =>
        prev
          .filter((msg) => msg.id !== tempProcessingMsgId)
          .concat(assistantMessage)
      );

      // Dispatch custom event to notify dashboard to refresh tasks
      // Use polling to ensure backend has completed the operation
      let refreshAttempts = 0;
      const maxAttempts = 5;
      const pollInterval = 400;

      const pollRefresh = async () => {
        refreshAttempts++;

        // Dispatch event to trigger refresh in all listening components
        window.dispatchEvent(new CustomEvent('tasks-updated'));

        // Continue polling if not at max attempts
        if (refreshAttempts < maxAttempts) {
          setTimeout(pollRefresh, pollInterval);
        }
      };

      // Start polling
      pollRefresh();

      // Reset retry count on success
      setRetryCount(0);
    } catch (err) {
      console.error('Failed to send message:', err);
      const errorMessage = err instanceof Error ? err.message : 'Failed to send message';
      setError(errorMessage);

      // Remove optimistic messages on error
      setMessages((prev) =>
        prev.filter((msg) => msg.id !== tempUserMsgId && msg.id !== tempProcessingMsgId)
      );

      // Store pending message for retry (if not session expired)
      if (!errorMessage.includes('Session expired') && !sessionExpired) {
        setPendingMessage(messageText);
      }

      // Show retry count if it was a network error
      if (errorMessage.includes('retries')) {
        setRetryCount(3); // Max retries exhausted
      }
    } finally {
      setIsLoading(false);
      setIsRetrying(false);
    }
  }, [sessionToken, conversationId, refreshTodos]);

  // Handle message send with validation and confirmation
  const handleSendMessage = useCallback(
    async (messageText: string) => {
      if (!sessionToken) return;

      // Validate input and provide guidance for ambiguous inputs
      const validation = validateChatInput(messageText);
      if (!validation.isValid) {
        // Show guidance message as an assistant message
        const guidanceMessage: Message = {
          id: `guidance-${Date.now()}`,
          conversationId: conversationId ? String(conversationId) : 'temp',
          content: validation.guidance || 'Please provide a valid message.',
          role: 'assistant',
          timestamp: new Date(),
          metadata: {
            status: 'guidance',
            examples: validation.examples,
          },
        };
        setMessages((prev) => [...prev, guidanceMessage]);
        setInputValue(''); // Clear input
        return;
      }

      // Check for destructive operations
      const destructiveInfo = detectDestructiveOperation(messageText);
      if (destructiveInfo.isDestructive) {
        // Show confirmation modal
        setConfirmationData({
          message: messageText,
          confirmationMessage:
            destructiveInfo.confirmationMessage || 'Are you sure you want to proceed?',
          estimatedAffected: destructiveInfo.estimatedAffected,
        });
        setShowConfirmation(true);
        return;
      }

      // Not destructive - execute immediately
      await executeSendMessage(messageText);
    },
    [sessionToken, conversationId, executeSendMessage]
  );

  // Handle confirmation of destructive operation
  const handleConfirmDestructive = useCallback(async () => {
    if (!confirmationData) return;

    setShowConfirmation(false);
    await executeSendMessage(confirmationData.message);
    setConfirmationData(null);
  }, [confirmationData, executeSendMessage]);

  // Handle cancellation of destructive operation
  const handleCancelDestructive = useCallback(() => {
    setShowConfirmation(false);
    setConfirmationData(null);
    // Don't clear input - let user edit their message
  }, []);

  // Rate-limited send wrapper
  const handleSendWithRateLimit = useCallback(() => {
    // Don't send if input is empty
    if (!inputValue.trim()) {
      return;
    }

    // Rate limiting: prevent rapid sends within 500ms
    const now = Date.now();
    const timeSinceLastSend = now - lastSendTimeRef.current;

    if (timeSinceLastSend < 500) {
      // Too soon - show rate limit feedback and debounce
      setIsRateLimited(true);

      // Clear previous feedback timer
      if (rateLimitFeedbackTimerRef.current) {
        clearTimeout(rateLimitFeedbackTimerRef.current);
      }

      // Hide feedback after 1 second
      rateLimitFeedbackTimerRef.current = setTimeout(() => {
        setIsRateLimited(false);
      }, 1000);

      // Clear previous debounce timer
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }

      // Schedule the actual send
      debounceTimerRef.current = setTimeout(() => {
        lastSendTimeRef.current = Date.now();
        handleSendMessage(inputValue);
      }, 500 - timeSinceLastSend);
      return;
    }

    lastSendTimeRef.current = now;
    handleSendMessage(inputValue);
  }, [inputValue, handleSendMessage]);

  // Handle Enter key press with rate limiting
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendWithRateLimit();
    }
  };

  // Don't render if not open
  if (!isOpen) {
    return null;
  }

  // Show authentication error if not authenticated
  if (!isAuthenticated) {
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

  // Render chat panel
  return (
    <div
      className="fixed bottom-6 right-6 z-40 flex h-[650px] w-[400px] flex-col overflow-hidden rounded-2xl border border-gray-300 bg-white shadow-[0_8px_30px_rgb(0,0,0,0.12)] transition-all duration-300"
      role="dialog"
      aria-label="AI Assistant Chat Panel"
      aria-modal="true"
      aria-describedby="chat-description"
    >
      {/* Hidden description for screen readers */}
      <span id="chat-description" className="sr-only">
        Chat with the AI assistant to manage your tasks. Use natural language to create, update, or
        delete tasks. Press Escape to close the chat panel.
      </span>

      {/* Header */}
      <header className="flex items-center justify-between border-b border-gray-200 bg-blue-600 p-4 text-white">
        <h2 id="chat-title" className="text-lg font-semibold">
          AI Assistant
        </h2>
        <button
          onClick={onClose}
          className="rounded-full p-1 transition-colors hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-blue-600"
          aria-label="Close chat panel (Escape)"
          title="Close chat panel"
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

      {/* Messages container */}
      <div
        ref={messagesContainerRef}
        className="flex-1 overflow-y-auto bg-gray-50 p-4"
        role="log"
        aria-live="polite"
        aria-label="Chat messages"
        aria-relevant="additions"
      >
        {messages.length === 0 ? (
          <div className="flex h-full flex-col items-center justify-center text-center text-gray-500">
            <svg
              className="mb-4 h-16 w-16 text-gray-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
              />
            </svg>
            <p className="text-lg font-medium">How can I help you manage your tasks?</p>
            <p className="mt-2 text-sm">
              Try saying "Add a task to buy groceries tomorrow at 5pm"
            </p>
          </div>
        ) : (
          <>
            {/* Load More button */}
            {hasMore && (
              <div className="mb-4 text-center">
                <button
                  onClick={loadMoreMessages}
                  disabled={isLoadingMore}
                  className="rounded-lg bg-blue-100 px-4 py-2 text-sm font-medium text-blue-700 transition-colors hover:bg-blue-200 focus:outline-none focus:ring-2 focus:ring-blue-600 focus:ring-offset-2 disabled:cursor-not-allowed disabled:bg-gray-200 disabled:text-gray-500"
                  aria-label="Load older messages"
                  aria-busy={isLoadingMore}
                  title="Load older messages from conversation history"
                >
                  {isLoadingMore ? (
                    <span className="flex items-center gap-2">
                      <svg
                        className="h-4 w-4 animate-spin"
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
                      Loading...
                    </span>
                  ) : (
                    'Load More Messages'
                  )}
                </button>
              </div>
            )}

            {messages.map((message) => (
              <ChatMessage key={message.id} message={message} />
            ))}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Session expired display */}
      {sessionExpired && (
        <div className="border-t border-gray-200 bg-yellow-50 px-4 py-3">
          <div className="flex items-start gap-3">
            <svg
              className="h-5 w-5 flex-shrink-0 text-yellow-600"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                fillRule="evenodd"
                d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                clipRule="evenodd"
              />
            </svg>
            <div className="flex-1">
              <h3 className="text-sm font-medium text-yellow-800">Session Expired</h3>
              <p className="mt-1 text-sm text-yellow-700">
                Your session has expired. Please log in again to continue.
                {pendingMessage && ' Your message will be sent automatically after login.'}
              </p>
              <button
                onClick={() => (window.location.href = '/login')}
                className="mt-3 rounded-lg bg-yellow-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-yellow-700"
              >
                Log In Again
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Error display with retry button */}
      {error && !sessionExpired && (
        <div className="border-t border-gray-200 bg-red-50 px-4 py-3">
          <div className="flex items-start gap-3">
            <svg
              className="h-5 w-5 flex-shrink-0 text-red-600"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                clipRule="evenodd"
              />
            </svg>
            <div className="flex-1">
              <p className="text-sm text-red-700">{error}</p>
              {retryCount > 0 && (
                <p className="mt-1 text-xs text-red-600">
                  Failed after {retryCount} retry attempts.
                </p>
              )}
              {pendingMessage && (
                <button
                  onClick={() => {
                    const msg = pendingMessage;
                    setPendingMessage(null);
                    setError(null);
                    setRetryCount(0);
                    handleSendMessage(msg);
                  }}
                  className="mt-3 rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
                >
                  Retry Message
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Rate limit feedback */}
      {isRateLimited && (
        <div
          className="border-t border-gray-200 bg-blue-50 px-4 py-2"
          role="status"
          aria-live="polite"
        >
          <div className="flex items-center gap-2 text-sm text-blue-700">
            <svg
              className="h-4 w-4 animate-pulse"
              fill="currentColor"
              viewBox="0 0 20 20"
              aria-hidden="true"
            >
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"
                clipRule="evenodd"
              />
            </svg>
            <span>Sending too quickly. Message will be sent shortly...</span>
          </div>
        </div>
      )}

      {/* Input area */}
      <form
        className="border-t border-gray-200 bg-white p-4"
        onSubmit={(e) => {
          e.preventDefault();
          handleSendWithRateLimit();
        }}
        aria-label="Message input form"
      >
        <div className="flex items-end gap-2">
          <div className="flex-1">
            <label htmlFor="chat-input" className="sr-only">
              Type your message to manage tasks
            </label>
            <textarea
              id="chat-input"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Type a message to create or manage tasks..."
              disabled={isLoading || isRateLimited}
              rows={1}
              className="w-full resize-none rounded-lg border border-gray-300 px-3 py-2 text-sm transition-colors focus:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-400 disabled:cursor-not-allowed disabled:bg-gray-100 disabled:text-gray-500"
              style={{ minHeight: '40px', maxHeight: '150px' }}
              aria-label="Message input"
              aria-describedby="input-help-text"
            />
          </div>

          <button
            type="submit"
            onClick={handleSendWithRateLimit}
            disabled={isLoading || !inputValue.trim() || isRateLimited}
            className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-lg bg-blue-600 text-white transition-colors hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-600 focus:ring-offset-2 disabled:cursor-not-allowed disabled:bg-gray-300 disabled:hover:bg-gray-300"
            aria-label={isLoading ? 'Sending message' : isRateLimited ? 'Rate limited, please wait' : 'Send message'}
            title={isRateLimited ? 'Please wait before sending' : 'Send message'}
          >
            {isLoading ? (
              <svg
                className="h-5 w-5 animate-spin"
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
            ) : (
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-5 w-5"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
              </svg>
            )}
          </button>
        </div>

        {/* Helper text */}
        <div id="input-help-text" className="mt-2 text-xs text-gray-500" role="status">
          Press Enter to send, Shift+Enter for new line
        </div>
      </form>

      {/* Confirmation Modal for Destructive Operations */}
      <ConfirmationModal
        isOpen={showConfirmation}
        title="Confirm Destructive Operation"
        message={confirmationData?.confirmationMessage || ''}
        estimatedAffected={confirmationData?.estimatedAffected}
        onConfirm={handleConfirmDestructive}
        onCancel={handleCancelDestructive}
        confirmText="Yes, Proceed"
        cancelText="Cancel"
      />
    </div>
  );
}
