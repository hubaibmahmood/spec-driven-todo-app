"""Integration tests for conversation history loading."""

import pytest
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from ai_agent.agent.context_manager import ContextManager
from ai_agent.database.models import Conversation, Message


@pytest.mark.asyncio
async def test_load_conversation_history(db_session: AsyncSession):
    """Integration: ContextManager should load conversation history from database."""
    # Arrange: Create test conversation and messages
    user_id = "test_user_123"
    conversation = Conversation(
        user_id=user_id,
        title="Test Conversation",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db_session.add(conversation)
    await db_session.commit()
    await db_session.refresh(conversation)

    # Add messages in chronological order
    messages = [
        Message(
            conversation_id=conversation.id,
            role="user",
            content="Hello, how are you?",
            created_at=datetime.now()
        ),
        Message(
            conversation_id=conversation.id,
            role="assistant",
            content="I'm doing well, thank you!",
            created_at=datetime.now()
        ),
        Message(
            conversation_id=conversation.id,
            role="user",
            content="Can you help me with a task?",
            created_at=datetime.now()
        ),
    ]
    for msg in messages:
        db_session.add(msg)
    await db_session.commit()

    # Act: Load conversation history
    manager = ContextManager()
    loaded_messages = await manager.load_conversation_history(
        conversation_id=conversation.id,
        user_id=user_id,
        session=db_session
    )

    # Assert: Messages loaded in correct order
    assert len(loaded_messages) == 3
    assert loaded_messages[0]["role"] == "user"
    assert loaded_messages[0]["content"] == "Hello, how are you?"
    assert loaded_messages[1]["role"] == "assistant"
    assert loaded_messages[1]["content"] == "I'm doing well, thank you!"
    assert loaded_messages[2]["role"] == "user"
    assert loaded_messages[2]["content"] == "Can you help me with a task?"


@pytest.mark.asyncio
async def test_load_conversation_with_ownership_validation(db_session: AsyncSession):
    """Integration: Loading conversation should validate user ownership."""
    # Arrange: Create conversation for user A
    user_a = "user_a_123"
    user_b = "user_b_456"

    conversation = Conversation(
        user_id=user_a,
        title="User A's Conversation",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db_session.add(conversation)
    await db_session.commit()
    await db_session.refresh(conversation)

    # Add a message
    message = Message(
        conversation_id=conversation.id,
        role="user",
        content="Private message",
        created_at=datetime.now()
    )
    db_session.add(message)
    await db_session.commit()

    # Act & Assert: User B should not be able to access User A's conversation
    manager = ContextManager()

    with pytest.raises(PermissionError, match="not authorized"):
        await manager.load_conversation_history(
            conversation_id=conversation.id,
            user_id=user_b,
            session=db_session
        )


@pytest.mark.asyncio
async def test_load_nonexistent_conversation(db_session: AsyncSession):
    """Integration: Loading nonexistent conversation should raise NotFoundError."""
    manager = ContextManager()

    with pytest.raises(ValueError, match="Conversation.*not found"):
        await manager.load_conversation_history(
            conversation_id=99999,
            user_id="test_user",
            session=db_session
        )


@pytest.mark.asyncio
async def test_load_empty_conversation(db_session: AsyncSession):
    """Integration: Loading conversation with no messages should return empty list."""
    # Arrange: Create conversation with no messages
    user_id = "test_user_123"
    conversation = Conversation(
        user_id=user_id,
        title="Empty Conversation",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db_session.add(conversation)
    await db_session.commit()
    await db_session.refresh(conversation)

    # Act: Load conversation history
    manager = ContextManager()
    loaded_messages = await manager.load_conversation_history(
        conversation_id=conversation.id,
        user_id=user_id,
        session=db_session
    )

    # Assert: Empty list returned
    assert loaded_messages == []
