"""
MLOps Reports Generator.
Generates markdown reports based on database state.
"""
import os
import json
from datetime import datetime
from .repository import MLOpsRepository

class ReportGenerator:
    def __init__(self, repository: MLOpsRepository, report_dir: str = "reports"):
        self.repository = repository
        self.report_dir = report_dir
        os.makedirs(self.report_dir, exist_ok=True)

    async def generate_model_registry_report(self):
        models = await self.repository.get_all_models()
        path = os.path.join(self.report_dir, "model_registry_report.md")
        
        with open(path, "w", encoding="utf-8") as f:
            f.write("# Model Registry Report\n\n")
            f.write(f"Generated at: {datetime.utcnow().isoformat()}\n\n")
            f.write("| Version | Status | Dataset | Feature Set | Metrics |\n")
            f.write("|---------|--------|---------|-------------|---------|\n")
            
            for m in models:
                metrics = json.loads(m.metrics)
                acc = metrics.get("accuracy", "N/A")
                f.write(f"| v{m.version} | {m.deployment_status} | {m.dataset_version} | {m.feature_version} | Acc: {acc} |\n")

    async def generate_drift_and_quality_report(self, dq_report):
        drift_reports = await self.repository.get_recent_drift_reports(limit=1)
        path = os.path.join(self.report_dir, "drift_and_quality_report.md")
        
        with open(path, "w", encoding="utf-8") as f:
            f.write("# Drift and Data Quality Report\n\n")
            f.write(f"Generated at: {datetime.utcnow().isoformat()}\n\n")
            
            f.write("## Data Quality\n")
            f.write(f"- Status: {dq_report.overall_status}\n")
            f.write(f"- Total Rows: {dq_report.total_rows}\n")
            f.write(f"- Duplicates: {dq_report.duplicate_rows}\n")
            f.write(f"- Out of range features: {', '.join(dq_report.out_of_range_features) if dq_report.out_of_range_features else 'None'}\n\n")
            
            f.write("## Data Drift\n")
            if drift_reports:
                latest = drift_reports[0]
                f.write(f"- Alert Status: {'ACTIVE' if latest.is_alert else 'CLEAR'}\n")
                f.write(f"- Reference Window: {latest.reference_window_start} to {latest.reference_window_end}\n")
                f.write(f"- Current Window: {latest.current_window_start} to {latest.current_window_end}\n\n")
                
                f.write("### Feature Stats\n")
                stats = json.loads(latest.feature_stats)
                for feature, stat in stats.items():
                    f.write(f"**{feature}**:\n")
                    f.write(f"- PSI: {stat.get('psi', 'N/A')}\n")
                    f.write(f"- Mean shift: {stat.get('reference_mean', 'N/A')} -> {stat.get('current_mean', 'N/A')}\n\n")
            else:
                f.write("No drift reports available.\n")

    async def generate_system_health_report(self, health_data):
        path = os.path.join(self.report_dir, "system_health_report.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write("# System Health Report\n\n")
            f.write(f"Generated at: {datetime.utcnow().isoformat()}\n\n")
            f.write(f"**Overall Status**: {health_data.get('status', 'Unknown')}\n\n")
            
            f.write("### Subsystems\n")
            f.write(f"- Database: {health_data.get('database', {}).get('status', 'Unknown')} (Latency: {health_data.get('database', {}).get('latency_ms', 'N/A')}ms)\n")
            f.write(f"- Cache: {health_data.get('cache', {}).get('status', 'Unknown')} (Latency: {health_data.get('cache', {}).get('latency_ms', 'N/A')}ms)\n")
