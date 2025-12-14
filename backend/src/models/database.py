"""SQLAlchemy database models."""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base
import enum

Base = declarative_base()


class PriorityLevel(str, enum.Enum):
    """Priority levels for tasks."""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    URGENT = "Urgent"


class Task(Base):
    """Task model for storing todo items."""

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String(255), nullable=False, index=True)  # Changed from UUID to String to match better-auth
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    completed = Column(Boolean, default=False, nullable=False)
    priority = Column(Enum(PriorityLevel, values_callable=lambda x: [e.value for e in x]), default=PriorityLevel.MEDIUM, nullable=False)
    due_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<Task(id={self.id}, title='{self.title}', completed={self.completed})>"


class UserSession(Base):
    """UserSession reference model (read-only, no migrations).

    This table is managed by the better-auth Node.js server.
    FastAPI only reads from this table for session validation.

    Note: better-auth uses camelCase column names, so we map them explicitly.
    Actual schema: id, userId, token, expiresAt, ipAddress, userAgent, createdAt, updatedAt
    """

    __tablename__ = "user_sessions"

    # Map snake_case Python attributes to camelCase database columns
    id = Column(String(255), primary_key=True)
    user_id = Column("userId", String(255), nullable=False, index=True)
    token = Column(String(255), nullable=False, unique=True, index=True)
    expires_at = Column("expiresAt", DateTime(timezone=False), nullable=False, index=True)  # timezone=False to match DB
    ip_address = Column("ipAddress", Text, nullable=True)
    user_agent = Column("userAgent", Text, nullable=True)
    created_at = Column("createdAt", DateTime(timezone=False), nullable=True)
    updated_at = Column("updatedAt", DateTime(timezone=False), nullable=True)

    def __repr__(self) -> str:
        return f"<UserSession(id={self.id}, user_id={self.user_id})>"
