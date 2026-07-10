import pytest
from unittest.mock import AsyncMock
from mlops.alerting import AlertingEngine

@pytest.mark.asyncio
async def test_alerting_engine_drift():
    repo = AsyncMock()
    engine = AlertingEngine(repo)
    engine.notifier.execute = AsyncMock()
    
    drift_data = {
        "is_alert": True,
        "feature_stats": "{'feat': 'stats'}"
    }
    
    await engine.evaluate_drift(drift_data)
    repo.create_alert.assert_called_once()
    engine.notifier.execute.assert_called_once()
