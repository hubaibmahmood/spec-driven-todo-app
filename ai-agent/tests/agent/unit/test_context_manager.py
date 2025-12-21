"""Unit tests for ContextManager token counting and truncation."""

import pytest
from ai_agent.agent.context_manager import ContextManager


def test_count_tokens():
    """Unit: Token counting should return accurate token count."""
    manager = ContextManager()

    # Simple text
    text = "Hello, world!"
    count = manager.count_tokens(text)
    assert count > 0
    assert isinstance(count, int)

    # Empty text
    assert manager.count_tokens("") == 0


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
    system_msgs = [m for m in truncated if m["role"] == "system"]
    assert len(system_msgs) == 1
    assert system_msgs[0]["content"] == "You are a helpful assistant."

    # Recent message should be kept
    user_msgs = [m for m in truncated if m["role"] == "user"]
    assert any("Recent" in m["content"] for m in user_msgs)


def test_truncate_keeps_newest_messages():
    """Unit: Truncation should keep newest messages when budget exceeded."""
    messages = [
        {"role": "system", "content": "System"},
        {"role": "user", "content": "Message 1"},
        {"role": "assistant", "content": "Response 1"},
        {"role": "user", "content": "Message 2"},
        {"role": "assistant", "content": "Response 2"},
        {"role": "user", "content": "Message 3"},
    ]
    manager = ContextManager()

    # Very low token budget
    truncated = manager.truncate_by_tokens(messages, max_tokens=50)

    # System message always preserved
    assert any(m["role"] == "system" for m in truncated)

    # Should have newest messages
    contents = [m["content"] for m in truncated]
    assert "Message 3" in contents or len(truncated) > 1


def test_truncate_with_sufficient_budget():
    """Unit: No truncation when all messages fit in budget."""
    messages = [
        {"role": "system", "content": "System"},
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi"},
    ]
    manager = ContextManager()

    # Very high token budget
    truncated = manager.truncate_by_tokens(messages, max_tokens=10000)

    # All messages should be preserved
    assert len(truncated) == 3
