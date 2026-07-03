import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import Session
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from feature_engineering.base import BaseFeatureGenerator
from feature_engineering.constants import VADER_NEGATIVE_THRESHOLD


class ReviewFeatureGenerator(BaseFeatureGenerator):
    """Generates Review and Sentiment features."""

    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()

    def generate(self, session: Session) -> pd.DataFrame:
        query = text(
            """
            SELECT 
                c.customer_unique_id,
                r.review_score,
                r.review_comment_message,
                r.review_creation_date
            FROM raw.customers c
            JOIN raw.orders o ON c.customer_id = o.customer_id
            JOIN raw.reviews r ON o.order_id = r.order_id
            """
        )
        df = pd.read_sql(query, session.bind)
        if df.empty:
            return pd.DataFrame()

        df["review_creation_date"] = pd.to_datetime(df["review_creation_date"])
        df = df.sort_values(["customer_unique_id", "review_creation_date"])

        def get_sentiment(text_msg):
            if not isinstance(text_msg, str) or not text_msg.strip():
                return 0.0
            return self.analyzer.polarity_scores(text_msg)["compound"]

        # Apply VADER (batch or apply)
        df["sentiment_score"] = df["review_comment_message"].apply(get_sentiment)
        df["is_negative"] = df["sentiment_score"] < VADER_NEGATIVE_THRESHOLD
        df["is_score_negative"] = df["review_score"] <= 2

        def aggregate_reviews(group):
            last_review = group.iloc[-1]
            first_review = group.iloc[0]
            
            trend = last_review["review_score"] - first_review["review_score"]
            if len(group) == 1:
                trend = 0.0
                
            return pd.Series({
                "avg_review_score": group["review_score"].mean(),
                "last_review_score": last_review["review_score"],
                "review_score_trend": trend,
                "review_sentiment_score": group["sentiment_score"].mean(),
                "has_negative_comment": group["is_negative"].any(),
                "negative_review_ratio": group["is_score_negative"].mean(),
            })

        features = df.groupby("customer_unique_id").apply(aggregate_reviews).reset_index()
        return features
