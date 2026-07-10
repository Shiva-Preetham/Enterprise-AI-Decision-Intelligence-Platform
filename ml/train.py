import time
from typing import Dict, Any, Tuple
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from sklearn.model_selection import RandomizedSearchCV
from structlog import get_logger

from ml.config import RANDOM_STATE, CV_FOLDS, SCORING_METRIC

logger = get_logger(__name__)

# Search spaces for Hyperparameter Tuning
SEARCH_SPACES = {
    "RandomForest": {
        "n_estimators": [100, 200, 300],
        "max_depth": [5, 10, None],
        "min_samples_split": [2, 5, 10]
    },
    "XGBoost": {
        "n_estimators": [100, 200],
        "max_depth": [3, 5, 7],
        "learning_rate": [0.01, 0.1, 0.2],
        "subsample": [0.8, 1.0]
    },
    "LightGBM": {
        "n_estimators": [100, 200],
        "max_depth": [3, 5, 7],
        "learning_rate": [0.01, 0.1, 0.2],
        "num_leaves": [31, 50]
    }
}

class ModelTrainer:
    """Handles model training and hyperparameter tuning."""
    
    def __init__(self):
        self.models = {
            "LogisticRegression": LogisticRegression(random_state=RANDOM_STATE, max_iter=1000),
            "RandomForest": RandomForestClassifier(random_state=RANDOM_STATE),
            "XGBoost": XGBClassifier(random_state=RANDOM_STATE, eval_metric="logloss"),
            "LightGBM": LGBMClassifier(random_state=RANDOM_STATE)
        }
        self.trained_models = {}
        self.best_params = {}

    def train_all(self, X_train, y_train):
        """Trains all models, tuning hyperparameters for tree-based models."""
        for name, model in self.models.items():
            logger.info("training_model", model=name)
            start_time = time.time()
            
            if name in SEARCH_SPACES:
                # Perform RandomizedSearchCV for hyperparameter tuning
                logger.info("tuning_hyperparameters", model=name)
                search = RandomizedSearchCV(
                    estimator=model,
                    param_distributions=SEARCH_SPACES[name],
                    n_iter=5, # Kept small for faster execution
                    scoring=SCORING_METRIC,
                    cv=CV_FOLDS,
                    random_state=RANDOM_STATE,
                    n_jobs=-1
                )
                search.fit(X_train, y_train)
                self.trained_models[name] = search.best_estimator_
                self.best_params[name] = search.best_params_
                logger.info("tuning_complete", model=name, best_params=search.best_params_)
            else:
                # Logistic Regression without tuning for baseline
                model.fit(X_train, y_train)
                self.trained_models[name] = model
                self.best_params[name] = "default"
                
            duration = time.time() - start_time
            logger.info("training_complete", model=name, duration_sec=round(duration, 2))
            
        return self.trained_models
