"""
Payment model — raw.payments.

Source: olist_order_payments_dataset.csv
Columns: order_id, payment_sequential, payment_type,
         payment_installments, payment_value

Design Notes:
    - Composite primary key (order_id, payment_sequential) because a single
      order can have multiple payment methods (e.g., credit card + voucher).
    - payment_sequential is 1-indexed per order.
    - Numeric(10,2) for payment_value ensures exact currency arithmetic.
"""

from __future__ import annotations

from sqlalchemy import ForeignKey, Index, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.base import SCHEMA_RAW, Base


class Payment(Base):
    """Raw payment records from Olist e-commerce dataset.

    Each row represents one payment method used for an order. Customers
    can split payment across multiple methods.

    Relationships:
        order: The order this payment belongs to.
    """

    __tablename__ = "payments"
    __table_args__ = (
        Index("ix_raw_payments_type", "payment_type"),
        {"schema": SCHEMA_RAW},
    )

    # Composite primary key
    order_id: Mapped[str] = mapped_column(
        String(32),
        ForeignKey(f"{SCHEMA_RAW}.orders.order_id"),
        primary_key=True,
    )

    payment_sequential: Mapped[int] = mapped_column(
        Integer, primary_key=True,
    )

    payment_type: Mapped[str] = mapped_column(
        String(30), nullable=False,
    )

    payment_installments: Mapped[int] = mapped_column(
        Integer, nullable=False,
    )

    payment_value: Mapped[float] = mapped_column(
        Numeric(10, 2), nullable=False,
    )

    # ---- Relationships -------------------------------------------------------
    order: Mapped["Order"] = relationship(
        "Order", back_populates="payments", lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<Payment(order={self.order_id!r}, seq={self.payment_sequential}, "
            f"type={self.payment_type!r})>"
        )


# Avoid circular imports
from backend.models.orders import Order  # noqa: E402, F401
