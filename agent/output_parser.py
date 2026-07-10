"""
Enterprise AI Customer Intelligence Platform — Output Parser.

Node that synthesizes the final response and structures it into the Pydantic schema.
"""

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from agent.state import AgentState
from agent.models import AgentResponse
from agent.prompts import REASONER_SYSTEM_PROMPT

async def reason_and_format_node(state: AgentState) -> dict:
    """
    Takes the tool outputs, the recommendation from the rule engine, and the original
    question, and generates the final structured JSON response.
    """
    from backend.config import settings
    # Force the LLM to output our Pydantic schema using structured output
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0, google_api_key=settings.GEMINI_API_KEY).with_structured_output(AgentResponse)
    
    recommendation = state.get("recommendation", "No specific recommendation.")
    
    # We pass the conversation history, plus the system prompt instructing it to synthesize
    messages = [
        SystemMessage(content=REASONER_SYSTEM_PROMPT),
    ] + state["messages"]
    
    # Add an explicit instruction message injecting the recommendation
    messages.append(HumanMessage(content=f"System Rule Engine Recommendation to incorporate: {recommendation}"))
    
    structured_response = await llm.ainvoke(messages)
    
    # Ensure sources used are populated from state if the LLM missed them
    if not structured_response.sources_used and state.get("tools_used"):
        structured_response.sources_used = state["tools_used"]
        
    return {"plan": structured_response.model_dump_json()} # We hijack the 'plan' state key to store the final JSON for the API route
