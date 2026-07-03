import pytest
from unittest.mock import AsyncMock, patch
from decision_engine.reasoning_engine import ReasoningEngine
from decision_engine.schemas import PolicyDecision, ReasoningOutput
from decision_engine.exceptions import PolicyViolationError

@pytest.mark.asyncio
async def test_reasoning_engine_valid_action():
    engine = ReasoningEngine()
    engine.llm = AsyncMock()
    
    mock_output = ReasoningOutput(
        selected_action="offer_discount",
        confidence=0.9,
        business_justification="Customer has high CLV.",
        expected_impact="High",
        estimated_cost=50.0
    )
    engine.llm.ainvoke.return_value = mock_output
    
    policy_decision = PolicyDecision(
        decision="ALLOW",
        allowed_actions=["offer_discount"],
        reason="Test",
        evaluated_policies=[]
    )
    
    result = await engine.generate_reasoning({}, policy_decision)
    assert result.selected_action == "offer_discount"

@pytest.mark.asyncio
async def test_reasoning_engine_policy_violation():
    engine = ReasoningEngine()
    engine.llm = AsyncMock()
    
    # LLM proposes an action that is not in allowed_actions
    mock_output = ReasoningOutput(
        selected_action="send_premium_gift",
        confidence=0.9,
        business_justification="Customer has high CLV.",
        expected_impact="High",
        estimated_cost=500.0
    )
    engine.llm.ainvoke.return_value = mock_output
    
    policy_decision = PolicyDecision(
        decision="ALLOW",
        allowed_actions=["offer_discount"], # Only discount allowed
        reason="Test",
        evaluated_policies=[]
    )
    
    with pytest.raises(PolicyViolationError) as exc:
        await engine.generate_reasoning({}, policy_decision)
    assert "not in the allowed policy set" in str(exc.value)
