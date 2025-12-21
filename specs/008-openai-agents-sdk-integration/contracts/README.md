# API Contracts: OpenAI Agents SDK Integration

**Feature**: 008-openai-agents-sdk-integration
**Date**: 2025-12-20

## Overview

This directory contains the formal contracts (interfaces, schemas, protocols) for the agent system integration. These contracts serve as the source of truth for:

1. **Test-Driven Development**: Write tests against these contracts before implementation
2. **Module Boundaries**: Clear interfaces between agent components
3. **API Compatibility**: OpenAPI schema for HTTP endpoints
4. **Type Safety**: Python protocols and Pydantic models

---

## Files

### `agent_interfaces.py`
Python interface definitions using ABC (Abstract Base Classes) and Protocol (structural typing).

**Contents**:
- `IAgentConfig`: Configuration interface
- `IMessageConverter`: Database ↔ Agent message conversion
- `IContextManager`: Context loading and token management
- `IMCPConnection`: MCP server connection management
- `IAgentService`: Agent orchestration and execution
- Data models: `AgentMessage`, `AgentContext`, `AgentResult`, `AgentExecutionError`
- Custom exceptions: `ConfigurationError`, `GeminiAPIError`, `MCPConnectionError`, etc.

**Usage**:
```python
# In tests - define mocks based on interfaces
class MockAgentService(IAgentService):
    async def run_agent_with_context(self, context: AgentContext) -> AgentResult:
        return AgentResult(response_text="Test response", ...)

# In implementation - implement interfaces
class AgentService(IAgentService):
    async def run_agent_with_context(self, context: AgentContext) -> AgentResult:
        # Real implementation
        ...
```

### `api_schema.yaml`
OpenAPI 3.0 specification for the `/api/chat` endpoint with agent integration.

**Contents**:
- POST `/api/chat`: Send message to AI agent
- GET `/api/conversations`: List conversations (unchanged from spec 007)
- GET `/api/conversations/{id}`: Get conversation detail (unchanged from spec 007)
- Request/Response schemas: `ChatRequest`, `ChatResponse`, `ErrorResponse`
- Data models: `Conversation`, `Message`, `ConversationDetail`
- Error handling: 400, 401, 403, 503 responses
- Examples: Common agent interactions (list tasks, create task, etc.)

**Usage**:
```bash
# Validate OpenAPI schema
npx @stoplight/spectral-cli lint api_schema.yaml

# Generate client code (optional)
openapi-generator generate -i api_schema.yaml -g python -o ./client

# View in Swagger UI
docker run -p 8080:8080 -e SWAGGER_JSON=/api_schema.yaml -v ${PWD}:/docs swaggerapi/swagger-ui
```

---

## Contract Testing Strategy

### 1. Contract Tests (Test Interfaces)

Write tests that verify implementations conform to interface contracts:

```python
# tests/agent/contract/test_message_converter_contract.py
from backend.src.agent.message_converter import MessageConverter
from backend.src.models import Message

def test_message_converter_implements_interface():
    """Contract: MessageConverter must implement IMessageConverter."""
    converter = MessageConverter()
    assert hasattr(converter, 'db_to_agent')
    assert hasattr(converter, 'db_messages_to_agent_batch')

def test_db_to_agent_converts_user_message():
    """Contract: db_to_agent must convert user message correctly."""
    db_msg = Message(role="user", content="Hello", metadata=None)
    converter = MessageConverter()

    result = converter.db_to_agent(db_msg)

    assert result.role == "user"
    assert result.content == "Hello"
    assert result.tool_calls is None
```

### 2. Integration Tests (Mock External Services)

Test component integration using mocks for external dependencies:

```python
# tests/agent/integration/test_agent_workflow.py
from unittest.mock import AsyncMock, MagicMock
import pytest

@pytest.mark.asyncio
async def test_agent_lists_tasks_end_to_end(mock_gemini, mock_mcp):
    """Integration: Full agent workflow with mocked Gemini and MCP."""
    # Setup mocks
    mock_gemini.chat.completions.create.return_value = AsyncMock(
        choices=[{"message": {"content": "Here are your tasks..."}}]
    )
    mock_mcp.list_tasks.return_value = [{"id": 1, "title": "Test"}]

    # Execute
    context = AgentContext(
        user_id="user123",
        user_message="show my tasks",
        conversation_history=[],
        config={}
    )
    result = await agent_service.run_agent_with_context(context)

    # Verify
    assert "Test" in result.response_text
    mock_mcp.list_tasks.assert_called_once()
```

