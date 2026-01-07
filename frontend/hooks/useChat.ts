// Custom hook for chat functionality with JWT authentication
// Spec: 009-frontend-chat-integration - User Story 1 (T029)

'use client';

import { useCallback } from 'react';
import { isAuthenticated } from '@/lib/jwt-auth-client';
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
}

/**
 * Custom hook for chat functionality with automatic JWT authentication
 * Integrates JWT authentication with chat API functions
 *
 * @returns Chat functions that automatically handle authentication
 * @throws Error if user is not authenticated
 */
export function useChat(): UseChatReturn {
  /**
   * Send a chat message with automatic timezone detection
   * JWT token is automatically included by httpClient
   */
  const sendMessage = useCallback(
    async (message: string, conversationId?: string): Promise<ChatApiResponse> => {
      if (!isAuthenticated()) {
        throw new Error('Not authenticated. Please log in to use chat.');
      }

      const timezone = getUserTimezone();

      const request: ChatApiRequest = {
        message,
        timezone,
        conversationId,
      };

      return apiSendChatMessage(request);
    },
    []
  );

  /**
   * Load conversation history with pagination
   * JWT token is automatically included by httpClient
   */
  const loadHistory = useCallback(
    async (
      conversationId: string,
      limit: number = 50,
      offset: number = 0
    ): Promise<ConversationHistoryResponse> => {
      if (!isAuthenticated()) {
        throw new Error('Not authenticated. Please log in to view history.');
      }

      return apiFetchConversationHistory(conversationId, limit, offset);
    },
    []
  );

  /**
   * Get existing conversation or create a new one
   * JWT token is automatically included by httpClient
   */
  const getOrCreateConversation = useCallback(
    async (userId: string) => {
      if (!isAuthenticated()) {
        throw new Error('Not authenticated. Please log in to use chat.');
      }

      return apiGetOrCreateConversation(userId);
    },
    []
  );

  return {
    sendMessage,
    loadHistory,
    getOrCreateConversation,
    isAuthenticated: isAuthenticated(),
  };
}
