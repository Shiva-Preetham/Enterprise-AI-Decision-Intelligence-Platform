"""
Celery Task — Analytics.

Pre-computes and caches dashboard metrics so the dashboard endpoint
serves from cache instead of running aggregation queries on every request.
"""

from __future__ import annotations

import time
from structlog import get_logger

from workers.celery_app import app

logger = get_logger(__name__)


@app.task(
    name="workers.tasks.analytics.refresh_dashboard_cache",
    bind=True,
    max_retries=3,
    default_retry_delay=30,
    queue="analytics",
)
def refresh_dashboard_cache(self) -> dict:
    """Pre-compute and cache dashboard metrics.

    Runs the same aggregation queries as the dashboard API endpoint,
    then writes the result to Redis so subsequent API calls are instant.
    """
    start_time = time.time()
    task_id = self.request.id
    logger.info("task_started", task="refresh_dashboard_cache", task_id=task_id)

    try:
        self.update_state(state="PROGRESS", meta={"step": "Aggregating metrics"})

        import json
        import redis
        from backend.config import settings
        from backend.db.engine import sync_engine
        from sqlalchemy import text

        # Run aggregation synchronously (Celery workers are sync)
        with sync_engine.connect() as conn:
            total = conn.execute(
                text("SELECT COUNT(DISTINCT customer_unique_id) FROM raw.customers")
            ).scalar() or 0

            row = conn.execute(text("""
                SELECT
                    AVG(total_lifetime_value) as avg_clv,
                    AVG(avg_review_score) as avg_review,
                    AVG(avg_order_value) as avg_order,
                    AVG(churn_label) as avg_churn,
                    SUM(CASE WHEN churn_label = 1 THEN 1 ELSE 0 END) as high_risk
                FROM analytics.customer_feature_store
            """)).first()

        metrics = {
            "total_customers": total,
            "high_risk_customers": int(row.high_risk) if row and row.high_risk else 0,
            "average_clv": round(float(row.avg_clv), 2) if row and row.avg_clv else 0.0,
            "average_review_score": round(float(row.avg_review), 2) if row and row.avg_review else 0.0,
            "average_order_value": round(float(row.avg_order), 2) if row and row.avg_order else 0.0,
            "average_churn_probability": round(float(row.avg_churn), 4) if row and row.avg_churn else 0.0,
        }

        # Write to Redis cache
        r = redis.from_url(settings.REDIS_URL, decode_responses=True)
        r.set("v1:dashboard", json.dumps(metrics), ex=settings.REDIS_CACHE_TTL_SECONDS)
        r.close()

        duration = round(time.time() - start_time, 2)
        logger.info("task_completed", task="refresh_dashboard_cache", task_id=task_id, duration_sec=duration)

        return {
            "status": "completed",
            "task": "refresh_dashboard_cache",
            "metrics": metrics,
            "duration_seconds": duration,
        }

    except Exception as exc:
        logger.error("task_failed", task="refresh_dashboard_cache", task_id=task_id, error=str(exc))
        raise self.retry(exc=exc)
