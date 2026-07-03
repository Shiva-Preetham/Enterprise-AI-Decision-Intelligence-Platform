import pandas as pd
import pytest
from ml.preprocessing import FeaturePreprocessor
from ml.config import TARGET_COLUMN

@pytest.fixture
def mock_data():
    return pd.DataFrame({
        "customer_unique_id": ["id1", "id2", "id3", "id4", "id5"],
        "recency_days": [10, 20, 30, None, 50],
        "frequency_90d": [1, 2, 3, 4, 5],
        "customer_state": ["NY", "CA", "NY", None, "TX"],
        TARGET_COLUMN: [0, 1, 0, 1, 0]
    })

def test_preprocessing_pipeline(mock_data):
    preprocessor = FeaturePreprocessor()
    
    # Test split
    X_train, X_test, y_train, y_test = preprocessor.split_data(mock_data)
    
    assert len(X_train) == 4
    assert len(X_test) == 1
    
    # Test fit_transform
    X_train_transformed = preprocessor.fit_transform(X_train)
    
    # Check no missing values remain
    assert pd.DataFrame(X_train_transformed).isnull().sum().sum() == 0
    
    # Check feature names are extracted correctly
    assert len(preprocessor.feature_names) > 0
    
    # Test transform
    X_test_transformed = preprocessor.transform(X_test)
    assert X_test_transformed.shape[1] == X_train_transformed.shape[1]
