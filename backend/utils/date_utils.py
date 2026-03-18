# Utility functions for date handling
from datetime import datetime, timezone

def utc_now() -> datetime:
    """Return current UTC time."""
    return datetime.now(timezone.utc)

def format_datetime(dt: datetime, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format a datetime object as string."""
    return dt.strftime(fmt)