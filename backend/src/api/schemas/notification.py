"""Pydantic schemas for Notification operations."""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class NotificationResponse(BaseModel):
    """Schema for a single notification."""

    id: int
    user_id: str
    task_id: Optional[int]
    type: str
    message: str
    is_read: bool
    sent_email: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class NotificationListResponse(BaseModel):
    """Schema for notification list with unread count."""

    notifications: list[NotificationResponse]
    unread_count: int
