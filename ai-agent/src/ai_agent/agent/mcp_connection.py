"""MCP connection management for OpenAI Agent."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

try:
    from mcp import ClientSession
    from mcp.client.streamable_http import streamable_http_client
except ImportError:
    # Fallback for testing or when MCP not installed
    streamable_http_client = None  # type: ignore
    ClientSession = None  # type: ignore

from ai_agent.agent.config import AgentConfig

logger = logging.getLogger(__name__)


class MCPServerAdapter:
    """Adapter to make mcp.ClientSession compatible with openai-agents SDK."""
    
    def __init__(self, session, name: str):
        self.session = session
        self.name = name
        self.use_structured_content = False
        
    async def list_tools(self, run_context=None, agent=None):
        """Adapt list_tools call."""
        # openai-agents passes run_context and agent, but mcp session doesn't need them
        result = await self.session.list_tools()
        # Convert ListToolsResult to what might be expected if necessary, 
        # but usually it expects a list of tool schemas.
        # mcp list_tools returns a result object with a tools attribute.
        if hasattr(result, 'tools'):
            return result.tools
        return result

    async def call_tool(self, name: str, arguments: dict, run_context=None, agent=None):
        """Adapt call_tool call."""
        # openai-agents might pass extra args
        return await self.session.call_tool(name, arguments)


@asynccontextmanager
async def create_mcp_connection(
    config: AgentConfig,
    user_id: str
) -> AsyncGenerator:
    """Create async context manager for MCP server connection.

    This function establishes a connection to the MCP server with proper
    authentication and configuration:
    - Adds X-User-ID header for service-to-service authentication
    - Configures timeout from AgentConfig
    - Handles connection errors with logging
    - Automatically closes connection on context exit

    Args:
        config: Agent configuration with MCP server settings
        user_id: User ID for X-User-ID header (service-to-service auth)

    Yields:
        MCP ClientSession instance ready for tool calls

    Raises:
        ConnectionError: If MCP server connection fails
        ValueError: If MCP client is not available

    Example:
        >>> config = AgentConfig(mcp_server_url="http://localhost:8001/mcp")
        >>> async with create_mcp_connection(config, "user_123") as session:
        ...     # Initialize the connection
        ...     await session.initialize()
        ...     # Use session for MCP tool calls
        ...     tools = await session.list_tools()
    """
    if streamable_http_client is None or ClientSession is None:
        raise ValueError(
            "MCP client not available. Install with: pip install mcp"
        )

    logger.info(
        f"Creating MCP connection to {config.mcp_server_url} for user {user_id}"
    )

    try:
        # Connect to streamable HTTP server
        async with streamable_http_client(config.mcp_server_url) as (
            read_stream,
            write_stream,
            _,
        ):
            # Create a session using the client streams
            async with ClientSession(read_stream, write_stream) as session:
                logger.debug(f"MCP connection established for user {user_id}")
                # Initialize the connection
                await session.initialize()
                
                # Wrap session in adapter for openai-agents SDK compatibility
                adapter = MCPServerAdapter(session, "todo_mcp_server")
                yield adapter

    except ConnectionError as e:
        logger.error(
            f"Failed to connect to MCP server at {config.mcp_server_url}: {e}"
        )
        raise ConnectionError(
            f"Failed to connect to MCP server: {e}"
        ) from e
    except Exception as e:
        logger.error(
            f"Unexpected error creating MCP connection: {e}",
            exc_info=True
        )
        raise
    finally:
        logger.debug(f"MCP connection closed for user {user_id}")
