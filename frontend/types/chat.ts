// Chat-related TypeScript types for Frontend Chat Integration (Spec 009)

/**
 * Represents a single chat message displayed in the UI
 */
export interface Message {
  id: string;                    // UUID from backend
  conversationId: string;        // Parent conversation UUID
  content: string;               // Message text
  role: 'user' | 'assistant';    // Message sender
  timestamp: Date;               // ISO 8601 datetime (converted from backend string)
  metadata?: {                   // Optional AI agent operation metadata
    operation?: 'create_task' | 'update_task' | 'delete_task' | 'list_tasks' | 'mark_complete';
    taskId?: string;             // Affected task UUID
    status?: 'pending' | 'success' | 'error' | 'guidance';
    errorMessage?: string;       // If operation failed
    operations?: ToolCallOperation[];  // List of tool call operations
    examples?: string[];         // Example prompts for guidance messages
  };
}

/**
 * Represents the full chat conversation context for a user
 */
export interface Conversation {
  id: string;                    // UUID from backend
  userId: string;                // Owner user UUID (from better-auth session)
  messages: Message[];           // Ordered list of messages (newest last)
  createdAt: Date;               // ISO 8601 datetime
  updatedAt: Date;               // ISO 8601 datetime
  hasMore: boolean;              // True if more messages available for pagination
}

/**
 * Tracks the chat panel UI state (persisted in localStorage)
 */
export interface ChatPanelState {
  isOpen: boolean;               // Panel open (true) or closed (false)
  lastOpenedAt?: Date;           // Timestamp of last panel open (for analytics)
}

/**
 * Payload sent to POST /api/chat endpoint
 */
export interface ChatApiRequest {
  conversationId?: string;       // Optional: resume existing conversation
  message: string;               // User's natural language input
  timezone: string;              // IANA timezone (e.g., "America/New_York")
}

/**
 * Task object from backend API
 */
export interface Task {
  id: string;
  title: string;
  description?: string;
  priority: 'low' | 'medium' | 'high';
  completed: boolean;
  dueDate?: Date;                // ISO 8601 datetime, parsed to Date
}

/**
 * Task operation performed by AI agent
 */
export interface TaskOperation {
  type: 'create' | 'update' | 'delete' | 'mark_complete' | 'list';
  taskId?: string;               // Affected task UUID (not present for 'list')
  task?: Task;                   // Full task object (for create/update/list)
  status: 'success' | 'error';
  errorMessage?: string;         // If status is 'error'
}

/**
 * Tool call operation from backend
 */
export interface ToolCallOperation {
  tool_name: string;             // MCP tool name (e.g., "create_task")
  status: 'success' | 'error';   // Operation status
  details?: string;              // Optional details
}

/**
 * Response from POST /api/chat endpoint
 */
export interface ChatApiResponse {
  conversation_id: number;       // Conversation ID (created or existing)
  user_message: string;          // Echo of user message
  assistant_message: string;     // AI assistant's response
  operations?: ToolCallOperation[];  // List of tool call operations performed (if any)
}

/**
 * Parameters for fetching conversation history
 */
export interface ConversationHistoryParams {
  conversationId: string;        // Conversation UUID
  limit: number;                 // Number of messages to fetch (default: 50)
  offset: number;                // Pagination offset (default: 0)
}

/**
 * Response from GET /api/conversations/:id/messages
 */
export interface ConversationHistoryResponse {
  messages: Message[];           // Array of messages (ordered oldest to newest)
  total: number;                 // Total message count in conversation
  limit: number;                 // Applied limit
  offset: number;                // Applied offset
  hasMore: boolean;              // True if more messages available
}
