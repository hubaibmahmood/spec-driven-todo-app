# Quickstart: OpenAI Agents SDK Integration

**Feature**: 008-openai-agents-sdk-integration
**Date**: 2025-12-20
**Prerequisites**: Spec 007 (Chat Persistence), Spec 006 (MCP Server)

## Overview

This quickstart guide provides step-by-step instructions for implementing the OpenAI Agents SDK integration with Gemini API backend. Follow the **Red-Green-Refactor** TDD workflow for each component.

---

## Architecture Summary

```
User Message → /api/chat → AgentService → [Gemini API + MCP Server] → Response
                    ↓
              Conversation
              Persistence
              (PostgreSQL)
```

**Key Components**:
1. **AgentConfig** - Configuration management (Gemini key, MCP URL, etc.)
2. **MessageConverter** - Convert DB messages ↔ Agent format
3. **ContextManager** - Load history, truncate by tokens
4. **MCPConnection** - Connect to MCP server with auth
5. **AgentService** - Orchestrate agent execution
6. **ChatEndpoint** - Enhanced `/api/chat` endpoint

---

## Phase 1: Setup & Configuration

### Step 1.1: Install Dependencies

**RED**: Write failing test for dependency imports
```python
# tests/agent/contract/test_dependencies.py
def test_required_packages_importable():
    """Contract: All required packages must be importable."""
    try:
        import agents
        from agents import Agent, Runner
        from agents.mcp import MCPServerStreamableHttp
        from openai import AsyncOpenAI
        import tiktoken
    except ImportError as e:
        pytest.fail(f"Required package not installed: {e}")
```

**GREEN**: Install dependencies
```bash
cd ai-agent
uv add openai-agents-python openai httpx tiktoken pydantic-settings
uv add --dev pytest-asyncio httpx
```

**REFACTOR**: Verify installation, update `pyproject.toml`

---

### Step 1.2: Environment Configuration

**RED**: Write failing test for config validation
```python
# ai-agent/tests/agent/contract/test_agent_config.py
from ai_agent.agent.config import AgentConfig
import pytest

def test_agent_config_requires_gemini_api_key():
    """Contract: AgentConfig must validate GEMINI_API_KEY presence."""
    with pytest.raises(ValueError, match="GEMINI_API_KEY"):
        AgentConfig(gemini_api_key="")  # Empty key should fail
```

**GREEN**: Implement `AgentConfig`
```python
# ai-agent/src/ai_agent/agent/config.py
from pydantic_settings import BaseSettings
from pydantic import Field, validator

class AgentConfig(BaseSettings):
    gemini_api_key: str = Field(..., env="GEMINI_API_KEY")
    mcp_server_url: str = Field(default="http://localhost:8001/mcp", env="MCP_SERVER_URL")
    mcp_timeout: int = Field(default=10, env="MCP_TIMEOUT")
    mcp_retry_attempts: int = Field(default=3, env="MCP_RETRY_ATTEMPTS")
    system_prompt: str = Field(
        default="You are a helpful task management assistant. Use the available tools to help users manage their tasks.",
        env="SYSTEM_PROMPT"
    )
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, env="AGENT_TEMPERATURE")
    token_budget: int = Field(default=800_000, env="TOKEN_BUDGET")
    encoding_name: str = Field(default="cl100k_base", env="ENCODING_NAME")

    @validator("gemini_api_key")
    def validate_api_key(cls, v):
        if not v or v.strip() == "":
            raise ValueError("GEMINI_API_KEY is required and cannot be empty")
        return v

    class Config:
        env_file = ".env"
```

**REFACTOR**: Add `.env.example`
```bash
# ai-agent/.env.example
GEMINI_API_KEY=your_gemini_api_key_here
MCP_SERVER_URL=http://localhost:8001/mcp
AGENT_TEMPERATURE=0.7
TOKEN_BUDGET=800000
```

---

## Phase 2: Message Conversion

### Step 2.1: DB to Agent Format

