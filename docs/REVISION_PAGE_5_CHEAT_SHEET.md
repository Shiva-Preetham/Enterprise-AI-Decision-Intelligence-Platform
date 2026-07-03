# Interview Revision Guide — Page 5
**Topic: Ultimate Interview Cheat Sheet**

## Top 50 Rapid-Fire Questions

**1. Why PostgreSQL?**
It's reliable, ACID-compliant, open-source, and perfectly handles the complex SQL aggregations required for our Feature Store.

**2. Why Redis?**
It stores data entirely in RAM, providing sub-millisecond response times for our dashboard metrics.

**3. Why RabbitMQ?**
It guarantees message delivery and prevents data loss if a background worker crashes during a 3-hour ML training job.

**4. Why Celery?**
It offloads computationally heavy tasks so our FastAPI endpoints remain lightning-fast and non-blocking.

**5. Why Feature Store?**
It guarantees the exact same feature engineering logic is used for historical training and real-time inference.

**6. Why SHAP?**
Because business stakeholders need to know *why* a customer is churning, not just the raw probability percentage.

**7. Why SQLAlchemy?**
It prevents SQL injection and allows us to write database queries in Python using the async paradigm.

**8. Why FastAPI?**
It is async-native, incredibly fast, and automatically generates Pydantic-validated Swagger documentation.

**9. Difference between Service and Repository?**
The Repository only talks to the database; the Service handles business logic and orchestration.

**10. Difference between Redis and RabbitMQ?**
Redis is a high-speed key-value cache; RabbitMQ is a durable message queue for task orchestration.

**11. What is Dependency Injection?**
Passing required objects (like DB sessions) directly into functions, making code modular and easily mockable for tests.

**12. What is a Read-through Cache?**
Checking the cache first, and if empty, querying the DB and updating the cache automatically before returning data.

**13. Why Background Workers?**
To prevent a 10-minute ML training job from blocking HTTP requests and crashing the API server.

**14. How does Customer 360 work?**
It aggregates DB records, Feature Store metrics, and real-time XGBoost predictions into one unified JSON response.

**15. How does the Prediction Pipeline work?**
It loads cached `.pkl` files, transforms the user's features, and outputs a churn probability.

**16. How does SHAP explain predictions?**
It uses game theory to calculate the exact positive or negative contribution of every single feature toward the final prediction.

**17. How would this scale to 100 million customers?**
Scale FastAPI horizontally via Kubernetes, partition PostgreSQL, and add more Celery worker nodes.

**18. What is a Connection Pool?**
A cache of database connections kept open to avoid the TCP handshake overhead on every API request.

**19. Why `asyncpg` instead of `psycopg2`?**
`asyncpg` doesn't block the Python thread, allowing FastAPI to handle thousands of concurrent connections.

**20. What is Data Leakage?**
Accidentally using information from the future (or test set) to train the model, inflating perceived accuracy.

**21. Why use ROC AUC instead of Accuracy?**
Churn is imbalanced (90% retain, 10% churn). ROC AUC measures ranking ability, ignoring class imbalance.

**22. What does XGBoost do better than Random Forest?**
It builds trees sequentially to correct prior errors, yielding higher accuracy and faster inference on tabular data.

**23. What is Idempotency?**
The ability to run a script (like data ingestion) multiple times without creating duplicate rows or crashing.

**24. What is Graceful Degradation?**
If Redis crashes, our CacheService intercepts the error and falls back to PostgreSQL without breaking the API.

**25. Why version cache keys (e.g., `v1:dashboard`)?**
To prevent key collisions if we deploy an API `v2` with a different data structure in the future.

**26. What is the Unit of Work pattern?**
Grouping multiple database inserts/updates into a single transaction (e.g. `session.commit()`) to guarantee ACID consistency.

**27. Why use Composite Primary Keys?**
To enforce domain constraints natively in the database (e.g. `order_id` + `order_item_id`) without needing slow secondary checks.

**28. Why `Numeric` instead of `Float` for money?**
Floats use binary representation causing rounding errors; Numeric provides exact decimal precision preventing financial leaks.

**29. What is offline Alembic mode?**
Generating raw SQL scripts (`--sql`) instead of executing migrations directly, a standard requirement in enterprise deployments.

**30. Why use SQLAlchemy Core `insert()` instead of `session.add()`?**
`session.add()` is slow for bulk operations because it tracks every object in memory; Core `insert()` bypasses ORM overhead for speed.

**31. What is Topological Sort in data ingestion?**
Inserting independent tables (Customers) before dependent tables (Orders) to prevent Foreign Key constraint violations.

**32. Why use Pandas for data cleaning?**
It utilizes fast, C-based vectorized operations to clean data instantly instead of slow row-by-row Python loops.

**33. What is Structured Logging?**
Outputting logs as JSON (via `structlog`) instead of plain text, allowing aggregators like Datadog to instantly query and index fields.

**34. Why do we separate Offline and Online Feature Stores?**
Offline (Postgres) is optimized for heavy batch queries (training); Online (Redis) is optimized for low-latency single reads (inference).

**35. What is the Bias-Variance Tradeoff?**
Finding the sweet spot between a model that underfits (high bias) and a model that overfits to training noise (high variance).

**36. Why RandomizedSearchCV instead of GridSearchCV?**
GridSearch tries every combination and is incredibly slow; RandomizedSearch statistically finds near-optimal hyperparameters much faster.

**37. Why scale features only on the training set?**
Scaling on the whole dataset leaks information from the test set into the training set, ruining the validity of the evaluation.

**38. Why return Pydantic DTOs instead of ORM objects?**
To prevent accidental leakage of sensitive fields (like passwords) and avoid async lazy-loading errors during serialization.

**39. What is RequestID Middleware?**
Injects a unique UUID into every request and log, allowing engineers to easily trace a specific user's error across microservices.

**40. Why do we need `task_acks_late=True` in Celery?**
It ensures a task is only acknowledged *after* successful completion, preventing data loss if a worker crashes mid-execution.

**41. How does Celery handle task routing?**
We define specific queues (e.g., `ml`, `analytics`) so we can assign different hardware (like GPUs for ML) to specific workloads.

**42. Why is Churn Prediction formulated as a binary classification problem?**
We want a simple Yes/No probability output (Will they churn?) to decide if a marketing retention campaign should be triggered.

**43. What is LightGBM's main advantage over XGBoost?**
LightGBM uses a leaf-wise tree growth strategy which makes it faster and more memory-efficient on extremely large datasets.

**44. How does `pool_pre_ping=True` prevent production crashes?**
It silently runs a `SELECT 1` health check before using a database connection, discarding it if it died (e.g. during a DB restart).

**45. What happens if a FastAPI endpoint does not use `async def`?**
It runs in a separate threadpool instead of the main async event loop, reducing the application's ability to handle high concurrency.

**46. How do you invalidate a Read-through Cache?**
Using a decorator (`@invalidate_cache`) that deletes specific Redis keys immediately after a database mutation occurs.

**47. Why are SHAP explanations considered "Local" explainability?**
Because they explain the exact feature contributions for a *single specific customer's* prediction, rather than just the model globally.

**48. Why do we use `.pkl` files?**
To serialize (save) trained Python machine learning objects to disk so they can be instantly loaded by the backend without retraining.

**49. How do you prevent Circular Imports in Python?**
By using absolute imports, delaying imports inside functions, and ensuring architecture flows downwards (Router -> Service -> Repo).

**50. What is the ultimate goal of this entire platform?**
To turn raw transactional data into proactive, explainable intelligence that drives business retention, at an enterprise scale.
