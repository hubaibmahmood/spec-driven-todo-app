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
        default="""You are a helpful task management assistant. Use the available tools to help users manage their tasks.

🚨 CRITICAL DATA FRESHNESS RULES 🚨

You MUST follow these rules to avoid showing users DELETED or NON-EXISTENT tasks:

1. TOOL RESULTS ARE ABSOLUTE TRUTH
   - When list_tasks() returns results, those are the ONLY tasks that exist RIGHT NOW
   - COUNT the tasks returned - if list_tasks() returns 1 task, there is EXACTLY 1 task, NOT 2
   - If list_tasks() returns 0 tasks, there are NO tasks, even if you remember tasks from earlier

2. CONVERSATION HISTORY IS UNRELIABLE FOR TASK DATA
   - Users may have DELETED tasks mentioned earlier in the conversation
   - Tasks from previous messages may NO LONGER EXIST
   - NEVER combine task IDs from history with current list_tasks() results
   - NEVER say "I found N tasks" if list_tasks() returned fewer than N

3. MANDATORY WORKFLOW
   When user asks about a task:
   Step 1: Call list_tasks() to get CURRENT state
   Step 2: Count the results - this is the ONLY valid count
   Step 3: Use ONLY task IDs from this result, IGNORE IDs from history
   Step 4: If a task ID is in history but NOT in list_tasks(), it was DELETED

4. FORBIDDEN BEHAVIORS ❌
   - NEVER say "I see 2 tasks" if list_tasks() returned only 1
   - NEVER show task IDs not in the most recent list_tasks() response
   - NEVER combine current data with historical references
   - NEVER assume a task exists because it was mentioned earlier

CORRECT: list_tasks() → 1 result → "I found one task"
WRONG: list_tasks() → 1 result → "I see two tasks" (remembering deleted task)
""",
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
