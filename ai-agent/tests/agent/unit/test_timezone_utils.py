"""Unit tests for timezone utilities."""

import pytest
from datetime import datetime
from zoneinfo import ZoneInfo


def test_extract_timezone_from_header_valid():
    """Unit: Extract valid timezone from X-Timezone header."""
    from ai_agent.agent.timezone_utils import extract_timezone

    # Test valid IANA timezone
    result = extract_timezone("America/New_York")
    assert result == "America/New_York"

    # Test another valid timezone
    result = extract_timezone("Asia/Tokyo")
    assert result == "Asia/Tokyo"

    # Test UTC
    result = extract_timezone("UTC")
    assert result == "UTC"


def test_extract_timezone_missing_header_fallback_to_utc():
    """Unit: When X-Timezone header is missing, fallback to UTC."""
    from ai_agent.agent.timezone_utils import extract_timezone

    # None should fallback to UTC
    result = extract_timezone(None)
    assert result == "UTC"

    # Empty string should fallback to UTC
    result = extract_timezone("")
    assert result == "UTC"


def test_extract_timezone_invalid_iana_fallback_to_utc():
    """Unit: Invalid IANA timezone should fallback to UTC."""
    from ai_agent.agent.timezone_utils import extract_timezone

    # Invalid timezone string
    result = extract_timezone("Invalid/Timezone")
    assert result == "UTC"

    # Random string
    result = extract_timezone("not_a_timezone")
    assert result == "UTC"


def test_extract_timezone_validates_iana_format():
    """Unit: Timezone extraction validates IANA timezone format."""
    from ai_agent.agent.timezone_utils import extract_timezone

    # Valid formats
    assert extract_timezone("Europe/London") == "Europe/London"
    assert extract_timezone("America/Los_Angeles") == "America/Los_Angeles"
    assert extract_timezone("Australia/Sydney") == "Australia/Sydney"

    # Invalid formats should fallback to UTC
    assert extract_timezone("EST") == "UTC"  # Abbreviation, not IANA
    assert extract_timezone("GMT+5") == "UTC"  # Offset notation
    assert extract_timezone("12345") == "UTC"  # Numbers


def test_get_current_time_in_timezone_utc():
    """Unit: Get current time in UTC timezone."""
    from ai_agent.agent.timezone_utils import get_current_time_in_timezone

    result = get_current_time_in_timezone("UTC")

    # Should return a formatted string with timezone
    assert isinstance(result, str)
    assert "UTC" in result
    # Should be in ISO format or readable format
    assert len(result) > 0


def test_get_current_time_in_timezone_specific():
    """Unit: Get current time in specific timezone."""
    from ai_agent.agent.timezone_utils import get_current_time_in_timezone

    # Test with New York timezone
    result = get_current_time_in_timezone("America/New_York")
    assert isinstance(result, str)
    assert "America/New_York" in result or "EST" in result or "EDT" in result

    # Test with Tokyo timezone
    result = get_current_time_in_timezone("Asia/Tokyo")
    assert isinstance(result, str)
    assert "Asia/Tokyo" in result or "JST" in result


def test_get_current_time_in_timezone_invalid_fallback():
    """Unit: Invalid timezone in get_current_time should fallback to UTC."""
    from ai_agent.agent.timezone_utils import get_current_time_in_timezone

    result = get_current_time_in_timezone("Invalid/Timezone")
    assert isinstance(result, str)
    assert "UTC" in result


def test_timezone_resolution_priority_order():
    """Unit: Timezone resolution follows priority: header > UTC fallback."""
    from ai_agent.agent.timezone_utils import extract_timezone

    # Priority 1: Valid header value
    assert extract_timezone("Europe/Paris") == "Europe/Paris"

    # Priority 2: UTC fallback when header is None
    assert extract_timezone(None) == "UTC"

    # Priority 2: UTC fallback when header is empty
    assert extract_timezone("") == "UTC"

    # Priority 2: UTC fallback when header is invalid
    assert extract_timezone("BadTimezone") == "UTC"
