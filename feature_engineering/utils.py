import pandas as pd
from typing import List, Union

def calculate_entropy(series: pd.Series) -> float:
    """Calculates Shannon entropy for a categorical series."""
    counts = series.value_counts(normalize=True)
    if len(counts) <= 1:
        return 0.0
    import numpy as np
    return -(counts * np.log2(counts)).sum()

def coalesce(df: pd.DataFrame, columns: List[str], target: str) -> pd.DataFrame:
    """Coalesce multiple columns into a single target column (first non-null)."""
    df[target] = df[columns].bfill(axis=1).iloc[:, 0]
    return df
