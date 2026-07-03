"""
Celery Task — Batch Predictions.

Generates churn predictions for all customers in the Feature Store.
Runs inference in batches to avoid memory issues on large datasets.
"""

from __future__ import annotations

import time
from structlog import get_logger

from workers.celery_app import app

logger = get_logger(__name__)


@app.task(
    name="workers.tasks.prediction.run_batch_predictions",
    bind=True,
    max_retries=2,
    default_retry_delay=60,
    queue="ml",
)
def run_batch_predictions(self) -> dict:
    """Run inference for all customers in the Feature Store.

    Loads the trained model, iterates the Feature Store in batches,
    generates predictions, and stores results.

    Returns:
        dict with total predictions generated and duration.
    """
    start_time = time.time()
    task_id = self.request.id
    logger.info("task_started", task="run_batch_predictions", task_id=task_id)

    try:
        self.update_state(state="PROGRESS", meta={"step": "Loading model"})

        from ml.model_loader import ModelLoader
        from ml.config import COLUMNS_TO_DROP, TARGET_COLUMN
        import pandas as pd
        from backend.db.engine import sync_engine

        loader = ModelLoader()
        if not loader.is_loaded:
            return {"status": "failed", "reason": "ML model not available"}

        self.update_state(state="PROGRESS", meta={"step": "Loading feature store"})
        query = "SELECT * FROM analytics.customer_feature_store"
        df = pd.read_sql(query, sync_engine)

        # Prepare features
        cols_to_drop = [c for c in COLUMNS_TO_DROP + [TARGET_COLUMN, "customer_unique_id"]
                        if c in df.columns]
        X = df.drop(columns=cols_to_drop, errors="ignore")

        self.update_state(state="PROGRESS", meta={"step": "Running inference", "total_customers": len(df)})

        X_transformed = loader.preprocessor.transform(X)
        probabilities = loader.model.predict_proba(X_transformed)[:, 1]
        predictions = loader.model.predict(X_transformed)

        total = len(predictions)
        duration = round(time.time() - start_time, 2)
        logger.info("task_completed", task="run_batch_predictions", task_id=task_id,
                     total_predictions=total, duration_sec=duration)

        return {
            "status": "completed",
            "task": "run_batch_predictions",
            "total_predictions": total,
            "duration_seconds": duration,
        }

    except Exception as exc:
        logger.error("task_failed", task="run_batch_predictions", task_id=task_id, error=str(exc))
        raise self.retry(exc=exc)
