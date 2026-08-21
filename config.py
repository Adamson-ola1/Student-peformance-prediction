from pathlib import Path

# ----------------------------------------------------------------------
# Project paths
# ----------------------------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parent


MODELS_DIR = ROOT_DIR / "models"
MODEL_DIR = MODELS_DIR
CHARTS_DIR = ROOT_DIR / "eda_charts"

# Ensure directories exists
MODELS_DIR.mkdir(parents=True, exist_ok=True)
CHARTS_DIR.mkdir(parents=True, exist_ok=True)