"""
Product model — raw.products.

Source: olist_products_dataset.csv
Columns: product_id, product_category_name, product_name_lenght,
         product_description_lenght, product_photos_qty,
         product_weight_g, product_length_cm, product_height_cm,
         product_width_cm

Design Notes:
    - Column names preserve the original dataset spelling (e.g. "lenght"
      instead of "length") to maintain a 1:1 raw layer mapping. Corrections
      belong in the curated layer.
    - Dimension and weight columns are nullable because some products in
      the dataset have missing physical attributes.
    - product_category_name is nullable — some products lack categories.
"""

from __future__ import annotations

from sqlalchemy import Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.base import SCHEMA_RAW, Base


class Product(Base):
    """Raw product catalog records from Olist e-commerce dataset.

    Relationships:
        order_items: All order line items referencing this product.
    """

    __tablename__ = "products"
    __table_args__ = (
        Index("ix_raw_products_category", "product_category_name"),
        {"schema": SCHEMA_RAW},
    )

    # Primary key
    product_id: Mapped[str] = mapped_column(
        String(32), primary_key=True,
    )

    # Category — nullable because some products lack categorization
    product_category_name: Mapped[str | None] = mapped_column(
        String(100), nullable=True,
    )

    # NOTE: "lenght" is the original CSV spelling. Intentionally preserved
    # in the raw layer. Curated layer will correct to "length".
    product_name_lenght: Mapped[int | None] = mapped_column(
        Integer, nullable=True,
    )

    product_description_lenght: Mapped[int | None] = mapped_column(
        Integer, nullable=True,
    )

    product_photos_qty: Mapped[int | None] = mapped_column(
        Integer, nullable=True,
    )

    product_weight_g: Mapped[int | None] = mapped_column(
        Integer, nullable=True,
    )

    product_length_cm: Mapped[int | None] = mapped_column(
        Integer, nullable=True,
    )

    product_height_cm: Mapped[int | None] = mapped_column(
        Integer, nullable=True,
    )

    product_width_cm: Mapped[int | None] = mapped_column(
        Integer, nullable=True,
    )

    # ---- Relationships -------------------------------------------------------
    order_items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem", back_populates="product", lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Product(id={self.product_id!r}, category={self.product_category_name!r})>"


# Avoid circular imports
from backend.models.order_items import OrderItem  # noqa: E402, F401
