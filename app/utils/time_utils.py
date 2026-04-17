"""Time utilities for SentinelGuard."""

import time
from datetime import datetime, timezone
from typing import Union


def get_current_timestamp_ms() -> int:
    """Get current timestamp in milliseconds."""
    return int(time.time() * 1000)


def get_current_timestamp() -> int:
    """Get current timestamp in seconds."""
    return int(time.time())


def timestamp_to_datetime(timestamp: Union[int, float]) -> datetime:
    """Convert timestamp to datetime object."""
    return datetime.fromtimestamp(timestamp, timezone.utc)


def datetime_to_timestamp(dt: datetime) -> int:
    """Convert datetime to timestamp."""
    return int(dt.timestamp())


def get_window_start_ms(window_seconds: int) -> int:
    """Get window start timestamp in milliseconds."""
    now_ms = get_current_timestamp_ms()
    window_start_ms = now_ms - (window_seconds * 1000)
    return window_start_ms


def get_window_start(window_seconds: int) -> int:
    """Get window start timestamp in seconds."""
    now = get_current_timestamp()
    window_start = now - window_seconds
    return window_start


def format_timestamp_ms(timestamp_ms: int) -> str:
    """Format timestamp in milliseconds to ISO string."""
    return timestamp_to_datetime(timestamp_ms / 1000).isoformat()


def format_timestamp(timestamp: int) -> str:
    """Format timestamp in seconds to ISO string."""
    return timestamp_to_datetime(timestamp).isoformat()


def calculate_reset_time(window_seconds: int) -> int:
    """Calculate reset time for rate limiting."""
    now = get_current_timestamp()
    # Round up to next window boundary
    return ((now // window_seconds) + 1) * window_seconds
