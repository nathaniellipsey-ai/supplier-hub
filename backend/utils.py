"""Utility functions for Supplier Hub backend.

Provides helper functions for common operations.
"""

import logging
from typing import Any, Dict, List, Optional
from functools import wraps
from datetime import datetime
import json

logger = logging.getLogger(__name__)


def setup_logging(log_level: str = "INFO", log_format: str = None) -> None:
    """Configure application logging.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Custom log format string
    """
    if log_format is None:
        log_format = (
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    logging.basicConfig(
        level=getattr(logging, log_level),
        format=log_format,
    )


def sanitize_dict(data: Dict[str, Any], keys_to_remove: List[str] = None) -> Dict[str, Any]:
    """Remove sensitive fields from dictionary.
    
    Args:
        data: Dictionary to sanitize
        keys_to_remove: Keys to remove (default: ['password', 'secret'])
    
    Returns:
        Sanitized dictionary
    """
    if keys_to_remove is None:
        keys_to_remove = ['password', 'secret', 'api_key', 'token']
    
    sanitized = data.copy()
    for key in keys_to_remove:
        sanitized.pop(key, None)
    
    return sanitized


def validate_email(email: str) -> bool:
    """Simple email validation.
    
    Args:
        email: Email address to validate
    
    Returns:
        True if email is valid
    """
    if not email or not isinstance(email, str):
        return False
    
    # Simple check: must have @ and at least one character on each side
    parts = email.split('@')
    if len(parts) != 2:
        return False
    
    username, domain = parts
    if not username or not domain or '.' not in domain:
        return False
    
    return True


def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate string to maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
    
    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def format_datetime(dt: datetime, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format datetime object to string.
    
    Args:
        dt: Datetime object
        fmt: Format string
    
    Returns:
        Formatted datetime string
    """
    if not isinstance(dt, datetime):
        return str(dt)
    
    return dt.strftime(fmt)


def paginate(items: List[Any], page: int = 1, per_page: int = 50) -> tuple:
    """Paginate a list.
    
    Args:
        items: List to paginate
        page: Page number (1-indexed)
        per_page: Items per page
    
    Returns:
        Tuple of (paginated_items, total, page, pages)
    """
    if page < 1:
        page = 1
    if per_page < 1:
        per_page = 50
    
    total = len(items)
    pages = (total + per_page - 1) // per_page
    
    start = (page - 1) * per_page
    end = start + per_page
    
    return items[start:end], total, page, pages


def timing_middleware(func):
    """Decorator to measure function execution time.
    
    Args:
        func: Function to measure
    
    Returns:
        Wrapped function with timing
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = datetime.now()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            elapsed = (datetime.now() - start).total_seconds()
            logger.debug(f"[{func.__name__}] Executed in {elapsed:.3f}s")
    
    return wrapper


class APIResponse:
    """Helper class for consistent API responses."""

    @staticmethod
    def success(
        data: Any = None,
        message: str = "Success",
        code: int = 200
    ) -> Dict[str, Any]:
        """Create success response."""
        return {
            "status": "success",
            "code": code,
            "message": message,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }

    @staticmethod
    def error(
        message: str = "Error",
        code: int = 500,
        errors: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Create error response."""
        return {
            "status": "error",
            "code": code,
            "message": message,
            "errors": errors or {},
            "timestamp": datetime.now().isoformat()
        }

    @staticmethod
    def paginated(
        items: List[Any],
        total: int,
        page: int = 1,
        per_page: int = 50
    ) -> Dict[str, Any]:
        """Create paginated response."""
        pages = (total + per_page - 1) // per_page
        return {
            "status": "success",
            "data": items,
            "pagination": {
                "total": total,
                "page": page,
                "per_page": per_page,
                "pages": pages,
                "has_next": page < pages,
                "has_prev": page > 1
            },
            "timestamp": datetime.now().isoformat()
        }