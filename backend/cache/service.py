"""
Enterprise AI Customer Intelligence Platform — Cache Service.

Typed abstraction over raw Redis commands. Services inject CacheService
rather than calling Redis directly, keeping the cache concern isolated.

Design Decisions:
    - JSON serialization for all values (human-readable, debuggable).
    - Every method catches Redis errors and returns None / False,
      ensuring the API never crashes due to a cache failure.
    - Pattern-based delete uses SCAN (non-blocking) instead of KEYS
      (which blocks Redis on large keyspaces).
"""

from __future__ import annotations

import json
from typing import Any, Optional

from structlog import get_logger

from backend.cache.client import get_redis
from backend.config import settings

logger = get_logger(__name__)


class CacheService:
    """Typed interface for Redis cache operations.

    All methods degrade gracefully: if Redis is down, reads return None
    and writes silently fail. The API continues serving from the database.
    """

    async def get(self, key: str) -> Optional[Any]:
        """Read a value from cache. Returns None on miss or error."""
        client = get_redis()
        if client is None:
            return None
        try:
            value = await client.get(key)
            if value is not None:
                logger.debug("cache_hit", key=key)
                return json.loads(value)
            logger.debug("cache_miss", key=key)
            return None
        except Exception as exc:
            logger.warning("cache_get_error", key=key, error=str(exc))
            return None

    async def set(
        self, key: str, value: Any, ttl: Optional[int] = None
    ) -> bool:
        """Write a value to cache with optional TTL (seconds)."""
        client = get_redis()
        if client is None:
            return False
        try:
            ttl = ttl or settings.REDIS_CACHE_TTL_SECONDS
            serialized = json.dumps(value, default=str)
            await client.set(key, serialized, ex=ttl)
            logger.debug("cache_set", key=key, ttl=ttl)
            return True
        except Exception as exc:
            logger.warning("cache_set_error", key=key, error=str(exc))
            return False

    async def delete(self, key: str) -> bool:
        """Delete a specific key from cache."""
        client = get_redis()
        if client is None:
            return False
        try:
            deleted = await client.delete(key)
            if deleted:
                logger.info("cache_invalidated", key=key)
            return bool(deleted)
        except Exception as exc:
            logger.warning("cache_delete_error", key=key, error=str(exc))
            return False

    async def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching a glob pattern using SCAN.

        Uses SCAN instead of KEYS to avoid blocking Redis on large keyspaces.
        Returns the number of keys deleted.
        """
        client = get_redis()
        if client is None:
            return 0
        try:
            deleted_count = 0
            async for key in client.scan_iter(match=pattern, count=100):
                await client.delete(key)
                deleted_count += 1
            if deleted_count > 0:
                logger.info("cache_pattern_invalidated", pattern=pattern, count=deleted_count)
            return deleted_count
        except Exception as exc:
            logger.warning("cache_delete_pattern_error", pattern=pattern, error=str(exc))
            return 0

    async def exists(self, key: str) -> bool:
        """Check if a key exists in cache."""
        client = get_redis()
        if client is None:
            return False
        try:
            return bool(await client.exists(key))
        except Exception:
            return False

    async def health_check(self) -> bool:
        """Returns True if Redis is reachable."""
        client = get_redis()
        if client is None:
            return False
        try:
            return await client.ping()
        except Exception:
            return False
