# Sprint 1 — Database Foundation Notes

---

## Sprint Goal
Build a production-ready database layer: configuration, PostgreSQL schemas, SQLAlchemy ORM, Alembic migrations, ingestion pipeline, and structured logging.

---

## Milestones Summary

### Milestone 1: Application Configuration
- **What was built**: [backend/config.py](../backend/config.py) using Pydantic Settings.
- **Why it exists**: Centralizes configuration, validates environment variables at startup, and provides computed DB URLs (sync/async).
- **Core Decisions**:
  - `pydantic-settings`: Enforces types at startup (e.g. invalid port fails immediately).
  - `frozen=True`: Makes settings immutable, avoiding runtime bugs.
  - `lru_cache`: Caches configuration to avoid re-reading/re-validating.
- **Enterprise Alternatives**: HashiCorp Vault, AWS Secrets Manager.
- **Common Mistake**: Committing `.env` secrets to git; using unvalidated `os.getenv()`.

---

### Milestone 2: Database Infrastructure
- **What was built**: 
  - `backend/db/base.py` (Base class + schemas)
  - `backend/db/engine.py` (Sync/Async engines)
  - `backend/db/session.py` (Session maker + FastAPI Dependency)
- **Why it exists**: Manages database connection lifecycles, pooling, and session isolation.
- **Core Decisions**:
  - `asyncpg` (FastAPI runtime) & `psycopg2` (Alembic sync migrations).
  - Pool size: 5 (max 10 overflow) for development; supports pre-ping to clean stale connections.
  - `expire_on_commit=False`: Prevents lazy-load errors in async contexts.
- **Enterprise Alternatives**: PgBouncer (external connection pooling).
- **Common Mistake**: Creating database engine instances inside functions (causes connection exhaustion).

---

### Milestone 3: Database Models
- **What was built**: 7 ORM models in `backend/models/` matching the raw Olist dataset.
- **Why it exists**: Represents the raw data mirror in PostgreSQL with constraints and relationships.
- **Core Decisions**:
  - Natural keys (string PKs) matching CSV files to maintain simple data lineage.
  - Composite PKs for `order_items` and `payments` to match natural CSV boundaries.
  - `Numeric(10, 2)` for prices and values to avoid floating-point math errors.
  - `lazy="selectin"` for fast relation loading without N+1 queries.
- **Normal Form**: 3NF (Third Normal Form).
- **Common Mistake**: Using binary `Float` for monetary columns (causes fractional cents rounding errors).

---

### Milestone 4: Alembic Migrations
- **What was built**: `alembic.ini`, `alembic/env.py`, and migration scripting templates.
- **Why it exists**: Tracks database schema versions sequentially and lets you apply upgrades/downgrades.
- **Core Decisions**:
  - Standard synchronous psycopg2 connection for Alembic.
  - Automates schema creation (`raw`, `curated`, etc.) in `env.py` before tables are created.
  - Standardizes autogenerate by importing all models inside `env.py`.
- **Common Mistake**: Forgetting to import models in `env.py` (results in Alembic generating blank migrations or trying to drop existing tables).

---

### Milestone 5: Data Ingestion Framework
- **What was built**: A modular pipeline in `data_pipeline/ingestion/` (`base.py`, individual entity scripts, and `loader.py`).
- **Why it exists**: Loads and validates messy raw CSVs into PostgreSQL while keeping referential integrity intact.
- **Core Decisions**:
  - Base class (`BaseIngester`) controls core file validation, Pandas reading, deduplication, and bulk-inserts to keep code DRY.
  - Topological sorting in `loader.py` (ingests independent tables like customers/sellers first, then orders, then items) to avoid FK constraint crashes.
  - Idempotent: Skips duplicate rows by checking against existing database primary keys before run.
  - SQLAlchemy Core bulk `insert()` to bypass slow ORM object overhead.
- **Enterprise Alternatives**: Apache Airflow, Prefect, AWS Glue.

---

### Milestone 6: Centralized Logging
- **What was built**: Structured logging using `structlog` in `backend/logging.py`.
- **Why it exists**: Replaces unstructured plain text logs (`print()`) with structured, queryable JSON logs in production.
- **Core Decisions**:
  - Outputs JSON in production (easily parsed by Datadog/ELK) and colored text in dev (easily read by humans).
  - Context manager `log_execution_time` to automatically calculate and log runtime for pipeline steps.
  - Standard library routing: Third-party logs (Uvicorn, SQLAlchemy) are intercepted and formatted structuredly.
- **Common Mistake**: String interpolation (`f"..."`) inside logs, which stops log systems from indexing events.
