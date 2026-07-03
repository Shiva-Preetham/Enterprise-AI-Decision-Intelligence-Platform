# Interview Revision Guide — Page 3
**Topic: Sprint 2 & Sprint 3 (Machine Learning)**

## Core Concepts Explained

**Feature Store**
A centralized PostgreSQL table (`analytics.customer_feature_store`) storing aggregated, point-in-time features. It guarantees the exact same feature engineering logic is used for both model training and live API inference.

**Feature Engineering**
The process of transforming raw transaction data (orders, payments, reviews) into predictive metrics (RFM scores, delivery delays). This translates raw data into a format that machine learning algorithms can understand.

**Churn Prediction**
A binary classification machine learning task predicting whether a customer will stop buying. It helps businesses proactively target high-risk customers with retention campaigns before they leave.

**Random Forest**
An ensemble ML algorithm that builds multiple decision trees in parallel and averages their predictions. It is highly robust against overfitting but can consume a lot of memory and be slow to train on massive datasets.

**XGBoost**
Extreme Gradient Boosting. It builds decision trees sequentially, where each new tree corrects the specific errors of the previous ones. It is our best-performing model for tabular data due to its speed and accuracy.

**LightGBM**
A gradient boosting framework developed by Microsoft. It uses a leaf-wise tree growth strategy rather than level-wise, making it exceptionally fast and highly memory-efficient for extremely large datasets.

**SHAP**
Shapley Additive Explanations. A game-theoretic approach that provides local explainability, telling us exactly *why* a specific customer is predicted to churn (e.g., "high delivery delay increased risk by 15%").

**Model Registry**
A local directory (`models/`) storing serialized `.pkl` files of our trained models, preprocessors, and metadata. This allows the FastAPI backend to load pre-trained intelligence without retraining on startup.

**Prediction Pipeline**
The live inference flow: The system loads a customer's features from the Feature Store, applies the trained `.pkl` preprocessor, passes the data to the XGBoost model, and returns the probability and SHAP explanation.
