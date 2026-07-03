"""
Enterprise AI Customer Intelligence Platform — Task Schemas.

Pydantic V2 DTOs for background task management endpoints.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class TaskTriggerResponse(BaseModel):
    """Response returned immediately when a background task is queued."""

    task_id: str = Field(..., description="Celery task UUID for status polling")
    task_name: str = Field(..., description="Human-readable task name")
    status: str = Field("QUEUED", description="Initial task state")
    message: str = Field(..., description="Confirmation message")


class TaskStatusResponse(BaseModel):
    """Full task status, returned by GET /tasks/{task_id}."""

    task_id: str = Field(..., description="Celery task UUID")
    status: str = Field(..., description="PENDING | STARTED | PROGRESS | SUCCESS | FAILURE | RETRY")
    progress: Optional[dict] = Field(None, description="Current step info for long-running tasks")
    result: Optional[Any] = Field(None, description="Task result (on SUCCESS)")
    error: Optional[str] = Field(None, description="Error message (on FAILURE)")
    started_at: Optional[str] = Field(None, description="ISO timestamp when task started")
    completed_at: Optional[str] = Field(None, description="ISO timestamp when task finished")
    duration_seconds: Optional[float] = Field(None, description="Total execution time")
