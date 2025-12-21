"""Unit tests for MessageConverter."""

import pytest
from ai_agent.agent.message_converter import MessageConverter
from ai_agent.database.models import Message


def test_convert_user_message_to_agent_format():
    """Unit: Convert database user message to AgentMessage."""
    db_msg = Message(
        id=1,
        conversation_id=42,
        role="user",
        content="Show my tasks",
        message_metadata=None
    )
    converter = MessageConverter()

    result = converter.db_to_agent(db_msg)

    assert result["role"] == "user"
    assert result["content"] == "Show my tasks"
    assert "tool_calls" not in result or result.get("tool_calls") is None


def test_convert_assistant_message_to_agent_format():
    """Unit: Convert database assistant message to AgentMessage."""
    db_msg = Message(
        id=2,
        conversation_id=42,
        role="assistant",
        content="Here are your tasks.",
        message_metadata=None
    )
    converter = MessageConverter()

    result = converter.db_to_agent(db_msg)

    assert result["role"] == "assistant"
    assert result["content"] == "Here are your tasks."
    assert "tool_calls" not in result or result.get("tool_calls") is None


def test_convert_assistant_message_with_tool_calls():
    """Unit: Convert assistant message preserving tool calls from message_metadata."""
    db_msg = Message(
        id=3,
        conversation_id=42,
        role="assistant",
        content="I'll list your tasks.",
        message_metadata={
            "tool_calls": [
                {
                    "id": "call_123",
                    "type": "function",
                    "function": {"name": "list_tasks", "arguments": "{}"}
                }
            ]
        }
    )
    converter = MessageConverter()

    result = converter.db_to_agent(db_msg)

    assert result["role"] == "assistant"
    assert result["content"] == "I'll list your tasks."
    assert "tool_calls" in result
    assert result["tool_calls"] == db_msg.message_metadata["tool_calls"]
    assert result["tool_calls"][0]["id"] == "call_123"
    assert result["tool_calls"][0]["function"]["name"] == "list_tasks"


def test_convert_batch_messages():
    """Unit: Convert list of database messages to agent format."""
    messages = [
        Message(
            id=1,
            conversation_id=42,
            role="user",
            content="Hello",
            message_metadata=None
        ),
        Message(
            id=2,
            conversation_id=42,
            role="assistant",
            content="Hi there!",
            message_metadata=None
        ),
        Message(
            id=3,
            conversation_id=42,
            role="user",
            content="Show tasks",
            message_metadata=None
        ),
    ]
    converter = MessageConverter()

    result = converter.db_messages_to_agent_batch(messages)

    assert len(result) == 3
    assert result[0]["role"] == "user"
    assert result[0]["content"] == "Hello"
    assert result[1]["role"] == "assistant"
    assert result[1]["content"] == "Hi there!"
    assert result[2]["role"] == "user"
    assert result[2]["content"] == "Show tasks"
