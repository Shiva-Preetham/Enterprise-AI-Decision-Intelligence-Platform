"""
Enterprise AI Customer Intelligence Platform — Centralized Logging.

Provides structured logging using structlog, configured once and reused
by all components: pipelines, FastAPI, Celery workers, ML, agents.

Usage:
    from backend.logging import get_logger

    logger = get_logger(__name__)
    logger.info("pipeline_started", dataset="customers", rows=99332)
    logger.error("ingestion_failed", error=str(e))

Design Decisions:
    - structlog outputs key=value pairs (not prose), making logs
      machine-parseable for ELK/Datadog/CloudWatch.
    - JSON rendering in production, colored console in development.
    - Bound loggers carry context (e.g. component name) across calls.
    - stdlib integration ensures third-party libraries (SQLAlchemy,
      Alembic, uvicorn) also route through structlog.
"""

from __future__ import annotations

import logging
import sys
import time
from collections.abc import Callable
from contextlib import contextmanager
from typing import Any

import structlog

from backend.config import settings


def _configure_structlog() -> None:
    """Configure structlog processors and output format.

    Called once at module load. Idempotent — safe to call multiple times.
    """
    shared_processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    if settings.APP_ENV == "production":
        # JSON logs for production (machine-parseable)
        renderer = structlog.processors.JSONRenderer()
    else:
        # Colored console logs for development (human-readable)
        renderer = structlog.dev.ConsoleRenderer()

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configure stdlib root logger so third-party libraries also
    # route through structlog's formatting pipeline.
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        structlog.stdlib.ProcessorFormatter(
            processor=renderer,
            foreign_pre_chain=shared_processors,
        )
    )

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(getattr(logging, settings.APP_LOG_LEVEL.upper(), logging.INFO))

    # Quiet noisy libraries
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("alembic").setLevel(logging.INFO)


# Configure on import
_configure_structlog()


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger bound to the given component name.

    Args:
        name: Logger name, typically ``__name__``.

    Returns:
        A structlog BoundLogger instance.
    """
    return structlog.get_logger(name)


@contextmanager
def log_execution_time(logger: structlog.stdlib.BoundLogger, operation: str) -> Any:
    """Context manager that logs elapsed time for an operation.

    Usage:
        with log_execution_time(logger, "customer_ingestion"):
            ingest_customers()

    Logs:
        operation_started  operation=customer_ingestion
        operation_completed operation=customer_ingestion elapsed_seconds=2.34
    """
    logger.info("operation_started", operation=operation)
    start = time.perf_counter()
    try:
        yield
    except Exception:
        elapsed = round(time.perf_counter() - start, 3)
        logger.error("operation_failed", operation=operation, elapsed_seconds=elapsed)
        raise
    else:
        elapsed = round(time.perf_counter() - start, 3)
        logger.info("operation_completed", operation=operation, elapsed_seconds=elapsed)
