import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import Session

from feature_engineering.base import BaseFeatureGenerator
from feature_engineering.utils import calculate_entropy


class ProductFeatureGenerator(BaseFeatureGenerator):
    """Generates Product and Category features."""

    def generate(self, session: Session) -> pd.DataFrame:
        query = text(
            """
            SELECT 
                c.customer_unique_id,
                p.product_category_name
            FROM raw.customers c
            JOIN raw.orders o ON c.customer_id = o.customer_id
            JOIN raw.order_items oi ON o.order_id = oi.order_id
            JOIN raw.products p ON oi.product_id = p.product_id
            WHERE p.product_category_name IS NOT NULL
            """
        )
        df = pd.read_sql(query, session.bind)
        if df.empty:
            return pd.DataFrame()

        def aggregate_products(group):
            categories = group["product_category_name"]
            dom = categories.mode()
            dom_cat = dom.iloc[0] if not dom.empty else None
            
            return pd.Series({
                "distinct_categories": categories.nunique(),
                "category_entropy": calculate_entropy(categories),
                "dominant_category": dom_cat,
            })

        features = df.groupby("customer_unique_id").apply(aggregate_products).reset_index()
        return features
