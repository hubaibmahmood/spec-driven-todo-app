# Research: OpenAI Agents SDK Integration

**Feature**: 008-openai-agents-sdk-integration
**Date**: 2025-12-20
**Phase**: 0 - Research & Technical Decisions

## Overview

This document captures research findings and technical decisions for integrating OpenAI Agents SDK with Gemini API backend into the existing FastAPI chat service. All decisions resolve "NEEDS CLARIFICATION" items from the Technical Context and establish best practices for implementation.

---

## 1. OpenAI Agents SDK with Gemini API Integration

### Decision
Use OpenAI Agents SDK (openai-agents-python) with Gemini 2.5 Flash model via Google's OpenAI-compatible endpoint.

### Rationale
- **OpenAI Agents SDK provides**:
  - Built-in MCP (Model Context Protocol) support via `MCPServerStreamableHttp`, `MCPServerSse`, `MCPServerStdio`
  - Tool-calling abstraction with automatic tool discovery
  - Async execution model compatible with FastAPI
  - Type-safe agent configuration with `RunConfig`

- **Gemini via OpenAI-compatible endpoint**:
  - Cost-effective (Gemini 2.5 Flash is cheaper than GPT-4)
  - Fast response times suitable for conversational UI
  - Supports function/tool calling required for MCP integration
  - Uses familiar OpenAI SDK interface via `AsyncOpenAI` client with custom `base_url`

### Implementation Pattern
```python
from openai import AsyncOpenAI
from agents import Agent, Runner, OpenAIChatCompletionsModel, RunConfig
from agents.mcp import MCPServerStreamableHttp

# Configure Gemini via OpenAI-compatible endpoint
gemini_api_key = os.getenv("GEMINI_API_KEY")
external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client=external_client
)

config = RunConfig(
    model=model,
    model_provider=external_client,
    tracing_disabled=True
)
```

### Alternatives Considered
- **Direct OpenAI GPT-4o**: Higher cost, but better intelligence. Rejected due to budget constraints for MVP.
- **Anthropic Claude via agents SDK**: Requires different SDK setup. Rejected due to additional complexity.
- **Custom agent implementation**: Full control but significant development effort. Rejected in favor of proven SDK.

### References
- OpenAI Agents Python docs: https://github.com/openai/openai-agents-python
- Gemini OpenAI compatibility: https://ai.google.dev/gemini-api/docs/openai
- MCP integration guide: https://github.com/openai/openai-agents-python/blob/main/docs/mcp.md

---

## 2. MCP Server Connection Pattern

### Decision
Use `MCPServerStreamableHttp` class from OpenAI Agents SDK to connect to the existing MCP server (spec 006) with service-to-service authentication.

### Rationale
- **MCPServerStreamableHttp** is designed for HTTP-based MCP servers with custom headers
- Supports X-User-ID header for service-to-service auth (required by spec 006)
- Async context manager pattern ensures proper connection lifecycle
- Tool caching (`cache_tools_list=True`) reduces overhead for repeated requests
- Retry support (`max_retry_attempts`) handles transient failures

### Implementation Pattern
```python
async with MCPServerStreamableHttp(
    name="Todo MCP Server",
    params={
        "url": os.getenv("MCP_SERVER_URL"),  # e.g., "http://localhost:8001/mcp"
        "headers": {"X-User-ID": user_id},
        "timeout": 10,
    },
    cache_tools_list=True,
    max_retry_attempts=3,
) as server:
    agent = Agent(
        name="Todo Assistant",
        instructions="You are a helpful task management assistant...",
        mcp_servers=[server],
    )
    result = await Runner.run(agent, user_message, messages=history)
```

### Alternatives Considered
- **MCPServerSse**: For Server-Sent Events transport. Rejected because spec 006 MCP server uses standard HTTP.
- **HostedMCPTool**: For external hosted MCP servers. Rejected because our MCP server is internal/local.
- **Direct HTTP calls without SDK**: Full control but loses automatic tool discovery. Rejected in favor of SDK abstraction.

### References
- MCP Streamable HTTP docs: https://github.com/openai/openai-agents-python/blob/main/docs/mcp.md#create-streamable-http-mcp-server-connection

---

## 3. Token Counting and Context Window Management

### Decision
Use `tiktoken` library with token-based truncation strategy: count tokens in message history, maintain 80% budget of Gemini 2.5 Flash's context limit, truncate oldest messages first while preserving system prompts.

### Rationale
- **tiktoken** is the industry-standard token counting library used by OpenAI
- Gemini 2.5 Flash context window: ~1M tokens (verify exact limit)
- 80% budget (800k tokens) provides safety margin for:
  - Agent's response generation
  - MCP tool call overhead
  - System prompts and instructions
