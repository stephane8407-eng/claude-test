"""
Simple in-memory caching utilities for API responses.

For production, consider using Redis or Memcached.
For MVP, functools.lru_cache provides fast in-memory caching.
"""
from functools import wraps, lru_cache
from typing import Callable, Any
import hashlib
import json
from datetime import datetime, timedelta


# Global cache statistics
cache_stats = {
    "hits": 0,
    "misses": 0,
    "created_at": datetime.now()
}


def cache_key(*args, **kwargs) -> str:
    """
    Generate a cache key from function arguments.

    Args:
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        SHA256 hash of serialized arguments
    """
    # Convert args and kwargs to a stable string representation
    key_data = {
        "args": str(args),
        "kwargs": sorted(kwargs.items())
    }
    key_str = json.dumps(key_data, sort_keys=True, default=str)
    return hashlib.sha256(key_str.encode()).hexdigest()


def cached_query(ttl_seconds: int = 300, maxsize: int = 128):
    """
    Decorator to cache database query results.

    Args:
        ttl_seconds: Time to live for cached results (default 5 minutes)
        maxsize: Maximum number of cached entries (default 128)

    Usage:
        @cached_query(ttl_seconds=600, maxsize=256)
        def get_battle_stats(db: Session):
            # Expensive query here
            return results

    Note: For production, use Redis with proper TTL expiration.
    This is a simple in-memory cache suitable for MVP.
    """
    def decorator(func: Callable) -> Callable:
        # Use LRU cache for automatic eviction of old entries
        cached_func = lru_cache(maxsize=maxsize)(func)

        @wraps(func)
        def wrapper(*args, **kwargs):
            global cache_stats

            # Try to get from cache
            try:
                result = cached_func(*args, **kwargs)
                cache_stats["hits"] += 1
                return result
            except Exception:
                cache_stats["misses"] += 1
                # Cache miss or error - compute fresh result
                return func(*args, **kwargs)

        # Expose cache_info for debugging
        wrapper.cache_info = cached_func.cache_info
        wrapper.cache_clear = cached_func.cache_clear

        return wrapper

    return decorator


def get_cache_stats() -> dict:
    """
    Get current cache statistics.

    Returns:
        Dictionary with cache hits, misses, and hit rate
    """
    global cache_stats
    total = cache_stats["hits"] + cache_stats["misses"]
    hit_rate = (cache_stats["hits"] / total * 100) if total > 0 else 0

    return {
        "hits": cache_stats["hits"],
        "misses": cache_stats["misses"],
        "total_requests": total,
        "hit_rate_percent": round(hit_rate, 2),
        "uptime_seconds": (datetime.now() - cache_stats["created_at"]).total_seconds()
    }


def clear_all_caches():
    """
    Clear all cached data.

    Useful for:
    - After database updates
    - Manual cache invalidation
    - Testing
    """
    global cache_stats
    cache_stats = {
        "hits": 0,
        "misses": 0,
        "created_at": datetime.now()
    }
    # Note: Individual function caches need to be cleared separately
    # by calling function_name.cache_clear()


# Example usage:
"""
from app.utils.cache import cached_query

@cached_query(ttl_seconds=600, maxsize=256)
def get_expensive_stats(db: Session):
    # This will be cached for 10 minutes
    return db.query(...).all()
"""
