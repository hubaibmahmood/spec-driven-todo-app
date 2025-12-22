"""Delete task tool for MCP server."""

import logging
from typing import Any

import httpx
from fastmcp import Context
from fastmcp.server.dependencies import get_http_headers

from ..client import BackendClient
from ..schemas.task import ErrorResponse, ERROR_TYPES

logger = logging.getLogger(__name__)


async def delete_task(ctx: Context, task_id: int) -> dict[str, Any]:
    """
    Delete a task permanently.

    Args:
        ctx: MCP context containing user session metadata
        task_id: ID of task to delete

    Returns:
        Success message on deletion, or error response dictionary
    """
    # Extract user_id from HTTP headers using FastMCP helper
    headers = get_http_headers()
    user_id = headers.get('X-User-ID') or headers.get('x-user-id')

    # Fallback for testing/debugging
    if not user_id:
        user_id = "test_user_123"
        logger.warning(f"Could not extract user_id from X-User-ID header, using fallback: {user_id}")
        logger.info(f"Available headers: {list(headers.keys())}")

    logger.info(f"Deleting task {task_id} for user: {user_id}")

    client = BackendClient()

    try:
        response = await client.delete_task(user_id, task_id)

        if response.status_code == 204:
            logger.info(f"Successfully deleted task {task_id}")
            return {
                "success": True,
                "message": f"Task {task_id} has been deleted successfully.",
                "task_id": task_id,
            }

        elif response.status_code == 404:
            return ErrorResponse(
                error_type=ERROR_TYPES["not_found_error"],
                message=f"Task {task_id} not found.",
                suggestions=[
                    "The task may have already been deleted",
                    "Verify the task ID is correct",
                ],
            ).model_dump()

        elif response.status_code == 403:
            return ErrorResponse(
                error_type=ERROR_TYPES["authorization_error"],
                message=f"You don't have permission to delete task {task_id}.",
                suggestions=["You can only delete your own tasks"],
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
        logger.exception(f"Unexpected error in delete_task: {e}")
        return ErrorResponse(
            error_type=ERROR_TYPES["backend_error"],
            message=f"Unexpected error: {str(e)}",
            suggestions=["Contact support with error details"],
        ).model_dump()

    finally:
        await client.close()
