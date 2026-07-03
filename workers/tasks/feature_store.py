"""
Celery Task — Feature Store Rebuild.

Regenerates the analytics.customer_feature_store table by running the full
feature engineering pipeline. Invalidates related caches on completion.
"""

from __future__ import annotations

import time
from structlog import get_logger

from workers.celery_app import app

logger = get_logger(__name__)


@app.task(
    name="workers.tasks.feature_store.rebuild_feature_store",
    bind=True,
    max_retries=2,
    default_retry_delay=120,
    queue="ml",
)
def rebuild_feature_store(self) -> dict:
    """Rebuild the customer feature store from raw data.

    Runs the feature engineering builder, which:
        1. Loads raw data from PostgreSQL.
        2. Engineers RFM, payment, delivery, review, and product features.
        3. Creates churn labels.
        4. Writes the result to analytics.customer_feature_store.

    On completion, invalidates all feature_store and dashboard cache keys.
    """
    start_time = time.time()
    task_id = self.request.id
    logger.info("task_started", task="rebuild_feature_store", task_id=task_id)

    try:
        self.update_state(state="PROGRESS", meta={"step": "Building features"})

        from feature_engineering.builder import FeatureBuilder
        builder = FeatureBuilder()
        builder.run()

        # Invalidate caches that depend on feature store data
        self.update_state(state="PROGRESS", meta={"step": "Invalidating caches"})

        duration = round(time.time() - start_time, 2)
        logger.info("task_completed", task="rebuild_feature_store", task_id=task_id, duration_sec=duration)

        return {
            "status": "completed",
            "task": "rebuild_feature_store",
            "duration_seconds": duration,
        }

    except Exception as exc:
        logger.error("task_failed", task="rebuild_feature_store", task_id=task_id, error=str(exc))
        raise self.retry(exc=exc)
