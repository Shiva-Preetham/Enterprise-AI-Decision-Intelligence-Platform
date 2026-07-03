"""
Enterprise AI Customer Intelligence Platform — Reasoning Engine.
"""
import json
from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from .schemas import ReasoningOutput, PolicyDecision
from .prompts import REASONING_SYSTEM_PROMPT
from .exceptions import PolicyViolationError

class ReasoningEngine:
    """
    Invokes the LLM to provide a justification and preference ranking among policy-allowed actions.
    """
    
    def __init__(self):
        # We use strict structured outputs to ensure type safety
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0).with_structured_output(ReasoningOutput)

    async def generate_reasoning(self, context: Dict[str, Any], policy_decision: PolicyDecision) -> ReasoningOutput:
        """
        Generates reasoning restricted to the allowed actions from the policy decision.
        """
        # Format the system prompt with context and allowed actions
        context_str = json.dumps(context, default=str)
        allowed_actions_str = ", ".join(policy_decision.allowed_actions)
        
        sys_msg = REASONING_SYSTEM_PROMPT.format(
            context=context_str,
            allowed_actions=allowed_actions_str
        )
        
        messages = [
            SystemMessage(content=sys_msg),
            HumanMessage(content="Please provide the recommended action and justification.")
        ]
        
        # Invoke LLM
        output: ReasoningOutput = await self.llm.ainvoke(messages)
        
        # Safety Check: Did the LLM violate the policy boundary?
        if output.selected_action not in policy_decision.allowed_actions:
            raise PolicyViolationError(
                f"LLM proposed action '{output.selected_action}' which is not in the allowed policy set: {policy_decision.allowed_actions}."
            )
            
        return output
