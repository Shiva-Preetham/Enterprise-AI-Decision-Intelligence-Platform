"""
Enterprise AI Customer Intelligence Platform — Agent Router.

FastAPI endpoints for the LangGraph AI Copilot.
"""

from typing import Optional
import json
import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage

from backend.api.dependencies import get_customer_service, get_analytics_service, get_model_service
from backend.services.customer_service import CustomerService
from backend.services.analytics_service import AnalyticsService
from backend.services.model_service import ModelService

from agent.tools import inject_services
from agent.guardrails import check_guardrails
from agent.memory import get_memory_saver
from agent.graph import app as agent_app
from agent.models import AgentResponse

router = APIRouter(prefix="/agent", tags=["AI Copilot"])

class ChatRequest(BaseModel):
    question: str = Field(..., description="Natural language question for the AI Copilot.")
    customer_id: Optional[str] = Field(None, description="Contextual customer ID.")
    conversation_id: Optional[str] = Field(None, description="Session ID for conversational memory.")

@router.post("/chat", response_model=AgentResponse)
async def chat_with_agent(
    request: ChatRequest,
    customer_svc: CustomerService = Depends(get_customer_service),
    analytics_svc: AnalyticsService = Depends(get_analytics_service),
    model_svc: ModelService = Depends(get_model_service)
):
    """
    Main endpoint for interacting with the Enterprise AI Copilot.
    Uses LangGraph, tool calling, and Redis-backed memory to answer business questions.
    """
    # 1. Guardrails
    is_safe, reason = check_guardrails(request.question)
    if not is_safe:
        raise HTTPException(status_code=400, detail=reason)
        
    # 2. Inject Services into Tools
    inject_services(
        customer_service=customer_svc,
        analytics_service=analytics_svc,
        model_service=model_svc
    )
    
    # 3. Setup Memory and Config
    conversation_id = request.conversation_id or str(uuid.uuid4())
    config = {"configurable": {"thread_id": conversation_id}}
    
    # 4. Invoke LangGraph
    # If the user provided a customer_id, we can inject that context into the prompt
    msg_content = request.question
    if request.customer_id:
        msg_content += f"\n\n[Context: Focus on customer_id: {request.customer_id}]"
        
    input_state = {
        "messages": [HumanMessage(content=msg_content)],
        "customer_id": request.customer_id,
        "conversation_id": conversation_id
    }
    
    try:
        from agent.graph import workflow
        
        # Compile graph with memory saver if available
        checkpointer = get_memory_saver()
        compiled_app = workflow.compile(checkpointer=checkpointer) if checkpointer else workflow.compile()
            
        # Run graph
        final_state = await compiled_app.ainvoke(input_state, config=config)
        
        # Output Parser dumped the Pydantic JSON into the 'plan' key (as a hack) 
        # or we can just parse it directly.
        raw_json = final_state.get("plan", "{}")
        response_dict = json.loads(raw_json)
        
        # Ensure it has conversation_id in the follow ups or context?
        # Return structured output
        return AgentResponse(**response_dict)
        
    except Exception as exc:
        import structlog
        logger = structlog.get_logger(__name__)
        import traceback
        error_details = traceback.format_exc()
        logger.error("agent_execution_failed", error=str(exc))
        raise HTTPException(status_code=500, detail=f"Internal AI error during reasoning: {error_details}")
