import pandas as pd
from structlog import get_logger

logger = get_logger(__name__)

def validate_features(df: pd.DataFrame) -> bool:
    """Validates the generated feature store dataframe before insertion."""
    is_valid = True
    
    # 1. Check Primary Key
    if df["customer_unique_id"].isnull().any():
        logger.error("validation_failed", reason="Null customer_unique_id found")
        is_valid = False
        
    if df["customer_unique_id"].duplicated().any():
        logger.error("validation_failed", reason="Duplicate customer_unique_id found")
        is_valid = False
        
    # 2. Check Numeric Ranges
    if (df["recency_days"] < 0).any():
        logger.error("validation_failed", reason="Negative recency_days found")
        is_valid = False
        
    if (df["frequency_90d"] < 0).any():
        logger.error("validation_failed", reason="Negative frequency_90d found")
        is_valid = False
        
    if (df["monetary_90d"] < 0).any():
        logger.error("validation_failed", reason="Negative monetary_90d found")
        is_valid = False
        
    # 3. Check Review Scores
    if df["avg_review_score"].notnull().any():
        invalid_scores = df[(df["avg_review_score"] < 1) | (df["avg_review_score"] > 5)]
        if not invalid_scores.empty:
            logger.error("validation_failed", reason="avg_review_score out of bounds [1, 5]")
            is_valid = False

    if is_valid:
        logger.info("validation_passed", total_rows=len(df))
        
    return is_valid
