"""
Enterprise AI Customer Intelligence Platform — Database Session Management.

Provides async session factories and a dependency-injection-ready session
generator for use in FastAPI route handlers and data pipelines.

Design Decisions:
    - async_sessionmaker (SQLAlchemy 2.x) replaces the legacy sessionmaker
      for full async/await support with asyncpg.
    - expire_on_commit=False prevents lazy-load exceptions after commit.
      Without this, accessing an attribute on a committed object triggers
      a synchronous reload — which raises an error in async context.
    - The get_async_session() generator yields a session within a try/finally
      block to guarantee cleanup. FastAPI's Depends() calls it automatically.
    - Sessions are short-lived (one per request/task). They are NOT cached
      or reused across requests — each call gets a fresh session from the pool.

Usage in FastAPI (Sprint 3):
    @router.get("/customers")
    async def list_customers(
        session: AsyncSession = Depends(get_async_session),
    ):
        result = await session.execute(select(Customer))
        return result.scalars().all()

Usage in scripts/pipelines:
    async with AsyncSessionFactory() as session:
        result = await session.execute(select(Customer))
        customers = result.scalars().all()
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from backend.db.engine import async_engine

# =============================================================================
# Async Session Factory
# =============================================================================
# Creates new AsyncSession instances bound to the async engine.
# Each session represents a single unit-of-work (transaction boundary).

AsyncSessionFactory = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# =============================================================================
# Dependency Injection Generator
# =============================================================================

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session, ensuring cleanup on exit.

    This is designed for FastAPI's dependency injection system:
        session: AsyncSession = Depends(get_async_session)

    The try/finally guarantees the session is closed even if the
    request handler raises an exception. The connection is returned
    to the pool — not destroyed — so this is cheap.

    Yields:
        AsyncSession: A fresh database session from the connection pool.
    """
    async with AsyncSessionFactory() as session:
        try:
            yield session
        finally:
            await session.close()
