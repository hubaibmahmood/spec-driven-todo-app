# Data Model: Chat Persistence

## Entities

### Conversation
Represents a chat session owned by a user.

| Field | Type | Description |
|-------|------|-------------|
| `id` | `UUID` / `Int` | Primary Key |
| `user_id` | `String(255)` | Owner (references `users.id` in auth system) |
| `title` | `String(200)` | Descriptive title |
| `created_at` | `DateTime` | Creation timestamp |
| `updated_at` | `DateTime` | Last activity timestamp |

**Relationships**:
- Has Many `Message` entities.

### Message
An individual entry in a conversation history.

| Field | Type | Description |
|-------|------|-------------|
| `id` | `UUID` / `Int` | Primary Key |
| `conversation_id` | `UUID` / `Int` | Foreign Key to `Conversation` |
| `role` | `String(20)` | `user`, `assistant`, or `tool` (OpenAI-compatible) |
| `content` | `Text` | Message body |
| `metadata` | `JSONB` | Optional: stores `tool_calls`, `tool_call_id` for OpenAI integration (spec 008) |
| `created_at` | `DateTime` | Timestamp |

**Relationships**:
- Belongs to one `Conversation`.

**Notes**:
- `role='assistant'`: AI-generated responses (echo in spec 007, real AI in spec 008)
- `role='tool'`: Tool execution results (reserved for spec 008)
- `metadata`: Nullable JSONB field for future OpenAI message extensions

### UserSession (External/Read-Only)
Reference to the `user_sessions` table managed by Better-Auth.

| Field | Type | Mapping (to DB) |
|-------|------|-----------------|
| `id` | `String` | `id` |
| `user_id` | `String` | `userId` |
| `token` | `String` | `token` |
| `expires_at` | `DateTime` | `expiresAt` |

## State Transitions
1. **POST /api/chat (no ID)** -> Create `Conversation` -> Create `Message` (role='user') -> Create `Message` (role='assistant', echo response).
2. **POST /api/chat (with ID)** -> Validate ownership -> Create `Message` (role='user') -> Create `Message` (role='assistant', echo response).

**Note**: In spec 007, the assistant response is a simple echo. In spec 008, this will be replaced with OpenAI Agents SDK responses that may include tool calls stored in the `metadata` field.
