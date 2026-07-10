"""
MLOps Configuration extending core settings.
"""
from pydantic import Field
from backend.config import settings

class MLOpsConfig:
    """
    Feature flags and configurations specific to MLOps.
    We don't inherit from BaseSettings to avoid re-parsing environment variables;
    instead we just map fields and use environment defaults if needed, or rely on core settings.
    """
    # Feature Flags
    ENABLE_DRIFT_DETECTION: bool = True
    ENABLE_AUTO_ROLLBACK: bool = False
    
    # Drift Thresholds
    PSI_THRESHOLD: float = 0.2
    KS_P_VALUE_THRESHOLD: float = 0.05
    
    # Registry config
    MODEL_REGISTRY_PATH: str = "data/registry"

mlops_config = MLOpsConfig()
