import pandas as pd
from structlog import get_logger

from ml.metrics import compute_metrics, get_confusion_matrix, get_roc_curve_data, get_pr_curve_data
from ml.plots import plot_roc_curve, plot_pr_curve, plot_confusion_matrix, plot_feature_importance
from ml.config import REPORTS_DIR

logger = get_logger(__name__)

class ModelEvaluator:
    """Evaluates trained models and generates reports/plots."""

    def __init__(self, models: dict, feature_names: list):
        self.models = models
        self.feature_names = feature_names
        self.evaluation_results = {}
        self.best_model_name = None

    def evaluate_all(self, X_test, y_test):
        """Evaluates all models, saves plots, and determines the best model."""
        best_roc_auc = -1.0
        
        comparison_data = []

        for name, model in self.models.items():
            logger.info("evaluating_model", model=name)
            
            y_prob = model.predict_proba(X_test)[:, 1]
            y_pred = model.predict(X_test)

            metrics = compute_metrics(y_test, y_pred, y_prob)
            self.evaluation_results[name] = metrics
            
            # Track best model based on ROC AUC
            if metrics["roc_auc"] > best_roc_auc:
                best_roc_auc = metrics["roc_auc"]
                self.best_model_name = name

            metrics_row = {"Model": name, **metrics}
            comparison_data.append(metrics_row)

            # Generate Plots
            self._generate_plots(y_test, y_pred, y_prob, model, name)

        # Save comparison report
        comparison_df = pd.DataFrame(comparison_data)
        comparison_df.to_csv(REPORTS_DIR / "model_comparison.csv", index=False)
        
        # Save a text classification report for the best model
        with open(REPORTS_DIR / "classification_report.txt", "w") as f:
            f.write(f"Best Model: {self.best_model_name}\n")
            f.write(f"ROC AUC: {self.evaluation_results[self.best_model_name]['roc_auc']:.4f}\n")
            
        logger.info("evaluation_complete", best_model=self.best_model_name, best_roc_auc=best_roc_auc)
        return self.best_model_name, self.evaluation_results

    def _generate_plots(self, y_test, y_pred, y_prob, model, name):
        """Helper to generate and save all plots for a given model."""
        cm = get_confusion_matrix(y_test, y_pred)
        plot_confusion_matrix(cm, name, REPORTS_DIR / f"{name}_confusion_matrix.png")

        fpr, tpr, _ = get_roc_curve_data(y_test, y_prob)
        plot_roc_curve(fpr, tpr, self.evaluation_results[name]["roc_auc"], name, REPORTS_DIR / f"{name}_roc_curve.png")

        precision, recall, _ = get_pr_curve_data(y_test, y_prob)
        plot_pr_curve(precision, recall, name, REPORTS_DIR / f"{name}_pr_curve.png")

        # Feature Importance (skip for Logistic Regression unless we use coef_)
        if hasattr(model, "feature_importances_"):
            plot_feature_importance(model.feature_importances_, self.feature_names, name, REPORTS_DIR / f"{name}_feature_importance.png")
