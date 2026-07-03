import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import Session

from feature_engineering.base import BaseFeatureGenerator


class DeliveryFeatureGenerator(BaseFeatureGenerator):
    """Generates Delivery features."""

    def generate(self, session: Session) -> pd.DataFrame:
        query = text(
            """
            SELECT 
                c.customer_unique_id,
                o.order_estimated_delivery_date,
                o.order_delivered_customer_date
            FROM raw.customers c
            JOIN raw.orders o ON c.customer_id = o.customer_id
            WHERE o.order_status = 'delivered'
              AND o.order_delivered_customer_date IS NOT NULL
              AND o.order_estimated_delivery_date IS NOT NULL
            """
        )
        df = pd.read_sql(query, session.bind)
        if df.empty:
            return pd.DataFrame()

        df["est"] = pd.to_datetime(df["order_estimated_delivery_date"])
        df["act"] = pd.to_datetime(df["order_delivered_customer_date"])
        
        # Delay is actual - estimated. Positive means late.
        df["delivery_delay"] = (df["act"] - df["est"]).dt.total_seconds() / 86400.0
        df["is_late"] = df["delivery_delay"] > 0

        def aggregate_delivery(group):
            return pd.Series({
                "delivery_delay_avg": group["delivery_delay"].mean(),
                "late_delivery_rate": group["is_late"].mean(),
                "max_delivery_delay": group["delivery_delay"].max(),
            })

        features = df.groupby("customer_unique_id").apply(aggregate_delivery).reset_index()
        return features
