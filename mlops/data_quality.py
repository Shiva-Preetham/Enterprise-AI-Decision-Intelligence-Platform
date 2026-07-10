"""
MLOps Data Quality checks.
Automated checks against the feature store.
"""
from typing import Dict, Any, List
import pandas as pd
from datetime import datetime
import structlog
from .repository import MLOpsRepository
from .schemas import DataQualityReport

logger = structlog.get_logger(__name__)

class DataQualityChecker:
    def __init__(self, repository: MLOpsRepository):
        self.repository = repository
        
    async def run_checks(self) -> DataQualityReport:
        """
        Runs quality checks on the entire customer feature store table.
        Checks for missing values, duplicates, and out-of-range values.
        """
        records = await self.repository.get_all_customer_features()
        
        if not records:
            return DataQualityReport(
                timestamp=datetime.utcnow(),
                total_rows=0,
                missing_value_rates={},
                duplicate_rows=0,
                out_of_range_features=[],
                schema_mismatches=[],
                overall_status="No data"
            )
            
        # Convert to Pandas for vectorized checks
        df = pd.DataFrame([{
            "customer_unique_id": r.customer_unique_id,
            "total_lifetime_value": r.total_lifetime_value,
            "average_order_value": r.average_order_value,
            "purchase_count": r.purchase_count,
            "days_since_last_purchase": r.days_since_last_purchase,
            "review_score_mean": r.review_score_mean,
            "freight_value_sum": r.freight_value_sum
        } for r in records])
        
        total_rows = len(df)
        
        # Missing values
        missing_rates = (df.isnull().sum() / total_rows).to_dict()
        
        # Duplicates
        duplicates = int(df.duplicated(subset=['customer_unique_id']).sum())
        
        # Out-of-range features (reuse range logic conceptually)
        # e.g., purchase_count cannot be negative, review_score must be 1-5
        out_of_range = []
        if (df['purchase_count'] < 0).any():
            out_of_range.append("purchase_count")
        if (df['review_score_mean'] < 1).any() or (df['review_score_mean'] > 5).any():
            out_of_range.append("review_score_mean")
            
        status = "healthy"
        if duplicates > 0 or len(out_of_range) > 0 or any(v > 0.1 for v in missing_rates.values()):
            status = "degraded"
            
        report = DataQualityReport(
            timestamp=datetime.utcnow(),
            total_rows=total_rows,
            missing_value_rates=missing_rates,
            duplicate_rows=duplicates,
            out_of_range_features=out_of_range,
            schema_mismatches=[],
            overall_status=status
        )
        
        logger.info("data_quality_checked", status=status, rows=total_rows)
        return report
