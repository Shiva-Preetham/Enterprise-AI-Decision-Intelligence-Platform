import json
from pathlib import Path
from typing import Any, Dict

class CustomJSONEncoder(json.JSONEncoder):
    """Handles serialization of NumPy/Pandas types that native json cannot."""
    def default(self, obj):
        import numpy as np
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)

def save_json(data: Dict[str, Any], filepath: Path) -> None:
    """Save dictionary to JSON safely."""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4, cls=CustomJSONEncoder)

def ensure_dir(path: Path) -> None:
    """Ensure directory exists."""
    path.mkdir(parents=True, exist_ok=True)
