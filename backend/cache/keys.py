"""
Enterprise AI Customer Intelligence Platform — Cache Key Builder.

Centralizes all cache key patterns. Every key is version-prefixed (`v1:`)
to allow future API versions to coexist without key collisions.

Key Design:
    v1:customer:{customer_id}
    v1:dashboard
    v1:prediction:{customer_id}
    v1:feature_store:{customer_id}
    v1:model_metadata
    v1:health

Pattern Invalidation:
    CacheKeys.customer_pattern() → "v1:customer:*"
    Used with SCAN + DEL for bulk invalidation.
"""

from __future__ import annotations

_VERSION_PREFIX = "v1"


class CacheKeys:
    """Typed cache key builder. All keys use a versioned prefix."""

    @staticmethod
    def customer(customer_id: str) -> str:
        return f"{_VERSION_PREFIX}:customer:{customer_id}"

    @staticmethod
    def customer_pattern() -> str:
        return f"{_VERSION_PREFIX}:customer:*"

    @staticmethod
    def dashboard() -> str:
        return f"{_VERSION_PREFIX}:dashboard"

    @staticmethod
    def prediction(customer_id: str) -> str:
        return f"{_VERSION_PREFIX}:prediction:{customer_id}"

    @staticmethod
    def prediction_pattern() -> str:
        return f"{_VERSION_PREFIX}:prediction:*"

    @staticmethod
    def feature_store(customer_id: str) -> str:
        return f"{_VERSION_PREFIX}:feature_store:{customer_id}"

    @staticmethod
    def feature_store_pattern() -> str:
        return f"{_VERSION_PREFIX}:feature_store:*"

    @staticmethod
    def model_metadata() -> str:
        return f"{_VERSION_PREFIX}:model_metadata"

    @staticmethod
    def health() -> str:
        return f"{_VERSION_PREFIX}:health"
