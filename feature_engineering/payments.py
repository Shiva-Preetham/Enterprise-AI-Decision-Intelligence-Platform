import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import Session

from feature_engineering.base import BaseFeatureGenerator


class PaymentFeatureGenerator(BaseFeatureGenerator):
    """Generates Payment features."""

    def generate(self, session: Session) -> pd.DataFrame:
        query = text(
            """
            SELECT 
                c.customer_unique_id,
                p.payment_type,
                p.payment_installments
            FROM raw.customers c
            JOIN raw.orders o ON c.customer_id = o.customer_id
            JOIN raw.payments p ON o.order_id = p.order_id
            """
        )
        df = pd.read_sql(query, session.bind)
        if df.empty:
            return pd.DataFrame()

        def aggregate_payments(group):
            preferred = group["payment_type"].mode()
            pref_type = preferred.iloc[0] if not preferred.empty else None
            
            distinct_types = group["payment_type"].nunique()
            
            return pd.Series({
                "preferred_payment_type": pref_type,
                "avg_installments": group["payment_installments"].mean(),
                "payment_type_changed": distinct_types > 1,
            })

        features = df.groupby("customer_unique_id").apply(aggregate_payments).reset_index()
        return features