- Token-based truncation is more precise than message-count truncation
- Preserving system prompts ensures agent behavior remains consistent

### Implementation Pattern
```python
import tiktoken

def truncate_messages_by_tokens(
    messages: list[dict],
    max_tokens: int = 800_000,  # 80% of 1M token limit
    encoding_name: str = "cl100k_base"
) -> list[dict]:
    """Truncate messages to fit within token budget, preserving system prompts."""
    encoding = tiktoken.get_encoding(encoding_name)

    # Separate system messages (always keep)
    system_msgs = [m for m in messages if m.get("role") == "system"]
    other_msgs = [m for m in messages if m.get("role") != "system"]

    # Count tokens
    system_tokens = sum(len(encoding.encode(str(m))) for m in system_msgs)
    available_tokens = max_tokens - system_tokens

    # Add messages from newest to oldest until budget exhausted
    kept_msgs = []
    current_tokens = 0
    for msg in reversed(other_msgs):
        msg_tokens = len(encoding.encode(str(msg)))
        if current_tokens + msg_tokens <= available_tokens:
            kept_msgs.insert(0, msg)
            current_tokens += msg_tokens
        else:
            break

    return system_msgs + kept_msgs
```

### Alternatives Considered
- **Message count (N recent messages)**: Simpler but imprecise. Rejected for production due to unpredictable cutoffs.
- **Sliding window with summarization**: Best UX but complex. Deferred to future enhancement (P2/P3).
- **No truncation**: Risks API errors on long conversations. Rejected for reliability.

### References
- tiktoken library: https://github.com/openai/tiktoken
- Gemini context limits: https://ai.google.dev/gemini-api/docs/models/gemini

---

## 4. Message Format Conversion (Database ↔ Agent)

### Decision
Convert database Message models (spec 007) to OpenAI Agents SDK message format using explicit mapping with role validation and metadata preservation.

### Rationale
- Spec 007 Message model has: `role` (user/assistant/tool), `content`, `metadata` (JSONB for tool calls)
- OpenAI Agents SDK expects: `{"role": str, "content": str}` format for `Runner.run(messages=...)`
- Tool calls stored in `metadata` field must be preserved for multi-turn context
- Explicit conversion function ensures type safety and handles edge cases

### Implementation Pattern
```python
from typing import List, Dict, Any
from backend.src.models import Message  # spec 007 model

def convert_db_messages_to_agent_format(
    db_messages: List[Message]
) -> List[Dict[str, Any]]:
    """Convert database messages to OpenAI Agents SDK format."""
    agent_messages = []

    for msg in db_messages:
        # Basic message structure
        agent_msg = {
            "role": msg.role,  # user | assistant | tool
            "content": msg.content,
        }

        # Preserve tool call metadata if present
        if msg.metadata and "tool_calls" in msg.metadata:
            agent_msg["tool_calls"] = msg.metadata["tool_calls"]

        agent_messages.append(agent_msg)

    return agent_messages
```

### Alternatives Considered
- **Include history as system prompt**: Loses structure and increases tokens. Rejected.
- **Automatic conversion via Pydantic**: Type mismatch between models. Rejected for explicit control.
- **Store messages in agent format directly**: Violates spec 007 schema. Rejected for compatibility.

### References
- OpenAI Agents messages format: https://github.com/openai/openai-agents-python

---

## 5. Integration with `/api/chat` Endpoint (Spec 007)

### Decision
Enhance existing `/api/chat` POST endpoint to integrate agent execution within the request/response cycle, maintaining backward compatibility with current persistence logic.

### Rationale
- Spec 007 established `/api/chat` endpoint with conversation/message persistence
- Agent integration should be transparent to API consumers
- Request flow: Load conversation → Load messages → Convert to agent format → Run agent → Save response → Return
- Async context manager for MCP connection fits naturally within async FastAPI handler
- Error handling must gracefully degrade when Gemini API unavailable (FR-012)

