"""
MLOps Exceptions.
"""

class MLOpsError(Exception):
    """Base exception for MLOps module."""
    pass

class ModelNotFoundError(MLOpsError):
    """Raised when a specific model version is not found."""
    pass

class DriftAlert(MLOpsError):
    """Raised when data drift exceeds thresholds."""
    pass

class RollbackError(MLOpsError):
    """Raised when model rollback fails."""
    pass
