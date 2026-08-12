import pickle
import time
import numpy as np
import pandas as pd
from pathlib import Path


# ─────────────────────────────────────────────
# PATHS
# ─────────────────────────────────────────────
ROOT_DIR        = Path(__file__).resolve().parent.parent
MODELS_DIR      = ROOT_DIR / "models"
MODEL_PATH      = MODELS_DIR / "student_performance_model.pkl"
CLASSIFIER_PATH = MODELS_DIR / "student_performance_classifier.pkl"
META_PATH       = MODELS_DIR / "student_performance_model_meta.pkl"


# ─────────────────────────────────────────────
# FEATURE ORDER — must match training order
# ─────────────────────────────────────────────
FEATURE_ORDER = [
    "age",
    "attendance_rate",
      "study_hours_per_week",
      "previous_gpa",
      "extracurricular_score",
      "gender_Male",
      "family_income_Low",
      "family_income_Medium",
      "study_efficiency_ratio",
      "attendance_x_study"
]


# ─────────────────────────────────────────────
# LAZY LOADING GLOBALS
# Start as None — only loaded when first needed
# ─────────────────────────────────────────────
_regressor  = None
_classifier = None
_metadata   = None


# ─────────────────────────────────────────────
# SAFE PICKLE LOADER (with file check)
# ─────────────────────────────────────────────
def _load_pickle(path: Path):
    if not path.exists():
        raise FileNotFoundError(
            f"\n[ERROR] Model file not found:\n{path}\n\n"
            "Make sure save_model.py has been executed:\n"
            "  python save_model.py"
        )
    with open(path, "rb") as f:
        return pickle.load(f)


# ─────────────────────────────────────────────
# LAZY GETTERS
# Each model is loaded only on first access
# ─────────────────────────────────────────────
def get_regressor():
    global _regressor
    if _regressor is None:
        print(f"  Loading regressor  : {MODEL_PATH}")
        t = time.time()
        _regressor = _load_pickle(MODEL_PATH)
        print(f"  ✓ Regressor ready  : {time.time() - t:.2f}s")
    return _regressor


def get_classifier():
    global _classifier
    if _classifier is None:
        print(f"  Loading classifier : {CLASSIFIER_PATH}")
        t = time.time()
        _classifier = _load_pickle(CLASSIFIER_PATH)
        print(f"  ✓ Classifier ready : {time.time() - t:.2f}s")
    return _classifier


def get_metadata():
    global _metadata
    if _metadata is None:
        print(f"  Loading metadata   : {META_PATH}")
        t = time.time()
        _metadata = _load_pickle(META_PATH)
        print(f"  ✓ Metadata ready   : {time.time() - t:.2f}s")
    return _metadata


# ─────────────────────────────────────────────
# CALLED FROM main.py on_startup
# Pre-loads all models in the server process only
# ─────────────────────────────────────────────
def load_models():
    print(f"\n  Project Root : {ROOT_DIR}")
    total = time.time()

    get_regressor()
    get_classifier()
    get_metadata()

    print(f"  ✓ All models loaded in {time.time() - total:.2f}s total\n")


# ─────────────────────────────────────────────
# PREPARE INPUT FEATURES
# ─────────────────────────────────────────────
def prepare_features(data: dict) -> pd.DataFrame:
    row = {f: float(data.get(f, 0)) for f in FEATURE_ORDER}
    return pd.DataFrame([row], columns=FEATURE_ORDER)

# ─────────────────────────────────────────────
# PREDICT GPA + PASS/FAIL
# ─────────────────────────────────────────────
def predict_performance(data: dict) -> dict:
    regressor  = get_regressor()
    classifier = get_classifier()

    features = prepare_features(data)

    # Regression — predicted GPA
    predicted_gpa = round(float(regressor.predict(features)[0]), 2)

    # Classification — pass/fail
    predicted_class  = classifier.predict(features)[0]
    probabilities    = classifier.predict_proba(features)[0]
    pass_probability = round(float(probabilities[1]), 4)
    fail_probability = round(float(probabilities[0]), 4)
    pass_fail        = "Pass" if predicted_class == 1 else "Fail"

    return {
        "predicted_gpa":    predicted_gpa,
        "pass_fail":        pass_fail,
        "pass_probability": pass_probability,
        "fail_probability": fail_probability,
    }


# ─────────────────────────────────────────────
# MODEL INFO
# ─────────────────────────────────────────────
def get_model_info() -> dict:
    regressor  = get_regressor()
    classifier = get_classifier()
    metadata   = get_metadata()

    return {
        "model_type":       type(regressor).__name__,
        "classifier_type":  type(classifier).__name__,
        "feature_count":    len(FEATURE_ORDER),
        "feature_order":    FEATURE_ORDER,
        "metadata":         metadata,
    }