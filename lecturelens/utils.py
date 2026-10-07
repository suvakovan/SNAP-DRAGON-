"""
General utility functions for LectureLens.
"""

import hashlib
import time
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Optional

from lecturelens.logging_setup import logger


def timer(label: Optional[str] = None):
    """Decorator to log execution time of a function."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            name = label or func.__name__
            start = time.time()
            result = func(*args, **kwargs)
            elapsed = time.time() - start
            logger.info(f"[TIMER] {name}: {elapsed:.3f}s")
            return result
        return wrapper
    return decorator


def file_checksum(filepath: Path, algorithm: str = "sha256") -> str:
    """Compute hex digest checksum of a file."""
    h = hashlib.new(algorithm)
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def truncate_text(text: str, max_words: int = 50) -> str:
    """Truncate text to max_words, adding ellipsis if truncated."""
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words]) + "..."


def format_duration(seconds: float) -> str:
    """Format seconds into human-readable duration string."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    minutes = int(seconds // 60)
    secs = seconds % 60
    if minutes < 60:
        return f"{minutes}m {secs:.0f}s"
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours}h {mins}m {secs:.0f}s"


def safe_filename(title: str, max_length: int = 50) -> str:
    """Convert a title into a filesystem-safe filename."""
    safe = "".join(c if c.isalnum() or c in (" ", "-", "_") else "_" for c in title)
    safe = safe.strip().replace(" ", "_")
    return safe[:max_length]
