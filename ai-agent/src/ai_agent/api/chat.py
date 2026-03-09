"""Chat endpoints for AI Agent service."""

import json
import logging
import os
from datetime import datetime, UTC
from typing import AsyncGenerator

from fastapi import APIRouter, HTTPException, Header, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from openai.types.responses import ResponseTextDeltaEvent
from agents import Runner

from ai_agent.api.deps import CurrentUser, DbSession
from ai_agent.database.models import Conversation, Message
from ai_agent.agent.agent_service import AgentService
from ai_agent.agent.config import AgentConfig
from ai_agent.agent.context_manager import ContextManager
from ai_agent.agent.mcp_connection import create_mcp_connection
from ai_agent.agent.message_converter import MessageConverter
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
            conversation.updated_at = datetime.now(UTC)

        else:
            # Create new conversation
            timestamp = datetime.now(UTC)
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
        now = datetime.now(UTC)
        user_message = Message(
            conversation_id=conversation.id,  # type: ignore
            role="user",
            content=request.message,
            created_at=now,
        )
        db.add(user_message)

        # Save assistant message
        assistant_message = Message(
            conversation_id=conversation.id,  # type: ignore
            role="assistant",
            content=agent_result.response_text,
            created_at=now,
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


async def _stream_agent_response(
    agent_service: AgentService,
    user_id: str,
    db: AsyncSession,
    conversation_id: int,
    config: AgentConfig,
    formatted_messages: list,
    user_message_text: str,
    user_timezone: str,
) -> AsyncGenerator[str, None]:
    """SSE generator that streams agent response token-by-token."""
    try:
        async with create_mcp_connection(config, user_id) as mcp_server:
            agent = await agent_service.initialize_agent(mcp_server)
            agent_service._enhance_agent_instructions(agent, user_timezone)

            messages = formatted_messages + [{"role": "user", "content": user_message_text}]
            run_config = agent_service.create_run_config()

            result = Runner.run_streamed(agent, input=messages, run_config=run_config)
            async for event in result.stream_events():
                if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                    chunk = event.data.delta
                    if chunk:
                        yield f"data: {json.dumps({'type': 'text_delta', 'content': chunk})}\n\n"

            # Stream complete — save messages and emit done
            tool_calls = agent_service._extract_tool_calls(result.new_items)
            now = datetime.now(UTC)
            db.add(Message(
                conversation_id=conversation_id,
                role="user",
                content=user_message_text,
                created_at=now,
            ))
            db.add(Message(
                conversation_id=conversation_id,
                role="assistant",
                content=result.final_output or "",
                created_at=now,
            ))
            await db.commit()

            operations = [
                {"tool_name": tc.get("function", {}).get("name", "unknown"), "status": "success", "details": None}
                for tc in tool_calls
            ]
            yield f"data: {json.dumps({'type': 'done', 'conversation_id': conversation_id, 'operations': operations})}\n\n"

    except Exception as e:
        logger.error(f"Streaming agent error for user {user_id}: {e}", exc_info=True)
        yield f"data: {json.dumps({'type': 'error', 'detail': str(e)})}\n\n"


@router.post("/chat/stream", status_code=status.HTTP_200_OK)
async def chat_stream(
    request: ChatRequest,
    user_id: CurrentUser,
    db: DbSession,
    x_timezone: str | None = Header(None, alias="X-Timezone"),
) -> StreamingResponse:
    """
    Stream a chat response as Server-Sent Events.

    Emits:
      data: {"type": "text_delta", "content": "..."}  — one per token
      data: {"type": "done", "conversation_id": N, "operations": [...]}  — end of stream
      data: {"type": "error", "detail": "..."}  — on failure
    """
    logger.info(f"Streaming chat request from user {user_id[:8]}... conversation_id={request.conversation_id}")

    try:
        user_timezone = extract_timezone(x_timezone)

        backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
        service_auth_token = os.getenv("SERVICE_AUTH_TOKEN", "")

        try:
            api_key_service = ApiKeyRetrievalService(backend_url=backend_url)
            user_api_key = await api_key_service.get_user_api_key(user_id, service_auth_token)
        except ValueError as e:
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

        if not user_api_key:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please configure your Gemini API key in Settings to use AI features. "
                       "Visit the Settings page to add your API key."
            )

        config = AgentConfig(gemini_api_key=user_api_key)
        agent_service = AgentService(config)
        context_manager = ContextManager()

        # Get or create conversation
        if request.conversation_id:
            statement = select(Conversation).where(
                Conversation.id == request.conversation_id,
                Conversation.user_id == user_id,
            )
            result = await db.execute(statement)
            conv = result.scalar_one_or_none()
            if not conv:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found or you don't have access",
                )
            conversation = conv
            conversation.updated_at = datetime.now(UTC)
        else:
            timestamp = datetime.now(UTC)
            conversation = Conversation(
                user_id=user_id,
                title=f"Chat - {timestamp.strftime('%Y-%m-%d %H:%M')}",
                created_at=timestamp,
                updated_at=timestamp,
            )
            db.add(conversation)
            await db.commit()
            await db.refresh(conversation)

        history = await context_manager.load_conversation_history(
            session=db, conversation_id=conversation.id, user_id=user_id
        )
        truncated = context_manager.truncate_by_tokens(messages=history, max_tokens=config.token_budget)

        if truncated and isinstance(truncated[0], dict):
            formatted_messages = truncated
        else:
            converter = MessageConverter()
            formatted_messages = converter.db_messages_to_agent_batch(truncated)

        return StreamingResponse(
            _stream_agent_response(
                agent_service=agent_service,
                user_id=user_id,
                db=db,
                conversation_id=conversation.id,
                config=config,
                formatted_messages=formatted_messages,
                user_message_text=request.message,
                user_timezone=user_timezone,
            ),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
                "Connection": "keep-alive",
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat stream endpoint error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service temporarily unavailable. Please try again.",
        )
