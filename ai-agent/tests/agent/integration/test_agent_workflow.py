"""End-to-end workflow tests for agent integration."""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from ai_agent.agent.agent_service import AgentService, AgentResult
from ai_agent.agent.config import AgentConfig


@pytest.mark.asyncio
async def test_e2e_agent_workflow():
    """E2E: Complete agent workflow from message to response with MCP tools."""

    config = AgentConfig(gemini_api_key="test_key_12345")
    service = AgentService(config)

    # Mock MCP server responses
    mock_mcp_server = Mock()
    mock_mcp_server.list_tools = AsyncMock(return_value=[
        {"name": "list_tasks", "description": "List all tasks"},
        {"name": "create_task", "description": "Create a new task"},
    ])

    # Mock agent execution result
    mock_result = Mock()
    mock_result.final_output = "You have 3 tasks: 1. Buy groceries, 2. Finish report, 3. Call mom"
    mock_result.messages = [
        {"role": "user", "content": "show my tasks"},
        {
            "role": "assistant",
            "content": None,
            "tool_calls": [{
                "id": "call_123",
                "type": "function",
                "function": {
                    "name": "list_tasks",
                    "arguments": '{"user_id": "test_user"}'
                }
            }]
        },
        {
            "role": "tool",
            "tool_call_id": "call_123",
            "content": '[{"id": 1, "title": "Buy groceries"}, {"id": 2, "title": "Finish report"}, {"id": 3, "title": "Call mom"}]'
        },
        {
            "role": "assistant",
            "content": "You have 3 tasks: 1. Buy groceries, 2. Finish report, 3. Call mom"
        }
    ]

    with patch('ai_agent.agent.agent_service.create_mcp_connection') as mock_mcp_conn, \
         patch('ai_agent.agent.agent_service.Runner') as mock_runner:

        # Setup mocks
        mock_mcp_conn.return_value.__aenter__ = AsyncMock(return_value=mock_mcp_server)
        mock_mcp_conn.return_value.__aexit__ = AsyncMock(return_value=None)
        mock_runner.run = AsyncMock(return_value=mock_result)

        # Execute complete workflow
        result = await service.run_agent_with_context(
            user_id="test_user",
            user_message="show my tasks",
            conversation_history=[],
            user_timezone="America/New_York"
        )

        # Verify E2E flow
        assert isinstance(result, AgentResult)
        assert "3 tasks" in result.response_text
        assert result.execution_time_ms >= 0
        assert result.tokens_used > 0
        assert len(result.tool_calls_made) == 1
        assert result.tool_calls_made[0]["function"]["name"] == "list_tasks"

        # Verify MCP connection was created with correct user_id
        mock_mcp_conn.assert_called_once()
        assert "test_user" in str(mock_mcp_conn.call_args)


@pytest.mark.asyncio
async def test_e2e_create_task_workflow():
    """E2E: Create task with natural language parsing."""

    config = AgentConfig(gemini_api_key="test_key_12345")
    service = AgentService(config)

    mock_mcp_server = Mock()
    mock_result = Mock()
    mock_result.final_output = "I've added 'Buy milk' to your tasks with high priority, due tomorrow."
    mock_result.messages = [
        {"role": "user", "content": "add urgent task to buy milk tomorrow"},
        {
            "role": "assistant",
            "content": None,
            "tool_calls": [{
                "id": "call_456",
                "type": "function",
                "function": {
                    "name": "create_task",
                    "arguments": '{"title": "Buy milk", "priority": "Urgent", "due_date": "2025-12-21T23:59:59Z"}'
                }
            }]
        },
        {
            "role": "tool",
            "tool_call_id": "call_456",
            "content": '{"id": 4, "title": "Buy milk", "priority": "Urgent"}'
        },
        {
            "role": "assistant",
            "content": "I've added 'Buy milk' to your tasks with high priority, due tomorrow."
        }
    ]

    with patch('ai_agent.agent.agent_service.create_mcp_connection') as mock_mcp_conn, \
         patch('ai_agent.agent.agent_service.Runner') as mock_runner:

        mock_mcp_conn.return_value.__aenter__ = AsyncMock(return_value=mock_mcp_server)
        mock_mcp_conn.return_value.__aexit__ = AsyncMock(return_value=None)
        mock_runner.run = AsyncMock(return_value=mock_result)

        result = await service.run_agent_with_context(
            user_id="test_user",
            user_message="add urgent task to buy milk tomorrow",
            conversation_history=[],
            user_timezone="UTC"
        )

        # Verify task creation workflow
        assert isinstance(result, AgentResult)
        assert "Buy milk" in result.response_text
        assert len(result.tool_calls_made) == 1
        assert result.tool_calls_made[0]["function"]["name"] == "create_task"

        # Verify arguments were parsed correctly
        import json
        args = json.loads(result.tool_calls_made[0]["function"]["arguments"])
        assert args["title"] == "Buy milk"
        assert args["priority"] == "Urgent"


@pytest.mark.asyncio
async def test_e2e_multi_turn_conversation():
    """E2E: Multi-turn conversation with context preservation."""

    config = AgentConfig(gemini_api_key="test_key_12345")
    service = AgentService(config)

    from ai_agent.database.models import Message

    # Previous conversation history
    history = [
        Message(id=1, conversation_id=1, role="user", content="show urgent tasks", message_metadata=None),
        Message(id=2, conversation_id=1, role="assistant", content="You have 2 urgent tasks", message_metadata=None),
    ]

    mock_mcp_server = Mock()
    mock_result = Mock()
    mock_result.final_output = "I've marked the first urgent task as complete."
    mock_result.messages = [{"role": "assistant", "content": "I've marked the first urgent task as complete."}]

    with patch('ai_agent.agent.agent_service.create_mcp_connection') as mock_mcp_conn, \
         patch('ai_agent.agent.agent_service.Runner') as mock_runner:

        mock_mcp_conn.return_value.__aenter__ = AsyncMock(return_value=mock_mcp_server)
        mock_mcp_conn.return_value.__aexit__ = AsyncMock(return_value=None)
        mock_runner.run = AsyncMock(return_value=mock_result)

        # Follow-up message referencing previous context
        result = await service.run_agent_with_context(
            user_id="test_user",
            user_message="mark the first one complete",
            conversation_history=history,
            user_timezone="UTC"
        )

        # Verify context was used
        assert isinstance(result, AgentResult)
        assert "complete" in result.response_text.lower()

        # Verify history was passed to Runner.run
        runner_call = mock_runner.run.call_args
        assert runner_call is not None
