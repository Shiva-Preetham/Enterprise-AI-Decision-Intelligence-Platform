# Sprint 2 — Feature Engineering & Customer Feature Store Notes

---

## Sprint Goal
Build a modular feature engineering pipeline to transform raw, normalized transactional data into a denormalized customer-level analytical feature store. This table (`analytics.customer_feature_store`) acts as the single source of truth for ML model training (Sprint 3).

---

## What is a Feature Store?
A **Feature Store** is a centralized repository that allows data scientists to find, share, and reuse engineered features for ML models. 

### Offline vs Online Feature Stores
- **Offline Feature Store** (What we built): Stores historical feature values (usually in data warehouses or databases like PostgreSQL) to construct point-in-time training datasets. Optimized for high-throughput batch reads.
- **Online Feature Store**: Stores only the *latest* feature values (usually in fast key-value stores like Redis) for real-time model inference. Optimized for low-latency point reads.

---

## Architecture Decisions

| Component | Decision | Rationale |
|-----------|----------|-----------|
| Data Processing | Pandas | Vectorized operations are extremely fast in-memory for the 100k-row Olist dataset. Avoids complex, hard-to-test raw SQL logic. |
| DB Write | SQLAlchemy Core `insert()` | Skips the ORM object instantiation overhead to insert tens of thousands of rows quickly. |
| Modularity | Domain-Specific Modules | Kept `rfm`, `reviews`, `payments`, etc. separate. Prevents "god objects" and giant scripts. |
| Idempotency | Delete-before-Insert | The builder drops existing features before writing. Ensures running the pipeline twice doesn't crash or double-count. |
| Sentiment | VADER | Fast, lexicon-based sentiment analysis tuned for social media and short texts (like product reviews). No deep learning infrastructure needed. |

---

## Feature Lineage & Business Reasoning

### RFM & Purchase Features (`rfm.py`)
- **`recency_days`**: Days since last order. *Strongest churn signal.*
- **`frequency_90d` / `frequency_lifetime`**: Number of orders. *Identifies habitual buyers.*
- **`monetary_90d` / `avg_lifetime_order_value`**: Total spend. *Key to CLV (Customer Lifetime Value) and VIP segmentation.*
- **`order_gap_trend`**: Avg days between purchases. *Helps detect if a user's buying cycle is slowing down.*

### Payment Features (`payments.py`)
- **`preferred_payment_type`**: Most frequently used payment method. *Useful for targeted promotions (e.g. Credit Card rewards).*
- **`payment_type_changed`**: Boolean. *Can indicate financial stress or security concerns.*

### Delivery Features (`delivery.py`)
- **`delivery_delay_avg`**: Avg days actual delivery was past estimated delivery. *Service degradation indicator.*
- **`late_delivery_rate`**: % of late orders. *Strong predictor of customer dissatisfaction.*
- **`max_delivery_delay`**: The single worst delivery experience. *Often more predictive of churn than the average.*

### Review & Satisfaction Features (`reviews.py`)
- **`avg_review_score`**: Standard CSAT metric (1-5).
- **`review_sentiment_score`**: VADER compound score (-1 to 1) of the review text. *Captures nuance when the text is angry but the score is high.*
- **`negative_review_ratio`**: % of reviews scoring 1 or 2. *Highly correlated with churn.*

### Product & Geography (`products.py`, `geography.py`)
- **`distinct_categories`**: Breadth of customer interests.
- **`category_entropy`**: Information theory metric measuring predictability of purchase habits. 
- **`customer_state` / `customer_city`**: Useful for regional logistics ML models.

### Target Label (`label.py`)
- **`churn_label`**: 1 if the customer has made no purchase for 90 days after their *last* purchase within the observation window. 

---

## Data Leakage Prevention
Data leakage occurs when information from outside the training dataset (or from the future) is used to create the model. We prevent this by strictly using the `OBSERVATION_DATE` (e.g., September 3, 2018) as the hard cutoff for all feature aggregations, ensuring no future data "leaks" into historical features.

## Enterprise Architecture Comparison
Our implementation mimics a lightweight version of enterprise platforms like **Feast** or **Tecton**.
- **The Gap**: We lack an Online Store (Redis), streaming ingestion (Kafka), and automated data drift monitoring. (These are usually added in MLOps phases).
