# Sprint 1 — Database Foundation

---

## Sprint Goal

Build a production-grade database foundation: configuration, PostgreSQL schemas, SQLAlchemy ORM, Alembic migrations, data ingestion, and structured logging.

---

## Milestones

### Milestone 1 — Application Configuration ✅

**What was built:**

[backend/config.py](../backend/config.py) — Centralized configuration using Pydantic Settings.

**Why it exists:**

Every production application needs a single source of truth for configuration. Hardcoding database credentials, API keys, or service URLs into source code creates security vulnerabilities and makes deployment across environments (dev, staging, production) impossible.

**Why this design was chosen:**

| Decision | Rationale |
|----------|-----------|
| Pydantic Settings over `os.getenv()` | Type validation at startup. A missing `DATABASE_PORT` fails immediately with a clear error instead of silently becoming `None` and crashing at runtime. |
| Computed `DATABASE_URL` from parts | Eliminates duplication. If you store both `DATABASE_HOST` and `DATABASE_URL`, they can drift. Computing the URL from parts makes it impossible for them to disagree. |
| `frozen=True` | Configuration should be immutable after startup. Prevents accidental runtime mutation that causes non-reproducible bugs. |
| `lru_cache` factory | Settings object is created once, validated once, reused forever. The factory pattern enables dependency injection in FastAPI (Sprint 3) and test mocking. |
| Module-level `settings` instance | Convenience for simple scripts. Production FastAPI code should use `Depends(get_settings)` for testability. |
| Separate sync/async URLs | Alembic requires a synchronous driver (`psycopg2`). FastAPI uses async (`asyncpg`). Providing both avoids runtime driver conflicts. |

**Enterprise alternatives:**

| Alternative | When to use |
|-------------|-------------|
| HashiCorp Vault | When secrets must be rotated automatically and audited (financial services) |
| AWS Secrets Manager | When deploying to AWS and need IAM-integrated secret rotation |
| Azure Key Vault | Microsoft ecosystem deployments |
| Consul + Vault | Service discovery + secret management in microservice architectures |
| Spring Cloud Config | Java/Spring ecosystem equivalent |

**Production configuration strategy:**

```
.env.example → committed to Git (template)
.env         → local dev only, never committed
Staging      → environment variables set by CI/CD pipeline
Production   → secrets from Vault/Secrets Manager, injected as env vars
```

**Common mistakes:**

| Mistake | Consequence |
|---------|-------------|
| Committing `.env` to Git | Secrets in Git history are permanent, even after deletion |
| Using `os.getenv()` without defaults | Returns `None` → `TypeError` at an unpredictable time |
| Not validating types | `DATABASE_PORT="abc"` passes with `os.getenv()`, fails with Pydantic |
| Mutable configuration | Code that modifies settings at runtime creates Heisenbugs |
| Monolithic URL strings | `DATABASE_URL` stored directly can't be decomposed for health checks |

---

### Milestone 2 — Database Infrastructure ✅

**What was built:**

| File | Purpose |
|------|---------|
| [backend/db/\_\_init\_\_.py](../backend/db/__init__.py) | Package init — re-exports `Base`, engines, and session factory |
| [backend/db/base.py](../backend/db/base.py) | `DeclarativeBase` and PostgreSQL schema constants |
| [backend/db/engine.py](../backend/db/engine.py) | Async engine (asyncpg) + sync engine (psycopg2) with connection pooling |
| [backend/db/session.py](../backend/db/session.py) | `AsyncSessionFactory` and `get_async_session()` DI generator |

**Why it exists:**

The database layer is the foundation for all data operations — ingestion, API queries, ML feature reads. Without a properly configured engine and session factory, every module would create its own database connection, leading to connection exhaustion, leaked transactions, and untestable code.

**Why this design was chosen:**

| Decision | Rationale |
|----------|-----------|
| SQLAlchemy 2.x `DeclarativeBase` (class) | Replaces the legacy `declarative_base()` factory. Provides native type-checker support with `Mapped[]` columns. |
| Dual engines (async + sync) | FastAPI and data pipelines use `asyncpg` for non-blocking I/O. Alembic cannot use async drivers — it requires `psycopg2`. |
| Connection pooling defaults | `pool_size=5, max_overflow=10` handles typical dev load. Production tuning is documented but not hardcoded. |
| `pool_pre_ping=True` | Emits `SELECT 1` before handing out a connection. Prevents "connection reset by peer" errors after database restarts. |
| `pool_recycle=1800` | Recycles connections every 30 minutes. Prevents stale connections in long-running processes (data pipelines). |
| `expire_on_commit=False` | After committing, accessing a model attribute in async code would trigger a synchronous lazy load — which raises an error. Disabling expire prevents this. |
| `async_sessionmaker` | SQLAlchemy 2.x replacement for the legacy `sessionmaker`. Returns `AsyncSession` instances that work with `async/await`. |
| `get_async_session()` generator | Yields a session in a `try/finally` block, guaranteeing cleanup. Maps directly to FastAPI's `Depends()` pattern. |
| Schema constants in `base.py` | Single source of truth. Models, migrations, and seed scripts all reference `SCHEMA_RAW`, never raw strings. |

