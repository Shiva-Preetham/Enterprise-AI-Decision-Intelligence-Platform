"""
Enterprise AI Customer Intelligence Platform — Policy Engine.
"""
from typing import Dict, Any
from .schemas import PolicyDecision
from .policies.registry import PolicyRegistry

class PolicyEngine:
    """
    Evaluates business context against a deterministic registry of policy rules.
    """
    
    @staticmethod
    def evaluate(context: Dict[str, Any]) -> PolicyDecision:
        """
        Executes the policy rules and returns a structured PolicyDecision.
        """
        result = PolicyRegistry.evaluate_all(context)
        return PolicyDecision(**result)