**RED**: Write failing conversion test
```python
# tests/agent/unit/test_message_converter.py
from ai_agent.agent.message_converter import MessageConverter
from ai_agent.database.models import Message
import pytest

def test_convert_user_message_to_agent_format():
    """Unit: Convert database user message to AgentMessage."""
    db_msg = Message(
        id=1,
        conversation_id=42,
        role="user",
        content="Show my tasks",
        metadata=None
    )
    converter = MessageConverter()

    result = converter.db_to_agent(db_msg)

    assert result["role"] == "user"
    assert result["content"] == "Show my tasks"
    assert "tool_calls" not in result or result["tool_calls"] is None

def test_convert_assistant_message_with_tool_calls():
    """Unit: Convert assistant message preserving tool calls."""
    db_msg = Message(
        role="assistant",
        content="I'll list your tasks.",
        metadata={
            "tool_calls": [
                {"id": "call_123", "type": "function", "function": {"name": "list_tasks", "arguments": "{}"}}
            ]
        }
    )
    converter = MessageConverter()

    result = converter.db_to_agent(db_msg)

    assert result["role"] == "assistant"
    assert result["tool_calls"] == db_msg.metadata["tool_calls"]
```

**GREEN**: Implement `MessageConverter`
```python
# backend/src/agent/message_converter.py
from typing import List, Dict, Any, Optional
from ai_agent.database.models import Message

class MessageConverter:
    """Convert between database Message models and agent-compatible format."""

    def db_to_agent(self, db_message: Message) -> Dict[str, Any]:
        """Convert database Message to agent format."""
        agent_msg = {
            "role": db_message.role,
            "content": db_message.content,
        }

        # Preserve tool calls from metadata
        if db_message.metadata and "tool_calls" in db_message.metadata:
            agent_msg["tool_calls"] = db_message.metadata["tool_calls"]

        return agent_msg

    def db_messages_to_agent_batch(self, db_messages: List[Message]) -> List[Dict[str, Any]]:
        """Convert list of database messages to agent format."""
        return [self.db_to_agent(msg) for msg in db_messages]
```

**REFACTOR**: Extract validation, add type hints

---

## Phase 3: Context Management

### Step 3.1: Token Counting

**RED**: Write failing token truncation test
```python
# tests/agent/unit/test_context_manager.py
from ai_agent.agent.context_manager import ContextManager
import pytest

def test_truncate_preserves_system_messages():
    """Unit: Token truncation must preserve all system messages."""
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Old message" * 1000},  # Very long
        {"role": "assistant", "content": "Old response" * 1000},
        {"role": "user", "content": "Recent message"},
    ]
    manager = ContextManager()

    truncated = manager.truncate_by_tokens(messages, max_tokens=500)

    # System message must be preserved
    assert any(m["role"] == "system" for m in truncated)
    # Recent message should be kept
    assert any("Recent" in m["content"] for m in truncated)
    # Old long messages should be dropped
    assert not any("Old message" in m.get("content", "") for m in truncated)
```

**GREEN**: Implement token truncation
```python
# backend/src/agent/context_manager.py
import tiktoken
from typing import List, Dict, Any

class ContextManager:
    """Manage agent execution context including token truncation."""

    def __init__(self, encoding_name: str = "cl100k_base"):
        self.encoding = tiktoken.get_encoding(encoding_name)

    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        return len(self.encoding.encode(text))

    def truncate_by_tokens(
        self,
        messages: List[Dict[str, Any]],
        max_tokens: int
    ) -> List[Dict[str, Any]]:
        """Truncate messages to fit within token budget."""
        # Separate system messages (always keep)
        system_msgs = [m for m in messages if m.get("role") == "system"]
        other_msgs = [m for m in messages if m.get("role") != "system"]

        # Count system message tokens
        system_tokens = sum(self.count_tokens(str(m)) for m in system_msgs)
        available_tokens = max_tokens - system_tokens

        if available_tokens <= 0:
            return system_msgs  # Only system messages fit

        # Add messages from newest to oldest
        kept_msgs = []
        current_tokens = 0
        for msg in reversed(other_msgs):
            msg_tokens = self.count_tokens(str(msg))
            if current_tokens + msg_tokens <= available_tokens:
                kept_msgs.insert(0, msg)
                current_tokens += msg_tokens
            else:
                break

        return system_msgs + kept_msgs
```

**REFACTOR**: Optimize token counting (cache results)

---

### Step 3.2: Load Conversation History

