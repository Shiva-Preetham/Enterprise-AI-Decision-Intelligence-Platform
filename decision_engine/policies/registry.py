"""
Enterprise AI Customer Intelligence Platform — Policy Registry.
"""
from typing import List, Dict, Any
from .base import PolicyRule

class PolicyRegistry:
    """
    Holds an ordered list of policy rules to evaluate.
    """
    _rules: List[PolicyRule] = []

    @classmethod
    def register(cls, rule: PolicyRule):
        cls._rules.append(rule)

    @classmethod
    def evaluate_all(cls, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates rules in order. The first rule that returns a decision (not None) wins.
        """
        evaluated = []
        for rule in cls._rules:
            evaluated.append(rule.__class__.__name__)
            result = rule.evaluate(context)
            if result is not None:
                result["evaluated_policies"] = evaluated
                return result
        
        # Fallback if no rule matches
        return {
            "decision": "REQUIRE_APPROVAL",
            "allowed_actions": ["assign_rm", "escalate_case"],
            "reason": "No explicit policy matched. Escalate for human review.",
            "evaluated_policies": evaluated
        }

    @classmethod
    def clear(cls):
        cls._rules = []
