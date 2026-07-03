"""
Enterprise AI Customer Intelligence Platform — Cache Decorators.

Reusable decorators that eliminate duplicate caching logic across services.

Usage:
    @cached(key_builder=lambda customer_id: CacheKeys.customer(customer_id))
    async def get_customer_profile(self, customer_id: str):
        ...

    @invalidate_cache(patterns=[CacheKeys.customer_pattern(), CacheKeys.dashboard()])
    async def update_customer(self, customer_id: str, data: dict):
        ...
"""

from __future__ import annotations

import functools
import json
from typing import Any, Callable, List, Optional, Union

from structlog import get_logger

from backend.cache.service import CacheService
from backend.config import settings

logger = get_logger(__name__)

# Shared singleton — services don't need to instantiate their own.
_cache_service = CacheService()


def cached(
    key_builder: Callable[..., str],
    ttl: Optional[int] = None,
) -> Callable:
    """Read-through cache decorator for async service methods.

    1. Builds a cache key from the method arguments.
    2. Checks Redis. If hit, returns the cached value.
    3. If miss, calls the wrapped method, caches the result, and returns it.

    Args:
        key_builder: Function that receives the same args as the decorated
                     method and returns a cache key string.
        ttl: Cache lifetime in seconds. Defaults to REDIS_CACHE_TTL_SECONDS.
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Build key — skip `self` (args[0]) when calling key_builder
            try:
                key = key_builder(*args[1:], **kwargs)
            except Exception:
                # If key building fails, skip cache and call function directly
                return await func(*args, **kwargs)

            # Try cache first
            cached_value = await _cache_service.get(key)
            if cached_value is not None:
                return cached_value

            # Cache miss — execute function
            result = await func(*args, **kwargs)

            # Cache the result (serialize Pydantic models)
            try:
                if hasattr(result, "model_dump"):
                    serializable = result.model_dump(mode="json")
                elif isinstance(result, (dict, list, str, int, float, bool)):
                    serializable = result
                else:
                    serializable = None

                if serializable is not None:
                    await _cache_service.set(key, serializable, ttl=ttl)
            except Exception as exc:
                logger.warning("cache_serialization_error", key=key, error=str(exc))

            return result

        return wrapper

    return decorator


def invalidate_cache(
    patterns: Union[List[str], Callable[..., List[str]]],
) -> Callable:
    """Decorator that invalidates cache entries after the wrapped method completes.

    Args:
        patterns: Either a static list of key patterns to delete, or a callable
                  that receives the method args and returns patterns dynamically.
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = await func(*args, **kwargs)

            # Resolve patterns
            if callable(patterns):
                keys_to_invalidate = patterns(*args[1:], **kwargs)
            else:
                keys_to_invalidate = patterns

            for pattern in keys_to_invalidate:
                if "*" in pattern:
                    await _cache_service.delete_pattern(pattern)
                else:
                    await _cache_service.delete(pattern)

            return result

        return wrapper

    return decorator