**Enterprise alternatives:**

| Alternative | When to use |
|-------------|-------------|
| PgBouncer | External connection pooler for high-concurrency production (500+ connections) |
| AWS RDS Proxy | Managed connection pooling for AWS RDS/Aurora deployments |
| SQLAlchemy `NullPool` | For serverless (AWS Lambda) where connections can't be reused |
| Prisma / TypeORM | ORM alternatives in TypeScript ecosystems |
| Django ORM | Batteries-included alternative with tighter Django coupling |

**Common mistakes:**

| Mistake | Consequence |
|---------|-------------|
| Creating engines inside functions | New connection pool per call → connection exhaustion |
| Not using `pool_pre_ping` | Stale connections cause `OperationalError` after DB restarts |
| `expire_on_commit=True` with async | Accessing attributes after commit triggers sync I/O → `MissingGreenlet` error |
| Sharing sessions across requests | One request's rollback affects another request's data |
| No `pool_recycle` in long processes | Connections time out at the DB level → silent failures |

---

### Milestone 3 — Database Models ✅

**What was built:**

7 normalized ORM models in the `raw` schema:

| Model | Table | PK | FKs | Source CSV |
|-------|-------|----|-----|------------|
| [Customer](../backend/models/customers.py) | `raw.customers` | `customer_id` | — | `olist_customers_dataset.csv` |
| [Order](../backend/models/orders.py) | `raw.orders` | `order_id` | `customer_id` | `olist_orders_dataset.csv` |
| [OrderItem](../backend/models/order_items.py) | `raw.order_items` | `(order_id, order_item_id)` | `order_id`, `product_id`, `seller_id` | `olist_order_items_dataset.csv` |
| [Payment](../backend/models/payments.py) | `raw.payments` | `(order_id, payment_sequential)` | `order_id` | `olist_order_payments_dataset.csv` |
| [Product](../backend/models/products.py) | `raw.products` | `product_id` | — | `olist_products_dataset.csv` |
| [Review](../backend/models/reviews.py) | `raw.reviews` | `review_id` | `order_id` | `olist_order_reviews_dataset.csv` |
| [Seller](../backend/models/sellers.py) | `raw.sellers` | `seller_id` | — | `olist_sellers_dataset.csv` |

**Why it exists:**

The raw layer is a 1:1 mirror of the source CSV files in a relational database. This provides:
- Referential integrity (FKs prevent orphaned records)
- Indexed access patterns (no CSV scanning)
- Transactional guarantees (ACID)
- Foundation for curated/analytics layers in future sprints

**Why this design was chosen:**

| Decision | Rationale |
|----------|-----------|
| Preserve raw column names (e.g. `product_name_lenght`) | The raw layer is a faithful mirror of source data. Corrections belong in the curated layer. Changing column names in raw would break lineage tracking. |
| `customer_unique_id` indexed, not PK | The CSV uses `customer_id` as the per-order identifier. `customer_unique_id` is the business identifier. Keeping the CSV's natural PK preserves data lineage while the index enables fast business lookups. |
| Composite PKs for `order_items` and `payments` | `order_item_id` and `payment_sequential` are only unique within their parent order. A surrogate PK would hide this domain constraint. |
| `Numeric(10,2)` for monetary values | IEEE 754 floats lose precision with currency (e.g., `0.1 + 0.2 ≠ 0.3`). `Numeric` uses exact decimal arithmetic. |
| Nullable timestamps on orders | Orders in various lifecycle stages have missing timestamps (e.g., an order that was never delivered has no `order_delivered_customer_date`). |
| `Text` type for review comments | Review text can be arbitrarily long. `String(N)` would truncate or reject long reviews. |
| `lazy="selectin"` on relationships | Avoids N+1 queries by loading related objects in a second `SELECT ... IN (...)` query. More efficient than `joined` for one-to-many. |
| String PKs (not UUIDs or integers) | The Olist dataset uses 32-character hex strings. Using the natural key preserves data lineage and avoids a mapping layer. |

**Normalization analysis:**

The raw schema is in **3NF** (Third Normal Form):
- **1NF**: All columns contain atomic values (no arrays or nested structures)
- **2NF**: No partial dependencies — every non-key column depends on the full PK (important for composite PKs in `order_items` and `payments`)
- **3NF**: No transitive dependencies — `customer_city` depends on `customer_zip_code_prefix`, but in the raw layer we preserve the source structure

**Trade-offs:**

| Trade-off | Decision | Alternative |
|-----------|----------|-------------|
| Raw layer has denormalization (city/state + zip) | Accepted — raw mirrors source | Normalize in curated layer |
| String PKs instead of integer surrogates | Preserves lineage, costs more storage | Add surrogate `id SERIAL` columns |
| No soft deletes | Raw data is immutable (insert-only) | Add `deleted_at` for mutable tables |

### Milestone 4 — Alembic Migrations ✅

