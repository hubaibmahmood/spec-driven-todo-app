"""Timezone utilities for handling user timezone context."""

from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


def extract_timezone(timezone_header: str | None) -> str:
    """
    Extract and validate timezone from X-Timezone header.

    Priority order:
    1. Valid IANA timezone from header
    2. UTC fallback for invalid/missing header

    Args:
        timezone_header: Value from X-Timezone header (e.g., "America/New_York")

    Returns:
        Valid IANA timezone string (e.g., "America/New_York") or "UTC" as fallback

    Examples:
        >>> extract_timezone("America/New_York")
        "America/New_York"
        >>> extract_timezone(None)
        "UTC"
        >>> extract_timezone("Invalid/Timezone")
        "UTC"
    """
    # Handle missing or empty header
    if not timezone_header:
        return "UTC"

    # Only accept standard IANA format (Region/City or UTC)
    # Reject abbreviations (EST, PST) and offset notations (GMT+5)
    if timezone_header != "UTC" and "/" not in timezone_header:
        return "UTC"

    # Validate IANA timezone format using zoneinfo
    try:
        # Attempt to load the timezone to verify it's valid
        ZoneInfo(timezone_header)
        return timezone_header
    except ZoneInfoNotFoundError:
        # Invalid timezone, fallback to UTC
        return "UTC"
    except Exception:
        # Any other error, fallback to UTC
        return "UTC"


def get_current_time_in_timezone(timezone: str) -> str:
    """
    Get current time formatted in the specified timezone.

    Args:
        timezone: IANA timezone string (e.g., "America/New_York", "UTC")

    Returns:
        Formatted string with current time and timezone
        Format: "2025-12-20 15:30:45 America/New_York (EST)"

    Examples:
        >>> get_current_time_in_timezone("UTC")
        "2025-12-20 15:30:45 UTC"
        >>> get_current_time_in_timezone("America/New_York")
        "2025-12-20 10:30:45 America/New_York (EST)"
    """
    # Validate and fallback to UTC if invalid
    validated_tz = extract_timezone(timezone)

    try:
        # Get current time in the specified timezone
        tz = ZoneInfo(validated_tz)
        now = datetime.now(tz)

        # Format: "YYYY-MM-DD HH:MM:SS Timezone (Abbreviation)"
        # %Z gives timezone abbreviation (EST, JST, etc.)
        formatted = now.strftime(f"%Y-%m-%d %H:%M:%S {validated_tz} (%Z)")

        return formatted
    except Exception:
        # Fallback to UTC if any error occurs
        utc_now = datetime.now(ZoneInfo("UTC"))
        return utc_now.strftime("%Y-%m-%d %H:%M:%S UTC")
