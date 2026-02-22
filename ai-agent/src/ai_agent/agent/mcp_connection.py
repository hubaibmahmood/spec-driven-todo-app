"""MCP connection management for OpenAI Agent."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

try:
    from mcp import ClientSession
    from mcp.client.streamable_http import streamable_http_client
    import httpx
except ImportError:
    # Fallback for testing or when MCP not installed
    streamable_http_client = None  # type: ignore
    ClientSession = None  # type: ignore
    httpx = None  # type: ignore

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

    def _get_failure_error_function(self, tool_name: str = None):
        """Return error function for tool call failures.

        This method is required by the OpenAI Agents SDK for error handling.
        Returns a function that formats tool call errors.

        Args:
            tool_name: Optional tool name for contextualized error messages
        """
        def format_error(error: Exception) -> str:
            """Format tool call error for agent context."""
            if tool_name:
                return f"MCP tool '{tool_name}' failed: {str(error)}"
            return f"MCP tool call failed: {str(error)}"
        return format_error

    def _get_needs_approval_for_tool(self, tool, agent=None):
        """Determine if a tool requires approval before execution.

        This method is required by the OpenAI Agents SDK v0.8.0+ for HITL workflows.
        Returns False for all tools as MCP server doesn't implement approval workflows.

        Args:
            tool: The tool to check for approval requirements
            agent: Optional agent context (unused in MCP adapter)

        Returns:
            bool: Always False (no approval needed for MCP tools)
        """
        # MCP tools don't require approval - return False for all
        return False


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
        # Create custom HTTP client with X-User-ID header for authentication
        custom_headers = {"X-User-ID": user_id}
        http_client = httpx.AsyncClient(headers=custom_headers, timeout=30.0)

        try:
            # Connect to streamable HTTP server with custom client
            async with streamable_http_client(
                config.mcp_server_url,
                http_client=http_client
            ) as (
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
        finally:
            # Close the HTTP client
            await http_client.aclose()

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
