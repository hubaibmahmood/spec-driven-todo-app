"""Agent service for orchestrating OpenAI Agent with Gemini backend."""

import logging
import time
from typing import Any, Dict, List

import tiktoken
from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel, RunConfig, Runner
from pydantic import BaseModel, ConfigDict

from ai_agent.agent.config import AgentConfig
from ai_agent.agent.mcp_connection import create_mcp_connection
from ai_agent.agent.message_converter import MessageConverter
from ai_agent.agent.timezone_utils import get_current_time_in_timezone
from ai_agent.database.models import Message

logger = logging.getLogger(__name__)


class AgentResult(BaseModel):
    """Result from agent execution."""

    model_config = ConfigDict(frozen=True)  # Immutable result

    response_text: str
    execution_time_ms: int
    tokens_used: int
    tool_calls_made: List[Dict[str, Any]]
    model: str


class AgentService:
    """Service for initializing and executing OpenAI Agent with Gemini."""

    def __init__(self, config: AgentConfig):
        """
        Initialize AgentService with configuration.

        Args:
            config: Agent configuration containing Gemini API key and settings
        """
        self.config = config

    def create_gemini_client(self) -> AsyncOpenAI:
        """
        Create AsyncOpenAI client configured for Gemini API.

        Returns:
            AsyncOpenAI client pointing to Gemini's OpenAI-compatible endpoint

        Examples:
            >>> config = AgentConfig(gemini_api_key="test_key")
            >>> service = AgentService(config)
            >>> client = service.create_gemini_client()
            >>> assert "generativelanguage.googleapis.com" in client.base_url.host
        """
        return AsyncOpenAI(
            api_key=self.config.gemini_api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        )

    def create_run_config(self) -> RunConfig:
        """
        Create RunConfig with Gemini model configuration.

        Returns:
            RunConfig configured for Gemini API execution

        Examples:
            >>> config = AgentConfig(gemini_api_key="test_key")
            >>> service = AgentService(config)
            >>> run_config = service.create_run_config()
            >>> assert run_config.tracing_disabled is True
        """
        # Create Gemini client
        external_client = self.create_gemini_client()

        # Configure OpenAI Chat Completions model with Gemini
        model = OpenAIChatCompletionsModel(model="gemini-2.5-flash", openai_client=external_client)

        # Configure run settings
        return RunConfig(
            model=model,
            model_provider=external_client,
            tracing_disabled=True,  # Disable tracing for MVP
        )

    async def initialize_agent(self, mcp_server) -> Agent:
        """
        Initialize OpenAI Agent with MCP server.

        Args:
            mcp_server: Connected MCP server instance (MCPServerStreamableHttp)

        Returns:
            Initialized Agent instance with MCP tools

        Examples:
            >>> config = AgentConfig(gemini_api_key="test_key")
            >>> service = AgentService(config)
            >>> agent = await service.initialize_agent(mock_mcp_server)
            >>> assert agent.name == "Todo Assistant"
            >>> assert len(agent.mcp_servers) == 1
        """
        # Create agent with MCP server and instructions
        # Note: RunConfig is NOT passed to Agent, it's used with Runner.run()
        agent = Agent(
            name="Todo Assistant",
            instructions=self.config.system_prompt,
            mcp_servers=[mcp_server],
        )

        return agent

    async def run_agent(
        self, agent: Agent, user_message: str, conversation_history: List[Dict[str, Any]]
    ) -> AgentResult:
        """
        Execute agent with user message and conversation history.

        Args:
            agent: Initialized Agent instance
            user_message: Current user message
            conversation_history: List of previous messages in agent format

        Returns:
            AgentResult with response_text, execution_time_ms, tokens_used, tool_calls_made

        Examples:
            >>> agent = await service.initialize_agent(mcp_server)
            >>> result = await service.run_agent(agent, "show my tasks", [])
            >>> assert result.response_text
            >>> assert result.execution_time_ms >= 0
        """
        # Track execution time
        start_time = time.time()

        # Prepare messages: history + new user message
        messages = conversation_history.copy()
        messages.append({"role": "user", "content": user_message})

        # Get run configuration
        run_config = self.create_run_config()

        # Execute agent with Runner.run()
        result = await Runner.run(agent, input=messages, run_config=run_config)

        # Calculate execution time in milliseconds
        execution_time_ms = int((time.time() - start_time) * 1000)

        # Extract tool calls from result messages
        tool_calls_made = self._extract_tool_calls(result.new_items)

        # Count tokens in final conversation
        tokens_used = result.context_wrapper.usage.total_tokens

        return AgentResult(
            response_text=result.final_output,
            execution_time_ms=execution_time_ms,
            tokens_used=tokens_used,
            tool_calls_made=tool_calls_made,
            model="gemini-2.5-flash",
        )

    def _extract_tool_calls(self, messages: List[Any]) -> List[Dict[str, Any]]:
        """
        Extract tool calls from agent result messages.

        Args:
            messages: List of messages (dicts or objects) from agent execution

        Returns:
            List of tool call dictionaries
        """
        tool_calls = []

        for message in messages:
            # Handle both dicts (history) and objects (result.new_items)
            if isinstance(message, dict):
                role = message.get("role")
                msg_tool_calls = message.get("tool_calls", [])
            else:
                role = getattr(message, "role", None)
                msg_tool_calls = getattr(message, "tool_calls", [])

            if role == "assistant" and msg_tool_calls:
                # Extract tool call information
                for tool_call in msg_tool_calls:
                    # Tool call might be dict or object
                    if isinstance(tool_call, dict):
                         tc_id = tool_call.get("id")
                         tc_type = tool_call.get("type")
                         func = tool_call.get("function", {})
                         func_name = func.get("name")
                         func_args = func.get("arguments")
                    else:
                         tc_id = getattr(tool_call, "id", None)
                         tc_type = getattr(tool_call, "type", None)
                         func = getattr(tool_call, "function", None)
                         func_name = getattr(func, "name", None) if func else None
                         func_args = getattr(func, "arguments", None) if func else None

                    tool_calls.append(
                        {
                            "id": tc_id,
                            "type": tc_type,
                            "function": {
                                "name": func_name,
                                "arguments": func_args,
                            },
                        }
                    )

        return tool_calls

    def _count_tokens(self, messages: List[Any]) -> int:
        """
        Count tokens in message list using tiktoken.

        Args:
            messages: List of messages to count

        Returns:
            Total token count
        """
        try:
            encoding = tiktoken.get_encoding(self.config.encoding_name)
            total_tokens = 0

            for message in messages:
                # Handle both dicts and objects
                if isinstance(message, dict):
                    content = message.get("content")
                    msg_tool_calls = message.get("tool_calls", [])
                else:
                    content = getattr(message, "content", None)
                    msg_tool_calls = getattr(message, "tool_calls", [])

                # Count tokens in content
                if content and isinstance(content, str):
                    total_tokens += len(encoding.encode(content))

                # Count tokens in tool calls if present
                if msg_tool_calls:
                    for tool_call in msg_tool_calls:
                        if isinstance(tool_call, dict):
                            func = tool_call.get("function", {})
                            name = func.get("name")
                            args = func.get("arguments")
                        else:
                            func = getattr(tool_call, "function", None)
                            name = getattr(func, "name", None) if func else None
                            args = getattr(func, "arguments", None) if func else None

                        if name:
                            total_tokens += len(encoding.encode(name))
                        if args:
                            total_tokens += len(encoding.encode(args))

            return total_tokens

        except Exception:
            # Fallback if token counting fails
            return 0

    async def run_agent_with_context(
        self,
        user_id: str,
        user_message: str,
        conversation_history: List[Message],
        user_timezone: str = "UTC",
    ) -> AgentResult:
        """
        Orchestrate agent execution with full context management.

        Args:
            user_id: User ID for MCP authentication
            user_message: Current user message
            conversation_history: List of DB Message objects
            user_timezone: IANA timezone string (e.g., "America/New_York")

        Returns:
            AgentResult with response and metadata

        Raises:
            Exception: On Gemini API or MCP connection errors
        """
        logger.info(f"Starting agent execution for user {user_id} with timezone {user_timezone}")

        try:
            # Create MCP connection with user authentication
            async with create_mcp_connection(self.config, user_id) as mcp_server:
                logger.debug(f"MCP connection established for user {user_id}")

                # Initialize agent with MCP server
                agent = await self.initialize_agent(mcp_server)

                # Enhance system prompt with timezone context
                current_time = get_current_time_in_timezone(user_timezone)
                enhanced_instructions = f"""{agent.instructions}

Current time in user's timezone: {current_time}

When parsing dates/times from user input:
- Use the timezone: {user_timezone}
- "today" means today in {user_timezone}
- "tomorrow" means tomorrow in {user_timezone}
- "EOD" (end of day) means 23:59:59 in {user_timezone}
- Always convert to UTC before storing

Priority mapping:
- "urgent", "critical", "asap" → Priority.URGENT
- "high", "important" → Priority.HIGH
- "normal", "medium" → Priority.MEDIUM
- "low" → Priority.LOW
"""
                agent.instructions = enhanced_instructions

                # Convert DB messages to agent format if necessary
                if conversation_history and isinstance(conversation_history[0], dict):
                    agent_messages = conversation_history
                else:
                    converter = MessageConverter()
                    agent_messages = converter.db_messages_to_agent_batch(conversation_history)

                logger.debug(f"Executing agent with {len(agent_messages)} history messages")

                # Execute agent
                result = await self.run_agent(
                    agent=agent, user_message=user_message, conversation_history=agent_messages
                )

                logger.info(
                    f"Agent execution completed for user {user_id}: {result.execution_time_ms}ms, {result.tokens_used} tokens"
                )

                return result

        except Exception as e:
            logger.error(f"Agent execution failed for user {user_id}: {e}", exc_info=True)
            raise
