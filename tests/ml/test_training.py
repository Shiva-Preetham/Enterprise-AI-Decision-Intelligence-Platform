import numpy as np
import pytest
from ml.train import ModelTrainer
from ml.evaluate import ModelEvaluator

@pytest.fixture
def mock_train_data():
    X_train = np.random.rand(100, 5)
    y_train = np.random.randint(0, 2, 100)
    return X_train, y_train

@pytest.fixture
def mock_test_data():
    X_test = np.random.rand(20, 5)
    y_test = np.random.randint(0, 2, 20)
    return X_test, y_test

def test_model_training_and_evaluation(mock_train_data, mock_test_data):
    X_train, y_train = mock_train_data
    X_test, y_test = mock_test_data
    
    trainer = ModelTrainer()
    
    # Train only Logistic Regression to speed up the test
    # Delete others from the trainer dict for the test
    trainer.models = {"LogisticRegression": trainer.models["LogisticRegression"]}
    
    trained_models = trainer.train_all(X_train, y_train)
    assert "LogisticRegression" in trained_models
    
    feature_names = [f"feat_{i}" for i in range(5)]
    evaluator = ModelEvaluator(trained_models, feature_names)
    
    best_model_name, results = evaluator.evaluate_all(X_test, y_test)
    
    assert best_model_name == "LogisticRegression"
    assert "roc_auc" in results["LogisticRegression"]
    assert results["LogisticRegression"]["roc_auc"] >= 0.0
