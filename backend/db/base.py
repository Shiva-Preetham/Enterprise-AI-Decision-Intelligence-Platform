"""
Enterprise AI Customer Intelligence Platform — Declarative Base & Schema Registry.

Defines the SQLAlchemy DeclarativeBase that all ORM models inherit from,
and the PostgreSQL schema constants used for logical data separation.

Design Decisions:
    - SQLAlchemy 2.x DeclarativeBase (class-based) replaces the legacy
      declarative_base() factory for better type-checker support.
    - Schemas are defined as constants here so that models, migrations,
      and seed scripts all reference the same source of truth.
    - Schema creation SQL is provided as a helper for Alembic migrations.

Schema Strategy:
    raw       — Ingested source data, 1:1 mirror of CSV/API sources
    curated   — Cleaned, deduplicated, business-ready tables
    analytics — Aggregated metrics, feature store, ML outputs
    platform  — Application metadata (users, audit logs, configs)

Usage:
    from backend.db.base import Base, SCHEMA_RAW

    class Customer(Base):
        __tablename__ = "customers"
        __table_args__ = {"schema": SCHEMA_RAW}
"""

from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass

# =============================================================================
# PostgreSQL Schema Constants
# =============================================================================
# These schemas provide logical separation of data by purpose.
# Only SCHEMA_RAW is populated in Sprint 1. The remaining schemas
# are created as empty namespaces for future sprints.

SCHEMA_RAW = "raw"
SCHEMA_CURATED = "curated"
SCHEMA_ANALYTICS = "analytics"
SCHEMA_PLATFORM = "platform"

ALL_SCHEMAS = [SCHEMA_RAW, SCHEMA_CURATED, SCHEMA_ANALYTICS, SCHEMA_PLATFORM]


# =============================================================================
# Declarative Base
# =============================================================================

class Base(DeclarativeBase):
    """Base class for all ORM models.

    SQLAlchemy 2.x uses class inheritance instead of the legacy
    declarative_base() factory. This provides:
      - Native type-checker support (mypy, pyright)
      - Mapped column type inference
      - Consistent metadata across all models

    All models inherit from this class:
        class Customer(Base):
            __tablename__ = "customers"
            ...
    """

    pass
