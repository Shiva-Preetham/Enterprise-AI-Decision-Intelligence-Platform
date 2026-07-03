"""
Enterprise AI Customer Intelligence Platform — Model Service.

Reads model metadata from disk with caching. Metadata is loaded once
per ModelService lifetime (singleton via @lru_cache in dependencies.py).
"""

from __future__ import annotations

import json
from pathlib import Path

from structlog import get_logger

from backend.core.exceptions import ModelLoadError
from ml.config import MODELS_DIR

logger = get_logger(__name__)


class ModelService:
    """Reads and serves ML model metadata.

    The metadata file is read once at instantiation. Since dependencies.py
    uses @lru_cache, this effectively makes ModelService a singleton.
    """

    def __init__(self) -> None:
        self.metadata = self._load_metadata()

    def _load_metadata(self) -> dict:
        try:
            metadata_path = MODELS_DIR / "model_metadata.json"
            if metadata_path.exists():
                with open(metadata_path, "r") as f:
                    return json.load(f)
            return {}
        except Exception as exc:
            logger.warning("model_metadata_load_failed", error=str(exc))
            return {}

    def get_model_info(self) -> dict:
        """Returns raw model metadata dictionary."""
        return self.metadata

    def get_performance_metrics(self) -> dict:
        """Returns formatted performance metrics for the API."""
        metrics = self.metadata.get("EvaluationMetrics", {})
        return {
            "Algorithm": self.metadata.get("Algorithm", "Unknown"),
            "Accuracy": metrics.get("accuracy", 0.0),
            "Precision": metrics.get("precision", 0.0),
            "Recall": metrics.get("recall", 0.0),
            "F1": metrics.get("f1_score", 0.0),
            "ROC_AUC": metrics.get("roc_auc", 0.0),
            "TrainingDate": self.metadata.get("TrainingDate"),
            "FeatureVersion": self.metadata.get("FeatureVersion"),
            "PipelineVersion": self.metadata.get("PipelineVersion"),
        }

    def reload_metadata(self) -> None:
        """Force-reload metadata from disk. Called after model retraining."""
        self.metadata = self._load_metadata()
        logger.info("model_metadata_reloaded")
