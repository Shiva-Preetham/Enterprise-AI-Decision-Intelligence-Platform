"""
Review model — raw.reviews.

Source: olist_order_reviews_dataset.csv
Columns: review_id, order_id, review_score, review_comment_title,
         review_comment_message, review_creation_date,
         review_answer_timestamp

Design Notes:
    - review_id is the PK. While most orders have exactly one review,
      the dataset contains a small number of duplicate review_ids across
      different orders, so order_id is NOT part of the PK.
    - Comment title and message are nullable — many reviews have no text.
    - review_score is an integer 1–5 (star rating).
    - Text type for comment fields allows arbitrarily long review text.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.base import SCHEMA_RAW, Base


class Review(Base):
    """Raw customer review records from Olist e-commerce dataset.

    Relationships:
        order: The order being reviewed.
    """

    __tablename__ = "reviews"
    __table_args__ = (
        Index("ix_raw_reviews_order_id", "order_id"),
        Index("ix_raw_reviews_score", "review_score"),
        {"schema": SCHEMA_RAW},
    )

    # Primary key
    review_id: Mapped[str] = mapped_column(
        String(32), primary_key=True,
    )

    # Foreign key to orders
    order_id: Mapped[str] = mapped_column(
        String(32),
        ForeignKey(f"{SCHEMA_RAW}.orders.order_id"),
        nullable=False,
    )

    review_score: Mapped[int] = mapped_column(
        Integer, nullable=False,
    )

    review_comment_title: Mapped[str | None] = mapped_column(
        Text, nullable=True,
    )

    review_comment_message: Mapped[str | None] = mapped_column(
        Text, nullable=True,
    )

    review_creation_date: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True,
    )

    review_answer_timestamp: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True,
    )

    # ---- Relationships -------------------------------------------------------
    order: Mapped["Order"] = relationship(
        "Order", back_populates="reviews", lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Review(id={self.review_id!r}, score={self.review_score})>"


# Avoid circular imports
from backend.models.orders import Order  # noqa: E402, F401
