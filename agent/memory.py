"""
Enterprise AI Customer Intelligence Platform — Agent Memory.

Provides a Redis-backed memory saver for LangGraph conversations.
"""

from typing import Optional
from langgraph.checkpoint.redis import RedisSaver
import redis.asyncio as aioredis
from backend.config import settings

def get_memory_saver() -> Optional[RedisSaver]:
    """
    Creates a Redis-backed checkpointer for LangGraph.
    Uses the same REDIS_URL from the main configuration.
    Falls back to None (in-memory) if Redis connection fails.
    """
    try:
        # Create a dedicated connection pool for the checkpointer
        pool = aioredis.ConnectionPool.from_url(
            settings.REDIS_URL, 
            decode_responses=False # Checkpointer needs bytes
        )
        redis_conn = aioredis.Redis(connection_pool=pool)
        return RedisSaver(conn=redis_conn)
    except Exception as e:
        import structlog
        logger = structlog.get_logger(__name__)
        logger.warning("redis_memory_failed_fallback_to_none", error=str(e))
        return None