**RED**: Write integration test for history loading
```python
# tests/agent/integration/test_context_loading.py
from ai_agent.agent.context_manager import ContextManager
from ai_agent.database.models import Conversation, Message
import pytest

@pytest.mark.asyncio
async def test_load_conversation_history(db_session):
    """Integration: Load and convert conversation history."""
    # Setup test data
    conv = Conversation(user_id="user123")
    db_session.add(conv)
    await db_session.commit()

    msg1 = Message(conversation_id=conv.id, role="user", content="Hello")
    msg2 = Message(conversation_id=conv.id, role="assistant", content="Hi there")
    db_session.add_all([msg1, msg2])
    await db_session.commit()

    # Test
    manager = ContextManager()
    history = await manager.load_conversation_history(conv.id, "user123", db_session)

    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[1]["role"] == "assistant"
```

**GREEN**: Implement history loading
```python
# backend/src/agent/context_manager.py (add method)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ai_agent.database.models import Conversation, Message

class ContextManager:
    # ... existing methods ...

    async def load_conversation_history(
        self,
        conversation_id: int,
        user_id: str,
        db: AsyncSession
    ) -> List[Dict[str, Any]]:
        """Load conversation history from database."""
        from ai_agent.agent.message_converter import MessageConverter

        # Verify conversation ownership
        conv = await db.get(Conversation, conversation_id)
        if not conv or conv.user_id != user_id:
            raise PermissionError("User does not own this conversation")

        # Load messages
        result = await db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
        )
        messages = result.scalars().all()

        # Convert to agent format
        converter = MessageConverter()
        return converter.db_messages_to_agent_batch(messages)
```

**REFACTOR**: Extract database queries to service layer

---

## Phase 4: MCP Connection

### Step 4.1: MCP Server Connection

**RED**: Write MCP connection test
```python
# tests/agent/contract/test_mcp_connection.py
from ai_agent.agent.mcp_connection import create_mcp_connection
from ai_agent.agent.config import AgentConfig
import pytest

@pytest.mark.asyncio
async def test_create_mcp_connection(mock_mcp_server):
    """Contract: create_mcp_connection establishes MCPServerStreamableHttp."""
    config = AgentConfig(
        gemini_api_key="test_key",
        mcp_server_url="http://localhost:8001/mcp"
    )

    async with create_mcp_connection("user123", config) as server:
        assert server is not None
        # Verify connection parameters
        assert "X-User-ID" in server.params["headers"]
        assert server.params["headers"]["X-User-ID"] == "user123"
```

**GREEN**: Implement MCP connection
```python
# backend/src/agent/mcp_connection.py
from agents.mcp import MCPServerStreamableHttp
from ai_agent.agent.config import AgentConfig
from contextlib import asynccontextmanager

@asynccontextmanager
async def create_mcp_connection(user_id: str, config: AgentConfig):
    """Create MCP server connection with user authentication."""
    async with MCPServerStreamableHttp(
        name="Todo MCP Server",
        params={
            "url": config.mcp_server_url,
            "headers": {"X-User-ID": user_id},
            "timeout": config.mcp_timeout,
        },
        cache_tools_list=True,
        max_retry_attempts=config.mcp_retry_attempts,
    ) as server:
        yield server
```

**REFACTOR**: Add connection error handling

---

## Phase 5: Agent Service

### Step 5.1: Agent Initialization

**RED**: Write agent initialization test
```python
# tests/agent/contract/test_agent_service.py
from ai_agent.agent.agent_service import AgentService
from ai_agent.agent.config import AgentConfig
import pytest

@pytest.mark.asyncio
async def test_initialize_agent_with_gemini(mock_mcp_server):
    """Contract: initialize_agent creates Agent with Gemini model."""
    config = AgentConfig(gemini_api_key="test_key")
    service = AgentService(config)

    agent = await service.initialize_agent(mock_mcp_server)

    assert agent is not None
    # Verify agent has MCP server
    assert len(agent.mcp_servers) == 1
```

