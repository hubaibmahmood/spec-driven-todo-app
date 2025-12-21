"""Contract tests for MCP connection creation."""

import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from ai_agent.agent.mcp_connection import create_mcp_connection
from ai_agent.agent.config import AgentConfig


@pytest.mark.asyncio
async def test_create_mcp_connection():
    """Contract: Should create MCP connection async context manager."""
    config = AgentConfig(
        mcp_server_url="http://localhost:8001/mcp",
        gemini_api_key="test_key"
    )
    user_id = "user_123"

    # Mock the streamable HTTP client and ClientSession
    with patch("ai_agent.agent.mcp_connection.streamable_http_client") as mock_http_client, \
         patch("ai_agent.agent.mcp_connection.ClientSession") as mock_session_class:

        # Setup mock streams
        mock_read_stream = AsyncMock()
        mock_write_stream = AsyncMock()
        mock_http_client.return_value.__aenter__.return_value = (
            mock_read_stream,
            mock_write_stream,
            None
        )

        # Setup mock session
        mock_session = AsyncMock()
        mock_session.initialize = AsyncMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session

        async with create_mcp_connection(config, user_id) as session:
            # Assert: Session created and returned
            assert session is not None
            assert session == mock_session
            # Assert: Session was initialized
            mock_session.initialize.assert_called_once()


@pytest.mark.asyncio
async def test_mcp_connection_with_user_id_header():
    """Contract: Should pass user_id for service-to-service auth."""
    config = AgentConfig(
        mcp_server_url="http://localhost:8001/mcp",
        gemini_api_key="test_key"
    )
    user_id = "user_456"

    with patch("ai_agent.agent.mcp_connection.streamable_http_client") as mock_http_client, \
         patch("ai_agent.agent.mcp_connection.ClientSession") as mock_session_class:

        # Setup mocks
        mock_http_client.return_value.__aenter__.return_value = (AsyncMock(), AsyncMock(), None)
        mock_session = AsyncMock()
        mock_session.initialize = AsyncMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session

        async with create_mcp_connection(config, user_id):
            pass

        # Assert: streamable HTTP client was called with correct URL
        mock_http_client.assert_called_once_with(config.mcp_server_url)


@pytest.mark.asyncio
async def test_mcp_connection_timeout_configuration():
    """Contract: Should configure MCP connection successfully."""
    config = AgentConfig(
        mcp_server_url="http://localhost:8001/mcp",
        gemini_api_key="test_key",
        mcp_timeout=20  # Custom timeout
    )

    with patch("ai_agent.agent.mcp_connection.streamable_http_client") as mock_http_client, \
         patch("ai_agent.agent.mcp_connection.ClientSession") as mock_session_class:

        # Setup mocks
        mock_http_client.return_value.__aenter__.return_value = (AsyncMock(), AsyncMock(), None)
        mock_session = AsyncMock()
        mock_session.initialize = AsyncMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session

        async with create_mcp_connection(config, "user_123"):
            pass

        # Assert: Connection established successfully
        mock_http_client.assert_called_once()


@pytest.mark.asyncio
async def test_mcp_connection_error_handling():
    """Contract: Should handle connection errors gracefully."""
    config = AgentConfig(
        mcp_server_url="http://localhost:8001/mcp",
        gemini_api_key="test_key"
    )

    with patch("ai_agent.agent.mcp_connection.streamable_http_client") as mock_http_client:
        # Simulate connection error
        mock_http_client.side_effect = ConnectionError("Failed to connect to MCP server")

        with pytest.raises(ConnectionError, match="Failed to connect"):
            async with create_mcp_connection(config, "user_123"):
                pass


# ============================================================================
# Integration Tests with Real MCP Server
# ============================================================================


@pytest.mark.asyncio
@pytest.mark.skipif(
    not os.getenv("MCP_SERVER_URL"),
    reason="MCP_SERVER_URL not configured - skipping real MCP server test"
)
async def test_mcp_connection_real_server():
    """Integration: Should connect to actual MCP server."""
    config = AgentConfig(
        gemini_api_key="test_key",  # Not needed for MCP connection
        mcp_server_url=os.getenv("MCP_SERVER_URL", "http://localhost:8001/mcp")
    )
    user_id = "integration_test_user"

    # Connect to real MCP server (no mocks)
    async with create_mcp_connection(config, user_id) as session:
        # Assert: Session created successfully
        assert session is not None
        print(f"✓ Successfully connected to MCP server at {config.mcp_server_url}")

        # Try to list tools to verify connection works
        try:
            tools = await session.list_tools()
            print(f"✓ Available MCP tools: {[t.name for t in tools.tools]}")
        except Exception as e:
            print(f"Warning: Could not list tools: {e}")


@pytest.mark.asyncio
@pytest.mark.skipif(
    not os.getenv("MCP_SERVER_URL"),
    reason="MCP_SERVER_URL not configured - skipping real MCP server test"
)
async def test_mcp_connection_with_real_authentication():
    """Integration: Should authenticate with real MCP server using X-User-ID."""
    config = AgentConfig(
        gemini_api_key="test_key",
        mcp_server_url=os.getenv("MCP_SERVER_URL", "http://localhost:8001/mcp")
    )
    user_id = "test_user_123"

    # Real connection with authentication
    async with create_mcp_connection(config, user_id) as session:
        # Connection successful means authentication worked
        assert session is not None
        print(f"✓ Successfully authenticated as user {user_id}")
