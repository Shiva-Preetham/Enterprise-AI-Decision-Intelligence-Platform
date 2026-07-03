import pandas as pd
# pyrefly: ignore [missing-import]
from sqlalchemy import text
from sqlalchemy.orm import Session

from feature_engineering.base import BaseFeatureGenerator


class GeographyFeatureGenerator(BaseFeatureGenerator):
    """Generates Geographic features."""

    def generate(self, session: Session) -> pd.DataFrame:
        query = text(
            """
            SELECT 
                c.customer_unique_id,
                c.customer_state,
                c.customer_city,
                o.order_purchase_timestamp
            FROM raw.customers c
            LEFT JOIN raw.orders o ON c.customer_id = o.customer_id
            """
        )
        df = pd.read_sql(query, session.bind)
        if df.empty:
            return pd.DataFrame()

        df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"])
        # We take the most recent known location for a customer
        df = df.sort_values(["customer_unique_id", "order_purchase_timestamp"])

        def aggregate_geo(group):
            last_record = group.iloc[-1]
            return pd.Series({
                "customer_state": last_record["customer_state"],
                "customer_city": last_record["customer_city"],
            })

        features = df.groupby("customer_unique_id").apply(aggregate_geo).reset_index()
        return features
