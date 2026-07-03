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

### 3. Sprint 4: Enterprise FastAPI Backend
The API layer adheres strictly to Clean Architecture to separate concerns.

```text
Request -> Router (HTTP) -> Service (Business Logic) -> Repository (SQLAlchemy) -> DB
```

Key features:
- **Dependency Injection**: Passes the DB session and Singleton ML Models down the stack.
- **Middlewares**: `RequestIDMiddleware` injects UUIDs, `ObservabilityMiddleware` handles standardized request logging.
- **Strict DTOs**: Pydantic V2 Response models guarantee that raw ORM objects never leak to the client.
- **Global Error Handling**: Standardized error responses to prevent stack traces from reaching end-users.er architecture:

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
├── analytics  ← Sprint 2: Feature Store (`customer_feature_store`)
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

### Machine Learning Pipeline (Sprint 3)
```
Feature Store (PostgreSQL)
       │
       ▼
   Preprocessing (Imputers, OneHotEncoder)
       │
       ▼
   Model Training (RF, XGBoost, LightGBM) ◄── Hyperparameter Tuning (RandomizedSearchCV)
       │
       ▼
   Evaluation (ROC AUC, PR AUC) ──► SHAP Explainability
       │
       ▼
   Model Registry (models/)
```

---

## Technology Decisions

| Service | Tech Stack | Responsibility |
|---|---|---|
| **API Backend** | FastAPI, Uvicorn | High-performance REST APIs, Model Serving, dependency injection |
| **Database Layer**| PostgreSQL, asyncpg| High-performance ACID storage, normalized data |
| **Ingestion**   | Pandas, SQLAlchemy | ETL pipeline to move raw data into Postgres |
| **Feature Store**| SQL (Materialized) | Aggregated, point-in-time ML features |
| **ML Pipeline** | Scikit-Learn, XGBoost| Training, hyperparameter tuning, evaluation |
| **Explainability**| SHAP | Global and Local model interpretability |
| Sentiment Analysis     | VADER          | Fast, lexicon-based NLP for short texts         |
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
