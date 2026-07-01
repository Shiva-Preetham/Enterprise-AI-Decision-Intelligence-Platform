"""
Seller model — raw.sellers.

Source: olist_sellers_dataset.csv
Columns: seller_id, seller_zip_code_prefix, seller_city, seller_state

Design Notes:
    - seller_id is the natural PK from the dataset.
    - Location fields mirror the customer location pattern.
    - Index on seller_state supports geographic analysis queries.
"""

from __future__ import annotations

from sqlalchemy import Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.base import SCHEMA_RAW, Base


class Seller(Base):
    """Raw seller records from Olist e-commerce dataset.

    Relationships:
        order_items: All order line items fulfilled by this seller.
    """

    __tablename__ = "sellers"
    __table_args__ = (
        Index("ix_raw_sellers_state", "seller_state"),
        Index("ix_raw_sellers_zip", "seller_zip_code_prefix"),
        {"schema": SCHEMA_RAW},
    )

    # Primary key
    seller_id: Mapped[str] = mapped_column(
        String(32), primary_key=True,
    )

    seller_zip_code_prefix: Mapped[str] = mapped_column(
        String(10), nullable=False,
    )

    seller_city: Mapped[str] = mapped_column(
        String(100), nullable=False,
    )

    seller_state: Mapped[str] = mapped_column(
        String(2), nullable=False,
    )

    # ---- Relationships -------------------------------------------------------
    order_items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem", back_populates="seller", lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Seller(id={self.seller_id!r}, city={self.seller_city!r})>"


# Avoid circular imports
from backend.models.order_items import OrderItem  # noqa: E402, F401
