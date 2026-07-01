"""
Order model — raw.orders.

Source: olist_orders_dataset.csv
Columns: order_id, customer_id, order_status, order_purchase_timestamp,
         order_approved_at, order_delivered_carrier_date,
         order_delivered_customer_date, order_estimated_delivery_date

Design Notes:
    - order_id is the natural PK from the source dataset.
    - customer_id is a FK to raw.customers, enforcing referential integrity.
    - Timestamp columns use nullable DateTime because some orders are
      not yet approved, delivered, etc. (the CSV has blank values).
    - Indexes on status and purchase_timestamp support common query patterns:
      "all delivered orders" and "orders in date range".
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.base import SCHEMA_RAW, Base


class Order(Base):
    """Raw order records from Olist e-commerce dataset.

    Each row represents one order. An order may contain multiple items
    (OrderItem), multiple payments (Payment), and one review (Review).

    Relationships:
        customer:    The customer who placed this order.
        order_items: Line items within this order.
        payments:    Payment records for this order.
        reviews:     Customer reviews for this order.
    """

    __tablename__ = "orders"
    __table_args__ = (
        Index("ix_raw_orders_customer_id", "customer_id"),
        Index("ix_raw_orders_status", "order_status"),
        Index("ix_raw_orders_purchase_ts", "order_purchase_timestamp"),
        {"schema": SCHEMA_RAW},
    )

    # Primary key
    order_id: Mapped[str] = mapped_column(
        String(32), primary_key=True,
    )

    # Foreign key to customers
    customer_id: Mapped[str] = mapped_column(
        String(32),
        ForeignKey(f"{SCHEMA_RAW}.customers.customer_id"),
        nullable=False,
    )

    order_status: Mapped[str] = mapped_column(
        String(20), nullable=False,
    )

    order_purchase_timestamp: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True,
    )

    order_approved_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True,
    )

    order_delivered_carrier_date: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True,
    )

    order_delivered_customer_date: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True,
    )

    order_estimated_delivery_date: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True,
    )

    # ---- Relationships -------------------------------------------------------
    customer: Mapped["Customer"] = relationship(
        "Customer", back_populates="orders", lazy="selectin",
    )

    order_items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem", back_populates="order", lazy="selectin",
    )

    payments: Mapped[list["Payment"]] = relationship(
        "Payment", back_populates="order", lazy="selectin",
    )

    reviews: Mapped[list["Review"]] = relationship(
        "Review", back_populates="order", lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Order(id={self.order_id!r}, status={self.order_status!r})>"


# Avoid circular imports — used as string references above.
from backend.models.customers import Customer  # noqa: E402, F401
from backend.models.order_items import OrderItem  # noqa: E402, F401
from backend.models.payments import Payment  # noqa: E402, F401
from backend.models.reviews import Review  # noqa: E402, F401
