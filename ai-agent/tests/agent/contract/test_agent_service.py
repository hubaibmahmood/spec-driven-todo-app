"""Contract tests for AgentService."""

import pytest
from unittest.mock import AsyncMock, Mock, MagicMock
from ai_agent.agent.config import AgentConfig


@pytest.mark.asyncio
async def test_agent_service_initialization():
    """Contract: AgentService should initialize with config."""
    from ai_agent.agent.agent_service import AgentService

    config = AgentConfig(gemini_api_key="test_key_12345")
    service = AgentService(config)

    assert service.config == config
    assert service.config.gemini_api_key == "test_key_12345"


@pytest.mark.asyncio
async def test_create_gemini_client():
    """Contract: create_gemini_client() returns AsyncOpenAI client configured for Gemini."""
    from ai_agent.agent.agent_service import AgentService

    config = AgentConfig(gemini_api_key="test_key_12345")
    service = AgentService(config)

    # Create Gemini client
    client = service.create_gemini_client()

    # Verify client is configured for Gemini
    assert client is not None
    assert client.api_key == "test_key_12345"
    # Should point to Gemini's OpenAI-compatible endpoint
    assert "generativelanguage.googleapis.com" in client.base_url.host


@pytest.mark.asyncio
async def test_initialize_agent_with_mcp_server():
    """Contract: initialize_agent creates Agent with Gemini model and MCP server."""
    from ai_agent.agent.agent_service import AgentService

    config = AgentConfig(gemini_api_key="test_key_12345")
    service = AgentService(config)

    # Mock MCP server
    mock_mcp_server = Mock()
    mock_mcp_server.list_tools = AsyncMock(return_value=[])

    # Initialize agent
    agent = await service.initialize_agent(mock_mcp_server)

    # Verify agent was created
    assert agent is not None
    # Agent should have the MCP server configured
    assert len(agent.mcp_servers) == 1
    assert agent.mcp_servers[0] == mock_mcp_server


@pytest.mark.asyncio
async def test_initialize_agent_configures_model():
    """Contract: initialize_agent creates agent and create_run_config() provides model configuration."""
    from ai_agent.agent.agent_service import AgentService

    config = AgentConfig(
        gemini_api_key="test_key_12345",
        temperature=0.8
    )
    service = AgentService(config)

    mock_mcp_server = Mock()
    mock_mcp_server.list_tools = AsyncMock(return_value=[])

    agent = await service.initialize_agent(mock_mcp_server)

    # Verify agent was created
    assert agent is not None
    assert agent.name == "Todo Assistant"

    # Verify run_config can be created separately
    run_config = service.create_run_config()
    assert run_config is not None
    assert run_config.tracing_disabled is True


@pytest.mark.asyncio
async def test_initialize_agent_with_system_prompt():
    """Contract: initialize_agent includes system prompt from config."""
    from ai_agent.agent.agent_service import AgentService

    custom_prompt = "You are a helpful task management assistant."
    config = AgentConfig(
        gemini_api_key="test_key_12345",
        system_prompt=custom_prompt
    )
    service = AgentService(config)

    mock_mcp_server = Mock()
    mock_mcp_server.list_tools = AsyncMock(return_value=[])

    agent = await service.initialize_agent(mock_mcp_server)

    # System prompt should be used in agent instructions
    assert agent is not None
    assert agent.instructions == custom_prompt
