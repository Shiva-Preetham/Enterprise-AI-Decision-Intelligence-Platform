# Sprint 3 — Machine Learning Pipeline & Explainable AI Notes

---

## Sprint Goal
Build a complete, automated, enterprise-grade ML pipeline that predicts customer churn using the Feature Store built in Sprint 2. Incorporate multiple models, hyperparameter tuning, SHAP explainability, and a robust Model Registry.

---

## Preprocessing Strategy
- **Source**: `analytics.customer_feature_store` (No raw data reading).
- **Leakage Prevention**: Metadata columns (`computed_at`, `pipeline_version`, etc.) and the Primary Key (`customer_unique_id`) are explicitly dropped. 
- **Missing Values**: Handled via `SimpleImputer` (median for numerics, most frequent for categoricals).
- **Encoding**: Handled via `OneHotEncoder`.
- **Pipeline Integration**: Imputers and Encoders are wrapped in a Scikit-Learn `ColumnTransformer` to ensure test-time data receives the exact same transformations as training data, preventing skew.

---

## Model Selection & Tuning
We train four distinct models to evaluate performance tradeoffs:
1. **Logistic Regression**: Linear baseline. Highly interpretable but struggles with non-linear relationships.
2. **Random Forest**: Ensemble of bagging trees. Robust to overfitting, handles non-linearities well.
3. **XGBoost**: Gradient Boosting Machine. Typically the highest performing tabular model, builds sequential trees to correct errors of previous trees.
4. **LightGBM**: Leaf-wise tree growth algorithm. Extremely fast and memory efficient on large datasets.

**Tuning**: Used `RandomizedSearchCV` instead of `GridSearchCV` to explore hyperparameter space faster in this local environment.

---

## Model Evaluation Metrics
Why do we track so many metrics? 
- **Accuracy**: Often misleading in churn (highly imbalanced datasets). If 95% of customers don't churn, a naive model predicting "Will Not Churn" is 95% accurate but completely useless.
- **Precision**: Out of all predicted churners, how many actually churned? (Crucial if retention campaigns are expensive).
- **Recall**: Out of all actual churners, how many did we find? (Crucial if losing a customer is highly expensive).
- **F1-Score**: Harmonic mean of Precision and Recall.
- **ROC AUC**: Area Under the Receiver Operating Characteristic Curve. Represents the probability that the model ranks a random positive example higher than a random negative one. We use this as our **primary selection metric** because it is threshold-invariant.
- **PR AUC**: Best evaluated via Precision-Recall Curve when datasets are heavily imbalanced.

---

## Explainability (SHAP)
**SHapley Additive exPlanations (SHAP)** provides game-theoretic feature attribution.
Why not just use Scikit-Learn's `feature_importances_`?
- Standard feature importance tells you a feature is "important" globally, but not *how* it affects a specific customer (positive or negative impact).
- SHAP generates **local explanations** (Waterfall plots) showing exactly which features pushed a single customer's risk score up or down.

---

## Model Registry Architecture
Enterprise MLOps requires strict versioning and reproducibility. 
Our lightweight registry (`ml/registry.py`) saves:
1. `best_model.pkl`: The serialized estimator.
2. `preprocessor.pkl`: The exact fitted ColumnTransformer.
3. `shap_explainer.pkl`: For real-time explainability APIs later.
4. `model_metadata.json`: Crucial metadata mapping the model back to the exact code (`pipeline_version`) and data (`data_snapshot_date`) used to train it. 

---

## Prediction Pipeline
Inference (`ml/predict.py`) maps the raw probability output (0.0 to 1.0) into actionable business categories:
- **Low Risk** (<0.2)
- **Medium Risk** (0.2 - 0.5)
- **High Risk** (0.5 - 0.8)
- **Very High Risk** (>0.8)

This makes the ML output digestible for marketing and customer success teams.
