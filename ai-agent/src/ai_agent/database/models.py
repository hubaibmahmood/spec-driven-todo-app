"""Database models for AI Agent service."""

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import JSON
from sqlmodel import Column, Field, SQLModel


class UserSession(SQLModel, table=True):
    """
    Read-only model for user_sessions table managed by better-auth.

    Maps camelCase database columns to snake_case Python attributes.
    Used only for authentication validation.
    """

    __tablename__ = "user_sessions"  # type: ignore

    id: str = Field(primary_key=True)
    user_id: str = Field(sa_column_kwargs={"name": "userId"})
    token: str
    expires_at: datetime = Field(sa_column_kwargs={"name": "expiresAt"})
    ip_address: Optional[str] = Field(default=None, sa_column_kwargs={"name": "ipAddress"})
    user_agent: Optional[str] = Field(default=None, sa_column_kwargs={"name": "userAgent"})


class Conversation(SQLModel, table=True):
    """
    Conversation model for storing chat sessions.

    Each conversation belongs to a user and contains multiple messages.
    """

    __tablename__ = "conversations"  # type: ignore

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    title: str = Field(max_length=200)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Message(SQLModel, table=True):
    """
    Message model for storing individual chat messages.

    Each message belongs to a conversation and has a role (user, assistant, tool).
    The message_metadata field stores OpenAI-compatible data like tool_calls.
    """

    __tablename__ = "messages"  # type: ignore

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id", index=True)
    role: str = Field(max_length=20)  # 'user', 'assistant', or 'tool'
    content: str
    message_metadata: Optional[dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
