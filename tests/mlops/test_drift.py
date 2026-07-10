import pytest
import numpy as np
from unittest.mock import AsyncMock, patch
from mlops.drift_detection import DriftDetector
from mlops.models import DriftReportModel
from mlops.exceptions import DriftAlert
from mlops.config import mlops_config

@pytest.mark.asyncio
async def test_drift_detection_flags_injected_drift():
    repo = AsyncMock()
    
    detector = DriftDetector(repo)
    
    # Mock the database returning empty, which triggers the simulation block in DriftDetector
    # In simulation block, it creates a stable feature (total_lifetime_value) and an injected drift feature (purchase_count)
    repo.get_all_customer_features.return_value = []
    
    # Enable auto alerting
    mlops_config.ENABLE_DRIFT_DETECTION = True
    
    # Capture the report created
    created_report = None
    async def mock_create(report):
        nonlocal created_report
        created_report = report
        return report
    
    repo.create_drift_report = AsyncMock(side_effect=mock_create)
    
    with pytest.raises(DriftAlert):
        await detector.detect_drift()
        
    assert created_report is not None
    assert created_report.is_alert is True
    
    # We must assert the actual PSI value crosses the threshold.
    import json
    stats = json.loads(created_report.feature_stats)
    
    # 'purchase_count' had a mean shift of +0.5 injected
    psi_stable = stats['total_lifetime_value']['psi']
    psi_drifted = stats['purchase_count']['psi']
    
    # Assert it correctly flags the injected-drift feature
    assert psi_drifted > mlops_config.PSI_THRESHOLD
    # The stable feature might slightly drift due to random noise, but typically less than +0.5 mean shift
