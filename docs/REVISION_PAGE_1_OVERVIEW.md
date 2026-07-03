# Interview Revision Guide — Page 1
**Topic: Entire Project Overview**

## Problem
Enterprises collect massive amounts of customer transaction data but struggle to predict churn or extract actionable insights in real-time. Heavy ML tasks often block systems, and business stakeholders lack clear explanations for AI decisions.

## Solution
An end-to-end Enterprise AI Customer Intelligence Platform. It ingests raw data, engineers features into a centralized Feature Store, predicts churn using XGBoost, explains predictions via SHAP, and serves insights asynchronously via a high-performance FastAPI backend.

## Architecture
1. **Database Layer**: PostgreSQL stores raw transactions and the engineered Feature Store.
2. **Backend Layer**: FastAPI handles HTTP requests using Clean Architecture (Router -> Service -> Repository).
3. **Caching Layer**: Redis provides read-through caching for sub-millisecond responses.
4. **Asynchronous Layer**: RabbitMQ queues heavy ML workloads, which Celery workers process in the background.

## Data Flow
1. **Ingestion**: Raw CSVs are cleaned via Pandas and bulk-inserted into PostgreSQL.
2. **Engineering**: Data is aggregated into the `customer_feature_store` table.
3. **Training**: Python scripts train XGBoost, evaluate metrics, and save `.pkl` files to the Model Registry.
4. **Inference**: FastAPI loads the `.pkl` files, pulls features from PostgreSQL, runs predictions, and serves JSON to the client.

## Tech Stack
- **Backend**: Python, FastAPI, SQLAlchemy
- **Database**: PostgreSQL
- **Infrastructure**: Redis, RabbitMQ, Celery, Docker
- **Machine Learning**: Scikit-Learn, XGBoost, LightGBM, SHAP

## How to Explain the Project in Under 3 Minutes
> "I built an Enterprise AI Customer Intelligence Platform designed to predict customer churn and provide actionable insights. I started by engineering a robust data pipeline that cleans transactional data and feeds it into a PostgreSQL Feature Store. Using this data, I trained an XGBoost model and integrated SHAP to provide game-theoretic explainability—so business users know exactly *why* a customer might leave. 
> 
> To serve these predictions in production, I built a highly scalable backend using FastAPI. I implemented a clean three-tier architecture, utilizing Redis for read-through caching to keep dashboard load times under 2 milliseconds. Because ML tasks like batch inference are computationally heavy, I integrated RabbitMQ and Celery to process these tasks asynchronously in the background. This ensures the main API remains lightning-fast and perfectly mimics the architecture used at top tech and finance enterprises."
