"""MCP Server entry point for todo-app MCP tools."""

import logging
from fastmcp import FastMCP

from .config import settings
from .tools.list_tasks import list_tasks
from .tools.create_task import create_task
from .tools.mark_completed import mark_task_completed
from .tools.update_task import update_task
from .tools.delete_task import delete_task

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

# Tool 3: Mark Task Completed
mcp.tool()(mark_task_completed)
logger.info("Registered tool: mark_task_completed")

# Tool 4: Update Task
mcp.tool()(update_task)
logger.info("Registered tool: update_task")

# Tool 5: Delete Task
mcp.tool()(delete_task)
logger.info("Registered tool: delete_task")

logger.info("MCP server initialized with 5 tools")


def main():
    """Run the MCP server."""
    import os
    
    # Get port from environment variable (Railway/Render) or settings
    # Railway provides PORT, so we check that first
    port = int(os.environ.get("PORT", settings.mcp_server_port))
    
    logger.info(
        "Starting todo-mcp-server",
        extra={
            "backend_url": settings.fastapi_base_url,
            "log_level": settings.mcp_log_level,
            "port": port,
        },
    )

    # Run server with streamable HTTP transport
    # host="0.0.0.0" is required for Docker/Railway deployment
    mcp.run(transport="streamable-http", host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
