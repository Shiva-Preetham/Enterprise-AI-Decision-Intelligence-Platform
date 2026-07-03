"""
Main training pipeline script.
"""
import time
from structlog import get_logger

from ml.preprocessing import FeaturePreprocessor
from ml.train import ModelTrainer
from ml.evaluate import ModelEvaluator
from ml.explain import SHAPExplainer
from ml.registry import ModelRegistry

logger = get_logger(__name__)

def run_pipeline():
    start_time = time.time()
    logger.info("starting_ml_pipeline")
    
    # 1. Preprocessing
    preprocessor = FeaturePreprocessor()
    df = preprocessor.load_data()
    X_train, X_test, y_train, y_test = preprocessor.split_data(df)
    
    X_train_transformed = preprocessor.fit_transform(X_train)
    X_test_transformed = preprocessor.transform(X_test)
    
    # 2. Training
    trainer = ModelTrainer()
    trained_models = trainer.train_all(X_train_transformed, y_train)
    
    # 3. Evaluation
    evaluator = ModelEvaluator(trained_models, preprocessor.feature_names)
    best_model_name, evaluation_results = evaluator.evaluate_all(X_test_transformed, y_test)
    best_model = trained_models[best_model_name]
    best_params = trainer.best_params[best_model_name]
    best_metrics = evaluation_results[best_model_name]
    
    # 4. Explainability
    explainer_obj = SHAPExplainer(best_model, preprocessor.feature_names)
    # Generate explanation for the first 100 test samples to save time
    shap_explainer = explainer_obj.explain(X_test_transformed[:100])
    
    # 5. Registry
    registry = ModelRegistry()
    registry.save_model(
        model=best_model,
        preprocessor=preprocessor,
        feature_names=preprocessor.feature_names,
        metrics=best_metrics,
        best_params=best_params,
        explainer=shap_explainer,
        metadata_extras={"PipelineVersion": "1.0", "FeatureVersion": "1.0"}
    )
    
    duration = time.time() - start_time
    logger.info("ml_pipeline_completed", duration_sec=round(duration, 2), best_model=best_model_name)

if __name__ == "__main__":
    run_pipeline()
