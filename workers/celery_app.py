"""
Enterprise AI Customer Intelligence Platform — Celery Application.

Configures the Celery application with:
    - RabbitMQ as message broker (durable, acknowledgements, retry).
    - Redis as result backend (task status polling).
    - Task routing to dedicated queues (default, ml, analytics).
    - JSON serialization (human-readable, cross-language compatible).

Usage:
    # Start worker with all queues
    celery -A workers.celery_app worker -l info -Q default,ml,analytics

    # Start worker for ML queue only (dedicated GPU machine)
    celery -A workers.celery_app worker -l info -Q ml -c 1

    # Monitor tasks
    celery -A workers.celery_app flower
"""

from __future__ import annotations

from celery import Celery
from backend.config import settings

app = Celery("customer_intelligence")

# ---------------------------------------------------------------------------
# Broker & Backend
# ---------------------------------------------------------------------------
app.conf.broker_url = settings.CELERY_BROKER_URL
app.conf.result_backend = settings.CELERY_RESULT_BACKEND

# ---------------------------------------------------------------------------
# Serialization — JSON only (no pickle in production)
# ---------------------------------------------------------------------------
app.conf.task_serializer = "json"
app.conf.result_serializer = "json"
app.conf.accept_content = ["json"]

# ---------------------------------------------------------------------------
# Task Behavior
# ---------------------------------------------------------------------------
app.conf.task_acks_late = True                   # Acknowledge after completion (not on receive)
app.conf.task_reject_on_worker_lost = True        # Re-queue if worker crashes
app.conf.worker_prefetch_multiplier = 1           # One task at a time per worker
app.conf.task_track_started = True                # Track STARTED state
app.conf.result_expires = 86400                   # Results expire after 24h

# ---------------------------------------------------------------------------
# Retry Policy (global default — individual tasks can override)
# ---------------------------------------------------------------------------
app.conf.task_default_retry_delay = 60            # 60 seconds between retries
app.conf.task_max_retries = 3

# ---------------------------------------------------------------------------
# Task Routing — separate queues for different workload types
# ---------------------------------------------------------------------------
app.conf.task_routes = {
    "workers.tasks.training.*": {"queue": "ml"},
    "workers.tasks.prediction.*": {"queue": "ml"},
    "workers.tasks.feature_store.*": {"queue": "ml"},
    "workers.tasks.analytics.*": {"queue": "analytics"},
    "workers.tasks.maintenance.*": {"queue": "default"},
}

# ---------------------------------------------------------------------------
# Task Priority (0=highest, 9=lowest)
# ---------------------------------------------------------------------------
app.conf.task_queue_max_priority = 10
app.conf.task_default_priority = 5

# ---------------------------------------------------------------------------
# Timezone
# ---------------------------------------------------------------------------
app.conf.timezone = "UTC"
app.conf.enable_utc = True

# ---------------------------------------------------------------------------
# Auto-discover tasks from workers/tasks/ modules
# ---------------------------------------------------------------------------
app.autodiscover_tasks(["workers.tasks"])
