"""
MLOps Alerting Engine.
Evaluates rules and persists alerts using simulated execution.
"""
from typing import Dict, Any
import structlog
from .models import AlertModel
from .repository import MLOpsRepository

logger = structlog.get_logger(__name__)

class SlackNotifierExecutor:
    """
    Simulated executor matching the ExecutorBase pattern from decision_engine.
    Logs the alert instead of actually posting to Slack.
    """
    @staticmethod
    async def execute(alert_type: str, severity: str, details: str) -> Dict[str, str]:
        logger.warning(
            "simulated_slack_alert",
            alert_type=alert_type,
            severity=severity,
            details=details
        )
        return {"status": "Success", "message": "Logged to simulated Slack channel"}

class AlertingEngine:
    def __init__(self, repository: MLOpsRepository):
        self.repository = repository
        self.notifier = SlackNotifierExecutor()

    async def evaluate_drift(self, drift_results: Dict[str, Any]) -> None:
        """Evaluate drift results and trigger alert if necessary."""
        is_alert = drift_results.get("is_alert", False)
        
        if is_alert:
            details = f"Drift detected in features. Data: {drift_results.get('feature_stats')}"
            await self._trigger_alert("drift", "warning", details)

    async def evaluate_error_rate(self, error_count: int, threshold: int = 10) -> None:
        """Evaluate error rate spikes."""
        if error_count > threshold:
            details = f"Error rate spike detected: {error_count} errors."
            await self._trigger_alert("error_rate", "critical", details)

    async def _trigger_alert(self, alert_type: str, severity: str, details: str) -> None:
        alert = AlertModel(
            alert_type=alert_type,
            severity=severity,
            details=details,
            status="new"
        )
        await self.repository.create_alert(alert)
        await self.notifier.execute(alert_type, severity, details)
