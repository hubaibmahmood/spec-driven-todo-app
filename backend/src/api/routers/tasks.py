"""Task endpoints for CRUD operations."""

import math
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query, status

from src.api.dependencies import get_task_repository, get_current_user_or_service
from src.api.schemas.task import (
    TaskCreate,
    TaskListResponse,
    TaskResponse,
    CompletionUpdate,
    TaskUpdate,
    BulkDeleteRequest,
    BulkDeleteResponse,
)
from src.database.repository import TaskRepository
from src.models.database import PriorityLevel


router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/", response_model=TaskListResponse, status_code=status.HTTP_200_OK)
async def get_all_tasks(
    search: Optional[str] = Query(None, description="Search in title and description"),
    priority: Optional[PriorityLevel] = Query(None, description="Filter by priority"),
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    due_before: Optional[date] = Query(None, description="Tasks due on or before this date"),
    due_after: Optional[date] = Query(None, description="Tasks due on or after this date"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(1000, ge=1, le=1000, description="Items per page (max 1000)"),
    repository: TaskRepository = Depends(get_task_repository),
    current_user: str = Depends(get_current_user_or_service),
) -> TaskListResponse:
    """
    Get tasks for the authenticated user with optional filtering and pagination.

    Returns:
        Paginated task list with total count
    """
    tasks, total = await repository.get_all_by_user_filtered(
        user_id=current_user,
        search=search,
        priority=priority,
        completed=completed,
        due_before=due_before,
        due_after=due_after,
        page=page,
        limit=limit,
    )
    pages = math.ceil(total / limit) if total > 0 else 1
    return TaskListResponse(
        tasks=[TaskResponse.model_validate(t) for t in tasks],
        total=total,
        page=page,
        limit=limit,
        pages=pages,
    )


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    repository: TaskRepository = Depends(get_task_repository),
    current_user: str = Depends(get_current_user_or_service)
) -> TaskResponse:
    """
    Create a new task for the authenticated user.

    Args:
        task_data: Task creation data (title, description, priority, due_date)
        repository: Task repository dependency
        current_user: Current authenticated user

    Returns:
        Created task with ID and timestamps
    """
    task = await repository.create(
        user_id=current_user,
        title=task_data.title,
        description=task_data.description,
        priority=task_data.priority,
        due_date=task_data.due_date
    )
    return TaskResponse.model_validate(task)


@router.get("/{task_id}", response_model=TaskResponse, status_code=status.HTTP_200_OK)
async def get_task(
    task_id: int,
    repository: TaskRepository = Depends(get_task_repository),
    current_user: str = Depends(get_current_user_or_service)
) -> TaskResponse:
    """
    Get a specific task by ID.

    Only returns the task if it belongs to the authenticated user.

    Args:
        task_id: Task ID
        repository: Task repository dependency
        current_user: Current authenticated user

    Returns:
        Task details

    Raises:
        HTTPException: 404 if task not found or doesn't belong to user
    """
    from fastapi import HTTPException

    task = await repository.get_by_id(task_id, current_user)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )

    return TaskResponse.model_validate(task)


@router.patch("/{task_id}", response_model=TaskResponse, status_code=status.HTTP_200_OK)
async def update_task_completion(
    task_id: int,
    completion_data: CompletionUpdate,
    repository: TaskRepository = Depends(get_task_repository),
    current_user: str = Depends(get_current_user_or_service)
) -> TaskResponse:
    """
    Update task completion status.

    Only the owner can update their tasks.

    Args:
        task_id: Task ID
        completion_data: Completion status update
        repository: Task repository dependency
        current_user: Current authenticated user

    Returns:
        Updated task

    Raises:
        HTTPException: 404 if task not found or doesn't belong to user
    """
    from fastapi import HTTPException

    task = await repository.update(
        task_id=task_id,
        user_id=current_user,
        completed=completion_data.completed
    )

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )

    return TaskResponse.model_validate(task)


@router.put("/{task_id}", response_model=TaskResponse, status_code=status.HTTP_200_OK)
async def update_task_details(
    task_id: int,
    task_update: TaskUpdate,
    repository: TaskRepository = Depends(get_task_repository),
    current_user: str = Depends(get_current_user_or_service)
) -> TaskResponse:
    """
    Update task title and/or description.

    Only the owner can update their tasks.

    Args:
        task_id: Task ID
        task_update: Task update data (title, description, completed)
        repository: Task repository dependency
        current_user: Current authenticated user

    Returns:
        Updated task

    Raises:
        HTTPException: 404 if task not found or doesn't belong to user
    """
    from fastapi import HTTPException
    from src.database.repository import _UNSET

    # Build kwargs, only including fields that were explicitly set
    update_kwargs = {"task_id": task_id, "user_id": current_user}
    if task_update.title is not None:
        update_kwargs["title"] = task_update.title
    else:
        update_kwargs["title"] = _UNSET

    if task_update.description is not None or "description" in task_update.model_fields_set:
        update_kwargs["description"] = task_update.description
    else:
        update_kwargs["description"] = _UNSET

    if task_update.completed is not None:
        update_kwargs["completed"] = task_update.completed
    else:
        update_kwargs["completed"] = _UNSET

    if task_update.priority is not None:
        update_kwargs["priority"] = task_update.priority
    else:
        update_kwargs["priority"] = _UNSET

    if task_update.due_date is not None or "due_date" in task_update.model_fields_set:
        update_kwargs["due_date"] = task_update.due_date
    else:
        update_kwargs["due_date"] = _UNSET

    task = await repository.update(**update_kwargs)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )

    return TaskResponse.model_validate(task)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    repository: TaskRepository = Depends(get_task_repository),
    current_user: str = Depends(get_current_user_or_service)
) -> None:
    """
    Delete a task.

    Only the owner can delete their tasks.

    Args:
        task_id: Task ID
        repository: Task repository dependency
        current_user: Current authenticated user

    Raises:
        HTTPException: 404 if task not found or doesn't belong to user
    """
    from fastapi import HTTPException

    deleted = await repository.delete(task_id, current_user)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )


@router.post("/bulk-delete", response_model=BulkDeleteResponse, status_code=status.HTTP_200_OK)
async def bulk_delete_tasks(
    request: BulkDeleteRequest,
    repository: TaskRepository = Depends(get_task_repository),
    current_user: str = Depends(get_current_user_or_service)
) -> BulkDeleteResponse:
    """
    Delete multiple tasks in one request.

    Only the owner's tasks will be deleted.

    Args:
        request: Bulk delete request with list of task IDs
        repository: Task repository dependency
        current_user: Current authenticated user

    Returns:
        Lists of successfully deleted and not found task IDs
    """
    deleted, not_found = await repository.bulk_delete(request.task_ids, current_user)

    return BulkDeleteResponse(
        deleted=deleted,
        not_found=not_found
    )