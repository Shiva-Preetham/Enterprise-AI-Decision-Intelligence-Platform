"""
Enterprise AI Customer Intelligence Platform — ML Model Loader.

Loads serialized model artifacts from disk for inference.
Uses instance attributes (not a static method) to be compatible with
FastAPI's dependency injection and singleton startup pattern.
"""

import pickle
from pathlib import Path
from structlog import get_logger

from ml.config import MODELS_DIR

logger = get_logger(__name__)


class ModelLoader:
    """Loads and holds all trained ML artifacts in memory.

    Designed to be instantiated once at application startup via the FastAPI
    lifespan hook and cached globally. Never instantiate per-request.

    Attributes:
        model: The best-performing trained classifier.
        preprocessor: The fitted Scikit-Learn ColumnTransformer.
        feature_names: Ordered list of features used during training.
        explainer: The fitted SHAP explainer (optional, may be None).
    """

    def __init__(self) -> None:
        self.model = None
        self.preprocessor = None
        self.feature_names = None
        self.explainer = None
        self._load()

    def _load(self) -> None:
        """Loads all artifacts from the models/ directory."""
        model_path = MODELS_DIR / "best_model.pkl"
        preprocessor_path = MODELS_DIR / "preprocessor.pkl"
        feature_names_path = MODELS_DIR / "feature_names.pkl"
        explainer_path = MODELS_DIR / "shap_explainer.pkl"

        if not model_path.exists():
            logger.warning("model_artifacts_not_found", path=str(MODELS_DIR))
            return

        logger.info("loading_ml_artifacts", path=str(MODELS_DIR))

        with open(model_path, "rb") as f:
            self.model = pickle.load(f)

        with open(preprocessor_path, "rb") as f:
            self.preprocessor = pickle.load(f)

        with open(feature_names_path, "rb") as f:
            self.feature_names = pickle.load(f)

        if explainer_path.exists():
            with open(explainer_path, "rb") as f:
                self.explainer = pickle.load(f)

        logger.info("ml_artifacts_loaded_successfully", algorithm=type(self.model).__name__)

    @property
    def is_loaded(self) -> bool:
        """Returns True if the model has been successfully loaded."""
        return self.model is not None

    @classmethod
    def load_artifacts(cls):
        loader = cls()
        return loader.model, loader.preprocessor, loader.feature_names
