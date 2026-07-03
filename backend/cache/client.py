"""
Enterprise AI Customer Intelligence Platform — Redis Client.

Manages the async Redis connection pool lifecycle. The pool is created once
at application startup (via FastAPI lifespan) and shared across all requests.

Design Decisions:
    - redis.asyncio for non-blocking I/O on the FastAPI event loop.
    - Connection pooling avoids creating TCP connections per-request.
    - decode_responses=True so all values are returned as str, not bytes.
    - Graceful degradation: if Redis is unavailable, CacheService returns
      None (cache miss) instead of crashing the API.
"""

from __future__ import annotations

from typing import Optional

import redis.asyncio as aioredis
from structlog import get_logger

from backend.config import settings

logger = get_logger(__name__)

# Module-level singleton — initialized at startup, closed at shutdown.
_redis_pool: Optional[aioredis.Redis] = None


async def startup_redis() -> None:
    """Create the Redis connection pool. Call once during FastAPI lifespan startup."""
    global _redis_pool
    try:
        _redis_pool = aioredis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            max_connections=20,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
        )
        # Validate connectivity
        await _redis_pool.ping()
        logger.info("redis_connected", host=settings.REDIS_HOST, port=settings.REDIS_PORT)
    except Exception as exc:
        logger.error("redis_connection_failed", error=str(exc))
        _redis_pool = None


async def shutdown_redis() -> None:
    """Close the Redis connection pool. Call during FastAPI lifespan shutdown."""
    global _redis_pool
    if _redis_pool is not None:
        await _redis_pool.aclose()
        _redis_pool = None
        logger.info("redis_disconnected")


def get_redis() -> Optional[aioredis.Redis]:
    """Returns the active Redis client, or None if Redis is unavailable.

    Used by CacheService and as a FastAPI dependency.
    """
    return _redis_pool
