import json
from pathlib import Path
from backend.core.exceptions import ModelLoadError
from ml.config import MODELS_DIR

class ModelService:
    def __init__(self):
        self.metadata = self._load_metadata()

    def _load_metadata(self) -> dict:
        try:
            metadata_path = MODELS_DIR / "model_metadata.json"
            if metadata_path.exists():
                with open(metadata_path, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            raise ModelLoadError(f"Failed to read model metadata: {e}")

    def get_model_info(self) -> dict:
        return self.metadata

    def get_performance_metrics(self) -> dict:
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
            "PipelineVersion": self.metadata.get("PipelineVersion")
        }
