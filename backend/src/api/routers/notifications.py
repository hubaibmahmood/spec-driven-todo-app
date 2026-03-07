"""Notification endpoints for in-app notification bell."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_current_user_or_service
from src.api.schemas.notification import NotificationListResponse, NotificationResponse
from src.database.connection import get_db
from src.models.notification import Notification

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/", response_model=NotificationListResponse, status_code=status.HTTP_200_OK)
async def get_notifications(
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user_or_service),
) -> NotificationListResponse:
    """Get the 50 most recent notifications for the authenticated user."""
    stmt = (
        select(Notification)
        .where(Notification.user_id == current_user)
        .order_by(Notification.created_at.desc())
        .limit(50)
    )
    result = await db.execute(stmt)
    notifications = list(result.scalars().all())

    unread_count = sum(1 for n in notifications if not n.is_read)

    return NotificationListResponse(
        notifications=[NotificationResponse.model_validate(n) for n in notifications],
        unread_count=unread_count,
    )


@router.patch(
    "/{notification_id}/read",
    response_model=NotificationResponse,
    status_code=status.HTTP_200_OK,
)
async def mark_notification_read(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user_or_service),
) -> NotificationResponse:
    """Mark a single notification as read."""
    stmt = (
        update(Notification)
        .where(
            Notification.id == notification_id,
            Notification.user_id == current_user,
        )
        .values(is_read=True)
        .returning(Notification)
    )
    result = await db.execute(stmt)
    notification = result.scalar_one_or_none()
    await db.flush()

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notification {notification_id} not found",
        )

    return NotificationResponse.model_validate(notification)


@router.post("/read-all", status_code=status.HTTP_204_NO_CONTENT)
async def mark_all_notifications_read(
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user_or_service),
) -> None:
    """Mark all unread notifications as read for the current user."""
    stmt = (
        update(Notification)
        .where(
            Notification.user_id == current_user,
            Notification.is_read == False,  # noqa: E712
        )
        .values(is_read=True)
    )
    await db.execute(stmt)
    await db.flush()
