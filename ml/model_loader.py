import pickle
from ml.config import MODELS_DIR

class ModelLoader:
    """Utility to load model artifacts for prediction."""

    @staticmethod
    def load_artifacts():
        with open(MODELS_DIR / "best_model.pkl", "rb") as f:
            model = pickle.load(f)
            
        with open(MODELS_DIR / "preprocessor.pkl", "rb") as f:
            preprocessor = pickle.load(f)
            
        with open(MODELS_DIR / "feature_names.pkl", "rb") as f:
            feature_names = pickle.load(f)
            
        return model, preprocessor, feature_names
