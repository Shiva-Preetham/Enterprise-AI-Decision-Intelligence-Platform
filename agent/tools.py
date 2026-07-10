"""
Enterprise AI Customer Intelligence Platform — Agent Tools.

Wraps existing Backend Services into LangChain @tool decorators.
These tools are injected with the required Service instances at runtime.
"""

from typing import Dict, Any, Optional
from langchain_core.tools import tool
import json
import contextvars

# Thread-safe reference to backend services (injected by the router per request)
_services_ctx: contextvars.ContextVar[dict] = contextvars.ContextVar("agent_services", default={})

def inject_services(customer_service, analytics_service, model_service):
    """Sets the context-local service references used by the tools."""
    _services_ctx.set({
        "customer": customer_service,
        "analytics": analytics_service,
        "model": model_service
    })

@tool
async def get_customer_profile(customer_id: str) -> str:
    """
    Retrieves a complete Customer 360 profile including database records, 
    engineered Feature Store metrics, and live ML churn predictions.
    Use this when asked about a specific customer's details or risk.
    """
    svc = _services_ctx.get().get("customer")
    if not svc:
        return json.dumps({"error": "Customer service not available."})
    try:
        profile = await svc.get_customer_profile(customer_id)
        return profile.model_dump_json()
    except Exception as e:
        return json.dumps({"error": str(e)})

@tool
async def get_customer_timeline(customer_id: str) -> str:
    """
    Retrieves chronological events (recent orders, recent reviews) for a specific customer.
    Use this to understand a customer's recent interaction history.
    """
    svc = _services_ctx.get().get("customer")
    if not svc:
        return json.dumps({"error": "Customer service not available."})
    try:
        timeline = await svc.get_customer_timeline(customer_id)
        return json.dumps(timeline, default=str)
    except Exception as e:
        return json.dumps({"error": str(e)})

@tool
async def get_dashboard_metrics() -> str:
    """
    Retrieves aggregate platform analytics including total customers, high-risk count, 
    average CLV, average churn probability, and average order value.
    Use this for high-level business reporting.
    """
    svc = _services_ctx.get().get("analytics")
    if not svc:
        return json.dumps({"error": "Analytics service not available."})
    try:
        metrics = await svc.get_dashboard_metrics()
        return metrics.model_dump_json()
    except Exception as e:
        return json.dumps({"error": str(e)})

@tool
async def get_model_metadata() -> str:
    """
    Retrieves information about the current Machine Learning models in production,
    including Algorithm, Training Date, ROC AUC, F1 Score, and Pipeline Versions.
    Use this when asked about ML performance or versions.
    """
    svc = _services_ctx.get().get("model")
    if not svc:
        return json.dumps({"error": "Model service not available."})
    try:
        info = svc.get_performance_metrics()
        return json.dumps(info, default=str)
    except Exception as e:
        return json.dumps({"error": str(e)})

@tool
async def trigger_background_task(task_type: str) -> str:
    """
    Triggers a heavy background operation. 
    Allowed task_types: 'train', 'feature_store', 'batch_predict', 'refresh_dashboard'.
    Returns the task_id.
    """
    try:
        if task_type == 'train':
            from workers.tasks.training import retrain_model
            result = retrain_model.delay()
            return f"Model retraining queued. Task ID: {result.id}"
        elif task_type == 'feature_store':
            from workers.tasks.feature_store import rebuild_feature_store
            result = rebuild_feature_store.delay()
            return f"Feature store rebuild queued. Task ID: {result.id}"
        elif task_type == 'refresh_dashboard':
            from workers.tasks.analytics import refresh_dashboard_cache
            result = refresh_dashboard_cache.delay()
            return f"Dashboard cache refresh queued. Task ID: {result.id}"
        else:
            return "Error: Invalid task_type. Must be train, feature_store, or refresh_dashboard."
    except Exception as e:
        return f"Failed to trigger task: {str(e)}"

# List of all available tools to pass to the agent
AVAILABLE_TOOLS = [
    get_customer_profile,
    get_customer_timeline,
    get_dashboard_metrics,
    get_model_metadata,
    trigger_background_task
]
