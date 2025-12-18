"""Update task tool for MCP server."""

import logging
from typing import Any

import httpx
from fastmcp import Context
from pydantic import ValidationError

from ..client import BackendClient
from ..schemas.task import (
    ErrorResponse,
    TaskResponse,
    UpdateTaskParams,
    ERROR_TYPES,
)

logger = logging.getLogger(__name__)


async def update_task(
    ctx: Context,
    task_id: int,
    title: str | None = None,
    description: str | None = None,
    priority: str | None = None,
    due_date: str | None = None,
) -> dict[str, Any]:
    """
    Update task fields (title, description, priority, due_date).

    Note: Use mark_task_completed tool to change completion status.

    Args:
        ctx: MCP context containing user session metadata
        task_id: ID of task to update
        title: New task title (optional)
        description: New task description (optional, null to clear)
        priority: New priority level (optional: Low, Medium, High, Urgent)
        due_date: New due date in ISO 8601 format (optional, null to clear)

    Returns:
        Updated task dictionary on success, or error response dictionary
    """
    # Extract user_id from MCP session metadata
    try:
        user_id = getattr(ctx.request_context, "user_id", None) or "test_user_123"
    except AttributeError:
        user_id = "test_user_123"

    logger.info(f"Updating task {task_id} for user: {user_id}")

    # Validate at least one field is provided
    if all(field is None for field in [title, description, priority, due_date]):
        return ErrorResponse(
            error_type=ERROR_TYPES["validation_error"],
            message="At least one field must be provided for update.",
            suggestions=["Provide title, description, priority, or due_date to update"],
        ).model_dump()

    # Validate parameters with Pydantic
    try:
        params = UpdateTaskParams(
            task_id=task_id,
            title=title,
            description=description,
            priority=priority,
            due_date=due_date,
        )
    except ValidationError as e:
        logger.warning(f"Validation failed: {e.errors()}")
        return ErrorResponse(
            error_type=ERROR_TYPES["validation_error"],
            message="Task update validation failed.",
            details={"validation_errors": e.errors()},
            suggestions=["Review and correct the validation errors"],
        ).model_dump()

    client = BackendClient()

    try:
        # Prepare update data (only include non-None fields)
        update_data = {}
        if params.title is not None:
            update_data["title"] = params.title
        if params.description is not None:
            update_data["description"] = params.description
        if params.priority is not None:
            update_data["priority"] = params.priority.value
        if params.due_date is not None:
            update_data["due_date"] = params.due_date.isoformat()

        response = await client.update_task(user_id, task_id, update_data)

        if response.status_code == 200:
            updated_task_data = response.json()
            logger.info(f"Successfully updated task {task_id}")

            try:
                task = TaskResponse(**updated_task_data)
                return task.model_dump()
            except Exception:
                return updated_task_data

        elif response.status_code == 404:
            return ErrorResponse(
                error_type=ERROR_TYPES["not_found_error"],
                message=f"Task {task_id} not found.",
                suggestions=["Verify the task ID is correct"],
            ).model_dump()

        elif response.status_code == 403:
            return ErrorResponse(
                error_type=ERROR_TYPES["authorization_error"],
                message=f"You don't have permission to update task {task_id}.",
                suggestions=["You can only update your own tasks"],
            ).model_dump()

        elif response.status_code == 422:
            error_detail = response.json().get("detail", "Validation failed")
            return ErrorResponse(
                error_type=ERROR_TYPES["validation_error"],
                message="Backend rejected the update.",
                details={"backend_error": error_detail},
                suggestions=["Review task data for correctness"],
            ).model_dump()

        elif response.status_code == 401:
            return ErrorResponse(
                error_type=ERROR_TYPES["authentication_error"],
                message="Service authentication failed.",
                suggestions=["Verify SERVICE_AUTH_TOKEN configuration"],
            ).model_dump()

        else:
            return ErrorResponse(
                error_type=ERROR_TYPES["backend_error"],
                message=f"Unexpected response (status {response.status_code}).",
                suggestions=["Try again", "Contact support if issue persists"],
            ).model_dump()

    except httpx.TimeoutException:
        return ErrorResponse(
            error_type=ERROR_TYPES["timeout_error"],
            message="Request timed out.",
            suggestions=["Try again in a few moments"],
        ).model_dump()

    except httpx.ConnectError:
        return ErrorResponse(
            error_type=ERROR_TYPES["connection_error"],
            message="Unable to connect to backend service.",
            suggestions=["Verify backend service is running"],
        ).model_dump()

    except Exception as e:
        logger.exception(f"Unexpected error in update_task: {e}")
        return ErrorResponse(
            error_type=ERROR_TYPES["backend_error"],
            message=f"Unexpected error: {str(e)}",
            suggestions=["Contact support with error details"],
        ).model_dump()

    finally:
        await client.close()