### Implementation Pattern
```python
from fastapi import APIRouter, Depends, HTTPException
from ai_agent.agent.agent_service import run_agent_with_context
from backend.src.models import Conversation, Message
from backend.src.services.conversation_service import ConversationService

router = APIRouter()

@router.post("/api/chat")
async def chat(
    request: ChatRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Enhanced chat endpoint with OpenAI Agent integration."""

    # Load or create conversation (spec 007 logic)
    conv_service = ConversationService(db)
    conversation = await conv_service.get_or_create(
        user_id=user_id,
        conversation_id=request.conversation_id
    )

    # Load message history
    history = await conv_service.get_messages(conversation.id)

    # Convert to agent format
    agent_messages = convert_db_messages_to_agent_format(history)

    # Run agent with MCP connection
    try:
        agent_response = await run_agent_with_context(
            user_message=request.message,
            user_id=user_id,
            conversation_history=agent_messages,
        )
    except Exception as e:
        # Graceful degradation (FR-012)
        logger.error(f"Agent execution failed: {e}")
        raise HTTPException(status_code=503, detail="AI agent temporarily unavailable")

    # Save messages (spec 007 persistence)
    await conv_service.save_message(conversation.id, role="user", content=request.message)
    await conv_service.save_message(conversation.id, role="assistant", content=agent_response)

    return {"response": agent_response, "conversation_id": conversation.id}
```

### Alternatives Considered
- **Separate agent endpoint**: Duplicates persistence logic. Rejected for DRY principle.
- **Background job for agent execution**: Adds latency and complexity. Rejected for synchronous UX requirement.
- **WebSocket streaming**: Better UX but requires client changes. Deferred to future enhancement.

### References
- FastAPI async patterns: https://fastapi.tiangolo.com/async/
- Spec 007 chat endpoint: `/specs/007-chat-persistence-service/spec.md`

---

## 6. Testing Strategy for Async Agent Integration

### Decision
Three-tier testing approach: Contract tests for interfaces, Integration tests with mocked external services, Unit tests for business logic.

### Rationale
- **Contract tests**: Verify agent initialization, MCP connection setup, message format contracts
- **Integration tests**: End-to-end agent workflows with mocked Gemini API and MCP server (avoid external dependencies in tests)
- **Unit tests**: Context manager, token counting, message conversion (fast, isolated)
- pytest-asyncio for async test support
- httpx for mocking HTTP clients in tests

### Implementation Pattern
```python
# tests/agent/contract/test_agent_initialization.py
import pytest
from ai_agent.agent.config import create_agent_config
from ai_agent.agent.agent_service import initialize_agent

@pytest.mark.asyncio
async def test_agent_config_creation():
    """Contract: Agent config must initialize with Gemini model and MCP server."""
    config = create_agent_config()
    assert config.model.model == "gemini-2.5-flash"
    assert config.model_provider is not None

# tests/agent/integration/test_agent_workflow.py
@pytest.mark.asyncio
async def test_agent_executes_list_tasks(mock_gemini_api, mock_mcp_server):
    """Integration: Agent processes 'show my tasks' and calls list_tasks MCP tool."""
    # Mock Gemini to return tool call
    mock_gemini_api.chat.completions.create = AsyncMock(
        return_value={"tool_calls": [{"name": "list_tasks"}]}
    )

    # Mock MCP server response
    mock_mcp_server.list_tasks = AsyncMock(return_value=[{"id": 1, "title": "Test"}])

    result = await run_agent_with_context(
        user_message="show my tasks",
        user_id="user123",
        conversation_history=[],
    )

    assert "Test" in result
    mock_mcp_server.list_tasks.assert_called_once()

# tests/agent/unit/test_context_manager.py
def test_truncate_messages_preserves_system():
    """Unit: Token truncation must preserve system messages."""
    messages = [
        {"role": "system", "content": "System prompt"},
        {"role": "user", "content": "Old message" * 10000},  # Large message
        {"role": "user", "content": "Recent message"},
    ]

    truncated = truncate_messages_by_tokens(messages, max_tokens=100)

    # System message must be preserved
    assert any(m["role"] == "system" for m in truncated)
    # Recent message should be kept
    assert any("Recent" in m["content"] for m in truncated)
```

### Alternatives Considered
- **End-to-end tests with real APIs**: Flaky, slow, costs money. Rejected for reliability.
- **Only unit tests**: Misses integration issues. Rejected for insufficient coverage.
- **Manual testing only**: Not repeatable. Rejected for TDD requirement.

### References
- pytest-asyncio: https://pytest-asyncio.readthedocs.io/
- FastAPI testing: https://fastapi.tiangolo.com/tutorial/testing/

---

## 7. Error Handling and Graceful Degradation

### Decision
Implement layered error handling: API-level (Gemini), connection-level (MCP), and application-level (agent execution) with specific error messages and fallback behaviors.

### Rationale
- FR-012 requires graceful degradation when Gemini API unavailable
- SC-005 requires error responses within 5 seconds
- Users need actionable error messages (not generic 500 errors)
- Monitoring/logging required for debugging production issues (FR-010)

