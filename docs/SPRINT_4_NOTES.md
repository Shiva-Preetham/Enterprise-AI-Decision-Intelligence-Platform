# Sprint 4 Notes: Enterprise FastAPI Backend

## Objective
Build a production-grade FastAPI backend that exposes the Customer Intelligence Platform via REST APIs.

## Architecture
The backend strictly adheres to Clean Architecture and SOLID principles.

### Layers
1. **Routers (`backend/api/v1/`)**: Handles HTTP requests, path parameters, and query strings. Immediately delegates business logic to Services.
2. **Services (`backend/services/`)**: Orchestrates business logic, makes predictions via ML components, and aggregates data.
3. **Repositories (`backend/repositories/`)**: Manages all SQLAlchemy database queries. Services never write raw SQL or interact directly with the ORM.
4. **Schemas (`backend/schemas/`)**: Pydantic V2 DTOs (Data Transfer Objects) ensure that SQLAlchemy ORM objects never leak to the client, preventing lazy-loading bugs during serialization.

### Features Implemented
- **API Versioning**: All endpoints are prefixed with `/api/v1/`.
- **Dependency Injection**: Database sessions, repositories, services, and ML artifacts are injected using FastAPI's `Depends()`.
- **Centralized Error Handling**: Custom exceptions (`PlatformError`, `ResourceNotFoundError`) caught globally, returning standardized JSON responses.
- **Middleware**: 
  - `RequestIDMiddleware`: Injects UUIDs for tracing.
  - `ObservabilityMiddleware`: Logs method, endpoint, and execution time using `structlog`.
- **Startup Caching**: The ML Model (`best_model.pkl`) and `SHAPExplainer` are loaded into memory *once* during FastAPI's `@asynccontextmanager lifespan` hook.

## Endpoints
- `/api/v1/health`: Returns API, Database, and Model status.
- `/api/v1/customers`: Paginated customer list.
- `/api/v1/customers/{id}/profile`: The **Customer 360** endpoint returning profile, features, and risk score.
- `/api/v1/customers/{id}/timeline`: Chronological events (orders, reviews).
- `/api/v1/predict`: Generates a churn probability on the fly.
- `/api/v1/predict/{id}/explanation`: Returns SHAP waterfalls (positive/negative contributors).
- `/api/v1/analytics/dashboard`: Single request returning high-level metrics for the React frontend.
- `/api/v1/model/performance`: Exposes underlying ML algorithm metrics.
