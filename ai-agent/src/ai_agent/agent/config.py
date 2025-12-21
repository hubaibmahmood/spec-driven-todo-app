"""Configuration for OpenAI Agent with Gemini backend."""

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AgentConfig(BaseSettings):
    """Runtime configuration for OpenAI Agent with Gemini backend.

    This configuration class manages all settings for the agent including:
    - Gemini API credentials
    - MCP server connection parameters
    - Agent behavior settings (temperature, system prompt)
    - Context window management (token budget, encoding)

    All settings can be overridden via environment variables with the AGENT_ prefix.
    Example: AGENT_GEMINI_API_KEY, AGENT_TEMPERATURE, etc.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="AGENT_",
        extra="ignore",
    )

    # Gemini API Configuration
    gemini_api_key: str = Field(
        ...,
        description="API key for Gemini via OpenAI-compatible endpoint",
        min_length=1,
    )

    # MCP Server Configuration
    mcp_server_url: str = Field(
        default="http://localhost:8001/mcp",
        description="MCP server endpoint URL",
    )
    mcp_timeout: int = Field(
        default=10,
        description="MCP connection timeout in seconds",
        gt=0,
    )
    mcp_retry_attempts: int = Field(
        default=3,
        description="Max retry attempts for MCP calls",
        ge=0,
        le=10,
    )

    # Agent Behavior
    system_prompt: str = Field(
        default="You are a helpful task management assistant. Use the available tools to help users manage their tasks.",
        description="System-level instructions for agent behavior",
    )
    temperature: float = Field(
        default=0.7,
        description="Model temperature for response generation",
        ge=0.0,
        le=2.0,
    )

    # Context Window Management
    token_budget: int = Field(
        default=800_000,
        description="Maximum tokens for conversation history (80% of model limit)",
        gt=0,
    )
    encoding_name: str = Field(
        default="cl100k_base",
        description="Token encoding for tiktoken",
    )

    @field_validator("gemini_api_key")
    @classmethod
    def validate_api_key_not_empty(cls, v: str) -> str:
        """Ensure API key is not empty or whitespace-only."""
        if not v or not v.strip():
            raise ValueError("GEMINI_API_KEY is required and cannot be empty")
        return v.strip()
