"""FastAPI dependencies for dependency injection."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.connection import get_db
from src.database.repository import TaskRepository


async def get_task_repository(
    db: AsyncSession = Depends(get_db)
) -> TaskRepository:
    """
    Dependency to get TaskRepository instance.
    
    Args:
        db: Database session from get_db dependency
        
    Returns:
        TaskRepository instance
    """
    return TaskRepository(db)
