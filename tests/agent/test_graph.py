import pytest
from langchain_core.messages import HumanMessage, AIMessage
from agent.graph import should_continue

def test_should_continue_to_execute_tools():
    # Mock state where LLM decided to call a tool
    state = {
        "messages": [
            HumanMessage(content="What is the dashboard?"),
            AIMessage(content="", tool_calls=[{"name": "get_dashboard_metrics", "args": {}, "id": "123"}])
        ]
    }
    
    next_node = should_continue(state)
    assert next_node == "execute_tools_node"

def test_should_continue_to_rule_engine():
    # Mock state where LLM just answered
    state = {
        "messages": [
            HumanMessage(content="Hello"),
            AIMessage(content="Hello there! How can I help?")
        ]
    }
    
    next_node = should_continue(state)
    assert next_node == "rule_engine_node"
