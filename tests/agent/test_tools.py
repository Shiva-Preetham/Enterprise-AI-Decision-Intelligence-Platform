import pytest
import json
from unittest.mock import AsyncMock, MagicMock
from agent.tools import inject_services, get_dashboard_metrics

@pytest.mark.asyncio
async def test_get_dashboard_metrics_success():
    # Mock the analytics service
    mock_analytics = AsyncMock()
    mock_metrics = MagicMock()
    mock_metrics.model_dump_json.return_value = '{"total_customers": 100}'
    mock_analytics.get_dashboard_metrics.return_value = mock_metrics
    
    # Inject mock service
    inject_services(customer_service=None, analytics_service=mock_analytics, model_service=None)
    
    # Execute tool
    result = await get_dashboard_metrics.ainvoke({})
    
    assert result == '{"total_customers": 100}'
    mock_analytics.get_dashboard_metrics.assert_called_once()

@pytest.mark.asyncio
async def test_get_dashboard_metrics_missing_service():
    # Inject None for analytics service
    inject_services(customer_service=None, analytics_service=None, model_service=None)
    
    result = await get_dashboard_metrics.ainvoke({})
    assert "Analytics service not available" in result
