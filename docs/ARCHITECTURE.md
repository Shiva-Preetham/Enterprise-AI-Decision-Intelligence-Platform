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

---

## Component Diagram

*Placeholder — will be populated with C4-level component diagrams as the system evolves.*

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

---

## Security Considerations

*Placeholder — will cover JWT auth, CORS, input validation, secrets management.*

---

## Deployment Architecture

*Placeholder — will document AWS deployment topology in Sprint 9.*
