"""
Celery Task — Maintenance.

Periodic infrastructure tasks: cache cleanup, health pings.
"""

from __future__ import annotations

import time
from structlog import get_logger

from workers.celery_app import app

logger = get_logger(__name__)


@app.task(
    name="workers.tasks.maintenance.flush_expired_cache",
    bind=True,
    max_retries=1,
    queue="default",
)
def flush_expired_cache(self) -> dict:
    """Remove stale cache entries.

    Redis handles TTL-based expiration automatically, but this task
    provides an explicit way to force-clean all application cache keys
    (e.g., after a major deployment or schema change).
    """
    task_id = self.request.id
    logger.info("task_started", task="flush_expired_cache", task_id=task_id)

    try:
        import redis
        from backend.config import settings

        r = redis.from_url(settings.REDIS_URL, decode_responses=True)
        deleted = 0
        for key in r.scan_iter(match="v1:*", count=200):
            r.delete(key)
            deleted += 1
        r.close()

        logger.info("task_completed", task="flush_expired_cache", task_id=task_id, keys_deleted=deleted)
        return {"status": "completed", "keys_deleted": deleted}

    except Exception as exc:
        logger.error("task_failed", task="flush_expired_cache", task_id=task_id, error=str(exc))
        return {"status": "failed", "error": str(exc)}


@app.task(
    name="workers.tasks.maintenance.health_check_task",
    bind=True,
    queue="default",
)
def health_check_task(self) -> dict:
    """Periodic infrastructure health ping.

    Checks connectivity to PostgreSQL, Redis, and RabbitMQ. Useful for
    monitoring dashboards (Flower, Grafana) to detect outages.
    """
    task_id = self.request.id
    logger.info("task_started", task="health_check_task", task_id=task_id)

    results = {"postgres": False, "redis": False}

    # PostgreSQL
    try:
        from backend.db.engine import sync_engine
        from sqlalchemy import text
        with sync_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        results["postgres"] = True
    except Exception as exc:
        logger.warning("health_postgres_failed", error=str(exc))

    # Redis
    try:
        import redis
        from backend.config import settings
        r = redis.from_url(settings.REDIS_URL, decode_responses=True)
        r.ping()
        r.close()
        results["redis"] = True
    except Exception as exc:
        logger.warning("health_redis_failed", error=str(exc))

    logger.info("task_completed", task="health_check_task", task_id=task_id, results=results)
    return {"status": "completed", "services": results}
