# Data Model: Frontend Chat Integration

**Feature**: 009-frontend-chat-integration
**Date**: 2025-12-21
**Phase**: 1 (Design & Contracts)

## Overview

This document defines the frontend data structures for the chat interface. The backend entities (Conversation, Message) are already defined in spec 007. This model focuses on frontend-specific types, state management, and API response contracts.

---

## Frontend TypeScript Types

**Location**: `frontend/types/chat.ts` (new file to be created)

### 1. Message (Frontend)

Represents a single chat message displayed in the UI.

```typescript
interface Message {
  id: string;                    // UUID from backend
  conversationId: string;        // Parent conversation UUID
  content: string;               // Message text
  role: 'user' | 'assistant';    // Message sender
  timestamp: Date;               // ISO 8601 datetime (converted from backend string)
  metadata?: {                   // Optional AI agent operation metadata
    operation?: 'create_task' | 'update_task' | 'delete_task' | 'list_tasks' | 'mark_complete';
    taskId?: string;             // Affected task UUID
    status?: 'pending' | 'success' | 'error';
    errorMessage?: string;       // If operation failed
  };
}
```

**Validation Rules**:
- `id`: Required, non-empty UUID string
- `conversationId`: Required, non-empty UUID string
- `content`: Required, min length 1, max length 10,000 characters
- `role`: Must be exactly 'user' or 'assistant'
- `timestamp`: Must be valid Date object (parsed from ISO 8601 string)
- `metadata.operation`: Optional enum (5 allowed values)
- `metadata.taskId`: Optional UUID, only present if operation affects specific task

**Derived From**: Backend `Message` model (spec 007) with frontend-specific parsing

---

### 2. Conversation (Frontend)

Represents the full chat conversation context for a user.

```typescript
interface Conversation {
  id: string;                    // UUID from backend
  userId: string;                // Owner user UUID (from better-auth session)
  messages: Message[];           // Ordered list of messages (newest last)
  createdAt: Date;               // ISO 8601 datetime
  updatedAt: Date;               // ISO 8601 datetime
  hasMore: boolean;              // True if more messages available for pagination
}
```

**Validation Rules**:
- `id`: Required, non-empty UUID string
- `userId`: Required, non-empty UUID string
- `messages`: Array of Message objects, can be empty for new conversation
- `createdAt`: Must be valid Date object
- `updatedAt`: Must be >= createdAt
- `hasMore`: Boolean flag for pagination state

**State Transitions**:
1. **New conversation**: `messages: []`, `hasMore: false`
2. **Load initial history**: `messages: [last 50]`, `hasMore: true` (if more exist)
3. **Load more messages**: Prepend older messages to `messages` array
4. **Send new message**: Append to `messages` array

**Derived From**: Backend `Conversation` model (spec 007) with frontend pagination metadata

---

### 3. ChatPanelState (Frontend Only)

Tracks the chat panel UI state (persisted in localStorage).

```typescript
interface ChatPanelState {
  isOpen: boolean;               // Panel open (true) or closed (false)
  lastOpenedAt?: Date;           // Timestamp of last panel open (for analytics)
}
```

**Validation Rules**:
- `isOpen`: Required boolean
- `lastOpenedAt`: Optional Date object

**Persistence Strategy**:
- Stored in `localStorage` under key: `chat-panel-state`
- Serialized as JSON: `{ "isOpen": true, "lastOpenedAt": "2025-12-21T10:30:00Z" }`
- Read on component mount, written on panel toggle

**Not Persisted** (ephemeral state):
- Scroll position within chat history
- Input field draft text
- Loading states (message sending, history loading)

---

### 4. ChatApiRequest (Frontend)

Payload sent to POST /api/chat endpoint.

```typescript
interface ChatApiRequest {
  conversationId?: string;       // Optional: resume existing conversation
  message: string;               // User's natural language input
  timezone: string;              // IANA timezone (e.g., "America/New_York")
}
```

**Validation Rules**:
- `conversationId`: Optional UUID, sent if resuming conversation
- `message`: Required, min length 1, max length 5,000 characters (frontend validation)
- `timezone`: Required, must be valid IANA timezone string (from `Intl.DateTimeFormat()`)

**HTTP Headers** (included in request):
- `Authorization: Bearer <session-token>` (from better-auth)
- `Content-Type: application/json`
- `X-Timezone: <timezone>` (same as request body, for backend compatibility)

---

### 5. ChatApiResponse (Frontend)

Response from POST /api/chat endpoint.

```typescript
interface ChatApiResponse {
  conversationId: string;        // Conversation UUID (created or existing)
  message: Message;              // AI assistant's response message
  operations?: TaskOperation[];  // List of task operations performed (if any)
}

interface TaskOperation {
  type: 'create' | 'update' | 'delete' | 'mark_complete' | 'list';
  taskId?: string;               // Affected task UUID (not present for 'list')
  task?: Task;                   // Full task object (for create/update/list)
  status: 'success' | 'error';
  errorMessage?: string;         // If status is 'error'
}

interface Task {
  id: string;
  title: string;
  description?: string;
  priority: 'low' | 'medium' | 'high';
  completed: boolean;
  dueDate?: Date;                // ISO 8601 datetime, parsed to Date
}
```

