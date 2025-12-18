"""Mark task completed tool for MCP server."""

import logging
from typing import Any

import httpx
from fastmcp import Context

from ..client import BackendClient
from ..schemas.task import ErrorResponse, TaskResponse, ERROR_TYPES

logger = logging.getLogger(__name__)


async def mark_task_completed(ctx: Context, task_id: int) -> dict[str, Any]:
    """
    Mark a task as completed.

    Args:
        ctx: MCP context containing user session metadata
        task_id: ID of task to mark as completed

    Returns:
        Updated task dictionary on success, or error response dictionary
    """
    # Extract user_id from MCP session metadata
    try:
        user_id = getattr(ctx.request_context, "user_id", None) or "test_user_123"
    except AttributeError:
        user_id = "test_user_123"

    logger.info(f"Marking task {task_id} as completed for user: {user_id}")

    client = BackendClient()

    try:
        response = await client.mark_task_completed(user_id, task_id)

        if response.status_code == 200:
            updated_task_data = response.json()
            logger.info(f"Successfully marked task {task_id} as completed")

            try:
                task = TaskResponse(**updated_task_data)
                return task.model_dump()
            except Exception:
                return updated_task_data

        elif response.status_code == 404:
            return ErrorResponse(
                error_type=ERROR_TYPES["not_found_error"],
                message=f"Task {task_id} not found.",
                suggestions=["Verify the task ID is correct", "List tasks to see available task IDs"],
            ).model_dump()

        elif response.status_code == 403:
            return ErrorResponse(
                error_type=ERROR_TYPES["authorization_error"],
                message=f"You don't have permission to mark task {task_id} as completed.",
                suggestions=["You can only mark your own tasks as completed"],
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
                message=f"Unexpected response from backend (status {response.status_code}).",
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
        logger.exception(f"Unexpected error in mark_task_completed: {e}")
        return ErrorResponse(
            error_type=ERROR_TYPES["backend_error"],
            message=f"Unexpected error: {str(e)}",
            suggestions=["Contact support with error details"],
        ).model_dump()

    finally:
        await client.close()
