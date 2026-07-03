"""
Enterprise AI Customer Intelligence Platform — Recommendation Engine.
"""
from typing import Dict, Any
from .schemas import PolicyDecision, ReasoningOutput, RecommendationSchema
from .models import RecommendationModel
from .repository import DecisionRepository

class RecommendationEngine:
    """
    Combines Policy Engine output and LLM reasoning into a persisted Recommendation.
    """
    def __init__(self, repository: DecisionRepository):
        self.repository = repository

    async def generate_recommendation(
        self, 
        customer_id: str, 
        policy_decision: PolicyDecision, 
        reasoning: ReasoningOutput
    ) -> RecommendationSchema:
        
        priority = "high" if policy_decision.decision == "REQUIRE_APPROVAL" else "medium"
        
        model = RecommendationModel(
            customer_unique_id=customer_id,
            recommendation_type=reasoning.selected_action,
            priority=priority,
            confidence=reasoning.confidence,
            business_reason=reasoning.business_justification,
            expected_impact=reasoning.expected_impact,
            estimated_cost=reasoning.estimated_cost,
            required_approval=policy_decision.decision == "REQUIRE_APPROVAL",
            generated_by="llm_reasoning"
        )
        
        persisted = await self.repository.create_recommendation(model)
        return RecommendationSchema.model_validate(persisted)
