"""
Enterprise AI Customer Intelligence Platform — Decisions API Router.
"""
import uuid
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db.session import get_async_session

from decision_engine.repository import DecisionRepository
from decision_engine.audit_service import AuditService
from decision_engine.workflow_engine import WorkflowEngine
from decision_engine.approval_service import ApprovalService
from decision_engine.policy_engine import PolicyEngine
from decision_engine.reasoning_engine import ReasoningEngine
from decision_engine.recommendation_engine import RecommendationEngine
from decision_engine.execution.registry import get_executor
from decision_engine.models import ExecutionModel
from decision_engine.schemas import ApprovalRequest, RejectionRequest, RecommendationSchema, WorkflowSchema
from decision_engine.exceptions import InvalidTransitionError, PolicyViolationError

from backend.api.dependencies import get_customer_service, ml_globals
from backend.services.customer_service import CustomerService

router = APIRouter(prefix="/decisions", tags=["Decision Engine"])

def get_repository(session: AsyncSession = Depends(get_async_session)) -> DecisionRepository:
    return DecisionRepository(session)

def get_audit_service(repo: DecisionRepository = Depends(get_repository)) -> AuditService:
    return AuditService(repo)

def get_workflow_engine(repo: DecisionRepository = Depends(get_repository), audit: AuditService = Depends(get_audit_service)) -> WorkflowEngine:
    return WorkflowEngine(repo, audit)

def get_approval_service(we: WorkflowEngine = Depends(get_workflow_engine)) -> ApprovalService:
    return ApprovalService(we)

@router.post("/recommend", response_model=RecommendationSchema)
async def generate_recommendation(
    customer_id: str,
    repo: DecisionRepository = Depends(get_repository),
    audit_service: AuditService = Depends(get_audit_service),
    customer_svc: CustomerService = Depends(get_customer_service),
):
    """
    Triggers the full pipeline for a customer: Prediction -> SHAP -> Policy Engine -> Reasoning Engine -> Recommendation.
    """
    try:
        # 1. Gather context (Features, Prediction, SHAP, History)
        profile = await customer_svc.get_customer_profile(customer_id)
        prediction = profile.prediction if profile.prediction else {}
        
        # We simulate fetching SHAP for now if it's not cached, or call prediction_service
        # For this sprint, assume prediction dict has probability
        prob = prediction.get("probability", 0.0)
        
        features = profile.features.model_dump() if profile.features else {}
        history_orm = await repo.get_customer_history(customer_id)
        
        context = {
            "churn_probability": prob,
            **features,
            "decision_history": history_orm
        }
        
        # 2. Policy Engine (Deterministic rules)
        policy_decision = PolicyEngine.evaluate(context)
        await audit_service.log_event(customer_id, "policy_evaluated", json.dumps(policy_decision.model_dump()))
        
        # 3. Reasoning Engine (LLM Advisory)
        reasoning_engine = ReasoningEngine()
        reasoning = await reasoning_engine.generate_reasoning(context, policy_decision)
        await audit_service.log_event(customer_id, "reasoning_generated", json.dumps(reasoning.model_dump()))
        
        # 4. Recommendation Engine (Combines Both)
        rec_engine = RecommendationEngine(repo)
        recommendation = await rec_engine.generate_recommendation(customer_id, policy_decision, reasoning)
        await audit_service.log_event(customer_id, "recommendation_created", json.dumps(recommendation.model_dump(), default=str))
        
        # 5. Initialize Workflow state machine
        we = WorkflowEngine(repo, audit_service)
        await we.initialize_workflow(recommendation)
        
        return recommendation
        
    except PolicyViolationError as e:
        await audit_service.log_event(customer_id, "policy_violation", str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import structlog
        logger = structlog.get_logger(__name__)
        logger.error("recommendation_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post("/workflow/{id}/approve", response_model=WorkflowSchema)
async def approve_workflow(
    id: uuid.UUID,
    req: ApprovalRequest,
    repo: DecisionRepository = Depends(get_repository),
    app_svc: ApprovalService = Depends(get_approval_service)
):
    workflow = await repo.get_workflow(id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
        
    rec = await repo.get_recommendation(workflow.recommendation_id)
    try:
        return await app_svc.approve(id, req.approver_id, rec.customer_unique_id)
    except InvalidTransitionError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/workflow/{id}/reject", response_model=WorkflowSchema)
async def reject_workflow(
    id: uuid.UUID,
    req: RejectionRequest,
    repo: DecisionRepository = Depends(get_repository),
    app_svc: ApprovalService = Depends(get_approval_service)
):
    workflow = await repo.get_workflow(id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
        
    rec = await repo.get_recommendation(workflow.recommendation_id)
    try:
        return await app_svc.reject(id, req.approver_id, rec.customer_unique_id, req.reason)
    except InvalidTransitionError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/workflow/{id}/execute")
async def execute_workflow(
    id: uuid.UUID,
    repo: DecisionRepository = Depends(get_repository),
    we: WorkflowEngine = Depends(get_workflow_engine),
    audit: AuditService = Depends(get_audit_service)
):
    workflow = await repo.get_workflow(id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
        
    rec = await repo.get_recommendation(workflow.recommendation_id)
    
    # 1. State transition
    try:
        await we.transition(id, "Executing", rec.customer_unique_id)
    except InvalidTransitionError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    # 2. Execution (Synchronous simulation)
    executor = get_executor(rec.recommendation_type)
    result = await executor.execute(rec)
    
    # 3. Final transition and persistence
    final_status = "Completed" if result.get("status") == "Success" else "Failed"
    await we.transition(id, final_status, rec.customer_unique_id, json.dumps(result))
    
    exec_model = ExecutionModel(
        workflow_id=id,
        executor_type=executor.__class__.__name__,
        status=final_status,
        result_payload=json.dumps(result)
    )
    await repo.create_execution(exec_model)
    await audit.log_event(rec.customer_unique_id, f"execution_{final_status.lower()}", json.dumps(result), id)
    
    return {"status": final_status, "result": result}

@router.get("/workflow/{id}", response_model=WorkflowSchema)
async def get_workflow(id: uuid.UUID, repo: DecisionRepository = Depends(get_repository)):
    workflow = await repo.get_workflow(id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return WorkflowSchema.model_validate(workflow)

@router.get("/audit/{workflow_id}")
async def get_audit(workflow_id: uuid.UUID, audit: AuditService = Depends(get_audit_service)):
    return await audit.get_workflow_audit_trail(workflow_id)

@router.post("/feedback/{workflow_id}")
async def record_feedback(
    workflow_id: uuid.UUID,
    feedback: dict,
    repo: DecisionRepository = Depends(get_repository),
    audit: AuditService = Depends(get_audit_service)
):
    """Records an outcome for MLOps tracking. No consumer built yet."""
    workflow = await repo.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
        
    rec = await repo.get_recommendation(workflow.recommendation_id)
    await audit.log_event(rec.customer_unique_id, "feedback_received", json.dumps(feedback), workflow_id)
    return {"status": "Feedback recorded."}
