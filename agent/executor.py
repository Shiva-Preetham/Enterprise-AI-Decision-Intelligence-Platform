"""
Enterprise AI Customer Intelligence Platform — Agent Executor.

Node that physically executes the tools selected by the Planner.
"""

import json
from langchain_core.messages import ToolMessage
from langgraph.prebuilt import ToolNode
from agent.state import AgentState
from agent.tools import AVAILABLE_TOOLS

# LangGraph provides a built-in ToolNode that handles executing bounded tools
# and returning ToolMessages to the state.
tool_node = ToolNode(tools=AVAILABLE_TOOLS)

async def execute_tools_node(state: AgentState) -> dict:
    """
    Wrapper around the prebuilt ToolNode. Also extracts raw outputs and tool names 
    for the state so the Rule Engine can use them.
    """
    # Execute the tools
    result = await tool_node.ainvoke(state)
    
    # The result contains new ToolMessages
    new_messages = result.get("messages", [])
    
    tool_outputs = []
    tools_used = []
    for msg in new_messages:
        if isinstance(msg, ToolMessage):
            tool_outputs.append(msg.content)
            tools_used.append(msg.name)
            
    return {
        "messages": new_messages,
        "tool_outputs": json.dumps(tool_outputs),
        "tools_used": tools_used
    }
