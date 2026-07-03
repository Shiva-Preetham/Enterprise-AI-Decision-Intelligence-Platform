"""
Centralized Configuration for ML Pipeline.
"""

from pathlib import Path

# Paths
ROOT_DIR = Path(__file__).parent.parent
MODELS_DIR = ROOT_DIR / "models"
REPORTS_DIR = ROOT_DIR / "reports"

# Create directories if they don't exist
MODELS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Training Config
RANDOM_STATE = 42
TEST_SIZE = 0.2
CV_FOLDS = 3  # Reduced for faster training in local/educational setup
SCORING_METRIC = "roc_auc"

# Features to drop before training
COLUMNS_TO_DROP = [
    "customer_unique_id",
    "feature_version",
    "pipeline_version",
    "computed_at",
    "data_snapshot_date",
]

TARGET_COLUMN = "churn_label"

# Risk Categories
RISK_BINS = [0.0, 0.2, 0.5, 0.8, 1.0]
RISK_LABELS = ["Low Risk", "Medium Risk", "High Risk", "Very High Risk"]
