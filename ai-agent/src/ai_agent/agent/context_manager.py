"""Context management for agent execution including token counting and history loading."""

import logging
import tiktoken
from datetime import datetime, timedelta
from typing import Any, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ai_agent.database.models import Conversation, Message

logger = logging.getLogger(__name__)


class ContextManager:
    """Manage agent execution context including token truncation.

    This class handles:
    - Token counting using tiktoken
    - Message history truncation to fit within token budget
    - System message preservation during truncation
    - Conversation history loading from database

    The truncation strategy keeps the most recent messages while always
    preserving system prompts, ensuring agent behavior remains consistent.
    """

    def __init__(self, encoding_name: str = "cl100k_base"):
        """Initialize ContextManager with token encoding.

        Args:
            encoding_name: Token encoding name for tiktoken (default: cl100k_base)
        """
        self.encoding = tiktoken.get_encoding(encoding_name)

    def count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken encoding.

        Args:
            text: Text to count tokens for

        Returns:
            Number of tokens in the text

        Example:
            >>> manager = ContextManager()
            >>> manager.count_tokens("Hello, world!")
            4
        """
        if not text:
            return 0
        return len(self.encoding.encode(text))

    def truncate_by_tokens(
        self,
        messages: list[dict[str, Any]],
        max_tokens: int
    ) -> list[dict[str, Any]]:
        """Truncate messages to fit within token budget, preserving system messages.

        This method implements a smart truncation strategy:
        1. Always preserve all system messages (contain agent instructions)
        2. Count tokens for system messages first
        3. Add other messages from newest to oldest until budget exhausted
        4. Return system messages + kept messages in chronological order

        Args:
            messages: List of messages in agent format
            max_tokens: Maximum token budget

        Returns:
            Truncated list of messages fitting within token budget

        Example:
            >>> messages = [
            ...     {"role": "system", "content": "You are helpful"},
            ...     {"role": "user", "content": "Old message" * 1000},
            ...     {"role": "user", "content": "Recent message"}
            ... ]
            >>> manager = ContextManager()
            >>> truncated = manager.truncate_by_tokens(messages, max_tokens=500)
            >>> # System message + recent message kept, old dropped
        """
        # Separate system messages (always keep)
        system_msgs = [m for m in messages if m.get("role") == "system"]
        other_msgs = [m for m in messages if m.get("role") != "system"]

        # Count system message tokens
        system_tokens = sum(self.count_tokens(str(m)) for m in system_msgs)
        available_tokens = max_tokens - system_tokens

        if available_tokens <= 0:
            # Only system messages fit
            return system_msgs

        # Add messages from newest to oldest until budget exhausted
        kept_msgs: list[dict[str, Any]] = []
        current_tokens = 0

        for msg in reversed(other_msgs):
            msg_tokens = self.count_tokens(str(msg))
            if current_tokens + msg_tokens <= available_tokens:
                kept_msgs.insert(0, msg)  # Insert at beginning to maintain order
                current_tokens += msg_tokens
            else:
                break

        # Return system messages + kept messages in chronological order
        return system_msgs + kept_msgs

    def _contains_task_references(self, content: str) -> bool:
        """Check if content contains task-specific references.

        Returns True if the message mentions tasks, task IDs, or task operations,
        indicating it should be removed to prevent stale data confusion.

        Args:
            content: Message content to check

        Returns:
            True if content mentions tasks, False otherwise
        """
        import re

        # Patterns that indicate task-specific content
        task_patterns = [
            r'\btask\s+\d+',           # "task 22", "Task 2"
            r'\(id\s*\d+\)',           # "(ID 2)"
            r'\bid\s*[:=]?\s*\d+',     # "ID: 22"
            r'found\s+\d+\s+task',     # "found 2 tasks"
            r'have\s+\d+\s+task',      # "you have 3 tasks"
            r'i\s+see\s+\d+\s+task',   # "I see two tasks"
            r'there\s+(is|are)\s+\d+\s+task',  # "there are 2 tasks"
            r'description:\s*"',       # Task descriptions
            r'priority:\s*(high|medium|low|urgent)',  # Task priorities
        ]

        content_lower = content.lower()
        for pattern in task_patterns:
            if re.search(pattern, content_lower):
                return True

        return False

    def _sanitize_task_references(self, content: str) -> str:
        """Remove specific task ID references from assistant messages.

        This prevents the AI from seeing outdated task data in conversation history.
        Keeps the general context but removes specific task IDs/details that may be stale.

        Args:
            content: Original message content

        Returns:
            Sanitized content with task-specific details removed
        """
        import re

        logger.debug(f"🔬 Sanitizing content (length={len(content)}): {content[:100]}...")

        # Comprehensive patterns to catch all task ID variations
        # These patterns are applied in order, each replacing matches with placeholders
        patterns_to_sanitize = [
            # Pattern 1: "Task 2:", "Task 22:", etc.
            (r'Task\s+\d+:', ''),

            # Pattern 2: "(ID 2)", "(ID 22)", etc.
            (r'\(ID\s+\d+\)', ''),

            # Pattern 3: "(Task 2)", "(Task 22)", etc.
            (r'\(Task\s+\d+\)', ''),

            # Pattern 4: "Task ID: 2", "Task ID=22", "task id 2", etc.
            (r'Task\s+ID\s*[:=]?\s*\d+', ''),

            # Pattern 5: "ID: 2", "ID 22", "id 2", etc. (standalone)
            (r'\bID\s*[:=]?\s*\d+\b', ''),

            # Pattern 6: "task with ID 2", etc.
            (r'task\s+with\s+ID\s+\d+', 'task'),

            # Pattern 7: "the task #2", "task #22", etc.
            (r'task\s*#\s*\d+', 'task'),
        ]

        sanitized = content
        for pattern, replacement in patterns_to_sanitize:
            sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)

        # Clean up extra whitespace caused by removals
        sanitized = re.sub(r'\s+', ' ', sanitized)
        sanitized = re.sub(r'\s+([.,!?])', r'\1', sanitized)  # Fix spacing before punctuation
        sanitized = sanitized.strip()

        if sanitized != content:
            logger.info(f"✂️ Sanitization changed content: {len(content)} → {len(sanitized)} chars")

        return sanitized

    async def load_conversation_history(
        self,
        conversation_id: int,
        user_id: str,
        session: AsyncSession,
        sanitize_task_refs: bool = True
    ) -> list[dict[str, Any]]:
        """Load conversation history from database with ownership validation.

        This method:
        1. Validates the conversation exists
        2. Validates user owns the conversation (security check)
        3. Loads messages in chronological order
        4. Converts database messages to agent message format
        5. Optionally sanitizes task-specific references to prevent stale data issues

        Args:
            conversation_id: ID of conversation to load
            user_id: ID of user requesting the history (for ownership check)
            session: Async database session
            sanitize_task_refs: If True, removes specific task IDs from assistant messages
                               to prevent AI from referencing deleted/outdated tasks (default: True)

        Returns:
            List of messages in agent format (role, content)

        Raises:
            ValueError: If conversation not found
            PermissionError: If user is not authorized to access conversation

        Example:
            >>> manager = ContextManager()
            >>> messages = await manager.load_conversation_history(
            ...     conversation_id=123,
            ...     user_id="user_abc",
            ...     session=db_session
            ... )
        """
        # Load conversation and validate ownership
        result = await session.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conversation = result.scalar_one_or_none()

        if conversation is None:
            raise ValueError(
                f"Conversation with ID {conversation_id} not found"
            )

        if conversation.user_id != user_id:
            raise PermissionError(
                f"User {user_id} is not authorized to access conversation {conversation_id}"
            )

        # Load messages in chronological order
        result = await session.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
        )
        db_messages = result.scalars().all()

        logger.info(f"🔍 load_conversation_history called: conv_id={conversation_id}, messages={len(db_messages)}, sanitize={sanitize_task_refs}")

        # Convert to agent message format
        agent_messages: list[dict[str, Any]] = []
        sanitized_count = 0
        removed_count = 0

        for msg in db_messages:
            content = msg.content

            # Remove assistant messages that mention tasks to prevent stale data confusion
            if sanitize_task_refs and msg.role == "assistant":
                # Check if message mentions task-specific information
                if self._contains_task_references(content):
                    removed_count += 1
                    logger.info(f"🗑️ Removed assistant message {msg.id}: contains task references")
                    continue  # Skip this message entirely

            agent_msg = {
                "role": msg.role,
                "content": content
            }
            # Include metadata if present (e.g., tool_calls)
            if msg.message_metadata:
                agent_msg.update(msg.message_metadata)
            agent_messages.append(agent_msg)

        if removed_count > 0:
            logger.info(
                f"Removed {removed_count} assistant messages containing task references from conversation {conversation_id}"
            )

        return agent_messages

    def store_task_list_context(self, task_list: list[dict[str, Any]]) -> dict[str, Any]:
        """Store task list metadata for ordinal reference resolution.

        Creates a position-to-ID mapping that allows users to reference tasks
        using ordinal positions like "first", "second", "last" in follow-up messages.

        Args:
            task_list: List of task dictionaries with 'id' field

        Returns:
            Metadata dictionary with task_context containing positions and timestamp

        Example:
            >>> manager = ContextManager()
            >>> tasks = [{"id": 1, "title": "Task 1"}, {"id": 2, "title": "Task 2"}]
            >>> metadata = manager.store_task_list_context(tasks)
            >>> # metadata = {"task_context": {"positions": {"1": 1, "2": 2}, "timestamp": "..."}}
        """
        positions = {str(i + 1): task["id"] for i, task in enumerate(task_list)}

        return {
            "task_context": {
                "positions": positions,
                "timestamp": datetime.now().isoformat(),
            }
        }

    def get_task_list_context(
        self,
        metadata: dict[str, Any],
        expiration_minutes: int = 5
    ) -> Optional[dict[str, Any]]:
        """Retrieve task context from metadata if not expired.

        Task context expires after a configurable time window (default 5 minutes)
        to prevent stale references in long conversations.

        Args:
            metadata: Message metadata containing task_context
            expiration_minutes: Context expiration time in minutes (default: 5)

        Returns:
            Task context dict if valid and not expired, None otherwise

        Example:
            >>> metadata = {"task_context": {"positions": {"1": 1}, "timestamp": "..."}}
            >>> context = manager.get_task_list_context(metadata)
            >>> if context:
            ...     print(context["positions"])
        """
        if "task_context" not in metadata:
            return None

        context = metadata["task_context"]

        # Check expiration
        try:
            timestamp = datetime.fromisoformat(context["timestamp"])
            now = datetime.now()
            age = now - timestamp

            if age > timedelta(minutes=expiration_minutes):
                return None  # Context expired

            return context
        except (KeyError, ValueError):
            return None  # Invalid context

    def resolve_ordinal_reference(
        self,
        reference: str,
        context: dict[str, Any]
    ) -> Optional[int]:
        """Resolve ordinal reference to task ID using stored context.

        Supports:
        - Numeric positions: "1", "2", "3", etc.
        - Ordinal words: "first", "second", "third", etc.
        - Special: "last" for the highest position

        Args:
            reference: Ordinal reference string (e.g., "first", "2", "last")
            context: Task context with positions mapping

        Returns:
            Task ID if reference is valid, None otherwise

        Example:
            >>> context = {"positions": {"1": 10, "2": 20, "3": 30}}
            >>> manager.resolve_ordinal_reference("first", context)
            10
            >>> manager.resolve_ordinal_reference("last", context)
            30
        """
        if "positions" not in context:
            return None

        positions = context["positions"]
        reference_lower = reference.lower()

        # Map ordinal words to numeric positions
        ordinal_map = {
            "first": "1",
            "second": "2",
            "third": "3",
            "fourth": "4",
            "fifth": "5",
            "sixth": "6",
            "seventh": "7",
            "eighth": "8",
            "ninth": "9",
            "tenth": "10",
        }

        # Handle "last" special case
        if reference_lower == "last":
            if not positions:
                return None
            max_position = max(int(p) for p in positions.keys())
            return positions.get(str(max_position))

        # Convert ordinal word to numeric
        if reference_lower in ordinal_map:
            position = ordinal_map[reference_lower]
        else:
            # Assume it's already a numeric position
            position = reference

        return positions.get(position)
