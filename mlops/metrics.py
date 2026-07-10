"""
MLOps Prometheus Metrics.
Exposes standard metrics for scraping.
"""
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import APIRouter, Response

# Metrics Registry
HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status_code"]
)

HTTP_REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"]
)

MODEL_INFERENCE_DURATION = Histogram(
    "model_inference_duration_seconds",
    "Model inference duration in seconds",
    ["model_name", "version"]
)

RECOMMENDATION_COUNT = Counter(
    "recommendation_count_total",
    "Total number of recommendations generated",
    ["recommendation_type"]
)

APPROVAL_COUNT = Counter(
    "approval_count_total",
    "Total number of approvals processed",
    ["status"] # approved, rejected
)

CACHE_HITS = Counter("cache_hits_total", "Total cache hits")
CACHE_MISSES = Counter("cache_misses_total", "Total cache misses")
ERROR_RATE = Counter("error_rate_total", "Total application errors", ["error_type"])

router = APIRouter(tags=["Metrics"])

@router.get("/metrics")
async def get_metrics():
    """Endpoint for Prometheus scraping."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
