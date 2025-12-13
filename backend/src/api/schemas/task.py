"""Pydantic schemas for Task operations."""

from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional
from src.models.database import PriorityLevel


class TaskCreate(BaseModel):
    """Schema for creating a new task."""

    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, max_length=1000, description="Task description")
    priority: PriorityLevel = Field(PriorityLevel.MEDIUM, description="Task priority level")
    due_date: Optional[datetime] = Field(None, description="Task due date")

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate title is not empty or whitespace only."""
        if not v or not v.strip():
            raise ValueError('Title cannot be empty or whitespace only')
        return v.strip()

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Validate and clean description."""
        if v is None:
            return None
        if len(v.strip()) == 0:
            return None
        if len(v) > 1000:
            raise ValueError('Description cannot exceed 1000 characters')
        return v.strip()

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "priority": "Medium",
                "due_date": "2025-12-15T12:00:00Z"
            }
        }
    }


class CompletionUpdate(BaseModel):
    """Schema for updating task completion status."""

    completed: bool = Field(..., description="Completion status")

    model_config = {
        "json_schema_extra": {
            "example": {
                "completed": True
            }
        }
    }


class TaskUpdate(BaseModel):
    """Schema for updating a task (partial updates supported)."""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    completed: Optional[bool] = None
    priority: Optional[PriorityLevel] = None
    due_date: Optional[datetime] = None

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        """Validate title if provided."""
        if v is not None:
            if not v or not v.strip():
                raise ValueError('Title cannot be empty or whitespace only')
            return v.strip()
        return v

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Validate description if provided."""
        if v is not None:
            if len(v) > 1000:
                raise ValueError('Description cannot exceed 1000 characters')
            return v.strip() if v.strip() else None
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Buy groceries and vegetables",
                "completed": True,
                "priority": "High",
                "due_date": "2025-12-20T12:00:00Z"
            }
        }
    }


class TaskResponse(BaseModel):
    """Schema for task response."""

    id: int
    user_id: str
    title: str
    description: Optional[str]
    completed: bool
    priority: PriorityLevel
    due_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "user_id": "clx123abc456def789ghi012",
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "completed": False,
                "priority": "Medium",
                "due_date": "2025-12-15T12:00:00Z",
                "created_at": "2025-12-10T12:00:00Z",
                "updated_at": "2025-12-10T12:00:00Z"
            }
        }
    }


class BulkDeleteRequest(BaseModel):
    """Schema for bulk delete request."""
    
    task_ids: list[int] = Field(..., min_length=1, description="List of task IDs to delete")
    
    @field_validator('task_ids')
    @classmethod
    def validate_task_ids(cls, v: list[int]) -> list[int]:
        """Validate task IDs list is not empty."""
        if not v:
            raise ValueError('task_ids cannot be empty')
        return v
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "task_ids": [1, 2, 3]
            }
        }
    }


class BulkDeleteResponse(BaseModel):
    """Schema for bulk delete response."""
    
    deleted: list[int] = Field(..., description="IDs of successfully deleted tasks")
    not_found: list[int] = Field(..., description="IDs of tasks that were not found")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "deleted": [1, 3],
                "not_found": [2]
            }
        }
    }
