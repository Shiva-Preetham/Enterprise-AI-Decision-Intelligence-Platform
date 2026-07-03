import pandas as pd
from sqlalchemy import text
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from structlog import get_logger

from backend.db.engine import sync_engine
from ml.config import COLUMNS_TO_DROP, TARGET_COLUMN, RANDOM_STATE, TEST_SIZE

logger = get_logger(__name__)

class FeaturePreprocessor:
    """Handles loading and preprocessing data from the Feature Store."""

    def __init__(self):
        self.preprocessor = None
        self.feature_names = None

    def load_data(self) -> pd.DataFrame:
        """Loads features directly from analytics.customer_feature_store."""
        logger.info("loading_feature_store")
        query = "SELECT * FROM analytics.customer_feature_store"
        df = pd.read_sql(query, sync_engine)
        logger.info("feature_store_loaded", rows=len(df), cols=len(df.columns))
        return df

    def split_data(self, df: pd.DataFrame):
        """Splits data into train and test sets, avoiding data leakage."""
        logger.info("splitting_data")
        
        # Drop metadata and ID columns
        cols_to_drop = [c for c in COLUMNS_TO_DROP if c in df.columns]
        X = df.drop(columns=cols_to_drop + [TARGET_COLUMN])
        y = df[TARGET_COLUMN]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
        )
        logger.info("data_split_complete", train_size=len(X_train), test_size=len(X_test))
        return X_train, X_test, y_train, y_test

    def build_pipeline(self, X_train: pd.DataFrame) -> ColumnTransformer:
        """Builds the Scikit-Learn preprocessing pipeline."""
        numeric_features = X_train.select_dtypes(include=['int64', 'float64']).columns.tolist()
        categorical_features = X_train.select_dtypes(include=['object', 'bool']).columns.tolist()

        numeric_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler())
        ])

        categorical_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='most_frequent')),
            ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
        ])

        preprocessor = ColumnTransformer(
            transformers=[
                ('num', numeric_transformer, numeric_features),
                ('cat', categorical_transformer, categorical_features)
            ]
        )
        
        self.preprocessor = preprocessor
        return preprocessor

    def fit_transform(self, X_train: pd.DataFrame):
        """Fits the preprocessor and transforms the training data."""
        logger.info("fitting_preprocessor")
        preprocessor = self.build_pipeline(X_train)
        X_train_transformed = preprocessor.fit_transform(X_train)
        
        # Extract feature names after One-Hot Encoding
        num_cols = preprocessor.transformers_[0][2]
        cat_encoder = preprocessor.named_transformers_['cat']['onehot']
        cat_cols = preprocessor.transformers_[1][2]
        
        if len(cat_cols) > 0:
            cat_features = cat_encoder.get_feature_names_out(cat_cols).tolist()
        else:
            cat_features = []
            
        self.feature_names = num_cols + cat_features
        logger.info("preprocessor_fitted", num_features=len(self.feature_names))
        
        return X_train_transformed

    def transform(self, X: pd.DataFrame):
        """Transforms data using the fitted preprocessor."""
        if self.preprocessor is None:
            raise ValueError("Preprocessor has not been fitted yet.")
        return self.preprocessor.transform(X)
