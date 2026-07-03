import shap
import matplotlib.pyplot as plt
import pandas as pd
from structlog import get_logger

from ml.config import REPORTS_DIR

logger = get_logger(__name__)

class SHAPExplainer:
    """Generates SHAP values and explainability plots for the best model."""

    def __init__(self, model, feature_names):
        self.model = model
        self.feature_names = feature_names
        self.explainer = None
        self.shap_values = None

    def explain(self, X_sample: pd.DataFrame):
        """Computes SHAP values and saves explanation plots."""
        logger.info("generating_shap_explanations")
        
        # Convert to DataFrame with columns for SHAP
        X_df = pd.DataFrame(X_sample, columns=self.feature_names)
        
        # TreeExplainer works for RF, XGB, LGBM
        if hasattr(self.model, "tree_"): # basic check, but shap usually infers
            self.explainer = shap.TreeExplainer(self.model)
        else:
            self.explainer = shap.Explainer(self.model, X_df)
            
        self.shap_values = self.explainer(X_df)
        
        self._generate_plots(X_df)
        logger.info("shap_explanations_complete")
        return self.explainer

    def _generate_plots(self, X_df):
        """Generates Summary, Bar, and Waterfall plots."""
        # Global Feature Importance (Bar)
        plt.figure(figsize=(10, 6))
        shap.plots.bar(self.shap_values, show=False)
        plt.title("SHAP Global Feature Importance")
        plt.tight_layout()
        plt.savefig(REPORTS_DIR / "shap_bar_plot.png", dpi=300, bbox_inches='tight')
        plt.close()

        # Summary Plot (Dots)
        plt.figure(figsize=(10, 6))
        shap.summary_plot(self.shap_values, X_df, show=False)
        plt.title("SHAP Summary Plot")
        plt.tight_layout()
        plt.savefig(REPORTS_DIR / "shap_summary_plot.png", dpi=300, bbox_inches='tight')
        plt.close()

        # Waterfall Plot for the first customer
        plt.figure(figsize=(10, 6))
        shap.plots.waterfall(self.shap_values[0], show=False)
        plt.title("SHAP Waterfall Plot (Customer 0)")
        plt.tight_layout()
        plt.savefig(REPORTS_DIR / "shap_waterfall_plot.png", dpi=300, bbox_inches='tight')
        plt.close()
