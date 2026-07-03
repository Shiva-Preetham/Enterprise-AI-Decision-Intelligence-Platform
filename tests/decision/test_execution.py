import pytest
from decision_engine.execution.registry import get_executor
from decision_engine.execution.coupon_executor import CouponExecutor
from decision_engine.execution.notification_executor import NotificationExecutor
from unittest.mock import MagicMock

@pytest.mark.asyncio
async def test_get_executor():
    # Known type
    executor = get_executor("offer_discount")
    assert isinstance(executor, CouponExecutor)
    
    # Unknown type fallback
    executor = get_executor("some_fake_type")
    assert isinstance(executor, NotificationExecutor)

@pytest.mark.asyncio
async def test_coupon_executor():
    executor = CouponExecutor()
    rec = MagicMock()
    rec.customer_unique_id = "CUST-123"
    
    result = await executor.execute(rec)
    assert result["status"] == "Success"
    assert "Coupon code generated" in result["message"]
