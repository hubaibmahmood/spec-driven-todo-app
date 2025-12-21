"""Contract tests for AgentConfig validation."""

import pytest
from pydantic import ValidationError
from ai_agent.agent.config import AgentConfig


def test_agent_config_requires_gemini_api_key():
    """Contract: AgentConfig must validate GEMINI_API_KEY presence."""
    with pytest.raises(ValidationError):
        AgentConfig(gemini_api_key="")  # Empty key should fail


def test_agent_config_with_valid_key():
    """Contract: AgentConfig should accept valid API key."""
    config = AgentConfig(gemini_api_key="test_key_12345")
    assert config.gemini_api_key == "test_key_12345"


def test_agent_config_default_values():
    """Contract: AgentConfig should have sensible defaults."""
    config = AgentConfig(gemini_api_key="test_key")

    # Verify defaults
    assert config.mcp_server_url == "http://localhost:8001/mcp"
    assert config.mcp_timeout == 10
    assert config.mcp_retry_attempts == 3
    assert config.temperature == 0.7
    assert config.token_budget == 800_000
    assert config.encoding_name == "cl100k_base"
    assert "task management assistant" in config.system_prompt.lower()


def test_agent_config_temperature_validation():
    """Contract: Temperature must be between 0.0 and 2.0."""
    # Valid temperatures
    config = AgentConfig(gemini_api_key="test_key", temperature=0.0)
    assert config.temperature == 0.0

    config = AgentConfig(gemini_api_key="test_key", temperature=2.0)
    assert config.temperature == 2.0

    # Invalid temperatures
    with pytest.raises(ValidationError):
        AgentConfig(gemini_api_key="test_key", temperature=-0.1)

    with pytest.raises(ValidationError):
        AgentConfig(gemini_api_key="test_key", temperature=2.1)
