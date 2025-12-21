# Data Model: OpenAI Agents SDK Integration

**Feature**: 008-openai-agents-sdk-integration
**Date**: 2025-12-20
**Phase**: 1 - Design & Contracts

## Overview

This feature does NOT introduce new database models. It extends the existing chat persistence infrastructure (spec 007) and integrates with the MCP server (spec 006). This document describes the **runtime entities** (in-memory data structures) used by the agent system and their relationships to existing persisted models.

---

## Existing Database Models (Spec 007)

These models are **unchanged** by this feature. Agent system reads from and writes to these models.

### Conversation

```python
# ai-agent/src/ai_agent/database/models.py (EXISTING - spec 007)
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)  # From better-auth
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
```

**Usage in Agent System**:
- Agent loads conversation by ID to access message history
- Agent updates `updated_at` timestamp on new messages
- `user_id` used for MCP X-User-ID header authentication

**Validation Rules** (unchanged):
- `user_id` must be valid better-auth user ID
- One conversation can have many messages
- Deleting conversation cascades to messages

---

### Message

```python
# backend/src/models/message.py (EXISTING - spec 007)
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False, index=True)
    role = Column(String, nullable=False)  # "user" | "assistant" | "tool"
    content = Column(Text, nullable=False)
    metadata = Column(JSON, nullable=True)  # Tool calls, timestamps, etc.
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    conversation = relationship("Conversation", back_populates="messages")
```

**Usage in Agent System**:
- Messages loaded from DB and converted to agent format for Runner.run()
- Agent responses saved as new Message with `role="assistant"`
- User input saved as new Message with `role="user"`
- MCP tool calls stored in `metadata` field as JSON

**Validation Rules** (unchanged):
- `role` must be one of: "user", "assistant", "tool"
- `content` required (non-null)
- `metadata` is optional JSONB for extensibility
- Messages ordered by `created_at` ascending

**metadata Schema** (extended for agent tool calls):
```json
{
  "tool_calls": [
    {
      "id": "call_abc123",
      "type": "function",
      "function": {
        "name": "list_tasks",
        "arguments": "{}"
      }
    }
  ],
  "token_count": 245,
  "model": "gemini-2.5-flash"
}
```

---

## Runtime Entities (New - Not Persisted)

These are in-memory data structures used during agent execution. They are NOT stored in the database.

### AgentConfig

**Purpose**: Configuration for agent initialization including Gemini API setup, MCP connection params, and runtime settings.

**Structure**:
```python
# ai-agent/src/ai_agent/agent/config.py
from pydantic import BaseModel, Field
from typing import Optional

class AgentConfig(BaseModel):
    """Runtime configuration for OpenAI Agent with Gemini backend."""

    # Gemini API
    gemini_api_key: str = Field(..., description="API key for Gemini via OpenAI-compatible endpoint")

    # MCP Server
    mcp_server_url: str = Field(
        default="http://localhost:8001/mcp",
        description="MCP server endpoint URL"
    )
    mcp_timeout: int = Field(default=10, description="MCP connection timeout in seconds")
    mcp_retry_attempts: int = Field(default=3, description="Max retry attempts for MCP calls")

    # Agent Behavior
    system_prompt: str = Field(
        default="You are a helpful task management assistant. Use the available tools to help users manage their tasks.",
        description="System-level instructions for agent behavior"
    )
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Model temperature for response generation")

    # Context Window Management
    token_budget: int = Field(
        default=800_000,
        description="Maximum tokens for conversation history (80% of model limit)"
    )
    encoding_name: str = Field(default="cl100k_base", description="Token encoding for tiktoken")

    class Config:
        env_prefix = "AGENT_"  # Environment variables like AGENT_GEMINI_API_KEY
```

**Lifecycle**:
- Created once at application startup
- Loaded from environment variables
- Passed to agent initialization functions
- Immutable during request processing

**Validation Rules**:
- `gemini_api_key` must be non-empty string
- `temperature` must be between 0.0 and 2.0
- `token_budget` must be positive integer
- `mcp_timeout` must be positive integer
- `mcp_retry_attempts` must be 0-10

---

### AgentMessage

**Purpose**: Standardized message format for agent execution. Represents a single message in the conversation compatible with OpenAI Agents SDK.

