"""
Redis cache service with in-memory fallback
Provides caching functionality for frequently accessed data
"""
import json
import pickle
from typing import Any, Optional, Callable
from functools import wraps
import hashlib
from datetime import datetime, timedelta

try:
    import redis
    from redis.exceptions import RedisError
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

from app.config import get_config
from app.services.logger import get_logger

logger = get_logger(__name__)


class CacheBackend:
    """Base class for cache backends"""

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        raise NotImplementedError

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with optional TTL (seconds)"""
        raise NotImplementedError

    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        raise NotImplementedError

    def clear(self) -> bool:
        """Clear all cache entries"""
        raise NotImplementedError

    def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        raise NotImplementedError


class RedisBackend(CacheBackend):
    """Redis cache backend"""

    def __init__(self, redis_url: str):
        """
        Initialize Redis backend

        Args:
            redis_url: Redis connection URL
        """
        if not REDIS_AVAILABLE:
            raise ImportError("redis package is not installed. Install with: pip install redis")

        self.redis_url = redis_url
        self.client: Optional[redis.Redis] = None
        self._connect()

    def _connect(self):
        """Connect to Redis"""
        try:
            self.client = redis.from_url(
                self.redis_url,
                decode_responses=False,  # We'll handle encoding ourselves
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
            )
            # Test connection
            self.client.ping()
            logger.info(f"Connected to Redis: {self.redis_url.split('@')[-1]}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.client = None
            raise

    def get(self, key: str) -> Optional[Any]:
        """Get value from Redis"""
        if not self.client:
            return None

        try:
            value = self.client.get(key)
            if value is None:
                return None

            # Try to unpickle (for Python objects)
            try:
                return pickle.loads(value)
            except (pickle.UnpicklingError, AttributeError):
                # If unpickling fails, try JSON
                try:
                    return json.loads(value.decode('utf-8'))
                except (json.JSONDecodeError, UnicodeDecodeError):
                    # Return raw bytes as fallback
                    return value

        except RedisError as e:
            logger.error(f"Redis GET error for key '{key}': {e}")
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in Redis with optional TTL"""
        if not self.client:
            return False

        try:
            # Try to pickle (works for most Python objects)
            try:
                serialized = pickle.dumps(value)
            except (pickle.PicklingError, TypeError):
                # If pickling fails, try JSON
                try:
                    serialized = json.dumps(value).encode('utf-8')
                except (TypeError, ValueError):
                    logger.warning(f"Cannot serialize value for key '{key}'")
                    return False

            # Set with or without TTL
            if ttl:
                self.client.setex(key, ttl, serialized)
            else:
                self.client.set(key, serialized)

            return True

        except RedisError as e:
            logger.error(f"Redis SET error for key '{key}': {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete value from Redis"""
        if not self.client:
            return False

        try:
            self.client.delete(key)
            return True
        except RedisError as e:
            logger.error(f"Redis DELETE error for key '{key}': {e}")
            return False

    def clear(self) -> bool:
        """Clear all cache entries"""
        if not self.client:
            return False

        try:
            self.client.flushdb()
            logger.warning("Redis cache cleared")
            return True
        except RedisError as e:
            logger.error(f"Redis CLEAR error: {e}")
            return False

    def exists(self, key: str) -> bool:
        """Check if key exists in Redis"""
        if not self.client:
            return False

        try:
            return bool(self.client.exists(key))
        except RedisError as e:
            logger.error(f"Redis EXISTS error for key '{key}': {e}")
            return False


class InMemoryBackend(CacheBackend):
    """In-memory cache backend (fallback when Redis unavailable)"""

    def __init__(self):
        """Initialize in-memory cache"""
        self._cache: dict = {}
        self._expiry: dict = {}
        logger.warning("Using in-memory cache (Redis not available)")

    def _is_expired(self, key: str) -> bool:
        """Check if key has expired"""
        if key not in self._expiry:
            return False
        return datetime.utcnow() > self._expiry[key]

    def get(self, key: str) -> Optional[Any]:
        """Get value from memory"""
        if key not in self._cache:
            return None

        # Check expiry
        if self._is_expired(key):
            self.delete(key)
            return None

        return self._cache[key]

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in memory with optional TTL"""
        self._cache[key] = value

        if ttl:
            self._expiry[key] = datetime.utcnow() + timedelta(seconds=ttl)
        elif key in self._expiry:
            del self._expiry[key]

        return True

    def delete(self, key: str) -> bool:
        """Delete value from memory"""
        if key in self._cache:
            del self._cache[key]
        if key in self._expiry:
            del self._expiry[key]
        return True

    def clear(self) -> bool:
        """Clear all cache entries"""
        self._cache.clear()
        self._expiry.clear()
        logger.warning("In-memory cache cleared")
        return True

    def exists(self, key: str) -> bool:
        """Check if key exists in memory"""
        if key not in self._cache:
            return False
        if self._is_expired(key):
            self.delete(key)
            return False
        return True


class CacheService:
    """
    Cache service with automatic Redis/In-memory backend selection
    """

    def __init__(self):
        """Initialize cache service"""
        self.backend: Optional[CacheBackend] = None
        self.config = get_config()
        self._initialize_backend()

    def _initialize_backend(self):
        """Initialize cache backend (Redis or in-memory)"""
        if not self.config.CACHE_ENABLED:
            logger.info("Caching is disabled")
            return

        # Try Redis first if URL is provided
        if self.config.REDIS_URL and REDIS_AVAILABLE:
            try:
                self.backend = RedisBackend(self.config.REDIS_URL)
                logger.info("Cache backend: Redis")
                return
            except Exception as e:
                logger.warning(f"Redis unavailable, falling back to in-memory cache: {e}")

        # Fall back to in-memory cache
        self.backend = InMemoryBackend()
        logger.info("Cache backend: In-memory")

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        if not self.backend:
            return None
        return self.backend.get(key)

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set value in cache

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (optional)

        Returns:
            True if successful, False otherwise
        """
        if not self.backend:
            return False
        return self.backend.set(key, value, ttl)

    def delete(self, key: str) -> bool:
        """
        Delete value from cache

        Args:
            key: Cache key

        Returns:
            True if successful, False otherwise
        """
        if not self.backend:
            return False
        return self.backend.delete(key)

    def clear(self) -> bool:
        """
        Clear all cache entries

        Returns:
            True if successful, False otherwise
        """
        if not self.backend:
            return False
        return self.backend.clear()

    def exists(self, key: str) -> bool:
        """
        Check if key exists in cache

        Args:
            key: Cache key

        Returns:
            True if key exists, False otherwise
        """
        if not self.backend:
            return False
        return self.backend.exists(key)


# Global cache instance
_cache_service: Optional[CacheService] = None


def get_cache() -> CacheService:
    """
    Get global cache service instance

    Returns:
        CacheService instance
    """
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
    return _cache_service


def cache_key(*args, **kwargs) -> str:
    """
    Generate cache key from arguments

    Args:
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        MD5 hash of arguments as cache key
    """
    key_parts = [str(arg) for arg in args]
    key_parts.extend([f"{k}={v}" for k, v in sorted(kwargs.items())])
    key_string = ":".join(key_parts)
    return hashlib.md5(key_string.encode()).hexdigest()


def cached(ttl: Optional[int] = None, key_prefix: str = ""):
    """
    Decorator to cache function results

    Args:
        ttl: Time to live in seconds (uses config default if not provided)
        key_prefix: Prefix for cache key

    Example:
        @cached(ttl=300, key_prefix="user")
        def get_user(user_id: int):
            return db.query(User).get(user_id)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = get_cache()

            # Generate cache key
            key_parts = [key_prefix] if key_prefix else []
            key_parts.append(func.__name__)
            key_parts.append(cache_key(*args, **kwargs))
            cache_key_str = ":".join(key_parts)

            # Try to get from cache
            cached_value = cache.get(cache_key_str)
            if cached_value is not None:
                logger.debug(f"Cache HIT: {cache_key_str}")
                return cached_value

            # Cache miss - execute function
            logger.debug(f"Cache MISS: {cache_key_str}")
            result = func(*args, **kwargs)

            # Store in cache
            if result is not None:
                cache_ttl = ttl if ttl is not None else get_config().CACHE_TTL_MEDIUM
                cache.set(cache_key_str, result, cache_ttl)

            return result

        return wrapper
    return decorator


def invalidate_cache(key_prefix: str):
    """
    Invalidate all cache entries with given prefix
    Note: This is inefficient for Redis. For production, consider using Redis SCAN.

    Args:
        key_prefix: Cache key prefix to invalidate
    """
    cache = get_cache()
    if isinstance(cache.backend, InMemoryBackend):
        # For in-memory cache, we can iterate
        keys_to_delete = [k for k in cache.backend._cache.keys() if k.startswith(key_prefix)]
        for key in keys_to_delete:
            cache.delete(key)
        logger.info(f"Invalidated {len(keys_to_delete)} cache entries with prefix '{key_prefix}'")
    else:
        logger.warning("Cache invalidation by prefix not implemented for Redis backend")
