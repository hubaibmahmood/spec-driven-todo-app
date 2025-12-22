// Custom hook for chat functionality with better-auth integration
// Spec: 009-frontend-chat-integration - User Story 1 (T029)

'use client';

import { useCallback } from 'react';
import { useSession } from '@/lib/auth-client';
import {
  sendChatMessage as apiSendChatMessage,
  fetchConversationHistory as apiFetchConversationHistory,
  getOrCreateConversation as apiGetOrCreateConversation,
} from '@/lib/chat/chat-api';
import { getUserTimezone } from '@/lib/utils/timezone';
import type {
  ChatApiRequest,
  ChatApiResponse,
  ConversationHistoryResponse,
} from '@/types/chat';

interface UseChatReturn {
  sendMessage: (message: string, conversationId?: string) => Promise<ChatApiResponse>;
  loadHistory: (conversationId: string, limit?: number, offset?: number) => Promise<ConversationHistoryResponse>;
  getOrCreateConversation: (userId: string) => Promise<{ id: string; userId: string; createdAt: string; updatedAt: string }>;
  isAuthenticated: boolean;
  sessionError: string | null;
}

/**
 * Custom hook for chat functionality with automatic session management
 * Integrates better-auth session with chat API functions
 *
 * @returns Chat functions that automatically handle authentication
 * @throws Error if session is expired or user is not authenticated
 */
export function useChat(): UseChatReturn {
  const { data: session, error: sessionError } = useSession();

  // Get session token from better-auth
  const getSessionToken = useCallback((): string => {
    if (!session?.session?.token) {
      throw new Error('Not authenticated. Please log in to use chat.');
    }
    return session.session.token;
  }, [session]);

  /**
   * Send a chat message with automatic timezone detection and session token
   */
  const sendMessage = useCallback(
    async (message: string, conversationId?: string): Promise<ChatApiResponse> => {
      const sessionToken = getSessionToken();
      const timezone = getUserTimezone();

      const request: ChatApiRequest = {
        message,
        timezone,
        conversationId,
      };

      return apiSendChatMessage(request, sessionToken);
    },
    [getSessionToken]
  );

  /**
   * Load conversation history with pagination
   */
  const loadHistory = useCallback(
    async (
      conversationId: string,
      limit: number = 50,
      offset: number = 0
    ): Promise<ConversationHistoryResponse> => {
      const sessionToken = getSessionToken();
      return apiFetchConversationHistory(conversationId, sessionToken, limit, offset);
    },
    [getSessionToken]
  );

  /**
   * Get existing conversation or create a new one
   */
  const getOrCreateConversation = useCallback(
    async (userId: string) => {
      const sessionToken = getSessionToken();
      return apiGetOrCreateConversation(userId, sessionToken);
    },
    [getSessionToken]
  );

  return {
    sendMessage,
    loadHistory,
    getOrCreateConversation,
    isAuthenticated: !!session?.session?.token,
    sessionError: sessionError?.message || null,
  };
}
