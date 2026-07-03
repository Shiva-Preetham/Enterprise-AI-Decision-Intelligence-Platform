import pytest
from decision_engine.policies.churn_policies import HighCLVAlreadyOfferedCouponRule, BudgetCapRule
from decision_engine.policies.registry import PolicyRegistry

def test_high_clv_already_offered_coupon_rule():
    rule = HighCLVAlreadyOfferedCouponRule()
    
    class MockAudit:
        def __init__(self, t, d):
            self.event_type = t
            self.details = d
            
    # Matches rule
    context = {
        "churn_probability": 0.8,
        "total_lifetime_value": 1500.0,
        "decision_history": [MockAudit("executed", "issued coupon")]
    }
    result = rule.evaluate(context)
    assert result is not None
    assert result["decision"] == "REQUIRE_APPROVAL"
    assert "assign_rm" in result["allowed_actions"]

    # Does not match rule (no history)
    context_no_history = {
        "churn_probability": 0.8,
        "total_lifetime_value": 1500.0,
        "decision_history": []
    }
    assert rule.evaluate(context_no_history) is None

def test_budget_cap_rule():
    rule = BudgetCapRule()
    context = {"total_lifetime_value": 50.0}
    result = rule.evaluate(context)
    assert result is not None
    assert result["decision"] == "ALLOW"
    assert "send_email_notification" in result["allowed_actions"]

def test_registry_ordering():
    # Registry should evaluate in order and return the first matched rule
    # Because rules are evaluated in the order they are added, we just test evaluate_all
    context = {
        "churn_probability": 0.1,
        "total_lifetime_value": 5000.0
    }
    result = PolicyRegistry.evaluate_all(context)
    # With prob 0.1, DefaultLowRiskRule should trigger if no other triggered before
    assert result["decision"] == "ALLOW"
    assert "no_action" in result["allowed_actions"]
