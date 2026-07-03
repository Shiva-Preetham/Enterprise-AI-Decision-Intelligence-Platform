import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import Session

from feature_engineering.base import BaseFeatureGenerator
from feature_engineering.constants import OBSERVATION_DATE, RECENT_WINDOW_DAYS


class RFMFeatureGenerator(BaseFeatureGenerator):
    """Generates Recency, Frequency, Monetary and Purchase features."""

    def generate(self, session: Session) -> pd.DataFrame:
        query = text(
            """
            SELECT 
                c.customer_unique_id,
                o.order_id,
                o.order_purchase_timestamp,
                SUM(oi.price) as order_value,
                COUNT(oi.order_item_id) as items_in_order
            FROM raw.customers c
            JOIN raw.orders o ON c.customer_id = o.customer_id
            LEFT JOIN raw.order_items oi ON o.order_id = oi.order_id
            WHERE o.order_status = 'delivered'
            GROUP BY c.customer_unique_id, o.order_id, o.order_purchase_timestamp
            """
        )
        df = pd.read_sql(query, session.bind)
        if df.empty:
            return pd.DataFrame()

        df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"])
        df["order_value"] = df["order_value"].fillna(0.0)
        df["items_in_order"] = df["items_in_order"].fillna(0)

        # Sort values to calculate gaps
        df = df.sort_values(["customer_unique_id", "order_purchase_timestamp"])
        df["prev_order_date"] = df.groupby("customer_unique_id")["order_purchase_timestamp"].shift(1)
        df["order_gap"] = (df["order_purchase_timestamp"] - df["prev_order_date"]).dt.days

        recent_cutoff = pd.to_datetime(OBSERVATION_DATE) - pd.Timedelta(days=RECENT_WINDOW_DAYS)
        
        # Build aggregations
        def aggregate_customer(group):
            last_order_date = group["order_purchase_timestamp"].max()
            recency = (pd.to_datetime(OBSERVATION_DATE) - last_order_date).days
            
            recent_orders = group[group["order_purchase_timestamp"] >= recent_cutoff]
            
            return pd.Series({
                "recency_days": max(0, recency),
                "frequency_90d": len(recent_orders),
                "monetary_90d": recent_orders["order_value"].sum(),
                "avg_order_value": group["order_value"].mean(),
                "total_lifetime_value": group["order_value"].sum(),
                "frequency_lifetime": len(group),
                "avg_lifetime_order_value": group["order_value"].mean(),
                "days_since_last_order": max(0, recency),
                "order_gap_trend": group["order_gap"].mean(),
                "total_orders": len(group),
                "avg_items_per_order": group["items_in_order"].mean(),
            })

        features = df.groupby("customer_unique_id").apply(aggregate_customer).reset_index()
        return features
