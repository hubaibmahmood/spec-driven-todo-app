"""Integration tests for agent execution."""

import pytest
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from ai_agent.agent.config import AgentConfig
from ai_agent.agent.agent_service import AgentService


@pytest.mark.asyncio
async def test_run_agent_with_user_message():
    """Integration: run_agent processes user message and returns response."""
    config = AgentConfig(gemini_api_key="test_key_12345")
    service = AgentService(config)

    # Mock agent and Runner.run() result
    mock_agent = Mock()
    mock_agent.name = "Todo Assistant"
    mock_agent.instructions = config.system_prompt
    mock_agent.mcp_servers = [Mock()]

    # Mock Runner.run result
    mock_result = Mock()
    mock_result.final_output = "You have 3 tasks."
    mock_result.messages = [
        {"role": "user", "content": "show my tasks"},
        {"role": "assistant", "content": "You have 3 tasks."}
    ]

    with patch('ai_agent.agent.agent_service.Runner') as mock_runner:
        mock_runner.run = AsyncMock(return_value=mock_result)

        # Run agent with simple message
        result = await service.run_agent(
            agent=mock_agent,
            user_message="show my tasks",
            conversation_history=[]
        )

        # Verify result structure
        assert result is not None
        assert "response_text" in result or hasattr(result, 'response_text')
        assert "execution_time_ms" in result or hasattr(result, 'execution_time_ms')


@pytest.mark.asyncio
async def test_run_agent_tracks_execution_time():
    """Integration: run_agent tracks execution time in milliseconds."""
    config = AgentConfig(gemini_api_key="test_key_12345")
    service = AgentService(config)

    mock_agent = Mock()
    mock_result = Mock()
    mock_result.final_output = "Done."
    mock_result.messages = []

    with patch('ai_agent.agent.agent_service.Runner') as mock_runner:
        mock_runner.run = AsyncMock(return_value=mock_result)

        result = await service.run_agent(
            agent=mock_agent,
            user_message="test",
            conversation_history=[]
        )

        # Execution time should be tracked
        execution_time = result.get("execution_time_ms") if isinstance(result, dict) else getattr(result, 'execution_time_ms', None)
        assert execution_time is not None
        assert execution_time >= 0  # Should be non-negative milliseconds


@pytest.mark.asyncio
async def test_run_agent_with_conversation_history():
    """Integration: run_agent includes conversation history in Runner.run()."""
    config = AgentConfig(gemini_api_key="test_key_12345")
    service = AgentService(config)

    mock_agent = Mock()
    mock_result = Mock()
    mock_result.final_output = "Task completed."
    mock_result.messages = []

    conversation_history = [
        {"role": "user", "content": "show my tasks"},
        {"role": "assistant", "content": "You have 3 tasks."}
    ]

    with patch('ai_agent.agent.agent_service.Runner') as mock_runner:
        mock_runner.run = AsyncMock(return_value=mock_result)

        await service.run_agent(
            agent=mock_agent,
            user_message="mark first one complete",
            conversation_history=conversation_history
        )

        # Verify Runner.run was called with history
        mock_runner.run.assert_called_once()
        call_args = mock_runner.run.call_args

        # Check that messages parameter includes history
        assert 'messages' in call_args.kwargs or len(call_args.args) > 2


@pytest.mark.asyncio
async def test_run_agent_extracts_tool_calls():
    """Integration: run_agent extracts tool calls from result."""
    config = AgentConfig(gemini_api_key="test_key_12345")
    service = AgentService(config)

    mock_agent = Mock()

    # Mock result with tool calls
    mock_result = Mock()
    mock_result.final_output = "I've listed your tasks."
    mock_result.messages = [
        {
            "role": "assistant",
            "content": None,
            "tool_calls": [
                {
                    "id": "call_123",
                    "type": "function",
                    "function": {
                        "name": "list_tasks",
                        "arguments": '{"user_id": "user123"}'
                    }
                }
            ]
        }
    ]

    with patch('ai_agent.agent.agent_service.Runner') as mock_runner:
        mock_runner.run = AsyncMock(return_value=mock_result)

        result = await service.run_agent(
            agent=mock_agent,
            user_message="show my tasks",
            conversation_history=[]
        )

        # Verify tool calls are extracted
        tool_calls = result.get("tool_calls_made") if isinstance(result, dict) else getattr(result, 'tool_calls_made', None)
        assert tool_calls is not None
        # Tool calls should be extracted from result.messages


@pytest.mark.asyncio
async def test_run_agent_counts_tokens():
    """Integration: run_agent counts tokens used in conversation."""
    config = AgentConfig(gemini_api_key="test_key_12345")
    service = AgentService(config)

    mock_agent = Mock()
    mock_result = Mock()
    mock_result.final_output = "Response text here."
    mock_result.messages = [
        {"role": "user", "content": "show my tasks"},
        {"role": "assistant", "content": "Response text here."}
    ]

    with patch('ai_agent.agent.agent_service.Runner') as mock_runner:
        mock_runner.run = AsyncMock(return_value=mock_result)

        result = await service.run_agent(
            agent=mock_agent,
            user_message="show my tasks",
            conversation_history=[]
        )

        # Verify tokens are counted
        tokens_used = result.get("tokens_used") if isinstance(result, dict) else getattr(result, 'tokens_used', None)
        assert tokens_used is not None
        assert tokens_used >= 0  # Should have token count


@pytest.mark.asyncio
async def test_run_agent_with_context_orchestration():
    """Integration: run_agent_with_context orchestrates MCP connection, agent init, and execution."""
    from ai_agent.agent.agent_service import AgentService
    from ai_agent.database.models import Message

    config = AgentConfig(gemini_api_key="test_key_12345")
    service = AgentService(config)

    # Mock database messages
    db_messages = [
        Message(id=1, conversation_id=1, role="user", content="show tasks", message_metadata=None),
        Message(id=2, conversation_id=1, role="assistant", content="You have 3 tasks", message_metadata=None)
    ]

    # Mock result
    mock_result = Mock()
    mock_result.final_output = "Task completed."
    mock_result.messages = [{"role": "assistant", "content": "Task completed."}]

    with patch('ai_agent.agent.agent_service.create_mcp_connection') as mock_mcp, \
         patch('ai_agent.agent.agent_service.Runner') as mock_runner:

        # Mock MCP connection
        mock_server = Mock()
        mock_mcp.return_value.__aenter__ = AsyncMock(return_value=mock_server)
        mock_mcp.return_value.__aexit__ = AsyncMock(return_value=None)

        mock_runner.run = AsyncMock(return_value=mock_result)

        # Run with context
        result = await service.run_agent_with_context(
            user_id="user123",
            user_message="mark first complete",
            conversation_history=db_messages,
            user_timezone="America/New_York"
        )

        # Verify MCP connection created with user_id
        mock_mcp.assert_called_once()
        assert "user123" in str(mock_mcp.call_args)

        # Verify result
        assert result.response_text == "Task completed."
        assert result.execution_time_ms >= 0
