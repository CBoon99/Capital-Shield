"""
Time Utilities
"""
from datetime import datetime, timezone


def get_current_timestamp() -> str:
    """Get current timestamp in ISO format"""
    return datetime.now(timezone.utc).isoformat()


def parse_timestamp(ts: str) -> datetime:
    """Parse ISO timestamp string"""
    return datetime.fromisoformat(ts.replace('Z', '+00:00'))

