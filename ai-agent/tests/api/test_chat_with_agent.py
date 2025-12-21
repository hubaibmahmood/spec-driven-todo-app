"""API tests for chat endpoint with agent integration."""

import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch
from ai_agent.main import app
from ai_agent.agent.agent_service import AgentResult


@pytest.mark.asyncio
async def test_chat_endpoint_uses_agent():
    """API: /api/chat processes message through agent."""

    # Mock AgentService
    mock_result = AgentResult(
        response_text="You have 3 tasks pending.",
        execution_time_ms=150,
        tokens_used=45,
        tool_calls_made=[],
        model="gemini-2.5-flash"
    )

    with patch('ai_agent.api.chat.AgentService') as MockAgentService:
        mock_service = MockAgentService.return_value
        mock_service.run_agent_with_context = AsyncMock(return_value=mock_result)

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/chat",
                json={"message": "show my tasks", "conversation_id": None},
                headers={"X-User-ID": "test_user_123"}
            )

            assert response.status_code == 200
            data = response.json()
            assert "conversation_id" in data
            assert data["assistant_message"] == "You have 3 tasks pending."
            assert "test_user_123" in str(mock_service.run_agent_with_context.call_args)


@pytest.mark.asyncio
async def test_chat_endpoint_extracts_timezone_header():
    """API: /api/chat extracts X-Timezone header."""

    mock_result = AgentResult(
        response_text="Task added",
        execution_time_ms=100,
        tokens_used=20,
        tool_calls_made=[],
        model="gemini-2.5-flash"
    )

    with patch('ai_agent.api.chat.AgentService') as MockAgentService:
        mock_service = MockAgentService.return_value
        mock_service.run_agent_with_context = AsyncMock(return_value=mock_result)

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/chat",
                json={"message": "add task", "conversation_id": None},
                headers={
                    "X-User-ID": "test_user_123",
                    "X-Timezone": "America/New_York"
                }
            )

            assert response.status_code == 200

            # Verify timezone was passed to agent
            call_kwargs = mock_service.run_agent_with_context.call_args.kwargs
            assert call_kwargs.get("user_timezone") == "America/New_York"