### 3. API Contract Tests (HTTP Endpoints)

Test HTTP API conforms to OpenAPI schema:

```python
# tests/api/test_chat_api_contract.py
from fastapi.testclient import TestClient
import pytest

def test_chat_endpoint_accepts_valid_request(client: TestClient):
    """Contract: POST /api/chat accepts ChatRequest schema."""
    response = client.post(
        "/api/chat",
        json={"message": "Hello", "conversation_id": None},
        headers={"Authorization": "Bearer test_token"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "conversation_id" in data
    assert isinstance(data["response"], str)

def test_chat_endpoint_returns_503_on_agent_failure(client: TestClient, mock_agent_error):
    """Contract: POST /api/chat returns 503 when agent unavailable."""
    response = client.post(
        "/api/chat",
        json={"message": "Hello"},
        headers={"Authorization": "Bearer test_token"}
    )

    assert response.status_code == 503
    data = response.json()
    assert data["error"] == "service_unavailable"
    assert "retry_after" in data
```

---

## Validation Rules

### Request Validation

**ChatRequest**:
- `message`: Required, 1-10,000 characters
- `conversation_id`: Optional integer, null for new conversation

### Response Validation

**ChatResponse**:
- `response`: Required non-empty string
- `conversation_id`: Required integer
- `metadata`: Optional object with `tokens_used`, `model`, `execution_time_ms`, `tool_calls`

### Error Response Format

All errors follow this structure:
```json
{
  "error": "error_code",
  "message": "Human-readable message",
  "details": { /* optional additional info */ },
  "retry_after": 30  // for 503 errors only
}
```

**Error Codes**:
- `validation_error`: Request validation failed
- `unauthorized`: Missing/invalid authentication
- `forbidden`: User doesn't own resource
- `not_found`: Resource doesn't exist
- `service_unavailable`: Gemini API or MCP server error
- `internal_error`: Unexpected server error

---

## Interface Dependencies

```
┌─────────────────────────────────────────────────┐
│              /api/chat Endpoint                 │
│         (FastAPI request handler)               │
└───────────────────┬─────────────────────────────┘
                    │
                    ▼
        ┌───────────────────────────┐
        │   IAgentService           │
        │   run_agent_with_context()│
        └───────────┬───────────────┘
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
┌───────────────────┐   ┌──────────────────┐
│ IContextManager   │   │ IMCPConnection   │
│ load_history()    │   │ create_conn()    │
│ truncate_tokens() │   │                  │
└───────┬───────────┘   └────────┬─────────┘
        │                        │
        ▼                        │
┌───────────────────┐            │
│ IMessageConverter │            │
│ db_to_agent()     │            │
└───────────────────┘            │
                                 │
                    ┌────────────┴────────────┐
                    │   Agent + Runner        │
                    │   (OpenAI Agents SDK)   │
                    └─────────────────────────┘
```

---

## Contract Evolution

When modifying contracts:

1. **Backward Compatibility**: Avoid breaking changes to published contracts
2. **Versioning**: If breaking change required, version the interface (e.g., `IAgentServiceV2`)
3. **Documentation**: Update this README and inline documentation
4. **Tests**: Update contract tests to reflect changes
5. **Communication**: Notify team of contract changes before merging

**Breaking Changes Examples**:
- Removing required field from `ChatRequest`
- Changing return type of interface method
- Removing interface method

**Non-Breaking Changes Examples**:
- Adding optional field to `ChatRequest`
- Adding new interface method (with default implementation)
- Adding new error code

---

## References

- OpenAPI Specification: https://swagger.io/specification/
- Python Protocols: https://peps.python.org/pep-0544/
- Pydantic Models: https://docs.pydantic.dev/
- Contract Testing Guide: https://martinfowler.com/bliki/ContractTest.html

---

**Contracts Complete**: All interfaces defined. Ready for TDD implementation.
