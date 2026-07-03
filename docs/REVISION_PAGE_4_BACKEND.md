# Interview Revision Guide — Page 4
**Topic: Sprint 4 & Sprint 5 (Backend & Infrastructure)**

## Core Concepts Explained

**FastAPI**
A modern, high-performance Python web framework. We use it to build our backend APIs because of its native `async/await` support, incredible speed, and automatic Swagger documentation generation.

**REST APIs**
The interface connecting our frontend to our backend. They follow strict, resource-based URL conventions (e.g., `GET /api/v1/customers/{id}`) and utilize standard HTTP methods for communication.

**Customer 360**
A comprehensive profile endpoint aggregating a customer's raw database records, Feature Store metrics, recent timeline events, and live ML churn predictions into a single, unified JSON response.

**Redis**
An extremely fast, in-memory data store used as our caching layer. It serves frequently requested data (like dashboard metrics) in milliseconds, bypassing the slower PostgreSQL database.

**Read-through Cache**
A caching strategy implemented via Python decorators. The application checks Redis first; if the data is missing, it fetches it from PostgreSQL, saves it in Redis, and then returns it to the user.

**RabbitMQ**
A highly reliable message broker. It acts as the middleman, holding "task messages" (like a request to retrain the ML model) safely in a queue until a Celery worker is ready to process them.

**Celery**
A distributed task queue framework. It executes heavy operations (like batch inference) asynchronously, entirely outside of the FastAPI request-response cycle.

**Background Workers**
Independent Python processes running Celery. They constantly consume messages from RabbitMQ and perform the actual heavy lifting without slowing down or blocking the main API server.

**Task Queue**
A system for managing asynchronous workloads. FastAPI produces a task, RabbitMQ queues it, and Celery consumes it. The API immediately returns a `task_id` so the client can poll for status updates.
