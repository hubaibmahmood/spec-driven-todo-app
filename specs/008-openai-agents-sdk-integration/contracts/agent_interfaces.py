"""
Agent System Interface Contracts

This file defines the Python interface contracts (protocols/abstract classes)
for the agent system components. These serve as the contract layer between
modules and guide TDD test development.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Protocol
from datetime import datetime
from pydantic import BaseModel


# ============================================================================
# Configuration Contracts
# ============================================================================

class IAgentConfig(Protocol):
    """Configuration interface for agent initialization."""

    gemini_api_key: str
    mcp_server_url: str
    mcp_timeout: int
    mcp_retry_attempts: int
    system_prompt: str
    temperature: float
    token_budget: int
    encoding_name: str


# ============================================================================
# Message Conversion Contracts
# ============================================================================

class AgentMessage(BaseModel):
    """Standard agent message format (OpenAI Agents SDK compatible)."""

    role: str  # "user" | "assistant" | "system" | "tool"
    content: str
    tool_calls: Optional[List[Dict[str, Any]]] = None

    class Config:
        extra = "forbid"  # Strict validation


class IMessageConverter(ABC):
    """Interface for converting between database and agent message formats."""

    @abstractmethod
    def db_to_agent(self, db_message: Any) -> AgentMessage:
        """Convert database Message model to AgentMessage format.

        Args:
            db_message: SQLAlchemy Message model instance

        Returns:
            AgentMessage compatible with OpenAI Agents SDK

        Raises:
            ValueError: If message format invalid
        """
        pass

    @abstractmethod
    def db_messages_to_agent_batch(self, db_messages: List[Any]) -> List[AgentMessage]:
        """Convert list of database messages to agent format.

        Args:
            db_messages: List of SQLAlchemy Message model instances

        Returns:
            List of AgentMessages ordered by created_at ascending
        """
        pass


# ============================================================================
# Context Management Contracts
# ============================================================================

class AgentContext(BaseModel):
    """Execution context for agent request."""

    user_id: str
    conversation_id: Optional[int]
    user_message: str
    conversation_history: List[AgentMessage]
    config: Dict[str, Any]  # AgentConfig as dict for serialization

    class Config:
        extra = "forbid"


class IContextManager(ABC):
    """Interface for managing agent execution context."""

    @abstractmethod
    async def load_conversation_history(
        self,
        conversation_id: int,
        user_id: str
    ) -> List[AgentMessage]:
        """Load and convert conversation history from database.

        Args:
            conversation_id: Database conversation ID
            user_id: User ID for authorization check

        Returns:
            List of AgentMessages in chronological order

        Raises:
            PermissionError: If user doesn't own conversation
            NotFoundError: If conversation doesn't exist
        """
        pass

    @abstractmethod
    def truncate_by_tokens(
        self,
        messages: List[AgentMessage],
        max_tokens: int
    ) -> List[AgentMessage]:
        """Truncate messages to fit within token budget.

        Strategy: Keep system messages + most recent messages that fit.

        Args:
            messages: Full message history
            max_tokens: Token budget (e.g., 800,000)

        Returns:
            Truncated message list preserving system prompts
        """
        pass

    @abstractmethod
    async def create_context(
        self,
        user_id: str,
        user_message: str,
        conversation_id: Optional[int] = None
    ) -> AgentContext:
        """Create complete agent execution context.

        Args:
            user_id: Authenticated user ID
            user_message: Current user input
            conversation_id: Optional conversation ID for history

        Returns:
            AgentContext ready for agent execution
        """
        pass


# ============================================================================
# MCP Connection Contracts
# ============================================================================

class IMCPConnection(ABC):
    """Interface for MCP server connection management."""

    @abstractmethod
    async def __aenter__(self):
        """Establish MCP server connection (async context manager entry).

        Returns:
            MCPServerStreamableHttp instance

        Raises:
            ConnectionError: If MCP server unreachable
        """
        pass

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close MCP server connection (async context manager exit)."""
        pass

    @abstractmethod
    async def create_connection(self, user_id: str, config: IAgentConfig):
        """Create MCP server connection with user authentication.

        Args:
            user_id: User ID for X-User-ID header
            config: Agent configuration with MCP server URL

        Returns:
            MCPServerStreamableHttp instance

        Raises:
            ConnectionError: If connection fails
            ConfigurationError: If MCP URL invalid
        """
        pass


