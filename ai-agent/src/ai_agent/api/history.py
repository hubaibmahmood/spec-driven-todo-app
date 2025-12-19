"""Conversation history endpoints for AI Agent service."""

from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from sqlmodel import select

from ai_agent.api.deps import CurrentUser, DbSession
from ai_agent.database.models import Conversation, Message

router = APIRouter(tags=["history"])


class ConversationListResponse(BaseModel):
    """Response schema for conversation list item."""

    id: int
    title: str
    created_at: datetime
    updated_at: datetime


class MessageResponse(BaseModel):
    """Response schema for message."""

    id: int
    role: str
    content: str
    message_metadata: dict[str, Any] | None
    created_at: datetime


class ConversationDetailResponse(BaseModel):
    """Response schema for conversation detail with messages."""

    id: int
    title: str
    created_at: datetime
    updated_at: datetime
    messages: list[MessageResponse]


@router.get("/conversations", response_model=list[ConversationListResponse])
async def list_conversations(
    user_id: CurrentUser,
    db: DbSession,
) -> list[ConversationListResponse]:
    """
    List all conversations for the authenticated user.

    Conversations are ordered by most recently updated first.
    """
    statement = (
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
    )

    result = await db.execute(statement)
    conversations = result.scalars().all()

    return [
        ConversationListResponse(
            id=conv.id,  # type: ignore
            title=conv.title,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
        )
        for conv in conversations
    ]


@router.get("/conversations/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation(
    conversation_id: int,
    user_id: CurrentUser,
    db: DbSession,
) -> ConversationDetailResponse:
    """
    Get conversation details including all messages.

    Returns 404 if conversation doesn't exist or user doesn't have access.
    Messages are ordered chronologically (oldest first).
    """
    # Validate conversation ownership
    conv_statement = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == user_id,
    )
    conv_result = await db.execute(conv_statement)
    conversation = conv_result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found or you don't have access",
        )

    # Get messages for this conversation
    msg_statement = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
    )
    msg_result = await db.execute(msg_statement)
    messages = msg_result.scalars().all()

    return ConversationDetailResponse(
        id=conversation.id,  # type: ignore
        title=conversation.title,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        messages=[
            MessageResponse(
                id=msg.id,  # type: ignore
                role=msg.role,
                content=msg.content,
                message_metadata=msg.message_metadata,
                created_at=msg.created_at,
            )
            for msg in messages
        ],
    )
