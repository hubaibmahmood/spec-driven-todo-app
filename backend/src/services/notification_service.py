"""Notification service with APScheduler for scheduled task reminders."""

from __future__ import annotations

import httpx
from datetime import datetime, UTC, timedelta
from typing import Any

from sqlalchemy import select, update, and_
from sqlalchemy.ext.asyncio import AsyncSession

from apscheduler.schedulers.asyncio import AsyncIOScheduler  # type: ignore[import-untyped]
from apscheduler.triggers.interval import IntervalTrigger  # type: ignore[import-untyped]

from src.config import settings
from src.models.database import Task
from src.models.notification import Notification


class NotificationService:
    """Manages in-app notifications and email reminders via APScheduler."""

    def __init__(self, session_factory: Any) -> None:
        self._session_factory = session_factory
        self._scheduler = AsyncIOScheduler()

    def start(self) -> None:
        """Start the background scheduler."""
        self._scheduler.add_job(
            self._run_notification_check,
            IntervalTrigger(minutes=15),
            id="notification_check",
            replace_existing=True,
            next_run_time=datetime.now(UTC),  # Run once immediately on startup
        )
        self._scheduler.start()
        print("[notifications] Scheduler started (runs every 15 minutes)")

    def stop(self) -> None:
        """Shut down the scheduler gracefully."""
        if self._scheduler.running:
            self._scheduler.shutdown(wait=False)
            print("[notifications] Scheduler stopped")

    async def _run_notification_check(self) -> None:
        """Entry point for the scheduled job."""
        try:
            async with self._session_factory() as session:
                async with session.begin():
                    await self._check_due_soon(session)
                    await self._check_overdue(session)
        except Exception as exc:
            print(f"[notifications] Scheduler job error: {exc}")

    # ------------------------------------------------------------------
    # Due-soon notifications
    # ------------------------------------------------------------------

    async def _check_due_soon(self, session: AsyncSession) -> None:
        """Create notifications + send emails for tasks due within 24 hours."""
        now = datetime.now(UTC)
        in_24h = now + timedelta(hours=24)

        stmt = select(Task).where(
            and_(
                Task.due_date.isnot(None),
                Task.due_date.between(now, in_24h),
                Task.completed == False,  # noqa: E712
                Task.reminder_sent == False,  # noqa: E712
            )
        )
        result = await session.execute(stmt)
        tasks = result.scalars().all()

        for task in tasks:
            notification = Notification(
                user_id=task.user_id,
                task_id=task.id,
                type="due_soon",
                message=f'"{task.title}" is due soon',
                sent_email=False,
            )
            session.add(notification)

            await session.execute(
                update(Task).where(Task.id == task.id).values(reminder_sent=True)
            )

            await self._send_due_soon_email(session, task)

        if tasks:
            print(f"[notifications] Created {len(tasks)} due_soon notification(s)")

    # ------------------------------------------------------------------
    # Overdue notifications (max once per task per day)
    # ------------------------------------------------------------------

    async def _check_overdue(self, session: AsyncSession) -> None:
        """Create overdue notifications — at most once per task per day."""
        now = datetime.now(UTC)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        overdue_stmt = select(Task).where(
            and_(
                Task.due_date.isnot(None),
                Task.due_date < now,
                Task.completed == False,  # noqa: E712
            )
        )
        result = await session.execute(overdue_stmt)
        tasks = result.scalars().all()

        created = 0
        for task in tasks:
            existing = await session.execute(
                select(Notification).where(
                    and_(
                        Notification.task_id == task.id,
                        Notification.type == "overdue",
                        Notification.created_at >= today_start,
                    )
                )
            )
            if existing.scalar_one_or_none():
                continue

            session.add(
                Notification(
                    user_id=task.user_id,
                    task_id=task.id,
                    type="overdue",
                    message=f'"{task.title}" is overdue',
                    sent_email=False,
                )
            )
            created += 1

        if created:
            print(f"[notifications] Created {created} overdue notification(s)")

    # ------------------------------------------------------------------
    # Email delivery via Resend
    # ------------------------------------------------------------------

    async def _send_due_soon_email(self, session: AsyncSession, task: Task) -> None:
        """Send a reminder email via Resend (best-effort; never raises)."""
        if not settings.RESEND_API_KEY:
            return

        try:
            from sqlalchemy import text

            row = (
                await session.execute(
                    text("SELECT email, name FROM users WHERE id = :uid"),
                    {"uid": task.user_id},
                )
            ).fetchone()

            if not row or not row.email:  # type: ignore[union-attr]
                return

            due_str = (
                task.due_date.strftime("%B %d, %Y at %I:%M %p UTC")
                if task.due_date
                else "soon"
            )
            priority_label = task.priority.value if task.priority else "Medium"

            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    "https://api.resend.com/emails",
                    headers={
                        "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "from": "Momentum <notifications@momentum.intevia.cc>",
                        "to": [row.email],  # type: ignore[union-attr]
                        "subject": f'Reminder: "{task.title}" is due soon',
                        "text": (
                            f"Hi {row.name or 'there'},\n\n"  # type: ignore[union-attr]
                            f'Your task "{task.title}" is due on {due_str}.\n'
                            f"Priority: {priority_label}\n\n"
                            "Log in to Momentum to manage your tasks.\n\n"
                            "— The Momentum Team"
                        ),
                    },
                )
                if resp.status_code == 200:
                    print(f"[notifications] Email sent for task {task.id}")
        except Exception as exc:
            print(f"[notifications] Email error for task {task.id}: {exc}")


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_service: NotificationService | None = None


def get_notification_service(session_factory: Any) -> NotificationService:
    """Return the singleton NotificationService, creating it if needed."""
    global _service
    if _service is None:
        _service = NotificationService(session_factory)
    return _service