**What was built:**

| File | Purpose |
|------|---------|
| [alembic.ini](../alembic.ini) | Basic Alembic configuration. The DB URL here is overridden at runtime. |
| [alembic/env.py](../alembic/env.py) | Configures Alembic to read `backend.config.settings` and `Base.metadata`. |
| [alembic/script.py.mako](../alembic/script.py.mako) | Template for generated migrations. |

**Why it exists:**

Database schemas evolve. Without a migration tool, schema changes must be applied manually across all environments (dev, staging, prod), leading to inconsistencies and downtime. Alembic tracks schema versions and provides a way to upgrade and downgrade the database programmatically.

**Why this design was chosen:**

| Decision | Rationale |
|----------|-----------|
| Sync engine for Alembic | Alembic's migration runner does not support `asyncpg`. We use a separate `psycopg2` engine just for migrations. |
| Auto-schema creation | `env.py` runs `CREATE SCHEMA IF NOT EXISTS` for all our schemas before applying migrations. This prevents errors when a migration tries to create a table in a non-existent schema. |
| Importing all models in `env.py` | Alembic compares `Base.metadata` to the live database. If models aren't imported, they aren't registered with `Base`, and Alembic will think the tables should be dropped. |
| Offline mode support | `env.py` supports `--sql` generation. Required for enterprise deployments where DBAs must review SQL before it runs. |

**Common mistakes:**

| Mistake | Consequence |
|---------|-------------|
| Forgetting to import models | `alembic revision --autogenerate` drops all your tables. |
| Using asyncpg in alembic.ini | Alembic crashes with a `MissingGreenlet` error. |

---

### Milestone 5 — Data Ingestion Framework ✅

**What was built:**

A modular, dependency-ordered ingestion pipeline in `data_pipeline/ingestion/`.

| Component | Purpose |
|-----------|---------|
| [base.py](../data_pipeline/ingestion/base.py) | `BaseIngester` class handling file validation, CSV reading, duplicate removal, DB collision checks, and bulk inserts. |
| Entity Loaders | Subclasses (e.g., `customers.py`, `orders.py`) defining required columns and custom type casting (like converting strings to datetimes or handling empty strings as NULLs). |
| [loader.py](../data_pipeline/ingestion/loader.py) | Master script executing ingesters in topological order. |

**Why it exists:**

Raw data from CSVs is messy and has constraints (Foreign Keys). If we ingest `orders` before `customers`, the database will reject the inserts. A modular ingestion framework ensures data is validated, cleaned, and inserted in the correct order, with proper error handling and logging.

**Why this design was chosen:**

| Decision | Rationale |
|----------|-----------|
| Base class inheritance | Keeps code DRY. Entity classes only contain config (table name, filename, required columns) and custom cleaning logic. The complex deduplication and insert logic lives in `BaseIngester`. |
| Pandas for reading/cleaning | Fast CSV parsing and vectorized cleaning operations. |
| SQLAlchemy Core `insert()` | Bypasses the ORM for bulk inserts, significantly improving performance for millions of rows. |
| Topological sort | `loader.py` runs in this order: Customers, Sellers, Products → Orders → OrderItems, Payments, Reviews. This guarantees FK constraints are met. |
| Database-level deduplication | Checks the live database for existing Primary Keys before inserting. Prevents unique constraint violations if the pipeline runs twice. |

**Enterprise alternatives:**

| Alternative | When to use |
|-------------|-------------|
| Airflow / Prefect | Distributed, DAG-based orchestration with retries and scheduling. |
| dbt (data build tool) | For SQL-based transformations inside the data warehouse. |
| AWS Glue / EMR | Serverless Spark for massive scale (Terabytes+). |

---

### Milestone 6 — Centralized Logging ✅

**What was built:**

| File | Purpose |
|------|---------|
| [backend/logging.py](../backend/logging.py) | Structured logging framework using `structlog`. |

**Why it exists:**

`print()` statements are useless in production. Standard library logging outputs unstructured prose (e.g., `INFO: User 123 logged in`), which is hard to query in tools like Datadog or ELK. Structured logging outputs machine-readable JSON (e.g., `{"event": "login", "user_id": 123, "level": "info"}`).

**Why this design was chosen:**

| Decision | Rationale |
|----------|-----------|
| `structlog` library | Industry standard for structured logging in Python. |
| JSON in production, colored console in dev | Machines read JSON easily, humans read colored text easily. The environment dictates the renderer. |
| `log_execution_time` context manager | Standardizes how we measure performance across the codebase without scattering `time.time()` everywhere. |
| Stdlib integration | Routes standard library logs (like SQLAlchemy queries or Uvicorn logs) through structlog, ensuring a uniform log format for the entire application. |

**Common mistakes:**

| Mistake | Consequence |
|---------|-------------|
| Not intercepting standard library logs | Half your logs are JSON, the other half are plaintext, breaking your log aggregator. |
| String interpolation in logs | `logger.info(f"User {user_id} logged in")` prevents log aggregators from grouping events by type. |
