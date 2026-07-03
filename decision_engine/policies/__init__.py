"""
Enterprise AI Customer Intelligence Platform — Policy Engine Policies Init.
"""
from .registry import PolicyRegistry
from .churn_policies import HighCLVAlreadyOfferedCouponRule, DefaultLowRiskRule, HighRiskEscalationRule, BudgetCapRule

# Register policies
PolicyRegistry.register(HighCLVAlreadyOfferedCouponRule())
PolicyRegistry.register(BudgetCapRule())
PolicyRegistry.register(HighRiskEscalationRule())
PolicyRegistry.register(DefaultLowRiskRule())

__all__ = ["PolicyRegistry"]