**GREEN**: Implement agent initialization
```python
# backend/src/agent/agent_service.py
import os
from openai import AsyncOpenAI
from agents import Agent, OpenAIChatCompletionsModel, RunConfig
from ai_agent.agent.config import AgentConfig

class AgentService:
    def __init__(self, config: AgentConfig):
        self.config = config

    async def initialize_agent(self, mcp_server):
        """Initialize OpenAI Agent with Gemini backend and MCP server."""
        # Setup Gemini via OpenAI-compatible endpoint
        external_client = AsyncOpenAI(
            api_key=self.config.gemini_api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        )

        model = OpenAIChatCompletionsModel(
            model="gemini-2.5-flash",
            openai_client=external_client
        )

        run_config = RunConfig(
            model=model,
            model_provider=external_client,
            tracing_disabled=True,  # Disable for MVP
        )

        # Create agent
        agent = Agent(
            name="Todo Assistant",
            instructions=self.config.system_prompt,
            mcp_servers=[mcp_server],
            run_config=run_config,
        )

        return agent
```

**REFACTOR**: Extract client creation to helper function

---

### Step 5.2: Agent Execution

**RED**: Write agent execution test
```python
# tests/agent/integration/test_agent_execution.py
from ai_agent.agent.agent_service import AgentService
from ai_agent.agent.config import AgentConfig
import pytest

@pytest.mark.asyncio
async def test_run_agent_with_user_message(mock_gemini_api, mock_mcp_server):
    """Integration: run_agent processes user message and returns response."""
    config = AgentConfig(gemini_api_key="test_key")
    service = AgentService(config)

    # Mock Gemini response
    mock_gemini_api.completions.create.return_value = {
        "choices": [{"message": {"content": "You have 3 tasks."}}]
    }

    result = await service.run_agent_with_context(
        user_id="user123",
        user_message="show my tasks",
        conversation_history=[],
    )

    assert result.response_text == "You have 3 tasks."
    assert result.tokens_used > 0
```

**GREEN**: Implement agent execution
```python
# backend/src/agent/agent_service.py (add methods)
from agents import Runner
from typing import List, Dict, Any
from ai_agent.agent.mcp_connection import create_mcp_connection
import time

class AgentService:
    # ... existing methods ...

    async def run_agent_with_context(
        self,
        user_id: str,
        user_message: str,
        conversation_history: List[Dict[str, Any]],
    ):
        """Run agent with full context management."""
        start_time = time.time()

        async with create_mcp_connection(user_id, self.config) as mcp_server:
            agent = await self.initialize_agent(mcp_server)

            # Add system message to history
            messages = conversation_history + [
                {"role": "user", "content": user_message}
            ]

            # Run agent
            result = await Runner.run(agent, user_message, messages=messages)

            execution_time = int((time.time() - start_time) * 1000)

            return {
                "response_text": result.final_output,
                "tool_calls_made": [],  # TODO: Extract from result
                "tokens_used": 0,  # TODO: Count tokens
                "model": "gemini-2.5-flash",
                "execution_time_ms": execution_time,
            }
```

**REFACTOR**: Return AgentResult model, extract tool calls

---

## Phase 6: Enhanced Chat Endpoint

### Step 6.1: Integrate Agent into Endpoint

**RED**: Write endpoint integration test
```python
# tests/api/test_chat_with_agent.py
from fastapi.testclient import TestClient
import pytest

def test_chat_endpoint_uses_agent(client: TestClient, auth_headers):
    """Integration: /api/chat processes message through agent."""
    response = client.post(
        "/api/chat",
        json={"message": "show my tasks", "conversation_id": None},
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "conversation_id" in data
    assert len(data["response"]) > 0  # Non-empty response
```

