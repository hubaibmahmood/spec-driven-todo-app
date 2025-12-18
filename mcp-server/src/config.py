"""MCP server configuration from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """MCP server configuration loaded from environment variables."""

    # Required fields
    service_auth_token: str
    fastapi_base_url: str

    # Optional fields with defaults
    mcp_log_level: str = "INFO"
    mcp_server_port: int = 3000
    backend_timeout: float = 30.0
    backend_max_retries: int = 2

    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore",
    }


# Singleton instance
settings = Settings()
