# Interview Revision Guide — Page 2
**Topic: Sprint 0 & Sprint 1 (Foundation)**

## Core Concepts Explained

**PostgreSQL**
The primary relational database used for storing both raw transactional data and the curated Feature Store. It provides ACID compliance and handles complex SQL aggregations effortlessly.

**SQLAlchemy**
The ORM (Object Relational Mapper) used to map Python classes to database tables. We use the async version (`asyncpg`) to prevent database queries from blocking the FastAPI event loop.

**Alembic**
The database migration tool used alongside SQLAlchemy. It tracks database schema changes in version control and allows safe, programmatic database upgrades across development and production environments.

**Pydantic**
A data validation library used to create strict Data Transfer Objects (DTOs). It ensures our APIs only receive and return exactly what is expected, automatically rejecting invalid JSON payloads.

**Repository Pattern**
A design pattern that separates database query logic from business logic. Our services call repositories (e.g., `CustomerRepository`), making it incredibly easy to swap databases or mock data for unit tests.

**Service Layer**
The middle layer containing all the core business logic (e.g., `CustomerService`). It orchestrates data from repositories, ML models, and Redis caches, keeping the API routers perfectly clean.

**Dependency Injection**
A software design pattern where FastAPI injects required dependencies (like database sessions or cached ML models) directly into endpoint functions. It removes global state and makes the code highly modular and testable.

**Connection Pool**
A cache of open database connections kept alive in the background. It prevents the massive latency penalty of executing a TCP/TLS handshake for every single API request, allowing the application to scale.
