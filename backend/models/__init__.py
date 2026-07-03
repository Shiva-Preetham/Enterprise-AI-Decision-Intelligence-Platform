"""
Enterprise AI Customer Intelligence Platform — Models Package.

Imports all ORM models so that SQLAlchemy's metadata registry and
Alembic's autogenerate can discover them from a single import.

Usage:
    from backend.models import Customer, Order, Product
    # or
    import backend.models  # registers all models with Base.metadata

Design Decision:
    Importing all models here ensures Alembic's `target_metadata = Base.metadata`
    sees every table. Without this, autogenerate would produce empty migrations
    because models that are never imported are never registered.
"""

from backend.models.customers import Customer
from backend.models.order_items import OrderItem
from backend.models.orders import Order
from backend.models.payments import Payment
from backend.models.products import Product
from backend.models.reviews import Review
from backend.models.sellers import Seller
from backend.models.customer_feature_store import CustomerFeatureStore

__all__ = [
    "Customer",
    "Order",
    "OrderItem",
    "Payment",
    "Product",
    "Review",
    "Seller",
    "CustomerFeatureStore",
]
