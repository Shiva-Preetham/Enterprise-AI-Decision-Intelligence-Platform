"""
Enterprise AI Customer Intelligence Platform — Database Package.

Exposes the core database primitives for use across the application:

    from backend.db import Base, async_engine, get_async_session

Submodules:
    base.py    — Declarative Base and schema definitions
    engine.py  — Async and sync engine factories with connection pooling
    session.py — AsyncSession factory and dependency injection helpers
"""

from backend.db.base import Base
from backend.db.engine import async_engine, sync_engine
from backend.db.session import AsyncSessionFactory, get_async_session

__all__ = [
    "Base",
    "async_engine",
    "sync_engine",
    "AsyncSessionFactory",
    "get_async_session",
]
