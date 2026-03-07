"""Task repository for database operations."""

from datetime import date, datetime, time, UTC
from typing import Optional

from sqlalchemy import and_, func, or_, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.database import Task, PriorityLevel

# Sentinel value for "not provided" in updates
_UNSET = object()


class TaskRepository:
    """Repository for Task CRUD operations."""
    
    def __init__(self, session: AsyncSession):
        """
        Initialize repository with database session.
        
        Args:
            session: SQLAlchemy async session
        """
        self.session = session
    
    async def get_all_by_user_filtered(
        self,
        user_id: str,
        search: Optional[str] = None,
        priority: Optional[PriorityLevel] = None,
        completed: Optional[bool] = None,
        due_before: Optional[date] = None,
        due_after: Optional[date] = None,
        page: int = 1,
        limit: int = 1000,
    ) -> tuple[list[Task], int]:
        """
        Get filtered and paginated tasks for a user.

        Args:
            user_id: Task owner ID
            search: ILIKE search across title and description
            priority: Filter by priority level
            completed: Filter by completion status
            due_before: Tasks due on or before this date
            due_after: Tasks due on or after this date
            page: Page number (1-indexed)
            limit: Items per page

        Returns:
            Tuple of (tasks, total_count)
        """
        conditions = [Task.user_id == user_id]

        if search:
            term = f"%{search}%"
            conditions.append(
                or_(Task.title.ilike(term), Task.description.ilike(term))
            )
        if priority is not None:
            conditions.append(Task.priority == priority)
        if completed is not None:
            conditions.append(Task.completed == completed)
        if due_before is not None:
            cutoff = datetime.combine(due_before, time.max).replace(tzinfo=UTC)
            conditions.append(Task.due_date <= cutoff)
        if due_after is not None:
            start = datetime.combine(due_after, time.min).replace(tzinfo=UTC)
            conditions.append(Task.due_date >= start)

        where_clause = and_(*conditions)

        # Count
        count_stmt = select(func.count(Task.id)).where(where_clause)
        total: int = (await self.session.execute(count_stmt)).scalar_one()

        # Data
        offset = (page - 1) * limit
        data_stmt = (
            select(Task)
            .where(where_clause)
            .order_by(Task.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        tasks = list((await self.session.execute(data_stmt)).scalars().all())

        return tasks, total

    async def get_all_by_user(self, user_id: str) -> list[Task]:
        """
        Get all tasks for a specific user.

        Args:
            user_id: ID of the task owner (string format from better-auth)

        Returns:
            List of Task objects
        """
        stmt = (
            select(Task)
            .where(Task.user_id == user_id)
            .order_by(Task.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_all_unprotected(self) -> list[Task]:
        """
        Get all tasks without user ownership check. For testing purposes.

        Returns:
            List of Task objects
        """
        stmt = (
            select(Task)
            .order_by(Task.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_by_id(self, task_id: int, user_id: str) -> Optional[Task]:
        """
        Get a task by ID (with user ownership check).

        Args:
            task_id: Task ID
            user_id: ID of the task owner (string format from better-auth)

        Returns:
            Task object if found and owned by user, None otherwise
        """
        stmt = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def create(
        self,
        user_id: str,
        title: str,
        description: Optional[str] = None,
        priority: PriorityLevel = PriorityLevel.MEDIUM,
        due_date: Optional[datetime] = None
    ) -> Task:
        """
        Create a new task.

        Args:
            user_id: ID of the task owner (string format from better-auth)
            title: Task title
            description: Optional task description
            priority: Task priority level (default: MEDIUM)
            due_date: Optional task due date

        Returns:
            Created Task object
        """
        task = Task(
            user_id=user_id,
            title=title,
            description=description,
            completed=False,
            priority=priority,
            due_date=due_date
        )
        self.session.add(task)
        await self.session.flush()  # Flush to get ID without committing
        await self.session.refresh(task)
        return task
    
    async def update(
        self,
        task_id: int,
        user_id: str,
        title: Optional[str] = _UNSET,
        description: Optional[str] = _UNSET,
        completed: Optional[bool] = _UNSET,
        priority: Optional[PriorityLevel] = _UNSET,
        due_date: Optional[datetime] = _UNSET
    ) -> Optional[Task]:
        """
        Update a task (partial updates supported).

        Args:
            task_id: Task ID
            user_id: ID of the task owner (string format from better-auth)
            title: Optional new title (use None to keep current, explicit None not supported)
            description: Optional new description (use None to clear, _UNSET to keep current)
            completed: Optional new completion status
            priority: Optional new priority level
            due_date: Optional new due date (use None to clear, _UNSET to keep current)

        Returns:
            Updated Task object if found and owned by user, None otherwise
        """
        # Build update dict with only provided values
        update_data = {}
        if title is not _UNSET:
            update_data['title'] = title
        if description is not _UNSET:
            update_data['description'] = description
        if completed is not _UNSET:
            update_data['completed'] = completed
        if priority is not _UNSET:
            update_data['priority'] = priority
        if due_date is not _UNSET:
            update_data['due_date'] = due_date

        if not update_data:
            # No updates provided, just return the task
            return await self.get_by_id(task_id, user_id)

        stmt = (
            update(Task)
            .where(Task.id == task_id, Task.user_id == user_id)
            .values(**update_data)
            .returning(Task)
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.scalar_one_or_none()
    
    async def delete(self, task_id: int, user_id: str) -> bool:
        """
        Delete a task.

        Args:
            task_id: Task ID
            user_id: ID of the task owner (string format from better-auth)

        Returns:
            True if deleted, False if not found or not owned by user
        """
        stmt = delete(Task).where(Task.id == task_id, Task.user_id == user_id)
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount > 0
    
    async def bulk_delete(self, task_ids: list[int], user_id: str) -> tuple[list[int], list[int]]:
        """
        Delete multiple tasks.

        Args:
            task_ids: List of task IDs to delete
            user_id: ID of the task owner (string format from better-auth)

        Returns:
            Tuple of (deleted_ids, not_found_ids)
        """
        deleted = []
        not_found = []
        
        for task_id in task_ids:
            was_deleted = await self.delete(task_id, user_id)
            if was_deleted:
                deleted.append(task_id)
            else:
                not_found.append(task_id)
        
        return deleted, not_found