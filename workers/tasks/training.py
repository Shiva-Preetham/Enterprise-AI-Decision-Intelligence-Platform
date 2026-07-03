"""
Celery Task — Model Training.

Triggers the full ML pipeline (preprocessing, training, evaluation, SHAP,
model registry) as a background task. Returns metadata on completion.

Usage:
    from workers.tasks.training import retrain_model
    result = retrain_model.delay()
    print(result.id)  # task_id for polling
"""

from __future__ import annotations

import time
from structlog import get_logger

from workers.celery_app import app

logger = get_logger(__name__)


@app.task(
    name="workers.tasks.training.retrain_model",
    bind=True,
    max_retries=2,
    default_retry_delay=120,
    queue="ml",
)
def retrain_model(self) -> dict:
    """Execute the full ML training pipeline.

    Steps:
        1. Load features from analytics.customer_feature_store.
        2. Preprocess and split.
        3. Train all models with hyperparameter tuning.
        4. Evaluate and select best model.
        5. Generate SHAP explanations.
        6. Serialize artifacts to models/.

    Returns:
        dict with best_model name, metrics, and duration.
    """
    start_time = time.time()
    task_id = self.request.id
    logger.info("task_started", task="retrain_model", task_id=task_id)

    try:
        self.update_state(state="PROGRESS", meta={"step": "Loading feature store"})

        from ml.train_pipeline import run_pipeline
        run_pipeline()

        duration = round(time.time() - start_time, 2)
        logger.info("task_completed", task="retrain_model", task_id=task_id, duration_sec=duration)

        return {
            "status": "completed",
            "task": "retrain_model",
            "duration_seconds": duration,
        }

    except Exception as exc:
        logger.error("task_failed", task="retrain_model", task_id=task_id, error=str(exc))
        raise self.retry(exc=exc)
