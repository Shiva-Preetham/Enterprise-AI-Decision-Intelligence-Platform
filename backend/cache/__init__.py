"""
Enterprise AI Customer Intelligence Platform — Cache Package.

Provides Redis-backed caching infrastructure including:
- Async Redis client with connection pooling
- Typed CacheService abstraction
- Reusable @cached / @invalidate_cache decorators
- Version-aware cache key builders
"""

from backend.cache.client import get_redis, startup_redis, shutdown_redis
from backend.cache.service import CacheService
from backend.cache.decorators import cached, invalidate_cache
from backend.cache.keys import CacheKeys

__all__ = [
    "get_redis",
    "startup_redis",
    "shutdown_redis",
    "CacheService",
    "CacheKeys",
    "cached",
    "invalidate_cache",
]