# ============================================================================
# Agent Service Contracts
# ============================================================================

class AgentResult(BaseModel):
    """Result from successful agent execution."""

    response_text: str
    tool_calls_made: List[Dict[str, Any]]
    tokens_used: int
    model: str
    execution_time_ms: int

    class Config:
        extra = "forbid"


class AgentExecutionError(BaseModel):
    """Error information when agent execution fails."""

    error_type: str  # "gemini_api_error" | "mcp_connection_error" | "unknown_error"
    error_message: str
    user_facing_message: str
    timestamp: datetime

    class Config:
        extra = "forbid"


class IAgentService(ABC):
    """Interface for agent orchestration and execution."""

    @abstractmethod
    async def initialize_agent(
        self,
        config: IAgentConfig,
        mcp_server: Any  # MCPServerStreamableHttp instance
    ) -> Any:  # Agent instance
        """Initialize OpenAI Agent with Gemini model and MCP server.

        Args:
            config: Agent configuration
            mcp_server: Connected MCP server instance

        Returns:
            Initialized Agent instance

        Raises:
            ConfigurationError: If configuration invalid
        """
        pass

    @abstractmethod
    async def run_agent(
        self,
        agent: Any,
        user_message: str,
        conversation_history: List[AgentMessage]
    ) -> AgentResult:
        """Execute agent with user message and conversation context.

        Args:
            agent: Initialized Agent instance
            user_message: Current user input
            conversation_history: Token-truncated message history

        Returns:
            AgentResult with response and metadata

        Raises:
            GeminiAPIError: If Gemini API call fails
            MCPToolError: If MCP tool execution fails
        """
        pass

    @abstractmethod
    async def run_agent_with_context(
        self,
        context: AgentContext
    ) -> AgentResult:
        """High-level agent execution with full context management.

        This is the main entry point for agent execution. It:
        1. Creates Gemini client
        2. Establishes MCP connection
        3. Initializes agent
        4. Runs agent with context
        5. Returns result

        Args:
            context: AgentContext with user message and history

        Returns:
            AgentResult with response and metadata

        Raises:
            AgentExecutionError: For any execution failure
        """
        pass


# ============================================================================
# Persistence Contracts
# ============================================================================

class IConversationService(Protocol):
    """Interface for conversation persistence operations.

    Note: This interface exists in spec 007. Documented here for reference.
    """

    async def get_or_create(
        self,
        user_id: str,
        conversation_id: Optional[int] = None
    ) -> Any:  # Conversation model
        """Get existing conversation or create new one."""
        pass

    async def get_messages(self, conversation_id: int) -> List[Any]:  # List[Message]
        """Load all messages for a conversation."""
        pass

    async def save_message(
        self,
        conversation_id: int,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Any:  # Message model
        """Save new message to conversation."""
        pass


# ============================================================================
# Error Types
# ============================================================================

class ConfigurationError(Exception):
    """Raised when agent configuration is invalid."""
    pass


class GeminiAPIError(Exception):
    """Raised when Gemini API call fails."""
    pass


class MCPConnectionError(Exception):
    """Raised when MCP server connection fails."""
    pass


class MCPToolError(Exception):
    """Raised when MCP tool execution fails."""
    pass


class TokenBudgetExceededError(Exception):
    """Raised when message history exceeds token budget after truncation."""
    pass


class ConversationNotFoundError(Exception):
    """Raised when conversation ID doesn't exist."""
    pass


class UnauthorizedConversationAccessError(Exception):
    """Raised when user tries to access conversation they don't own."""
    pass
