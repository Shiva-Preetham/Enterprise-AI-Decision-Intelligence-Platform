"""
Customer model — raw.customers.

Source: olist_customers_dataset.csv
Columns: customer_id, customer_unique_id, customer_zip_code_prefix,
         customer_city, customer_state

Design Notes:
    - customer_id is the per-order identifier (PK). Each time a customer
      places an order, they receive a new customer_id mapped to their
      permanent customer_unique_id.
    - customer_unique_id is the canonical business identifier. It links
      a customer across multiple orders and is the key used for ML
      features like lifetime value and churn prediction.
    - An index on customer_unique_id supports fast lookups by business ID
      without changing the natural primary key from the source data.
"""

from __future__ import annotations

from sqlalchemy import Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.base import SCHEMA_RAW, Base


class Customer(Base):
    """Raw customer records from Olist e-commerce dataset.

    Each row represents one customer_id (per-order). Multiple customer_id
    values may map to the same customer_unique_id (the real person).

    Relationships:
        orders: All orders placed by this customer_id.
    """

    __tablename__ = "customers"
    __table_args__ = (
        Index("ix_raw_customers_unique_id", "customer_unique_id"),
        Index("ix_raw_customers_zip", "customer_zip_code_prefix"),
        Index("ix_raw_customers_state", "customer_state"),
        {"schema": SCHEMA_RAW},
    )

    # Primary key — per-order customer identifier
    customer_id: Mapped[str] = mapped_column(
        String(32), primary_key=True,
    )

    # Canonical business identifier — links same person across orders
    customer_unique_id: Mapped[str] = mapped_column(
        String(32), nullable=False,
    )

    customer_zip_code_prefix: Mapped[str] = mapped_column(
        String(10), nullable=False,
    )

    customer_city: Mapped[str] = mapped_column(
        String(100), nullable=False,
    )

    customer_state: Mapped[str] = mapped_column(
        String(2), nullable=False,
    )

    # ---- Relationships -------------------------------------------------------
    orders: Mapped[list["Order"]] = relationship(
        "Order", back_populates="customer", lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Customer(id={self.customer_id!r}, unique={self.customer_unique_id!r})>"


# Avoid circular import — Order is used as a string reference above.
from backend.models.orders import Order  # noqa: E402, F401
