import pickle
from datetime import datetime
from structlog import get_logger

from ml.config import MODELS_DIR
from ml.utils import save_json

logger = get_logger(__name__)

class ModelRegistry:
    """Handles serialization and metadata for models."""

    def save_model(self, model, preprocessor, feature_names, metrics, best_params, explainer, metadata_extras: dict):
        """Saves all artifacts and metadata to disk."""
        logger.info("saving_model_artifacts")
        
        # Save Pickle Artifacts
        with open(MODELS_DIR / "best_model.pkl", "wb") as f:
            pickle.dump(model, f)
            
        with open(MODELS_DIR / "preprocessor.pkl", "wb") as f:
            pickle.dump(preprocessor, f)
            
        with open(MODELS_DIR / "feature_names.pkl", "wb") as f:
            pickle.dump(feature_names, f)
            
        if explainer:
            with open(MODELS_DIR / "shap_explainer.pkl", "wb") as f:
                pickle.dump(explainer, f)

        # Save JSON Artifacts
        save_json(metrics, MODELS_DIR / "metrics.json")
        save_json(best_params, MODELS_DIR / "best_params.json")

        # Construct and Save Metadata
        metadata = {
            "Algorithm": type(model).__name__,
            "TrainingDate": datetime.utcnow().isoformat(),
            "EvaluationMetrics": metrics,
            **metadata_extras
        }
        save_json(metadata, MODELS_DIR / "model_metadata.json")
        
        logger.info("model_artifacts_saved", path=str(MODELS_DIR))
