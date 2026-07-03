"""
Enterprise AI Customer Intelligence Platform — Base Policy Interface.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class PolicyRule(ABC):
    """
    Abstract base class for deterministic policy rules.
    """
    
    @abstractmethod
    def evaluate(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Evaluates the rule against the customer context.
        Returns None if the rule does not apply (pass to next rule).
        If the rule applies, returns a dict with:
        - decision: "ALLOW", "DENY", "REQUIRE_APPROVAL"
        - allowed_actions: List of allowed action strings
        - reason: Human readable string
        """
        pass
