import time
from datetime import datetime
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import insert, select, delete
from structlog import get_logger

from backend.db.engine import sync_engine
from backend.models.customer_feature_store import CustomerFeatureStore
from feature_engineering.constants import OBSERVATION_DATE, PIPELINE_VERSION, FEATURE_VERSION
from feature_engineering.delivery import DeliveryFeatureGenerator
from feature_engineering.geography import GeographyFeatureGenerator
from feature_engineering.label import LabelGenerator
from feature_engineering.payments import PaymentFeatureGenerator
from feature_engineering.products import ProductFeatureGenerator
from feature_engineering.reviews import ReviewFeatureGenerator
from feature_engineering.rfm import RFMFeatureGenerator
from feature_engineering.validators import validate_features
from feature_engineering.utils import coalesce

logger = get_logger(__name__)

GENERATORS = [
    RFMFeatureGenerator(),
    PaymentFeatureGenerator(),
    DeliveryFeatureGenerator(),
    ReviewFeatureGenerator(),
    ProductFeatureGenerator(),
    GeographyFeatureGenerator(),
    LabelGenerator(),
]

def build_feature_store() -> None:
    """Orchestrates the entire feature generation process."""
    logger.info("feature_store_build_started", 
                pipeline_version=PIPELINE_VERSION, 
                feature_version=FEATURE_VERSION)
    start_time = time.time()
    
    with Session(sync_engine) as session:
        # 1. Collect all distinct customer_unique_ids as a base
        base_df = pd.read_sql(
            "SELECT DISTINCT customer_unique_id FROM raw.customers", 
            session.bind
        )
        total_processed = len(base_df)
        logger.info("base_customers_loaded", count=total_processed)
        
        final_df = base_df
        
        # 2. Run all generators and join
        for gen in GENERATORS:
            gen_name = gen.__class__.__name__
            logger.info("running_generator", generator=gen_name)
            
            gen_start = time.time()
            features_df = gen.generate(session)
            gen_duration = time.time() - gen_start
            
            if not features_df.empty:
                final_df = final_df.merge(features_df, on="customer_unique_id", how="left")
                logger.info("generator_completed", generator=gen_name, duration_sec=round(gen_duration, 2))
            else:
                logger.warning("generator_empty", generator=gen_name)
                
        # 3. Handle missing values
        null_counts = final_df.isnull().sum().to_dict()
        
        # Fill numeric NaNs with appropriate defaults (e.g., 0)
        numeric_cols = final_df.select_dtypes(include=['number']).columns
        final_df[numeric_cols] = final_df[numeric_cols].fillna(0)
        
        # Fill boolean NaNs with False
        bool_cols = final_df.select_dtypes(include=['bool']).columns
        final_df[bool_cols] = final_df[bool_cols].fillna(False)

        # 4. Add Metadata
        final_df["feature_version"] = FEATURE_VERSION
        final_df["pipeline_version"] = PIPELINE_VERSION
        final_df["computed_at"] = datetime.utcnow()
        final_df["data_snapshot_date"] = OBSERVATION_DATE

        # 5. Validate Features
        logger.info("validating_features")
        if not validate_features(final_df):
            logger.error("validation_failed_aborting_build")
            return

        # 6. Idempotent Database Insertion (Delete existing + Bulk Insert)
        logger.info("writing_to_database")
        
        try:
            # Drop existing features to ensure idempotency
            session.execute(delete(CustomerFeatureStore))
            
            # Convert NaN to None for SQLAlchemy
            final_df = final_df.replace({pd.NA: None})
            # Some columns might still be object/nan, ensure clean insertion
            
            records = final_df.to_dict(orient="records")
            
            # Bulk insert
            session.execute(insert(CustomerFeatureStore), records)
            session.commit()
            
            duration = time.time() - start_time
            logger.info(
                "feature_store_build_completed",
                customers_processed=total_processed,
                features_generated=len(final_df.columns) - 1, # minus ID
                missing_values_handled=sum(null_counts.values()),
                duplicates_removed=0, # handled by merge/groupby
                execution_time_sec=round(duration, 2),
                feature_store_version=FEATURE_VERSION,
                pipeline_version=PIPELINE_VERSION
            )
            
        except Exception as e:
            session.rollback()
            logger.exception("database_write_failed", error=str(e))

if __name__ == "__main__":
    build_feature_store()
