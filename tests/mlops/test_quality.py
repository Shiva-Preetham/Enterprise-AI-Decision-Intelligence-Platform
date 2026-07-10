import pytest
from unittest.mock import AsyncMock
import pandas as pd
from mlops.data_quality import DataQualityChecker

@pytest.mark.asyncio
async def test_data_quality_missing_values():
    repo = AsyncMock()
    
    # Setup mock data with missing values
    class MockRecord:
        def __init__(self, id, val):
            self.customer_unique_id = id
            self.total_lifetime_value = val
            self.avg_order_value = val
            self.total_orders = 1
            self.days_since_last_order = 10
            self.avg_review_score = 4.0
            
    records = [
        MockRecord("1", 100.0),
        MockRecord("2", None), # Missing value
        MockRecord("3", 200.0),
    ]
    
    repo.get_all_customer_features.return_value = records
    
    checker = DataQualityChecker(repo)
    report = await checker.run_checks()
    
    assert report.total_rows == 3
    # 1 out of 3 is missing -> 0.333
    assert report.missing_value_rates['total_lifetime_value'] > 0.3
    assert report.overall_status == "degraded"
