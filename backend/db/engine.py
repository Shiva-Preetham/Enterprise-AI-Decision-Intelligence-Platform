"""
Enterprise AI Customer Intelligence Platform — Database Engines.

Creates SQLAlchemy engine instances with production-grade connection pooling.

Two engines are provided:
    async_engine  — For application runtime (FastAPI, ingestion pipelines)
    sync_engine   — For Alembic migrations (which cannot use async drivers)

Design Decisions:
    - Connection pool tuning is critical for production. Defaults are set
      for local development; production values should be tuned via env vars.
    - pool_pre_ping=True detects stale connections before handing them out,
      which prevents "connection reset by peer" errors after DB restarts.
    - echo is tied to APP_DEBUG so SQL logging is automatic in development
      but silent in production.
    - Engine creation is module-level (not inside a function) because
      SQLAlchemy engines are designed to be long-lived singletons.

Connection Pool Parameters:
    pool_size      — Number of persistent connections kept open (default: 5)
    max_overflow   — Extra connections allowed beyond pool_size (default: 10)
    pool_timeout   — Seconds to wait for a connection before raising (default: 30)
    pool_recycle   — Seconds before a connection is recycled to prevent
                     stale connections from long-lived processes (default: 1800)
    pool_pre_ping  — Emit a SELECT 1 before using a connection to verify
                     it's still alive (default: True)

Usage:
    from backend.db.engine import async_engine

    async with async_engine.begin() as conn:
        await conn.execute(text("SELECT 1"))
"""

from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine

from backend.config import settings

# =============================================================================
# Async Engine (asyncpg) — Application Runtime
# =============================================================================
# Used by FastAPI request handlers, data ingestion pipelines, and any
# async code that needs database access.

async_engine = create_async_engine(
    url=settings.DATABASE_URL,
    echo=settings.APP_DEBUG,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True,
)

# =============================================================================
# Sync Engine (psycopg2) — Alembic Migrations
# =============================================================================
# Alembic's migration runner is synchronous. It cannot use asyncpg.
# This engine is ONLY used by alembic/env.py and administrative scripts.

sync_engine = create_engine(
    url=settings.DATABASE_URL_SYNC,
    echo=settings.APP_DEBUG,
    pool_size=2,
    max_overflow=0,
    pool_pre_ping=True,
)
