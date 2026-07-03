from datetime import datetime

# Feature Engineering Constants
CHURN_THRESHOLD_DAYS = 90
RECENT_WINDOW_DAYS = 90
OBSERVATION_DATE = datetime(2018, 9, 3)  # Just after the last order in the dataset

# Sentiment Thresholds
VADER_NEGATIVE_THRESHOLD = -0.05

# Feature Store Metadata
PIPELINE_VERSION = "1.0.0"
FEATURE_VERSION = "1.0.0"
