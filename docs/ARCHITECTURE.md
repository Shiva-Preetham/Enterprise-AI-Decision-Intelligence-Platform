# Architecture Overview

> Detailed software architecture for the Enterprise AI Customer Intelligence Platform.

---

## System Context

### Configuration Layer (Sprint 1 — Milestone 1)

The platform uses a centralized configuration system built on `pydantic-settings`:

```
.env file → Environment Variables → Pydantic Settings → Application Code
```

- **Single source of truth**: All services read from `backend.config.settings`
- **Type-safe**: Invalid values (e.g. `DATABASE_PORT=abc`) fail at startup
- **Immutable**: `frozen=True` prevents runtime mutation
- **Computed URLs**: Database, Redis, and RabbitMQ URLs are derived from parts — no duplication
- **DI-ready**: `get_settings()` factory supports dependency injection and test mocking

### Database Layer (Sprint 1 — Milestones 2 & 3)

The database layer follows a three-tier architecture:

```
Application Code
      │
      ▼
  Session (unit of work)
      │
      ▼
  Engine (connection pool)
      │
      ▼
  PostgreSQL (asyncpg / psycopg2)
```

- **Dual engines**: Async engine (`asyncpg`) for runtime, sync engine (`psycopg2`) for Alembic migrations
- **Connection pooling**: 5 persistent connections + 10 overflow, with pre-ping health checks
- **Session-per-request**: Each FastAPI request or pipeline task gets its own session from the pool
- **expire_on_commit=False**: Prevents lazy-load exceptions in async context

### Schema Architecture

```
PostgreSQL
├── raw        ← Sprint 1: 1:1 mirror of source CSVs (7 tables)
├── curated    ← Future: cleaned, deduplicated, business-ready
├── analytics  ← Future: aggregations, feature store, ML outputs
└── platform   ← Future: app metadata, users, audit logs
```

### Entity-Relationship Diagram (raw schema)

```
┌──────────┐     ┌──────────┐     ┌──────────────┐
│ customers│────<│  orders  │────<│  order_items  │
└──────────┘     └────┬─────┘     └──┬────┬──────┘
                      │              │    │
                 ┌────┴─────┐   ┌────┴──┐ │
                 │ payments │   │products│ │
                 └──────────┘   └───────┘ │
                 ┌──────────┐   ┌────────┴┐
                 │ reviews  │   │ sellers  │
                 └──────────┘   └─────────┘
```

### Data Ingestion Framework (Sprint 1 — Milestone 5)

The data ingestion framework loads raw CSV files into the database while maintaining referential integrity.

```
CSV Files (data/raw/)
      │
      ▼
  Pandas (Validation & Cleaning)
      │
      ▼
  Deduplication (CSV + Database levels)
      │
      ▼
  SQLAlchemy Core (Bulk Insert)
```

- **Topological Sort**: Tables are ingested in dependency order (Customers → Orders → OrderItems) to avoid Foreign Key violations.
- **Idempotent**: Pipeline checks for existing primary keys before insertion, allowing safe reruns.

### Centralized Logging (Sprint 1 — Milestone 6)

The platform uses `structlog` for structured, machine-readable logging.

- **Development**: Renders colored console output for human readability.
- **Production**: Renders JSON for log aggregators (ELK, Datadog).
- **Integration**: Standard library logs (SQLAlchemy, Uvicorn) are intercepted and routed through structlog to ensure uniform formatting.

---

## Data Flow

*Placeholder — will document the end-to-end data flow from ingestion to dashboard.*

---

## Technology Decisions

| Decision               | Choice         | Rationale                                      |
|------------------------|----------------|-------------------------------------------------|
| API Framework          | FastAPI        | Async-native, auto-docs, Pydantic integration  |
| Database               | PostgreSQL     | ACID compliance, JSON support, mature ecosystem |
| Cache                  | Redis          | Sub-ms latency, pub/sub, data structures        |
| Message Queue          | RabbitMQ       | Reliable delivery, routing, management UI       |
| ML Framework           | scikit-learn   | Production-proven, interpretable models         |
| LLM Orchestration      | LangGraph      | Stateful agent graphs, tool calling             |
| Frontend               | React + Vite   | Component model, fast HMR, TypeScript support   |
| Containerization       | Docker Compose | Reproducible local dev, service orchestration   |
| ORM                    | SQLAlchemy 2.x | Async-native, type-safe Mapped columns          |
| Async DB Driver        | asyncpg        | Native async PostgreSQL, fastest Python driver  |
| Sync DB Driver         | psycopg2       | Required for Alembic (synchronous migrations)   |
| Migrations             | Alembic        | SQLAlchemy-native schema versioning             |
| Data Ingestion         | Pandas         | Fast CSV parsing, vectorized cleaning           |
| Structured Logging     | structlog      | JSON output for production, colored for dev     |

---

## Security Considerations

*Placeholder — will cover JWT auth, CORS, input validation, secrets management.*

---

## Deployment Architecture

*Placeholder — will document AWS deployment topology in Sprint 9.*
