"""Message conversion between database models and agent format."""

from typing import Any, TypedDict


class MessageConverter:
    """Convert between database Message models and agent-compatible format.

    This class handles the conversion of Message models from the database
    (spec 007) to the format expected by the OpenAI Agents SDK.

    The agent format follows the OpenAI message structure:
    {
        "role": "user" | "assistant" | "system" | "tool",
        "content": str,
        "tool_calls": Optional[List[Dict]] # If agent made MCP tool calls
    }
    """

    def db_to_agent(self, db_message: Any) -> dict[str, Any]:
        """Convert database Message to agent-compatible format.

        Args:
            db_message: Message model from database (spec 007)

        Returns:
            Dictionary in OpenAI Agents SDK message format

        Example:
            >>> msg = Message(role="user", content="Show tasks", metadata=None)
            >>> converter = MessageConverter()
            >>> agent_msg = converter.db_to_agent(msg)
            >>> agent_msg
            {"role": "user", "content": "Show tasks"}
        """
        # Basic message structure
        agent_msg: dict[str, Any] = {
            "role": db_message.role,
            "content": db_message.content,
        }

        # Preserve tool calls from message_metadata if present
        if db_message.message_metadata and "tool_calls" in db_message.message_metadata:
            agent_msg["tool_calls"] = db_message.message_metadata["tool_calls"]

        return agent_msg

    def db_messages_to_agent_batch(self, db_messages: list[Any]) -> list[dict[str, Any]]:
        """Convert list of database messages to agent format.

        Args:
            db_messages: List of Message models from database

        Returns:
            List of dictionaries in agent format

        Example:
            >>> messages = [
            ...     Message(role="user", content="Hello"),
            ...     Message(role="assistant", content="Hi!")
            ... ]
            >>> converter = MessageConverter()
            >>> agent_messages = converter.db_messages_to_agent_batch(messages)
            >>> len(agent_messages)
            2
        """
        return [self.db_to_agent(msg) for msg in db_messages]
