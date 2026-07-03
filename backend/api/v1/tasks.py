"""
Enterprise AI Customer Intelligence Platform — Tasks Router (API v1).

Exposes endpoints for triggering and monitoring background tasks.
Heavy operations (training, feature store rebuild, batch predictions)
return a task_id immediately. Clients poll GET /tasks/{task_id} for status.
"""

from __future__ import annotations

from fastapi import APIRouter

from backend.core.responses import SuccessResponse
from backend.schemas.task import TaskStatusResponse, TaskTriggerResponse

router = APIRouter(prefix="/tasks", tags=["Background Tasks"])


# ---------------------------------------------------------------------------
# Task Triggers
# ---------------------------------------------------------------------------

@router.post(
    "/train",
    response_model=SuccessResponse[TaskTriggerResponse],
    summary="Trigger model retraining",
    description="Queues a full ML pipeline run (preprocessing, training, evaluation, SHAP, registry).",
)
async def trigger_train() -> SuccessResponse:
    from workers.tasks.training import retrain_model

    result = retrain_model.delay()
    return SuccessResponse(
        message="Model retraining task queued",
        data=TaskTriggerResponse(
            task_id=result.id,
            task_name="retrain_model",
            status="QUEUED",
            message="ML training pipeline has been queued for background execution.",
        ),
    )


@router.post(
    "/feature-store",
    response_model=SuccessResponse[TaskTriggerResponse],
    summary="Trigger Feature Store rebuild",
    description="Queues a full feature engineering pipeline run.",
)
async def trigger_feature_store_rebuild() -> SuccessResponse:
    from workers.tasks.feature_store import rebuild_feature_store

    result = rebuild_feature_store.delay()
    return SuccessResponse(
        message="Feature Store rebuild task queued",
        data=TaskTriggerResponse(
            task_id=result.id,
            task_name="rebuild_feature_store",
            status="QUEUED",
            message="Feature Store rebuild has been queued for background execution.",
        ),
    )


@router.post(
    "/batch-predict",
    response_model=SuccessResponse[TaskTriggerResponse],
    summary="Trigger batch predictions",
    description="Queues churn predictions for all customers in the Feature Store.",
)
async def trigger_batch_predictions() -> SuccessResponse:
    from workers.tasks.prediction import run_batch_predictions

    result = run_batch_predictions.delay()
    return SuccessResponse(
        message="Batch prediction task queued",
        data=TaskTriggerResponse(
            task_id=result.id,
            task_name="run_batch_predictions",
            status="QUEUED",
            message="Batch predictions have been queued for background execution.",
        ),
    )


@router.post(
    "/refresh-dashboard",
    response_model=SuccessResponse[TaskTriggerResponse],
    summary="Trigger dashboard cache refresh",
    description="Queues a refresh of the cached dashboard metrics.",
)
async def trigger_dashboard_refresh() -> SuccessResponse:
    from workers.tasks.analytics import refresh_dashboard_cache

    result = refresh_dashboard_cache.delay()
    return SuccessResponse(
        message="Dashboard refresh task queued",
        data=TaskTriggerResponse(
            task_id=result.id,
            task_name="refresh_dashboard_cache",
            status="QUEUED",
            message="Dashboard cache refresh has been queued for background execution.",
        ),
    )


# ---------------------------------------------------------------------------
# Task Status Polling
# ---------------------------------------------------------------------------

@router.get(
    "/{task_id}",
    response_model=SuccessResponse[TaskStatusResponse],
    summary="Get task status",
    description=(
        "Poll the status of a background task by its task_id. "
        "Returns PENDING, STARTED, PROGRESS, SUCCESS, FAILURE, or RETRY."
    ),
)
async def get_task_status(task_id: str) -> SuccessResponse:
    from workers.celery_app import app as celery_app

    result = celery_app.AsyncResult(task_id)

    # Extract progress info for PROGRESS state
    progress = None
    if result.state == "PROGRESS" and isinstance(result.info, dict):
        progress = result.info

    # Extract error message for FAILURE state
    error = None
    if result.state == "FAILURE":
        error = str(result.info) if result.info else "Unknown error"

    # Extract result for SUCCESS state
    task_result = None
    duration = None
    if result.state == "SUCCESS" and isinstance(result.result, dict):
        task_result = result.result
        duration = result.result.get("duration_seconds")

    return SuccessResponse(
        message=f"Task status: {result.state}",
        data=TaskStatusResponse(
            task_id=task_id,
            status=result.state,
            progress=progress,
            result=task_result,
            error=error,
            duration_seconds=duration,
        ),
    )
