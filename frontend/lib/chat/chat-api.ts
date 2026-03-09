// Chat API client functions
// Spec: 009-frontend-chat-integration

'use client';

import { httpClient } from '@/lib/http-client';
import type {
  ChatApiRequest,
  ChatApiResponse,
  ChatStreamEvent,
  ConversationHistoryResponse,
  Message,
  ToolCallOperation,
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
 * Send a chat message and receive the response as a stream of SSE events.
 * Uses fetch + ReadableStream (not EventSource) to support custom Authorization header.
 *
 * @param message - User's message text
 * @param conversationId - Existing conversation ID (null for new conversation)
 * @param accessToken - JWT Bearer token
 * @param timezone - IANA timezone string
 * @param onDelta - Called for each text chunk as it arrives
 * @param onDone - Called when streaming completes with conversation_id and operations
 * @param onError - Called on error
 * @param signal - Optional AbortSignal to cancel the stream
 */
export async function sendChatMessageStreaming(
  message: string,
  conversationId: number | null,
  accessToken: string,
  timezone: string,
  onDelta: (text: string) => void,
  onDone: (conversationId: number, operations: ToolCallOperation[]) => void,
  onError: (detail: string) => void,
  signal?: AbortSignal
): Promise<void> {
  const AI_AGENT_URL = process.env.NEXT_PUBLIC_AI_AGENT_URL || 'http://localhost:8002';

  const response = await fetch(`${AI_AGENT_URL}/api/chat/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${accessToken}`,
      'X-Timezone': timezone,
    },
    body: JSON.stringify({ message, conversation_id: conversationId }),
    signal,
  });

  if (!response.ok) {
    let detail = `Request failed: ${response.statusText}`;
    try {
      const errData = await response.json();
      if (errData.detail) detail = errData.detail;
    } catch {
      // ignore JSON parse failure
    }
    onError(detail);
    return;
  }

  const reader = response.body?.getReader();
  if (!reader) {
    onError('No response body from server.');
    return;
  }

  const decoder = new TextDecoder();
  let buffer = '';

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n\n');
      buffer = lines.pop() ?? '';

      for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed.startsWith('data:')) continue;
        const jsonStr = trimmed.slice('data:'.length).trim();
        try {
          const event: ChatStreamEvent = JSON.parse(jsonStr);
          if (event.type === 'text_delta') {
            onDelta(event.content);
          } else if (event.type === 'done') {
            onDone(event.conversation_id, event.operations ?? []);
          } else if (event.type === 'error') {
            onError(event.detail);
          }
        } catch {
          // ignore malformed SSE lines
        }
      }
    }
  } finally {
    reader.releaseLock();
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
