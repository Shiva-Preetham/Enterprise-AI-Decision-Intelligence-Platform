import pandas as pd
from sqlalchemy.orm import Session
from abc import ABC, abstractmethod

class BaseFeatureGenerator(ABC):
    """Base class for modular feature generation."""
    
    @abstractmethod
    def generate(self, session: Session) -> pd.DataFrame:
        """
        Extracts raw data via the SQLAlchemy session and transforms it into features.
        
        Returns:
            pd.DataFrame: A dataframe where the index or a column is `customer_unique_id`
                          and the remaining columns are the generated features.
        """
        pass
