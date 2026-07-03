"""
Enterprise AI Customer Intelligence Platform — Decision Engine Exceptions.
"""

class PolicyViolationError(Exception):
    """Raised when the LLM proposes an action not authorized by the Policy Engine."""
    pass

class InvalidTransitionError(Exception):
    """Raised when an invalid state machine transition is attempted."""
    pass

class ActionExecutionError(Exception):
    """Raised when an execution engine fails to perform an action."""
    pass
