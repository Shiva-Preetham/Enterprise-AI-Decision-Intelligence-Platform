"""
Enterprise AI Customer Intelligence Platform — LangGraph Compilation.

Compiles the nodes into an executable Directed Acyclic Graph (DAG).
"""

from typing import Literal
from langgraph.graph import StateGraph, END, START
from langchain_core.messages import AIMessage

from agent.state import AgentState
from agent.planner import plan_node
from agent.executor import execute_tools_node
from agent.output_parser import reason_and_format_node
from agent.recommendation import generate_recommendation

def should_continue(state: AgentState) -> Literal["execute_tools_node", "rule_engine_node"]:
    """
    Edge routing logic. Determines if the Planner chose to call tools or if it
    wants to respond directly.
    """
    messages = state["messages"]
    last_message = messages[-1]
    
    # If the LLM made a tool call, route to execution
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "execute_tools_node"
        
    # Otherwise, go straight to generating the recommendation and formatting
    return "rule_engine_node"

async def rule_engine_node(state: AgentState) -> dict:
    """Wrapper node to execute the Next Best Action rule engine."""
    tool_outputs = state.get("tool_outputs", "{}")
    recommendation = generate_recommendation(tool_outputs)
    return {"recommendation": recommendation}


# 1. Initialize Graph
workflow = StateGraph(AgentState)

# 2. Add Nodes
workflow.add_node("plan_node", plan_node)
workflow.add_node("execute_tools_node", execute_tools_node)
workflow.add_node("rule_engine_node", rule_engine_node)
workflow.add_node("reason_and_format_node", reason_and_format_node)

# 3. Define Edges (Data Flow)
workflow.add_edge(START, "plan_node")

# Conditional Edge from Planner -> Tools OR directly to Synthesis
workflow.add_conditional_edges("plan_node", should_continue)

# After tools execute, run the rule engine
workflow.add_edge("execute_tools_node", "rule_engine_node")

# After rules engine, reason and format the final output
workflow.add_edge("rule_engine_node", "reason_and_format_node")

# Finish
workflow.add_edge("reason_and_format_node", END)

# 4. Compile App
# The memory checkpointer will be passed at runtime in the router
app = workflow.compile()
