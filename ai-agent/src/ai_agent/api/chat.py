"""Chat endpoints for AI Agent service."""

import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from sqlmodel import select

from ai_agent.api.deps import CurrentUser, DbSession
from ai_agent.database.models import Conversation, Message

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])


class ChatRequest(BaseModel):
    """Request schema for chat endpoint."""

    message: str
    conversation_id: int | None = None


class ChatResponse(BaseModel):
    """Response schema for chat endpoint."""

    conversation_id: int
    user_message: str
    assistant_message: str


@router.post("/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat(
    request: ChatRequest,
    user_id: CurrentUser,
    db: DbSession,
) -> ChatResponse:
    """
    Send a message and receive a response.

    Creates a new conversation if conversation_id is not provided,
    or adds to existing conversation if ID is provided.

    For spec 007, returns an echo response. In spec 008, this will be replaced
    with OpenAI Agents SDK integration.
    """
    logger.info(f"Chat request from user {user_id[:8]}... conversation_id={request.conversation_id}")
    conversation: Conversation

    # Get or create conversation
    if request.conversation_id:
        # Validate conversation ownership
        statement = select(Conversation).where(
            Conversation.id == request.conversation_id,
            Conversation.user_id == user_id,
        )
        result = await db.execute(statement)
        conv = result.scalar_one_or_none()

        if not conv:
            logger.error(f"Conversation {request.conversation_id} not found for user {user_id[:8]}...")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found or you don't have access",
            )

        conversation = conv
        # Update conversation timestamp
        conversation.updated_at = datetime.utcnow()

    else:
        # Create new conversation
        timestamp = datetime.utcnow()
        title = f"Chat - {timestamp.strftime('%Y-%m-%d %H:%M')}"
        conversation = Conversation(
            user_id=user_id,
            title=title,
            created_at=timestamp,
            updated_at=timestamp,
        )
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)

    # Save user message
    user_message = Message(
        conversation_id=conversation.id,  # type: ignore
        role="user",
        content=request.message,
        created_at=datetime.utcnow(),
    )
    db.add(user_message)

    # Generate assistant response (echo for now)
    assistant_response = f"Echo: {request.message}"

    # Save assistant message
    assistant_message = Message(
        conversation_id=conversation.id,  # type: ignore
        role="assistant",
        content=assistant_response,
        created_at=datetime.utcnow(),
    )
    db.add(assistant_message)

    await db.commit()

    return ChatResponse(
        conversation_id=conversation.id,  # type: ignore
        user_message=request.message,
        assistant_message=assistant_response,
    )
