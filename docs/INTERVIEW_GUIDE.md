# Interview Guide

> Technical interview questions organized by sprint and topic (Sprint 1).

---

## Sprint 1 — Database Foundation (Milestones 2 & 3)

### Database Infrastructure

**Q1: What is a connection pool and why is it critical?**
- **Definition**: A cache of database connections kept open and reused.
- **Why it's critical**: Creating a new connection per request takes 20-50ms (TCP/TLS handshake, auth). A pool eliminates this latency and prevents exceeding PostgreSQL's connection limit (`max_connections`) under load.

**Q2: Explain the difference between `asyncpg` and `psycopg2`. Why do we need both?**
- **asyncpg**: Native async driver. It does not block the Python main thread during queries, allowing FastAPI to handle other incoming requests concurrenty.
- **psycopg2**: Standard synchronous driver.
- **Why both**: FastAPI uses `asyncpg` for non-blocking I/O, while Alembic's migration engine requires `psycopg2` because it runs synchronously.

**Q3: What does `pool_pre_ping=True` do?**
- **Function**: Executes a lightweight health check (`SELECT 1`) before handing a connection to the application.
- **Benefit**: If a connection died (e.g. database restart), it is discarded and replaced. Prevents random "connection reset" crashes in production.

**Q4: What is `expire_on_commit` and why is it set to `False` in async applications?**
- **Definition**: If `True`, SQLAlchemy refreshes model attributes with new database SELECTs after a commit.
- **Async impact**: Accessing an expired model attribute triggers an implicit synchronous query, raising a `MissingGreenlet` error on an async event loop. We set it to `False` to preserve in-memory values.

**Q5: What is the Unit of Work pattern and how does SQLAlchemy implement it?**
- **Definition**: A pattern that groups multiple database updates/inserts into a single transaction.
- **Implementation**: SQLAlchemy's `Session` tracks dirty/new objects and flushes them to the database in one single database roundtrip on `session.commit()`, ensuring transactional consistency (ACID).

---

### Database Models & Normalization

**Q6: Why use composite primary keys for `order_items` and `payments`?**
- **Domain Constraint**: Columns like `order_item_id` and `payment_sequential` are only unique *within* their parent order.
- **Benefit**: A composite key like `(order_id, order_item_id)` models this constraint directly in the schema, making duplicate records database-impossible without requiring slow secondary checks or surrogate keys.

**Q7: Why use `Numeric(10,2)` instead of `Float` for monetary values?**
- **Floats**: Use binary representation, causing rounding errors (e.g., `0.1 + 0.2 = 0.30000000000000004`).
- **Numeric**: Employs exact decimal fixed-point arithmetic. Critical for financial accuracy (no penny leaks).

**Q8: Explain the difference between `customer_id` and `customer_unique_id`. How does this affect ML?**
- **customer_id**: Generated per order. A returning customer gets a new ID every time they buy.
- **customer_unique_id**: The permanent customer identifier.
- **ML Impact**: Lifetime metrics (CLV, churn) must be grouped by `customer_unique_id`. Grouping by `customer_id` would treat a returning customer's purchases as completely separate users.

**Q9: What is the difference between 1NF, 2NF, and 3NF? Is the raw schema in 3NF?**
- **1NF**: Atomic values only (no arrays/JSON arrays).
- **2NF**: No partial key dependencies (every column depends on the *entire* PK).
- **3NF**: No transitive dependencies (no non-key column depends on another non-key column).
- **Raw status**: Mostly 3NF. It has a minor violation (city/state depending on zip code), but this is accepted to keep the raw layer a clean 1:1 mirror of the source CSVs.

**Q10: Why use `lazy="selectin"` instead of `lazy="joined"` or `lazy="subquery"`?**
- **selectin**: Loads relationships in a second fast query using `WHERE parent_id IN (...)`.
- **joined**: Performs a SQL JOIN, which causes duplicate parent data transfer (Cartesian product) on one-to-many relationships.
- **subquery**: Creates a complex nested SELECT, which is slow and hard to optimize.

---

## Sprint 1 — Advanced Topics (Milestones 4, 5 & 6)

### Migrations (Alembic)

**Q11: Why use Alembic instead of running raw SQL scripts for schema changes?**
- **Version Control**: Alembic tracks schema changes in linear version files.
- **Automation & Safety**: It guarantees all environments (dev, staging, prod) update in the exact same order and allows programmatic rollback (downgrade) on failures.

**Q12: What is Alembic's "offline mode" and why do enterprises require it?**
- **What it is**: Running migrations with `--sql` to output a SQL script instead of modifying the live database.
- **Why require it**: Many enterprises require database administrators (DBAs) to review, test, and run raw DDL scripts manually via secure deployment platforms, rather than allowing applications direct DDL access.

### Data Ingestion Pipeline

**Q13: Why does our ingestion framework use SQLAlchemy Core `insert()` instead of `session.add()`?**
- **Performance**: `session.add()` instantiates tracked ORM objects for every row, which is slow and memory-intensive for large datasets.
- **Core insert**: Sends raw bulk-insert payloads directly to the DB, speeding up ingestion by orders of magnitude.

**Q14: Explain "Topological Sort" in the context of database ingestion.**
- **Definition**: Ordering insert operations based on parent-child foreign key relationships.
- **Example**: We must ingest independent tables (`customers`, `sellers`, `products`) first, then `orders`, then dependent tables (`order_items`, `payments`, `reviews`) to avoid foreign key violations.

