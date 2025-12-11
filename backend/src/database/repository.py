"""Task repository for database operations."""

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from src.models.database import Task

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
    
    async def create(self, user_id: str, title: str, description: Optional[str] = None) -> Task:
        """
        Create a new task.

        Args:
            user_id: ID of the task owner (string format from better-auth)
            title: Task title
            description: Optional task description

        Returns:
            Created Task object
        """
        task = Task(
            user_id=user_id,
            title=title,
            description=description,
            completed=False
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
        completed: Optional[bool] = _UNSET
    ) -> Optional[Task]:
        """
        Update a task (partial updates supported).

        Args:
            task_id: Task ID
            user_id: ID of the task owner (string format from better-auth)
            title: Optional new title (use None to keep current, explicit None not supported)
            description: Optional new description (use None to clear, _UNSET to keep current)
            completed: Optional new completion status

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
