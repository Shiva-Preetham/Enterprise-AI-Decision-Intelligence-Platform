import pandas as pd
import pytest
from unittest.mock import patch, MagicMock

from ml.predict import Predictor

@pytest.fixture
def mock_predictor():
    with patch("ml.predict.ModelLoader.load_artifacts") as mock_loader:
        mock_model = MagicMock()
        import numpy as np
        mock_model.predict_proba.return_value = np.array([[0.1, 0.9]]) # High probability of class 1
        mock_model.predict.return_value = [1]
        
        mock_preprocessor = MagicMock()
        mock_preprocessor.transform.return_value = [[1.0, 2.0]]
        
        mock_feature_names = ["feat1", "feat2"]
        
        mock_loader.return_value = (mock_model, mock_preprocessor, mock_feature_names)
        
        yield Predictor()

def test_prediction_output(mock_predictor):
    mock_input = pd.DataFrame({"feat1": [1.0], "feat2": [2.0]})
    result = mock_predictor.predict(mock_input)
    
    assert "Probability" in result
    assert result["Probability"] == 0.9
    assert result["PredictedLabel"] == 1
    assert "RiskCategory" in result
    assert result["RiskCategory"] == "Very High Risk"
