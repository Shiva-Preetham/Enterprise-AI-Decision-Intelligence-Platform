"""
MLOps Experiment Tracker.
Logs every run to the database and CSV.
"""
import csv
import os
import structlog
from typing import Dict, Any

from .models import ExperimentModel
from .repository import MLOpsRepository

logger = structlog.get_logger(__name__)

class ExperimentTracker:
    def __init__(self, repository: MLOpsRepository, report_dir: str = "reports"):
        self.repository = repository
        self.report_dir = report_dir
        self.csv_path = os.path.join(self.report_dir, "experiment_history.csv")
        os.makedirs(self.report_dir, exist_ok=True)
        self._ensure_csv_headers()

    def _ensure_csv_headers(self):
        if not os.path.exists(self.csv_path):
            with open(self.csv_path, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "run_id", "timestamp", "duration_seconds", "params",
                    "metrics", "dataset_ref", "feature_count", "algorithm", "cv_scores"
                ])

    async def track_run(self, 
        run_id: str,
        duration_seconds: float,
        params: str,
        metrics: str,
        dataset_ref: str,
        feature_count: int,
        algorithm: str,
        cv_scores: str
    ) -> ExperimentModel:
        """Tracks the experiment run."""
        
        # 1. DB
        exp = ExperimentModel(
            run_id=run_id,
            duration_seconds=duration_seconds,
            params=params,
            metrics=metrics,
            dataset_ref=dataset_ref,
            feature_count=feature_count,
            algorithm=algorithm,
            cv_scores=cv_scores
        )
        saved = await self.repository.create_experiment(exp)
        
        # 2. CSV
        with open(self.csv_path, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                saved.run_id,
                saved.timestamp.isoformat() if saved.timestamp else "",
                saved.duration_seconds,
                saved.params,
                saved.metrics,
                saved.dataset_ref,
                saved.feature_count,
                saved.algorithm,
                saved.cv_scores
            ])
            
        logger.info("experiment_tracked", run_id=run_id, algorithm=algorithm)
        return saved
