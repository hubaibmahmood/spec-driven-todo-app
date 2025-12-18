"""Pydantic schemas for task tool parameters and responses."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class PriorityLevel(str, Enum):
    """Task priority levels."""

    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    URGENT = "Urgent"


class TaskResponse(BaseModel):
    """Task data returned to AI assistant."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Unique task identifier")
    title: str = Field(..., description="Task title", max_length=200)
    description: Optional[str] = Field(None, description="Detailed task description")
    completed: bool = Field(..., description="Whether task is completed")
    priority: PriorityLevel = Field(..., description="Task priority level")
    due_date: Optional[datetime] = Field(
        None, description="Task due date (ISO 8601 format)"
    )
    created_at: datetime = Field(..., description="Timestamp when task was created")
    updated_at: datetime = Field(
        ..., description="Timestamp when task was last updated"
    )
    user_id: str = Field(..., description="User who owns this task")


class CreateTaskParams(BaseModel):
    """Parameters for create_task tool."""

    title: str = Field(
        ...,
        description="Task title (required)",
        min_length=1,
        max_length=200,
        examples=["Buy milk", "Finish project report"],
    )
    description: Optional[str] = Field(
        None,
        description="Detailed task description (optional)",
        examples=["Pick up 2% milk from grocery store"],
    )
    priority: PriorityLevel = Field(
        PriorityLevel.MEDIUM, description="Task priority level (default: Medium)"
    )
    due_date: Optional[datetime] = Field(
        None,
        description="Task due date in ISO 8601 format (optional)",
        examples=["2025-12-20T10:00:00Z"],
    )


class UpdateTaskParams(BaseModel):
    """Parameters for update_task tool.

    Note: Completion status is handled by mark_task_completed tool.
    This tool is for updating title, description, priority, and due_date.
    """

    task_id: int = Field(..., description="ID of task to update", gt=0)
    title: Optional[str] = Field(
        None, description="New task title (optional)", min_length=1, max_length=200
    )
    description: Optional[str] = Field(
        None, description="New task description (optional, null to clear)"
    )
    priority: Optional[PriorityLevel] = Field(
        None, description="New priority level (optional)"
    )
    due_date: Optional[datetime] = Field(
        None,
        description="New due date in ISO 8601 format (optional, null to clear)",
    )


class DeleteTaskParams(BaseModel):
    """Parameters for delete_task tool."""

    task_id: int = Field(..., description="ID of task to delete", gt=0)


class MarkTaskCompletedParams(BaseModel):
    """Parameters for mark_task_completed tool.

    This is a focused tool for marking tasks complete.
    For other task updates, use UpdateTaskParams.
    """

    task_id: int = Field(..., description="ID of task to mark as completed", gt=0)


class ValidationErrorDetail(BaseModel):
    """Detailed validation error for a specific field."""

    field: str = Field(..., description="Name of the invalid field")
    message: str = Field(..., description="Error message for this field")
    received_value: Optional[str] = Field(None, description="Value that was rejected")
    suggestion: Optional[str] = Field(None, description="Suggested correction")


class ErrorResponse(BaseModel):
    """Structured error response for AI consumption."""

    error_type: str = Field(..., description="Error type identifier")
    message: str = Field(..., description="Human-readable error message for AI")
    details: Optional[dict] = Field(None, description="Additional error context")
    suggestions: Optional[list[str]] = Field(
        None, description="Suggested next actions"
    )


# Error type taxonomy
ERROR_TYPES = {
    "authentication_error": "Service authentication failed",
    "authorization_error": "User not authorized to access this resource",
    "not_found_error": "Requested resource not found",
    "validation_error": "Input validation failed",
    "backend_error": "Backend service error",
    "timeout_error": "Request timed out",
    "connection_error": "Unable to connect to backend service",
}
