"""
Feature Engineering Pipeline Module.

Orchestrates the creation and validation of customer-level features.
"""

from .builder import build_feature_store

__all__ = ["build_feature_store"]
