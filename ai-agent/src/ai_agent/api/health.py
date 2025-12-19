"""Health check endpoint for AI Agent service."""

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    """
    Health check endpoint.

    Returns:
        Simple status message confirming service is running
    """
    return {"status": "healthy", "service": "ai-agent"}
