# Interview Guide

> Technical interview questions organized by sprint and topic.

---

## Sprint 1 — Database Foundation (Milestones 2 & 3)

### Database Infrastructure

**Q1: What is a connection pool and why is it critical for production applications?**

A connection pool maintains a set of pre-established database connections that are reused across requests. Creating a new TCP connection for every query takes ~20–50ms (TCP handshake, TLS negotiation, PostgreSQL auth). A pool amortizes this cost to zero for all but the first 5 connections. Without pooling, a 500 RPS API would attempt 500 simultaneous connections — exceeding PostgreSQL's `max_connections` (default: 100) and crashing the database.

**Q2: Explain the difference between `asyncpg` and `psycopg2`. Why does this project need both?**

`asyncpg` is a native async PostgreSQL driver that integrates with Python's `asyncio` event loop. It never blocks the thread — while waiting for a query result, the event loop can handle other requests. `psycopg2` is synchronous: it blocks the calling thread until the query completes. This project needs both because FastAPI is async-native (requires `asyncpg`) but Alembic's migration runner is synchronous (requires `psycopg2`). Using `asyncpg` with Alembic would raise `MissingGreenlet` errors.

**Q3: What does `pool_pre_ping=True` do, and when would you disable it?**

It sends a lightweight `SELECT 1` before handing a connection to the application. If the connection was closed by the database (e.g., after a restart or idle timeout), the pool discards it and creates a new one instead of handing out a dead connection. You might disable it in ultra-high-throughput systems where the ~1ms overhead per checkout is measurable and you prefer to handle `OperationalError` at the application level.

**Q4: What is `expire_on_commit` and why is it set to `False` in async applications?**

When `expire_on_commit=True` (the default), SQLAlchemy marks all loaded attributes as expired after `session.commit()`. The next attribute access triggers a lazy load to refresh the data. In async code, this lazy load would use synchronous I/O on an async event loop, raising a `MissingGreenlet` exception. Setting it to `False` means attributes retain their in-memory values after commit — safe and predictable in async contexts.

**Q5: What is the Unit of Work pattern and how does SQLAlchemy implement it?**

The Unit of Work pattern tracks all changes (inserts, updates, deletes) made within a business transaction and flushes them to the database in a single coordinated operation. SQLAlchemy implements this through the `Session` object. When you call `session.add()`, the object is tracked. When you call `session.commit()`, all pending changes are flushed in a single database transaction. If anything fails, `session.rollback()` reverts everything — maintaining ACID guarantees.

---

### Database Models & Normalization

**Q6: Why use composite primary keys for `order_items` and `payments` instead of a surrogate `id` column?**

`order_item_id` (1, 2, 3...) is only unique within its parent order — `item_id=1` exists in thousands of orders. A composite PK `(order_id, order_item_id)` encodes this domain constraint directly in the schema. A surrogate `id SERIAL` would hide the constraint, allowing application bugs to insert `order_item_id=1` twice for the same order without a database-level violation. Composite PKs make invalid states unrepresentable.

**Q7: Why use `Numeric(10,2)` instead of `Float` for monetary values?**

IEEE 754 floating-point cannot represent all decimal fractions exactly. `0.1 + 0.2 = 0.30000000000000004` in float arithmetic. For an e-commerce platform processing millions of transactions, this rounding error accumulates. `Numeric(10,2)` uses exact fixed-point decimal arithmetic — `0.1 + 0.2 = 0.3` — which is required for financial correctness. Banks and payment systems universally use fixed-point or integer-cents representation.

**Q8: Explain the difference between `customer_id` and `customer_unique_id`. How does this affect ML feature engineering?**

`customer_id` is a per-order identifier — each time a customer places an order, they receive a new `customer_id`. `customer_unique_id` is the permanent business identifier that links the same person across all orders. For ML features like Customer Lifetime Value or churn prediction, you must aggregate by `customer_unique_id`, not `customer_id`. Aggregating by `customer_id` would treat each order as a separate customer, producing meaningless features.

**Q9: What is the difference between 1NF, 2NF, and 3NF? Is the raw schema in 3NF?**

- **1NF**: All columns contain atomic (scalar) values. No arrays, no nested objects. ✅
- **2NF**: Every non-key column depends on the entire primary key (no partial dependencies). This matters for composite PKs — `price` in `order_items` depends on `(order_id, order_item_id)`, not just `order_id`. ✅
- **3NF**: No transitive dependencies — non-key columns don't depend on other non-key columns. Technically, `customer_city` depends on `customer_zip_code_prefix` (a transitive dependency), so the raw schema has a minor 3NF violation. This is intentional: the raw layer mirrors the source data. The curated layer would normalize this.

**Q10: Why use `lazy="selectin"` instead of `lazy="joined"` or `lazy="subquery"` for relationships?**

- `lazy="joined"` creates a JOIN — efficient for one-to-one, but for one-to-many it produces duplicate parent rows in the result set (one per child), increasing data transfer.
- `lazy="subquery"` loads related objects in a subquery — can be slow with complex filters.
- `lazy="selectin"` loads related objects with `SELECT ... WHERE parent_id IN (...)` — a single flat query with no JOINs. It's the most efficient strategy for one-to-many relationships in async contexts because it avoids Cartesian products and works naturally with async sessions.