### Implementation Pattern
```python
import logging
from fastapi import HTTPException

logger = logging.getLogger(__name__)

async def run_agent_with_context(user_message: str, user_id: str, conversation_history: list):
    """Run agent with comprehensive error handling."""
    try:
        # MCP connection errors
        async with MCPServerStreamableHttp(...) as server:
            agent = Agent(mcp_servers=[server], ...)

            try:
                # Agent execution errors (Gemini API)
                result = await Runner.run(agent, user_message, messages=conversation_history)
                return result.final_output

            except OpenAIError as e:
                # Gemini API error (rate limit, timeout, etc.)
                logger.error(f"Gemini API error for user {user_id}: {e}")
                raise HTTPException(
                    status_code=503,
                    detail="AI service temporarily unavailable. Please try again in a moment."
                )

    except ConnectionError as e:
        # MCP server connection error
        logger.error(f"MCP server connection failed for user {user_id}: {e}")
        raise HTTPException(
            status_code=503,
            detail="Task service temporarily unavailable. Please try again later."
        )

    except Exception as e:
        # Unexpected errors
        logger.exception(f"Unexpected agent error for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred. Our team has been notified."
        )
```

### Alternatives Considered
- **Generic error messages**: Poor UX. Rejected for user clarity requirement.
- **Retry logic at endpoint level**: Can cause timeouts. Rejected for simpler MCP-level retries.
- **Circuit breaker pattern**: Over-engineering for MVP. Deferred to future enhancement.

### References
- FastAPI error handling: https://fastapi.tiangolo.com/tutorial/handling-errors/

---

## 8. Configuration Management

### Decision
Use environment variables for secrets (GEMINI_API_KEY, MCP_SERVER_URL) and code-level Pydantic settings for application config with validation.

### Rationale
- Secrets must not be hardcoded (security requirement)
- Different values for dev/staging/prod environments
- Type-safe configuration with Pydantic BaseSettings
- FastAPI integration via dependency injection

### Implementation Pattern
```python
# backend/src/agent/config.py
from pydantic_settings import BaseSettings
from pydantic import Field

class AgentConfig(BaseSettings):
    """Agent configuration with environment variable support."""

    gemini_api_key: str = Field(..., env="GEMINI_API_KEY")
    mcp_server_url: str = Field(
        default="http://localhost:8001/mcp",
        env="MCP_SERVER_URL"
    )
    agent_temperature: float = Field(default=0.7, env="AGENT_TEMPERATURE")
    token_budget: int = Field(default=800_000, env="TOKEN_BUDGET")
    system_prompt: str = Field(
        default="You are a helpful task management assistant. Use the available tools to help users manage their tasks.",
        env="SYSTEM_PROMPT"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Usage
config = AgentConfig()
```

### Alternatives Considered
- **Config file (YAML/JSON)**: Harder to override per environment. Rejected for env var convention.
- **Hardcoded values**: Security risk. Rejected.
- **Database config**: Over-engineering for static values. Rejected.

### References
- Pydantic Settings: https://docs.pydantic.dev/latest/concepts/pydantic_settings/

---

## Summary of Decisions

| Area | Decision | Key Rationale |
|------|----------|---------------|
| **Agent Framework** | OpenAI Agents SDK + Gemini 2.5 Flash | Built-in MCP support, cost-effective, async-compatible |
| **MCP Connection** | MCPServerStreamableHttp | Service-to-service auth support, tool caching, retry logic |
| **Context Management** | Token-based truncation (tiktoken, 80% budget) | Industry standard, precise, prevents API errors |
| **Message Conversion** | Explicit mapping function | Type safety, metadata preservation, spec 007 compatibility |
| **Endpoint Integration** | Enhance existing `/api/chat` | Maintains compatibility, reuses persistence logic |
| **Testing** | Contract + Integration (mocked) + Unit | TDD-compliant, fast, reliable |
| **Error Handling** | Layered with specific messages | User clarity, debugging support, graceful degradation |
| **Configuration** | Pydantic BaseSettings + env vars | Type-safe, environment-specific, secure |

---

## Open Questions / Future Enhancements

1. **Streaming responses**: Current implementation returns complete response. Future: implement streaming for better UX during long operations.
2. **Conversation summarization**: Current implementation uses truncation. Future: implement summarization for very long conversations (preserves more context).
3. **Multi-language support**: Agent instructions are English-only. Future: support i18n for global users.
4. **Custom tool approval flows**: Current implementation auto-approves all MCP tools. Future: implement approval workflows for sensitive operations.
5. **Agent performance monitoring**: Basic logging implemented. Future: add metrics (latency, token usage, tool call frequency) for optimization.

---

**Research Complete**: All technical decisions documented. Ready for Phase 1 (Design & Contracts).
