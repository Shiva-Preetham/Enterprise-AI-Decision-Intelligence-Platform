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

### Milestone 2 — Database Infrastructure

*Pending*

### Milestone 3 — Database Models

*Pending*

### Milestone 4 — Alembic Migrations

*Pending*

### Milestone 5 — Data Ingestion

*Pending*

### Milestone 6 — Logging

*Pending*
