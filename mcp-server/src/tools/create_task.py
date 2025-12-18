"""Create task tool for MCP server."""

import logging
from typing import Any

import httpx
from fastmcp import Context
from pydantic import ValidationError

from ..client import BackendClient
from ..schemas.task import (
    CreateTaskParams,
    ErrorResponse,
    TaskResponse,
    ValidationErrorDetail,
    ERROR_TYPES,
)

logger = logging.getLogger(__name__)


async def create_task(
    ctx: Context,
    title: str,
    description: str | None = None,
    priority: str = "Medium",
    due_date: str | None = None,
) -> dict[str, Any]:
    """
    Create a new task for the authenticated user.

    This tool creates a task in the backend API with the provided details.
    It validates input parameters, handles errors gracefully, and returns
    AI-friendly responses.

    Args:
        ctx: MCP context containing user session metadata
        title: Task title (required, 1-200 characters)
        description: Optional task description
        priority: Task priority level (Low, Medium, High, Urgent). Default: Medium
        due_date: Optional due date in ISO 8601 format (e.g., "2025-12-31T23:59:59Z")

    Returns:
        Created task dictionary on success, or error response dictionary

    Example responses:
        Success: {"id": 1, "title": "Buy milk", "completed": false, ...}
        Validation Error: {"error_type": "validation_error", "message": "...", ...}
        Auth Error: {"error_type": "authentication_error", "message": "...", ...}
    """
    # Extract user_id from MCP session metadata
    # For MVP/testing, use a default test user
    # TODO: In production, integrate with better-auth to get real user_id from session
    try:
        user_id = getattr(ctx.request_context, "user_id", None) or "test_user_123"
    except AttributeError:
        user_id = "test_user_123"

    logger.info(f"Using user_id: {user_id}")

    # Validate parameters with Pydantic
    try:
        params = CreateTaskParams(
            title=title,
            description=description,
            priority=priority,
            due_date=due_date,
        )
    except ValidationError as e:
        logger.warning(
            "Task creation validation failed",
            extra={"user_id": user_id, "validation_errors": e.errors()},
        )

        # Translate Pydantic errors to AI-friendly format
        validation_details = []
        for error in e.errors():
            field = ".".join(str(loc) for loc in error["loc"])
            message = error["msg"]

            # Extract received value if available
            received_value = None
            if "input" in error:
                received_value = str(error["input"])

            # Provide helpful suggestions based on field
            suggestion = None
            if field == "title":
                if "at least 1 character" in message or "empty" in message.lower():
                    suggestion = "Title must not be empty. Provide a meaningful task title."
                elif "at most 200 characters" in message:
                    suggestion = "Title is too long. Please use 200 characters or less."
            elif field == "priority":
                suggestion = "Priority must be one of: Low, Medium, High, Urgent"
            elif field == "due_date":
                suggestion = "Provide due_date in ISO 8601 format (e.g., '2025-12-31T23:59:59Z')"

            validation_details.append(
                ValidationErrorDetail(
                    field=field,
                    message=message,
                    received_value=received_value,
                    suggestion=suggestion,
                )
            )

        return ErrorResponse(
            error_type=ERROR_TYPES["validation_error"],
            message=f"Task creation failed due to {len(validation_details)} validation error(s).",
            details={"validation_errors": [detail.model_dump() for detail in validation_details]},
            suggestions=["Review and correct the validation errors listed in details"],
        ).model_dump()

    # Initialize backend client
    client = BackendClient()

    try:
        logger.info(
            "Creating task for user",
            extra={
                "user_id": user_id,
                "title": params.title,
                "priority": params.priority.value,
                "tool": "create_task",
            },
        )

        # Prepare task data for backend
        task_data = {
            "title": params.title,
            "description": params.description,
            "priority": params.priority.value,
            "due_date": params.due_date.isoformat() if params.due_date else None,
        }

        # Make request to backend
        response = await client.create_task(user_id, task_data)

        # Handle different HTTP status codes
        if response.status_code == 201:
            created_task_data = response.json()
            logger.info(
                "Successfully created task",
                extra={
                    "user_id": user_id,
                    "task_id": created_task_data.get("id"),
                    "tool": "create_task",
                },
            )

            # Validate and return created task
            try:
                task = TaskResponse(**created_task_data)
                return task.model_dump()
            except Exception as e:
                logger.error(
                    f"Failed to validate created task response: {e}",
                    extra={"user_id": user_id, "task_data": created_task_data},
                )
                # Still return the task even if validation fails
                return created_task_data

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

        elif response.status_code == 422:
            # Backend validation error
            logger.error(
                "Backend validation failed",
                extra={"user_id": user_id, "status_code": 422},
            )
            error_detail = response.json().get("detail", "Validation failed")
            return ErrorResponse(
                error_type=ERROR_TYPES["validation_error"],
                message="Backend rejected the task data due to validation errors.",
                details={"backend_error": error_detail, "status_code": 422},
                suggestions=[
                    "Review task data for correctness",
                    "Ensure all required fields are provided with valid values",
                ],
            ).model_dump()

        elif response.status_code == 500:
            logger.error(
                "Backend server error",
                extra={"user_id": user_id, "status_code": 500},
            )
            return ErrorResponse(
                error_type=ERROR_TYPES["backend_error"],
                message="Backend service encountered an error while creating the task.",
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
            "Unexpected error in create_task",
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
