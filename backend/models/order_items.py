"""
OrderItem model — raw.order_items.

Source: olist_order_items_dataset.csv
Columns: order_id, order_item_id, product_id, seller_id,
         shipping_limit_date, price, freight_value

Design Notes:
    - Composite primary key (order_id, order_item_id) because order_item_id
      is a sequential integer within each order, not globally unique.
    - Foreign keys to orders, products, and sellers enforce referential integrity.
    - Numeric(10,2) for monetary values provides exact decimal arithmetic
      (IEEE 754 floats lose precision with currency).
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.base import SCHEMA_RAW, Base


class OrderItem(Base):
    """Raw order line-item records from Olist e-commerce dataset.

    Each row represents one product within an order. A single order
    can contain multiple items from different sellers.

    Relationships:
        order:   The parent order.
        product: The product in this line item.
        seller:  The seller fulfilling this line item.
    """

    __tablename__ = "order_items"
    __table_args__ = (
        Index("ix_raw_order_items_product_id", "product_id"),
        Index("ix_raw_order_items_seller_id", "seller_id"),
        {"schema": SCHEMA_RAW},
    )

    # Composite primary key
    order_id: Mapped[str] = mapped_column(
        String(32),
        ForeignKey(f"{SCHEMA_RAW}.orders.order_id"),
        primary_key=True,
    )

    order_item_id: Mapped[int] = mapped_column(
        Integer, primary_key=True,
    )

    # Foreign keys
    product_id: Mapped[str] = mapped_column(
        String(32),
        ForeignKey(f"{SCHEMA_RAW}.products.product_id"),
        nullable=False,
    )

    seller_id: Mapped[str] = mapped_column(
        String(32),
        ForeignKey(f"{SCHEMA_RAW}.sellers.seller_id"),
        nullable=False,
    )

    shipping_limit_date: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True,
    )

    price: Mapped[float] = mapped_column(
        Numeric(10, 2), nullable=False,
    )

    freight_value: Mapped[float] = mapped_column(
        Numeric(10, 2), nullable=False,
    )

    # ---- Relationships -------------------------------------------------------
    order: Mapped["Order"] = relationship(
        "Order", back_populates="order_items", lazy="selectin",
    )

    product: Mapped["Product"] = relationship(
        "Product", back_populates="order_items", lazy="selectin",
    )

    seller: Mapped["Seller"] = relationship(
        "Seller", back_populates="order_items", lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<OrderItem(order={self.order_id!r}, item={self.order_item_id})>"


# Avoid circular imports
from backend.models.orders import Order  # noqa: E402, F401
from backend.models.products import Product  # noqa: E402, F401
from backend.models.sellers import Seller  # noqa: E402, F401
