// Chat API client functions
// Spec: 009-frontend-chat-integration

'use client';

import { httpClient } from '@/lib/http-client';
import type {
  ChatApiRequest,
  ChatApiResponse,
  ConversationHistoryResponse,
  Message,
} from '@/types/chat';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';

/**
 * Send a chat message to the AI agent
 * @param request - Chat message request with user input and timezone
 * @returns AI assistant's response with any task operations performed
 * @throws Error if authentication fails or request fails
 */
export async function sendChatMessage(
  request: ChatApiRequest
): Promise<ChatApiResponse> {
  try {
    return await httpClient.post<ChatApiResponse>(
      `${API_BASE_URL}/api/chat`,
      request,
      {
        headers: {
          'X-Timezone': request.timezone,
        },
      }
    );
  } catch (error: any) {
    // httpClient already handles 401 errors with token refresh
    // Just re-throw with user-friendly message
    const errorMessage = error.message || 'Failed to send chat message';
    throw new Error(errorMessage);
  }
}

/**
 * Fetch conversation history with pagination
 * @param conversationId - Conversation UUID
 * @param limit - Number of messages to fetch (default: 50)
 * @param offset - Pagination offset (default: 0)
 * @returns Paginated list of messages
 * @throws Error if authentication fails or request fails
 */
export async function fetchConversationHistory(
  conversationId: string,
  limit: number = 50,
  offset: number = 0
): Promise<ConversationHistoryResponse> {
  try {
    const data = await httpClient.get<ConversationHistoryResponse>(
      `${API_BASE_URL}/api/conversations/${conversationId}/messages`,
      {
        params: {
          limit: limit.toString(),
          offset: offset.toString(),
        },
      }
    );

    // Parse ISO date strings to Date objects for all messages
    data.messages = data.messages.map((message) => ({
      ...message,
      timestamp: parseISODate(message.timestamp),
    }));

    return data;
  } catch (error: any) {
    const errorMessage = error.message || 'Failed to fetch conversation history';
    throw new Error(errorMessage);
  }
}

/**
 * Get existing conversation or create a new one for the user
 * @param userId - User UUID
 * @returns Conversation object with ID
 * @throws Error if authentication fails or request fails
 */
export async function getOrCreateConversation(
  userId: string
): Promise<{ id: string; userId: string; createdAt: string; updatedAt: string }> {
  try {
    return await httpClient.post<{ id: string; userId: string; createdAt: string; updatedAt: string }>(
      `${API_BASE_URL}/api/conversations`,
      { userId }
    );
  } catch (error: any) {
    const errorMessage = error.message || 'Failed to get or create conversation';
    throw new Error(errorMessage);
  }
}

/**
 * Parse ISO 8601 date string to Date object
 * Handles both string and Date inputs for flexibility
 */
function parseISODate(dateValue: string | Date): Date {
  if (dateValue instanceof Date) {
    return dateValue;
  }
  return new Date(dateValue);
}