**Structure**:
```python
# ai-agent/src/ai_agent/agent/message_converter.py
from typing import TypedDict, Optional, List, Dict, Any

class ToolCall(TypedDict):
    """Tool call structure within agent message."""
    id: str
    type: str  # "function"
    function: Dict[str, str]  # {"name": str, "arguments": str}

class AgentMessage(TypedDict):
    """Message format for OpenAI Agents SDK Runner.run()."""
    role: str  # "user" | "assistant" | "system" | "tool"
    content: str
    tool_calls: Optional[List[ToolCall]]  # Present if agent called MCP tools
```

**Lifecycle**:
- Created by converting database Message models to agent format
- Passed to `Runner.run(messages=...)` for context
- NOT persisted - ephemeral during request

**Validation Rules**:
- `role` must be one of: "user", "assistant", "system", "tool"
- `content` required (non-empty string)
- `tool_calls` optional, if present must be list of ToolCall dicts

**Conversion Logic** (Database Message → AgentMessage):
```python
def convert_db_message_to_agent_format(db_message: Message) -> AgentMessage:
    """Convert persisted Message to agent-compatible format."""
    agent_msg: AgentMessage = {
        "role": db_message.role,
        "content": db_message.content,
    }

    # Extract tool calls from metadata if present
    if db_message.metadata and "tool_calls" in db_message.metadata:
        agent_msg["tool_calls"] = db_message.metadata["tool_calls"]

    return agent_msg
```

---

### AgentContext

**Purpose**: Aggregates all contextual information needed for agent execution including user identity, conversation history, and configuration.

**Structure**:
```python
# ai-agent/src/ai_agent/agent/context_manager.py
from typing import List
from pydantic import BaseModel

class AgentContext(BaseModel):
    """Execution context for agent request."""

    user_id: str  # For MCP X-User-ID header
    conversation_id: Optional[int]  # For loading history
    user_message: str  # Current user input
    conversation_history: List[AgentMessage]  # Prior messages (token-truncated)
    config: AgentConfig  # Agent configuration

    class Config:
        arbitrary_types_allowed = True  # Allow AgentMessage TypedDict
```

**Lifecycle**:
- Created at the start of each `/api/chat` request
- Populated by loading conversation history from database
- Token truncation applied to `conversation_history`
- Passed to agent execution function
- Discarded after response generated

**Validation Rules**:
- `user_id` must be non-empty string (validated user from auth)
- `user_message` must be non-empty string
- `conversation_history` must be list (can be empty for first message)
- `conversation_id` optional (null for new conversation)

---

### AgentResult

**Purpose**: Encapsulates agent execution result including response text, tool calls made, and metadata for persistence.

**Structure**:
```python
# ai-agent/src/ai_agent/agent/agent_service.py
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class AgentResult(BaseModel):
    """Result from agent execution."""

    response_text: str  # Agent's final response to user
    tool_calls_made: List[Dict[str, Any]]  # MCP tools invoked during execution
    tokens_used: int  # Total tokens consumed (input + output)
    model: str  # Model used (e.g., "gemini-2.5-flash")
    execution_time_ms: int  # Time taken for agent execution

class AgentExecutionError(BaseModel):
    """Error information when agent execution fails."""

    error_type: str  # "gemini_api_error" | "mcp_connection_error" | "unknown_error"
    error_message: str
    user_facing_message: str  # Sanitized message safe to show user
    timestamp: datetime
```

**Lifecycle**:
- Returned from `run_agent_with_context()` function
- Used to create database Message record for assistant response
- Tool calls stored in Message.metadata
- Discarded after persistence

**Validation Rules**:
- `response_text` must be non-empty string
- `tokens_used` must be positive integer
- `tool_calls_made` can be empty list (if no tools used)
- `execution_time_ms` must be positive integer

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     /api/chat Request                            │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │   Load Conversation   │
                    │   (from PostgreSQL)   │
                    └──────────┬────────────┘
                               │
                               ▼
                    ┌───────────────────────┐
                    │   Load Messages       │
                    │   (conversation_id)   │
                    └──────────┬────────────┘
                               │
                               ▼
                ┌──────────────────────────────┐
                │  Convert to AgentMessage[]   │
                │  (message_converter.py)      │
                └──────────┬───────────────────┘
                           │
                           ▼
                ┌──────────────────────────────┐
                │  Token Truncation            │
                │  (context_manager.py)        │
                │  Keep 80% budget             │
                └──────────┬───────────────────┘
                           │
                           ▼
                ┌──────────────────────────────┐
                │  Create AgentContext         │
                │  (user_id, messages, config) │
                └──────────┬───────────────────┘
                           │
                           ▼
            ┌──────────────────────────────────────┐
            │  run_agent_with_context()            │
            │  - Initialize Gemini client          │
            │  - Connect to MCP server             │
            │  - Run Agent with Runner.run()       │
            └──────────┬───────────────────────────┘
                       │
                       ▼
            ┌──────────────────────────────┐
            │  AgentResult                 │
            │  - response_text             │
            │  - tool_calls_made           │
            │  - tokens_used               │
            └──────────┬───────────────────┘
                       │
                       ▼
            ┌──────────────────────────────┐
            │  Save Messages               │
            │  - User message (role=user)  │
            │  - Agent response (assist)   │
            │  - Metadata with tool_calls  │
            └──────────┬───────────────────┘
                       │
                       ▼
            ┌──────────────────────────────┐
            │  Return HTTP Response        │
            │  { response, conversation_id}│
            └──────────────────────────────┘
