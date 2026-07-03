import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from sklearn.metrics import ConfusionMatrixDisplay

def plot_roc_curve(fpr: np.ndarray, tpr: np.ndarray, auc_score: float, model_name: str, filepath: Path):
    """Plots and saves the ROC Curve."""
    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (area = {auc_score:.3f})')
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title(f'Receiver Operating Characteristic - {model_name}')
    plt.legend(loc="lower right")
    plt.grid(alpha=0.3)
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()

def plot_pr_curve(precision: np.ndarray, recall: np.ndarray, model_name: str, filepath: Path):
    """Plots and saves the Precision-Recall Curve."""
    plt.figure(figsize=(8, 6))
    plt.plot(recall, precision, color='blue', lw=2)
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title(f'Precision-Recall Curve - {model_name}')
    plt.grid(alpha=0.3)
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()

def plot_confusion_matrix(cm: np.ndarray, model_name: str, filepath: Path):
    """Plots and saves the Confusion Matrix."""
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=['Retained', 'Churned'])
    fig, ax = plt.subplots(figsize=(6, 6))
    disp.plot(ax=ax, cmap=plt.cm.Blues, values_format='d')
    plt.title(f'Confusion Matrix - {model_name}')
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()

def plot_feature_importance(importances: np.ndarray, feature_names: list, model_name: str, filepath: Path, top_n: int = 15):
    """Plots and saves Feature Importance for tree-based models."""
    indices = np.argsort(importances)[::-1][:top_n]
    top_features = [feature_names[i] for i in indices]
    top_importances = importances[indices]

    plt.figure(figsize=(10, 6))
    plt.title(f"Top {top_n} Feature Importances - {model_name}")
    plt.barh(range(top_n), top_importances[::-1], color="steelblue", align="center")
    plt.yticks(range(top_n), top_features[::-1])
    plt.xlabel("Relative Importance")
    plt.tight_layout()
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()
