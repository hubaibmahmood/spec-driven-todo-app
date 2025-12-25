"""Rate limiting service for API endpoints."""

import logging
from datetime import datetime, timedelta, UTC
from typing import Dict, Tuple
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class RateLimitRecord:
    """Record of rate limit attempts for a user."""
    attempts: int = 0
    window_start: datetime = field(default_factory=lambda: datetime.now(UTC))

    def reset(self):
        """Reset the rate limit record."""
        self.attempts = 0
        self.window_start = datetime.now(UTC)


class RateLimiter:
    """
    In-memory rate limiter for API endpoints.

    NOTE: This is a simple in-memory implementation. For production with multiple
    instances, consider using Redis or a distributed cache.
    """

    def __init__(self, max_requests: int, window_minutes: int):
        """
        Initialize rate limiter.

        Args:
            max_requests: Maximum number of requests allowed in the time window
            window_minutes: Time window in minutes
        """
        self.max_requests = max_requests
        self.window_minutes = window_minutes
        self._records: Dict[str, RateLimitRecord] = {}

    def check_rate_limit(self, user_id: str) -> Tuple[bool, int, datetime]:
        """
        Check if user has exceeded rate limit.

        Args:
            user_id: User identifier

        Returns:
            Tuple of (is_allowed, remaining_attempts, window_reset_time)
        """
        now = datetime.now(UTC)

        # Get or create record for this user
        if user_id not in self._records:
            self._records[user_id] = RateLimitRecord()

        record = self._records[user_id]
        window_end = record.window_start + timedelta(minutes=self.window_minutes)

        # Check if we're still in the current window
        if now < window_end:
            # Still in current window - check if limit exceeded
            if record.attempts >= self.max_requests:
                remaining = 0
                is_allowed = False
                logger.warning(
                    f"Rate limit exceeded - user_id={user_id[:8]}... "
                    f"attempts={record.attempts}/{self.max_requests} "
                    f"window_reset={window_end.isoformat()}"
                )
            else:
                # Increment attempt counter
                record.attempts += 1
                remaining = self.max_requests - record.attempts
                is_allowed = True
                logger.debug(
                    f"Rate limit check passed - user_id={user_id[:8]}... "
                    f"attempts={record.attempts}/{self.max_requests}"
                )
        else:
            # Window has expired - reset and allow
            record.reset()
            record.attempts = 1
            remaining = self.max_requests - 1
            is_allowed = True
            window_end = record.window_start + timedelta(minutes=self.window_minutes)
            logger.debug(
                f"Rate limit window reset - user_id={user_id[:8]}... "
                f"new_window_end={window_end.isoformat()}"
            )

        return is_allowed, remaining, window_end

    def get_status(self, user_id: str) -> Tuple[int, int, datetime]:
        """
        Get current rate limit status for a user.

        Args:
            user_id: User identifier

        Returns:
            Tuple of (current_attempts, max_requests, window_reset_time)
        """
        now = datetime.now(UTC)

        if user_id not in self._records:
            # No record yet - return fresh window
            window_end = now + timedelta(minutes=self.window_minutes)
            return 0, self.max_requests, window_end

        record = self._records[user_id]
        window_end = record.window_start + timedelta(minutes=self.window_minutes)

        # Check if window has expired
        if now >= window_end:
            return 0, self.max_requests, now + timedelta(minutes=self.window_minutes)

        return record.attempts, self.max_requests, window_end


# Global rate limiter instance for API key testing
# 5 requests per hour (60 minutes)
api_key_test_limiter = RateLimiter(max_requests=5, window_minutes=60)
