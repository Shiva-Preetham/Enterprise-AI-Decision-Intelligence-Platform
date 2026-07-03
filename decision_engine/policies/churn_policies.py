"""
Enterprise AI Customer Intelligence Platform — Churn Policies.
"""
from typing import Dict, Any, Optional
from .base import PolicyRule

class HighCLVAlreadyOfferedCouponRule(PolicyRule):
    """
    If CLV is high and churn risk is high, but the customer already
    received a coupon recently, deny another coupon and require a
    Relationship Manager assignment instead.
    """
    def evaluate(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        prob = context.get("churn_probability", 0.0)
        clv = context.get("total_lifetime_value", 0.0)
        history = context.get("decision_history", [])
        
        recent_coupons = sum(1 for e in history if e.event_type == "executed" and "coupon" in str(e.details).lower())
        
        if prob > 0.7 and clv > 1000.0:
            if recent_coupons > 0:
                return {
                    "decision": "REQUIRE_APPROVAL",
                    "allowed_actions": ["assign_rm", "escalate_case"],
                    "reason": "High CLV/Risk but already offered coupon recently. Requires RM assignment."
                }
        return None

class BudgetCapRule(PolicyRule):
    """
    Deny expensive actions for low CLV customers.
    """
    def evaluate(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        clv = context.get("total_lifetime_value", 0.0)
        
        if clv < 100.0:
            return {
                "decision": "ALLOW",
                "allowed_actions": ["send_email_notification", "no_action"],
                "reason": "Low CLV customer. Restricted to low-cost or no-cost actions."
            }
        return None

class HighRiskEscalationRule(PolicyRule):
    """
    For extremely high risk and high value, allow coupons but require approval for large ones.
    """
    def evaluate(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        prob = context.get("churn_probability", 0.0)
        clv = context.get("total_lifetime_value", 0.0)
        
        if prob > 0.8 and clv >= 100.0:
            return {
                "decision": "REQUIRE_APPROVAL",
                "allowed_actions": ["offer_discount", "assign_rm", "send_premium_gift"],
                "reason": "Critical risk. High-impact retention offers allowed but require approval."
            }
        return None

class DefaultLowRiskRule(PolicyRule):
    """
    For low risk customers, auto-allow standard notifications or no action.
    """
    def evaluate(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        prob = context.get("churn_probability", 0.0)
        if prob < 0.4:
            return {
                "decision": "ALLOW",
                "allowed_actions": ["no_action", "send_newsletter"],
                "reason": "Customer is low risk. Allowed standard engagement actions."
            }
        return None