**Validation Rules**:
- `conversationId`: Required UUID
- `message`: Required Message object
- `operations`: Optional array (empty if chat message didn't trigger task operations)
- `TaskOperation.type`: Required enum (5 allowed values)
- `TaskOperation.status`: Required enum ('success' or 'error')
- `Task`: Matches backend Task model (spec 003)

**Example Response**:
```json
{
  "conversationId": "550e8400-e29b-41d4-a716-446655440000",
  "message": {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "conversationId": "550e8400-e29b-41d4-a716-446655440000",
    "content": "I've created a task 'Buy groceries' with due date tomorrow at 5pm.",
    "role": "assistant",
    "timestamp": "2025-12-21T14:30:00Z",
    "metadata": {
      "operation": "create_task",
      "taskId": "770e8400-e29b-41d4-a716-446655440002",
      "status": "success"
    }
  },
  "operations": [
    {
      "type": "create",
      "taskId": "770e8400-e29b-41d4-a716-446655440002",
      "task": {
        "id": "770e8400-e29b-41d4-a716-446655440002",
        "title": "Buy groceries",
        "description": null,
        "priority": "medium",
        "completed": false,
        "dueDate": "2025-12-22T17:00:00Z"
      },
      "status": "success"
    }
  ]
}
```

---

### 6. ConversationHistoryRequest (Frontend)

Payload for fetching conversation history (GET /api/conversations/:id/messages).

```typescript
interface ConversationHistoryParams {
  conversationId: string;        // Conversation UUID
  limit: number;                 // Number of messages to fetch (default: 50)
  offset: number;                // Pagination offset (default: 0)
}
```

**Validation Rules**:
- `conversationId`: Required UUID
- `limit`: Integer, min 1, max 100, default 50
- `offset`: Integer, min 0, default 0

**URL Format**: `GET /api/conversations/{conversationId}/messages?limit=50&offset=0`

---

### 7. ConversationHistoryResponse (Frontend)

Response from GET /api/conversations/:id/messages.

```typescript
interface ConversationHistoryResponse {
  messages: Message[];           // Array of messages (ordered oldest to newest)
  total: number;                 // Total message count in conversation
  limit: number;                 // Applied limit
  offset: number;                // Applied offset
  hasMore: boolean;              // True if more messages available
}
```

**Validation Rules**:
- `messages`: Array of Message objects, can be empty
- `total`: Integer >= 0
- `limit`: Integer, matches request limit
- `offset`: Integer, matches request offset
- `hasMore`: Boolean, `true` if `offset + messages.length < total`

---

## React State Management

### Component State Hierarchy

```
App (Root)
└── TaskProvider (Context)
    ├── DashboardPage
    │   ├── TaskList (subscribes to TaskContext)
    │   └── ChatToggleButton
    └── ChatPanel (subscribes to TaskContext)
        ├── ChatMessages
        │   └── ChatMessage (repeats)
        └── ChatInput
```

**Shared State (React Context)**:
```typescript
interface TaskContextValue {
  tasks: Task[];                 // Current user's tasks
  addTask: (task: Task) => void; // Optimistic update
  updateTask: (id: string, updates: Partial<Task>) => void;
  deleteTask: (id: string) => void;
  markTaskComplete: (id: string) => void;
  refreshTasks: () => Promise<void>; // Force reload from backend
}
```

**ChatPanel Local State**:
```typescript
const [conversation, setConversation] = useState<Conversation | null>(null);
const [messages, setMessages] = useState<Message[]>([]);
const [isLoading, setIsLoading] = useState(false);
const [error, setError] = useState<string | null>(null);
const [panelState, setPanelState] = usePanelState(); // Custom hook for localStorage
```

---

## Data Flow Diagrams

### User Sends Message Flow

```
User types message → ChatInput
  ↓
ChatInput.onSubmit()
  ↓
ChatPanel.sendMessage(text)
  ↓
POST /api/chat { message, timezone, conversationId }
  ↓ (API request with Authorization header)
Backend processes message → AI agent executes task operation
  ↓
ChatApiResponse { message, operations }
  ↓
ChatPanel updates state:
  - Add assistant message to messages[]
  - If operations exist → TaskContext.addTask() (optimistic update)
  ↓
React re-renders:
  - ChatMessages shows new message
  - TaskList shows new task (via TaskContext)
```

### Load Conversation History Flow

```
User opens ChatPanel
  ↓
useEffect on mount
  ↓
GET /api/conversations/{userId}/latest (or create new)
  ↓
GET /api/conversations/{id}/messages?limit=50&offset=0
  ↓
ConversationHistoryResponse { messages, hasMore }
  ↓
setMessages(messages)
setConversation({ ...conversation, hasMore })
  ↓
ChatMessages renders history (scrolled to bottom)
  ↓
User clicks "Load More"
  ↓
GET /api/conversations/{id}/messages?limit=50&offset=50
  ↓
Prepend older messages to messages[]
  ↓
Auto-scroll to maintain user's scroll position
```

---

## Validation Summary

| Entity | Required Fields | Optional Fields | Max Length | Constraints |
|--------|----------------|-----------------|------------|-------------|
| Message | id, conversationId, content, role, timestamp | metadata | content: 10,000 | role enum |
| Conversation | id, userId, messages, createdAt, updatedAt, hasMore | - | - | updatedAt >= createdAt |
| ChatPanelState | isOpen | lastOpenedAt | - | isOpen boolean |
| ChatApiRequest | message, timezone | conversationId | message: 5,000 | timezone IANA format |
| ChatApiResponse | conversationId, message | operations | - | Message valid |
| TaskOperation | type, status | taskId, task, errorMessage | - | type/status enums |

---

## Relationship to Backend Models

- **Frontend Message** ← Backend `Message` (spec 007): Frontend adds `metadata` parsing and Date conversion
- **Frontend Conversation** ← Backend `Conversation` (spec 007): Frontend adds `hasMore` pagination flag
- **Frontend Task** ← Backend `Task` (spec 003): Exact match, no differences
- **Frontend ChatPanelState**: Frontend-only, no backend equivalent (localStorage)

---

**Next Steps**: Create API contracts in `/contracts/` directory to document endpoint specifications.
