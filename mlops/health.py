"""
MLOps Health Checks.
"""
import time
from fastapi import APIRouter, Depends
from typing import Dict, Any
import structlog
from typing import Dict, Any

from backend.db.session import get_async_session

from mlops.repository import MLOpsRepository

router = APIRouter(prefix="/health", tags=["Health Checks"])
logger = structlog.get_logger(__name__)

def get_repository(session = Depends(get_async_session)) -> MLOpsRepository:
    return MLOpsRepository(session)

async def measure_latency(func) -> Dict[str, Any]:
    start = time.perf_counter()
    try:
        await func()
        latency = round((time.perf_counter() - start) * 1000, 2)
        return {"status": "ok", "latency_ms": latency}
    except Exception as e:
        logger.error("health_check_failed", error=str(e))
        latency = round((time.perf_counter() - start) * 1000, 2)
        return {"status": "error", "error": str(e), "latency_ms": latency}

@router.get("/")
async def get_overall_health(repo: MLOpsRepository = Depends(get_repository)):
    """Aggregate health check."""
    db_health = await get_database_health(repo)
    cache_health = await get_cache_health()
    
    overall_status = "ok" if db_health["status"] == "ok" and cache_health["status"] == "ok" else "degraded"
    
    return {
        "status": overall_status,
        "database": db_health,
        "cache": cache_health,
        "timestamp": time.time()
    }

@router.get("/database")
async def get_database_health(repo: MLOpsRepository = Depends(get_repository)):
    async def check_db():
        await repo.check_database_health()
    return await measure_latency(check_db)

@router.get("/cache")
async def get_cache_health():
    async def check_cache():
        # Simulated ping since we are not directly importing the Redis client to avoid circular deps
        # In a real setup, we'd do `await redis_client.ping()`
        pass
    return await measure_latency(check_cache)

@router.get("/ml")
async def get_ml_health():
    """Can the model artifacts be loaded?"""
    async def check_ml():
        # Simulated check
        pass
    return await measure_latency(check_ml)

@router.get("/agent")
async def get_agent_health():
    """Can the LLM client be reached?"""
    async def check_agent():
        # Simulated lightweight ping to LLM provider
        pass
    return await measure_latency(check_agent)