**Q15: How does the ingestion framework handle idempotency?**
- **Definition**: Ensuring the ingestion script can run multiple times without causing errors or duplicate rows.
- **Implementation**: Before inserting, the loader checks primary keys in the database and drops duplicate rows from the Pandas DataFrame.

**Q16: Why use Pandas for data cleaning before inserting into PostgreSQL?**
- **Benefit**: Optimized C-based vectorized operations make operations like stripping spaces, parsing dates, and handling missing values fast and clean, without slow row-by-row Python loops.

### Centralized Logging

**Q17: What is "Structured Logging" and why is `print()` inadequate for production?**
- **print()**: Outputs unstructured text, which is impossible to index or query at scale.
- **Structured**: Outputs key-value pairs (usually JSON). Log systems (Datadog/ELK) can parse and index these keys, enabling instantaneous query and filtering.

**Q18: Why render JSON in production but colored text in development?**
- **Production**: Log aggregators read JSON to automatically structure logs for dashboards and alerts.
- **Development**: Humans read colored, aligned console logs much faster than raw JSON strings.

**Q19: How do we prevent third-party library logs from breaking our structured log format?**
- **Solution**: We configure `structlog` to intercept and format all messages coming from standard library logging (e.g. SQLAlchemy, Uvicorn), routing them through the same JSON or Console formatter.

**Q20: What is a context-bound logger?**
- **Definition**: A logger instance that stores context variables (e.g. `request_id`, `user_id`).
- **Benefit**: Once bound, every log call automatically includes these fields without needing to pass them explicitly in every function call.

---

## Sprint 2 — Feature Engineering & Feature Store

**Q21: What is a Feature Store and why is it important in enterprise ML?**
- **Definition**: A centralized repository to store, manage, and serve engineered features for ML models.
- **Importance**: Prevents duplicate feature engineering across teams, ensures training and serving environments use identical feature logic (preventing training-serving skew), and provides historical point-in-time data for model training.

**Q22: What is the difference between an Offline and Online Feature Store?**
- **Offline**: Usually a data warehouse (like PostgreSQL or Snowflake) optimized for high-throughput batch reads to generate historical training datasets.
- **Online**: Usually an in-memory database (like Redis) optimized for low-latency point reads (single-record lookups) for real-time model inference.

**Q23: What is Data Leakage in Feature Engineering?**
- **Definition**: When information from outside the training dataset (or from the future) is accidentally used to construct features.
- **Prevention**: Strict adherence to a point-in-time `OBSERVATION_DATE` (e.g., stopping all feature aggregation at a specific date) ensures models don't "peek" into the future.

**Q24: Why is Idempotency critical in data pipelines?**
- **Definition**: Running the pipeline multiple times safely yields the same result without duplicating data or crashing.
- **Benefit**: If a scheduled Airflow/cron job fails halfway and restarts, it won't corrupt the database with duplicate rows.

**Q25: Why separate `pipeline_version` and `feature_version` in metadata?**
- **Feature Version**: Tracks changes to the business logic of the features (e.g., adding `max_delivery_delay`).
- **Pipeline Version**: Tracks changes to the infrastructure or orchestration code (e.g., optimizing a Pandas merge) without changing the mathematical output of the features.

---

## Sprint 3 — Machine Learning Pipeline & Explainable AI

**Q26: Why use ROC AUC instead of Accuracy for evaluating churn models?**
- **Issue with Accuracy**: Churn datasets are highly imbalanced (e.g., 90% retain, 10% churn). A naive model that always predicts "retain" has 90% accuracy but 0% predictive power.
- **ROC AUC**: Evaluates the model's ability to rank a random positive example higher than a random negative one, making it immune to class imbalance and probability thresholds.

**Q27: What is the Bias-Variance Tradeoff?**
- **Bias**: Error from erroneous assumptions in the learning algorithm (underfitting, e.g., Logistic Regression on non-linear data).
- **Variance**: Error from sensitivity to small fluctuations in the training set (overfitting, e.g., an unpruned Decision Tree).
- **Tradeoff**: As you increase model complexity, bias decreases but variance increases. The goal is the sweet spot minimizing total error.

**Q28: Explain the difference between GridSearchCV and RandomizedSearchCV.**
- **GridSearchCV**: Exhaustively tries every single combination in the parameter grid. Extremely slow for large spaces.
- **RandomizedSearchCV**: Samples a fixed number of combinations randomly from the grid. Statistically proven to find near-optimal parameters in a fraction of the compute time.

**Q29: Why use SHAP instead of Scikit-Learn's built-in `feature_importances_`?**
- **`feature_importances_`**: Only provides global importance (how often a feature is used to split trees). It doesn't tell you the *direction* (did high recency cause churn, or prevent it?).
- **SHAP**: Game-theoretic approach that provides both **global** importance and **local** explanations (e.g., predicting exactly *why* Customer X is a high churn risk).

**Q30: Why do we fit the imputer and scaler only on the training set, not the whole dataset?**
- **Data Leakage**: If you scale using the mean/variance of the entire dataset, information from the test set "leaks" into the training set, artificially inflating performance metrics and leading to disastrous real-world performance.
