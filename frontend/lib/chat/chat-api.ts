// Chat API client functions
// Spec: 009-frontend-chat-integration

'use client';

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
 * @param sessionToken - Better-auth session token for authentication
 * @returns AI assistant's response with any task operations performed
 * @throws Error if session is expired (401) or request fails
 */
export async function sendChatMessage(
  request: ChatApiRequest,
  sessionToken: string
): Promise<ChatApiResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${sessionToken}`,
        'X-Timezone': request.timezone,
      },
      body: JSON.stringify(request),
    });

    if (response.status === 401) {
      throw new Error('Session expired. Please log in again.');
    }

    if (!response.ok) {
      // Try to parse error response body for better error messages
      let errorMessage = `Failed to send chat message: ${response.statusText}`;

      try {
        const errorData = await response.json();
        if (errorData.detail) {
          // Use the backend's error detail message (e.g., "Please configure your Gemini API key...")
          errorMessage = errorData.detail;
        }
      } catch {
        // If JSON parsing fails, stick with statusText
      }

      throw new Error(errorMessage);
    }

    const data: ChatApiResponse = await response.json();

    // No need to parse dates - response contains simple strings
    return data;
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error('Network error: Failed to send chat message');
  }
}

/**
 * Fetch conversation history with pagination
 * @param conversationId - Conversation UUID
 * @param sessionToken - Better-auth session token for authentication
 * @param limit - Number of messages to fetch (default: 50)
 * @param offset - Pagination offset (default: 0)
 * @returns Paginated list of messages
 * @throws Error if session is expired (401) or request fails
 */
export async function fetchConversationHistory(
  conversationId: string,
  sessionToken: string,
  limit: number = 50,
  offset: number = 0
): Promise<ConversationHistoryResponse> {
  try {
    const response = await fetch(
      `${API_BASE_URL}/api/conversations/${conversationId}/messages?limit=${limit}&offset=${offset}`,
      {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${sessionToken}`,
        },
      }
    );

    if (response.status === 401) {
      throw new Error('Session expired. Please log in again.');
    }

    if (!response.ok) {
      throw new Error(`Failed to fetch conversation history: ${response.statusText}`);
    }

    const data: ConversationHistoryResponse = await response.json();

    // Parse ISO date strings to Date objects for all messages
    data.messages = data.messages.map((message) => ({
      ...message,
      timestamp: parseISODate(message.timestamp),
    }));

    return data;
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error('Network error: Failed to fetch conversation history');
  }
}

/**
 * Get existing conversation or create a new one for the user
 * @param userId - User UUID from better-auth session
 * @param sessionToken - Better-auth session token for authentication
 * @returns Conversation object with ID
 * @throws Error if session is expired (401) or request fails
 */
export async function getOrCreateConversation(
  userId: string,
  sessionToken: string
): Promise<{ id: string; userId: string; createdAt: string; updatedAt: string }> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/conversations`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${sessionToken}`,
      },
      body: JSON.stringify({ userId }),
    });

    if (response.status === 401) {
      throw new Error('Session expired. Please log in again.');
    }

    if (!response.ok) {
      throw new Error(`Failed to get or create conversation: ${response.statusText}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error('Network error: Failed to get or create conversation');
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