**GREEN**: Enhance chat endpoint
```python
# ai-agent/src/ai_agent/api/chat.py (modify existing endpoint)
from fastapi import APIRouter, Depends, HTTPException
from ai_agent.agent.agent_service import AgentService
from ai_agent.agent.config import AgentConfig
from ai_agent.agent.context_manager import ContextManager

router = APIRouter()

@router.post("/api/chat")
async def chat(
    request: ChatRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Enhanced chat endpoint with agent integration."""
    # Load configuration
    config = AgentConfig()
    agent_service = AgentService(config)
    context_manager = ContextManager()

    # Load or create conversation
    conv_service = ConversationService(db)
    conversation = await conv_service.get_or_create(
        user_id=user_id,
        conversation_id=request.conversation_id
    )

    # Load and truncate history
    history = await context_manager.load_conversation_history(
        conversation.id, user_id, db
    )
    truncated_history = context_manager.truncate_by_tokens(
        history, max_tokens=config.token_budget
    )

    # Run agent
    try:
        result = await agent_service.run_agent_with_context(
            user_id=user_id,
            user_message=request.message,
            conversation_history=truncated_history,
        )
    except Exception as e:
        logger.error(f"Agent execution failed: {e}")
        raise HTTPException(
            status_code=503,
            detail="AI agent temporarily unavailable"
        )

    # Save messages
    await conv_service.save_message(conversation.id, "user", request.message)
    await conv_service.save_message(
        conversation.id,
        "assistant",
        result["response_text"],
        metadata={
            "tool_calls": result["tool_calls_made"],
            "tokens_used": result["tokens_used"],
            "model": result["model"],
        }
    )

    return {
        "response": result["response_text"],
        "conversation_id": conversation.id,
        "metadata": {
            "tokens_used": result["tokens_used"],
            "model": result["model"],
            "execution_time_ms": result["execution_time_ms"],
        }
    }
```

**REFACTOR**: Extract business logic to service layer

---

## Testing Strategy

### Test Order (TDD Workflow)

1. **Contract Tests**: Interface compliance
   - `test_dependencies.py`
   - `test_agent_config.py`
   - `test_message_converter_contract.py`
   - `test_mcp_connection.py`
   - `test_agent_service.py`

2. **Unit Tests**: Individual functions
   - `test_message_converter.py`
   - `test_context_manager.py`
   - `test_token_counting.py`

3. **Integration Tests**: Component interaction (mocked external services)
   - `test_context_loading.py`
   - `test_agent_execution.py`
   - `test_agent_workflow.py`

4. **API Tests**: HTTP endpoint behavior
   - `test_chat_with_agent.py`
   - `test_error_handling.py`

### Running Tests

```bash
# Run all tests
uv run pytest ai-agent/tests/agent/

# Run specific test category
uv run pytest ai-agent/tests/agent/contract/
uv run pytest ai-agent/tests/agent/unit/
uv run pytest ai-agent/tests/agent/integration/

# Run with coverage
uv run pytest ai-agent/tests/agent/ --cov=backend/src/agent --cov-report=html

# Run specific test
uv run pytest ai-agent/tests/agent/unit/test_message_converter.py::test_convert_user_message
```

---

## Verification Checklist

After implementation, verify:

- [ ] All tests pass (`uv run pytest ai-agent/tests/agent/`)
- [ ] Type checking passes (`uv run mypy backend/src/agent/`)
- [ ] Code style passes (`uv run ruff check backend/src/agent/`)
- [ ] Agent responds to "show my tasks" via `/api/chat`
- [ ] Agent creates tasks via natural language
- [ ] Multi-turn conversations maintain context
- [ ] Token truncation prevents API errors
- [ ] Graceful degradation on Gemini API failure
- [ ] MCP connection uses X-User-ID header correctly

---

## Common Issues & Solutions

### Issue: Gemini API Authentication Error

```python
Error: 401 Unauthorized from Gemini API
```

**Solution**: Verify `GEMINI_API_KEY` in `.env` is valid:
```bash
export GEMINI_API_KEY="your_actual_key"
uv run python -c "from ai_agent.agent.config import AgentConfig; print(AgentConfig().gemini_api_key)"
```

### Issue: MCP Server Connection Timeout

```python
Error: Connection timeout to MCP server
```

**Solution**: Verify MCP server is running:
```bash
# Start MCP server (from spec 006)
cd mcp-server
uv run python -m todo_mcp_server.server

# Verify endpoint
curl http://localhost:8001/mcp
```

### Issue: Token Counting Performance Slow

```python
Warning: Token counting takes >1s per request
```

**Solution**: Cache token counts in message metadata:
```python
# When saving message
metadata = {
    "token_count": context_manager.count_tokens(content),
    ...
}
```

---

## Next Steps

After completing this quickstart:

1. Run `/sp.tasks` to generate detailed task breakdown
2. Implement each module following TDD workflow above
3. Test end-to-end agent workflow with real Gemini API
4. Monitor performance and adjust token budget if needed
5. Add observability (logging, metrics) for production
6. Document any deviations from this quickstart

---

**Quickstart Complete**: Ready for TDD implementation following this guide.
