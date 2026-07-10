"""
Enterprise AI Customer Intelligence Platform — Agent Planner.

Node that determines which tools to call based on the user's question.
"""

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from agent.state import AgentState
from agent.prompts import PLANNER_SYSTEM_PROMPT
from agent.tools import AVAILABLE_TOOLS

async def plan_node(state: AgentState) -> dict:
    """
    Analyzes the user's request and outputs a strategic plan and the tools needed.
    """
    from backend.config import settings
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0, google_api_key=settings.GEMINI_API_KEY) # Enterprise typically prefers deterministic behavior
    
    # Bind the available tools to the LLM so it knows what it can do
    llm_with_tools = llm.bind_tools(AVAILABLE_TOOLS)
    
    # Get the latest user message
    user_message = state["messages"][-1]
    
    # Create the prompt sequence
    messages = [
        SystemMessage(content=PLANNER_SYSTEM_PROMPT),
        user_message
    ]
    
    # Invoke the LLM to get tool calls or a direct response
    response = await llm_with_tools.ainvoke(messages)
    
    # We return the AI message which contains tool_calls (if any)
    # This will be appended to state["messages"] by LangGraph
    return {"messages": [response]}
