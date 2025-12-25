"""Unit tests for rate limiting service."""

import pytest
from datetime import datetime, timedelta
from src.services.rate_limiter import RateLimiter, RateLimitRecord


class TestRateLimitRecord:
    """Tests for RateLimitRecord dataclass."""

    def test_initial_state(self):
        """Test initial state of RateLimitRecord."""
        record = RateLimitRecord()
        assert record.attempts == 0
        assert isinstance(record.window_start, datetime)

    def test_reset(self):
        """Test reset method."""
        record = RateLimitRecord(attempts=5)
        old_start = record.window_start

        # Wait a tiny bit to ensure timestamp changes
        import time
        time.sleep(0.01)

        record.reset()

        assert record.attempts == 0
        assert record.window_start > old_start


class TestRateLimiter:
    """Tests for RateLimiter service."""

    def test_initialization(self):
        """Test RateLimiter initialization."""
        limiter = RateLimiter(max_requests=5, window_minutes=60)
        assert limiter.max_requests == 5
        assert limiter.window_minutes == 60
        assert limiter._records == {}

    def test_first_request_allowed(self):
        """Test that first request is always allowed."""
        limiter = RateLimiter(max_requests=5, window_minutes=60)
        user_id = "test-user-123"

        is_allowed, remaining, window_end = limiter.check_rate_limit(user_id)

        assert is_allowed is True
        assert remaining == 4  # 5 max - 1 used = 4 remaining
        assert isinstance(window_end, datetime)

    def test_within_limit(self):
        """Test requests within the rate limit."""
        limiter = RateLimiter(max_requests=5, window_minutes=60)
        user_id = "test-user-123"

        # Make 5 requests (the limit)
        for i in range(5):
            is_allowed, remaining, window_end = limiter.check_rate_limit(user_id)
            assert is_allowed is True
            assert remaining == 4 - i

    def test_exceed_limit(self):
        """Test that exceeding limit blocks requests."""
        limiter = RateLimiter(max_requests=5, window_minutes=60)
        user_id = "test-user-123"

        # Make 5 requests (the limit)
        for _ in range(5):
            limiter.check_rate_limit(user_id)

        # 6th request should be blocked
        is_allowed, remaining, window_end = limiter.check_rate_limit(user_id)

        assert is_allowed is False
        assert remaining == 0
        assert isinstance(window_end, datetime)

    def test_window_reset(self):
        """Test that window resets after expiration."""
        # Use 1 second window for testing
        limiter = RateLimiter(max_requests=2, window_minutes=0.0167)  # ~1 second
        user_id = "test-user-123"

        # Make 2 requests (the limit)
        limiter.check_rate_limit(user_id)
        limiter.check_rate_limit(user_id)

        # 3rd request should be blocked
        is_allowed, _, _ = limiter.check_rate_limit(user_id)
        assert is_allowed is False

        # Wait for window to expire
        import time
        time.sleep(1.1)

        # Next request should be allowed (new window)
        is_allowed, remaining, _ = limiter.check_rate_limit(user_id)
        assert is_allowed is True
        assert remaining == 1  # Fresh window, 1 used

    def test_different_users(self):
        """Test that rate limits are per-user."""
        limiter = RateLimiter(max_requests=2, window_minutes=60)

        user1 = "user-1"
        user2 = "user-2"

        # User 1 makes 2 requests (the limit)
        limiter.check_rate_limit(user1)
        limiter.check_rate_limit(user1)

        # User 1 should be blocked
        is_allowed, _, _ = limiter.check_rate_limit(user1)
        assert is_allowed is False

        # User 2 should still be allowed
        is_allowed, remaining, _ = limiter.check_rate_limit(user2)
        assert is_allowed is True
        assert remaining == 1

    def test_get_status_no_record(self):
        """Test get_status for user with no record."""
        limiter = RateLimiter(max_requests=5, window_minutes=60)
        user_id = "new-user"

        attempts, max_requests, window_end = limiter.get_status(user_id)

        assert attempts == 0
        assert max_requests == 5
        assert isinstance(window_end, datetime)

    def test_get_status_with_record(self):
        """Test get_status for user with existing record."""
        limiter = RateLimiter(max_requests=5, window_minutes=60)
        user_id = "test-user"

        # Make 3 requests
        for _ in range(3):
            limiter.check_rate_limit(user_id)

        attempts, max_requests, window_end = limiter.get_status(user_id)

        assert attempts == 3
        assert max_requests == 5
        assert isinstance(window_end, datetime)

    def test_get_status_expired_window(self):
        """Test get_status for expired window."""
        # Use 1 second window
        limiter = RateLimiter(max_requests=5, window_minutes=0.0167)
        user_id = "test-user"

        # Make 3 requests
        for _ in range(3):
            limiter.check_rate_limit(user_id)

        # Wait for window to expire
        import time
        time.sleep(1.1)

        attempts, max_requests, window_end = limiter.get_status(user_id)

        # Window expired, should show 0 attempts
        assert attempts == 0
        assert max_requests == 5
        assert isinstance(window_end, datetime)


class TestApiKeyTestLimiter:
    """Tests for the global api_key_test_limiter instance."""

    def test_limiter_configuration(self):
        """Test that global limiter is configured correctly."""
        from src.services.rate_limiter import api_key_test_limiter

        assert api_key_test_limiter.max_requests == 5
        assert api_key_test_limiter.window_minutes == 60
