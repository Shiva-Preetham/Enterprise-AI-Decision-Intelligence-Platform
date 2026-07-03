import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import Session

from feature_engineering.base import BaseFeatureGenerator
from feature_engineering.constants import OBSERVATION_DATE, CHURN_THRESHOLD_DAYS


class LabelGenerator(BaseFeatureGenerator):
    """Generates Target Labels (Churn)."""

    def generate(self, session: Session) -> pd.DataFrame:
        query = text(
            """
            SELECT 
                c.customer_unique_id,
                MAX(o.order_purchase_timestamp) as last_purchase_date
            FROM raw.customers c
            JOIN raw.orders o ON c.customer_id = o.customer_id
            WHERE o.order_status = 'delivered'
            GROUP BY c.customer_unique_id
            """
        )
        df = pd.read_sql(query, session.bind)
        if df.empty:
            return pd.DataFrame()

        df["last_purchase_date"] = pd.to_datetime(df["last_purchase_date"])
        
        # A customer is churned if they have made no purchase for 90 days after their last purchase
        # within the observation window.
        obs_date = pd.to_datetime(OBSERVATION_DATE)
        
        # Calculate days since last purchase (from observation date)
        df["days_since_last"] = (obs_date - df["last_purchase_date"]).dt.days
        
        # 1 if churned, 0 otherwise
        df["churn_label"] = (df["days_since_last"] >= CHURN_THRESHOLD_DAYS).astype(int)

        features = df[["customer_unique_id", "churn_label"]]
        return features