```

---

## State Transitions

### Message Role Transitions

```
New Request
    │
    ├──> Create Message(role="user", content=user_input)
    │         │
    │         ▼
    │    [Agent Processing]
    │         │
    │         ├──> (Optional) Message(role="tool", content=tool_result)
    │         │
    │         ▼
    └──> Create Message(role="assistant", content=agent_response)
```

**Rules**:
- Every user message triggers exactly one assistant message
- Tool messages are intermediate (not directly returned to user)
- System messages are configuration-only (not persisted in spec 007 schema)

---

## Relationships

### Entity Relationship Diagram

```
┌─────────────────────┐
│   Conversation      │
│  (PostgreSQL)       │
│                     │
│  - id (PK)          │
│  - user_id          │
│  - created_at       │
│  - updated_at       │
└──────┬──────────────┘
       │ 1
       │
       │ has many
       │
       │ N
       ▼
┌─────────────────────┐
│   Message           │
│  (PostgreSQL)       │
│                     │
│  - id (PK)          │
│  - conversation_id  │
│  - role             │
│  - content          │
│  - metadata (JSON)  │
│  - created_at       │
└──────┬──────────────┘
       │
       │ converted to
       │
       ▼
┌─────────────────────┐
│   AgentMessage      │
│  (Runtime)          │
│                     │
│  - role             │
│  - content          │
│  - tool_calls?      │
└──────┬──────────────┘
       │
       │ used by
       │
       ▼
┌─────────────────────┐      ┌──────────────────┐
│   AgentContext      │      │   AgentConfig    │
│  (Runtime)          │◄─────┤  (Runtime)       │
│                     │      │                  │
│  - user_id          │      │  - gemini_key    │
│  - user_message     │      │  - mcp_url       │
│  - history[]        │      │  - temperature   │
└──────┬──────────────┘      └──────────────────┘
       │
       │ produces
       │
       ▼
┌─────────────────────┐
│   AgentResult       │
│  (Runtime)          │
│                     │
│  - response_text    │
│  - tool_calls_made  │
│  - tokens_used      │
└─────────────────────┘
```

---

## Validation Summary

| Entity | Key Validations |
|--------|----------------|
| **Conversation** | user_id non-empty; timestamps auto-managed |
| **Message** | role ∈ {user, assistant, tool}; content non-empty; metadata valid JSON |
| **AgentConfig** | gemini_api_key non-empty; temperature 0.0-2.0; token_budget > 0 |
| **AgentMessage** | role ∈ {user, assistant, system, tool}; content non-empty |
| **AgentContext** | user_id non-empty; user_message non-empty; history is list |
| **AgentResult** | response_text non-empty; tokens_used > 0; execution_time_ms > 0 |

---

## Database Schema Changes

**NONE** - This feature does NOT modify the database schema. It reuses existing tables from spec 007:
- `conversations` table (unchanged)
- `messages` table (unchanged)

The `metadata` column in `messages` table (already JSONB) is used to store tool call information without schema changes.

---

## Scalability Considerations

1. **Token Counting Performance**: tiktoken encoding is CPU-intensive. For very long conversations, consider caching token counts in Message.metadata.

2. **Message History Loading**: Loading all messages for a conversation can be slow for long histories. Current design loads all then truncates. Future: implement database-level pagination.

3. **Concurrent Requests**: Each agent instance is created per-request (no shared state). This scales horizontally but may create many Gemini API connections. Future: implement connection pooling.

4. **Database Queries**: Current design: 2 queries per request (load conversation + load messages). Consider eager loading or caching for high traffic.

---

**Data Model Complete**: All entities defined with validation rules. Ready for contract generation.
