"""Chat endpoints for AI Agent service."""

import logging
import os
from datetime import datetime

from fastapi import APIRouter, HTTPException, Header, status
from pydantic import BaseModel
from sqlmodel import select

from ai_agent.api.deps import CurrentUser, DbSession
from ai_agent.database.models import Conversation, Message
from ai_agent.agent.agent_service import AgentService
from ai_agent.agent.config import AgentConfig
from ai_agent.agent.context_manager import ContextManager
from ai_agent.agent.timezone_utils import extract_timezone
from ai_agent.services.api_key_retrieval import ApiKeyRetrievalService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])


class ChatRequest(BaseModel):
    """Request schema for chat endpoint."""

    message: str
    conversation_id: int | None = None


class ToolCallOperation(BaseModel):
    """Individual tool call operation metadata."""

    tool_name: str
    status: str  # "success" or "error"
    details: str | None = None


class ChatResponse(BaseModel):
    """Response schema for chat endpoint."""

    conversation_id: int
    user_message: str
    assistant_message: str
    operations: list[ToolCallOperation] = []


@router.post("/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat(
    request: ChatRequest,
    user_id: CurrentUser,
    db: DbSession,
    x_timezone: str | None = Header(None, alias="X-Timezone"),
) -> ChatResponse:
    """
    Send a message and receive a response via OpenAI Agent with Gemini backend.

    Creates a new conversation if conversation_id is not provided,
    or adds to existing conversation if ID is provided.

    Integrates with OpenAI Agents SDK (spec 008) for natural language task management.
    """
    logger.info(f"Chat request from user {user_id[:8]}... conversation_id={request.conversation_id}")

    try:
        # Extract and validate timezone
        user_timezone = extract_timezone(x_timezone)
        logger.debug(f"Using timezone: {user_timezone}")

        # Fetch user-specific API key from backend
        backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
        service_auth_token = os.getenv("SERVICE_AUTH_TOKEN", "")

        try:
            api_key_service = ApiKeyRetrievalService(backend_url=backend_url)
            user_api_key = await api_key_service.get_user_api_key(user_id, service_auth_token)
        except ValueError as e:
            # Service authentication failed - this is a configuration error, not user error
            logger.error(f"Service authentication error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal service configuration error. Please contact support."
            )
        except Exception as e:
            logger.error(f"Failed to retrieve API key: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve API key: {str(e)}"
            )

        # Check if user has configured an API key
        if not user_api_key:
            logger.info(f"User {user_id[:8]}... has no API key configured")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please configure your Gemini API key in Settings to use AI features. "
                       "Visit the Settings page to add your API key."
            )

        # Initialize agent configuration with user-specific API key
        # Override the default AGENT_GEMINI_API_KEY with user's key
        config = AgentConfig(gemini_api_key=user_api_key)
        agent_service = AgentService(config)
        context_manager = ContextManager()

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

        # Load conversation history (now with aggressive task-reference removal)
        history = await context_manager.load_conversation_history(
            session=db,
            conversation_id=conversation.id,  # type: ignore
            user_id=user_id
        )

        # Truncate history to fit token budget
        truncated_history = context_manager.truncate_by_tokens(
            messages=history,
            max_tokens=config.token_budget
        )

        logger.info(f"Loaded {len(history)} messages, truncated to {len(truncated_history)}")

        # Execute agent with context
        agent_result = await agent_service.run_agent_with_context(
            user_id=user_id,
            user_message=request.message,
            conversation_history=truncated_history,
            user_timezone=user_timezone
        )

        # Save user message
        user_message = Message(
            conversation_id=conversation.id,  # type: ignore
            role="user",
            content=request.message,
            created_at=datetime.utcnow(),
        )
        db.add(user_message)

        # Save assistant message
        assistant_message = Message(
            conversation_id=conversation.id,  # type: ignore
            role="assistant",
            content=agent_result.response_text,
            created_at=datetime.utcnow(),
        )
        db.add(assistant_message)

        await db.commit()

        logger.info(f"Agent response: {agent_result.execution_time_ms}ms, {agent_result.tokens_used} tokens")

        # Parse tool calls into operations
        operations = []
        for tool_call in agent_result.tool_calls_made:
            function = tool_call.get("function", {})
            tool_name = function.get("name", "unknown")
            # All tool calls are assumed successful if they completed
            operations.append(
                ToolCallOperation(
                    tool_name=tool_name,
                    status="success",
                    details=None
                )
            )

        return ChatResponse(
            conversation_id=conversation.id,  # type: ignore
            user_message=request.message,
            assistant_message=agent_result.response_text,
            operations=operations,
        )

    except HTTPException:
        # Re-raise HTTPException without modification (preserves status code and detail)
        raise
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}", exc_info=True)
        # Graceful degradation for unexpected errors
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service temporarily unavailable. Please try again.",
        )
