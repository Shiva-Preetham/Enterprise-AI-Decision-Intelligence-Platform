"""
Enterprise AI Customer Intelligence Platform — Agent Models.

Strict Pydantic V2 schemas for structured LLM outputs. Ensures the agent
always returns a consistent JSON payload to the FastAPI router.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class AgentResponse(BaseModel):
    """The final structured response returned by the AI Copilot."""
    answer: str = Field(..., description="The main conversational response to the user's question.")
    confidence: str = Field(..., description="Confidence level: HIGH, MEDIUM, or LOW based on data availability.")
    recommendation: Optional[str] = Field(None, description="A specific business action recommended based on the context.")
    sources_used: List[str] = Field(default_factory=list, description="List of tools or services invoked to answer the query.")
    follow_up_suggestions: List[str] = Field(default_factory=list, description="2-3 suggested follow-up questions for the user.")

class RecommendationAction(BaseModel):
    """Output from the Next Best Action rule engine."""
    action_type: str = Field(..., description="E.g., Send Coupon, Premium Outreach, No Action")
    reasoning: str = Field(..., description="Why this action was chosen.")
