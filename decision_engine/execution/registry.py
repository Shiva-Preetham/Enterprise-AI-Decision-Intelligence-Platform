"""
Enterprise AI Customer Intelligence Platform — Execution Registry.
"""
from typing import Dict, Type
from .base import ExecutorBase
from .coupon_executor import CouponExecutor
from .notification_executor import NotificationExecutor
from .crm_task_executor import CRMTaskExecutor

# Maps a recommendation_type to its concrete executor class
EXECUTOR_REGISTRY: Dict[str, Type[ExecutorBase]] = {
    "offer_discount": CouponExecutor,
    "send_premium_gift": CouponExecutor,
    "send_email_notification": NotificationExecutor,
    "send_newsletter": NotificationExecutor,
    "assign_rm": CRMTaskExecutor,
    "escalate_case": CRMTaskExecutor,
    "no_action": NotificationExecutor # Safe fallback
}

def get_executor(recommendation_type: str) -> ExecutorBase:
    """
    Returns an instantiated executor for the given recommendation type.
    """
    executor_cls = EXECUTOR_REGISTRY.get(recommendation_type)
    if not executor_cls:
        # Fallback for unrecognized types
        return NotificationExecutor()
    return executor_cls()
