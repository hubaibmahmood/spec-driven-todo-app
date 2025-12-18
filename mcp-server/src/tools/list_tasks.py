"""List tasks tool for MCP server."""

import logging
from typing import Any

import httpx
from fastmcp import Context

from ..client import BackendClient
from ..schemas.task import ErrorResponse, TaskResponse, ERROR_TYPES

logger = logging.getLogger(__name__)


async def list_tasks(ctx: Context) -> list[dict[str, Any]] | dict[str, Any]:
    """
    List all tasks for the authenticated user.

    This tool retrieves all tasks from the backend API that belong to the
    authenticated user. It handles authentication, error translation, and
    returns AI-friendly responses.

    Args:
        ctx: MCP context containing user session metadata

    Returns:
        List of tasks (as dictionaries) on success, or error response dictionary

    Example responses:
        Success: [{"id": 1, "title": "Buy milk", "completed": false, ...}, ...]
        Empty: []
        Error: {"error_type": "authentication_error", "message": "...", ...}
    """
    # Extract user_id from MCP session metadata
    # For MVP/testing, use a default test user
    # TODO: In production, integrate with better-auth to get real user_id from session
    try:
        user_id = getattr(ctx.request_context, "user_id", None) or "test_user_123"
    except AttributeError:
        user_id = "test_user_123"

    logger.info(f"Using user_id: {user_id}")

    # Initialize backend client
    client = BackendClient()

    try:
        logger.info(
            "Fetching tasks for user",
            extra={
                "user_id": user_id,
                "tool": "list_tasks",
            },
        )

        # Make request to backend
        response = await client.get_tasks(user_id)

        # Handle different HTTP status codes
        if response.status_code == 200:
            tasks_data = response.json()
            logger.info(
                "Successfully retrieved tasks",
                extra={
                    "user_id": user_id,
                    "task_count": len(tasks_data),
                    "tool": "list_tasks",
                },
            )

            # Validate and return tasks
            validated_tasks = []
            for task_data in tasks_data:
                try:
                    task = TaskResponse(**task_data)
                    validated_tasks.append(task.model_dump())
                except Exception as e:
                    logger.warning(
                        f"Failed to validate task data: {e}",
                        extra={"user_id": user_id, "task_data": task_data},
                    )
                    continue

            return validated_tasks

        elif response.status_code == 401:
            logger.error(
                "Authentication failed",
                extra={"user_id": user_id, "status_code": 401},
            )
            return ErrorResponse(
                error_type=ERROR_TYPES["authentication_error"],
                message="Service authentication failed. Invalid or expired service token.",
                details={"status_code": 401},
                suggestions=[
                    "Verify SERVICE_AUTH_TOKEN is correctly configured",
                    "Check that the service token matches between MCP server and backend",
                ],
            ).model_dump()

        elif response.status_code == 403:
            logger.error(
                "Authorization failed",
                extra={"user_id": user_id, "status_code": 403},
            )
            return ErrorResponse(
                error_type=ERROR_TYPES["authorization_error"],
                message="Access denied. User not authorized to view these tasks.",
                details={"status_code": 403},
                suggestions=["Verify user has permission to access their tasks"],
            ).model_dump()

        elif response.status_code == 500:
            logger.error(
                "Backend server error",
                extra={"user_id": user_id, "status_code": 500},
            )
            return ErrorResponse(
                error_type=ERROR_TYPES["backend_error"],
                message="Backend service encountered an error while processing the request.",
                details={"status_code": 500},
                suggestions=[
                    "Try the request again in a few moments",
                    "Contact support if the error persists",
                ],
            ).model_dump()

        else:
            # Handle other unexpected status codes
            logger.error(
                "Unexpected backend response",
                extra={
                    "user_id": user_id,
                    "status_code": response.status_code,
                },
            )
            return ErrorResponse(
                error_type=ERROR_TYPES["backend_error"],
                message=f"Unexpected response from backend (status {response.status_code}).",
                details={"status_code": response.status_code},
                suggestions=["Try the request again", "Contact support if issue persists"],
            ).model_dump()

    except httpx.TimeoutException as e:
        logger.error(
            "Request timeout",
            extra={"user_id": user_id, "error": str(e)},
        )
        return ErrorResponse(
            error_type=ERROR_TYPES["timeout_error"],
            message="Request timed out while waiting for backend response (>30s).",
            details={"error": str(e)},
            suggestions=[
                "The backend service may be experiencing high load",
                "Try again in a few moments",
                "Check backend service health",
            ],
        ).model_dump()

    except httpx.ConnectError as e:
        logger.error(
            "Connection failed",
            extra={"user_id": user_id, "error": str(e)},
        )
        return ErrorResponse(
            error_type=ERROR_TYPES["connection_error"],
            message="Unable to connect to backend service. Connection refused or network error.",
            details={"error": str(e)},
            suggestions=[
                "Verify backend service is running",
                "Check FASTAPI_BASE_URL configuration",
                "Verify network connectivity",
            ],
        ).model_dump()

    except Exception as e:
        # Catch-all for unexpected errors
        logger.exception(
            "Unexpected error in list_tasks",
            extra={"user_id": user_id, "error": str(e)},
        )
        return ErrorResponse(
            error_type=ERROR_TYPES["backend_error"],
            message=f"Unexpected error occurred: {str(e)}",
            details={"error": str(e), "error_type": type(e).__name__},
            suggestions=["Contact support with error details"],
        ).model_dump()

    finally:
        # Always clean up the client connection
        await client.close()
