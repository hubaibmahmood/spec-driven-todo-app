"""MCP Server entry point for todo-app MCP tools."""

import logging
from fastmcp import FastMCP

from .config import settings
from .tools.list_tasks import list_tasks
from .tools.create_task import create_task

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.mcp_log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("todo-mcp-server")

# Register tools
logger.info("Registering MCP tools...")

# Tool 1: List Tasks
mcp.tool()(list_tasks)
logger.info("Registered tool: list_tasks")

# Tool 2: Create Task
mcp.tool()(create_task)
logger.info("Registered tool: create_task")

logger.info("MCP server initialized with 2 tools")


def main():
    """Run the MCP server."""
    logger.info(
        "Starting todo-mcp-server",
        extra={
            "backend_url": settings.fastapi_base_url,
            "log_level": settings.mcp_log_level,
        },
    )

    # Run server with HTTP transport
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
