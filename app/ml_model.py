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
MODEL_PATH      = MODELS_DIR / "rf_regressor.pkl"
CLASSIFIER_PATH = MODELS_DIR / "rf_classifier.pkl"
META_PATH       = MODELS_DIR / "student_performance_model_meta.pkl"
FEATURE_NAMES_PATH = MODELS_DIR / "feature_names.pkl"


# ─────────────────────────────────────────────
# LAZY LOADING GLOBALS
# Start as None — only loaded when first needed
# ─────────────────────────────────────────────
_regressor  = None
_classifier = None
_metadata   = None
_feature_names = None


# ─────────────────────────────────────────────
# SAFE PICKLE LOADER (with file check)
# ─────────────────────────────────────────────
def _load_pickle(path: Path):
    if not path.exists():
        raise FileNotFoundError(
            f"\n[ERROR] Model file not found:\n{path}\n\n"
            "Make sure train.py has been executed:\n"
            "  python train.py"
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

def get_feature_names():
    global _feature_names
    if _feature_names is None:
        _feature_names = _load_pickle(FEATURE_NAMES_PATH)
    return _feature_names


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
    get_feature_names()

    print(f"  ✓ All models loaded in {time.time() - total:.2f}s total\n")


# ─────────────────────────────────────────────
# PREPARE INPUT FEATURES
# ─────────────────────────────────────────────
def prepare_features(data: dict) -> pd.DataFrame:
    feature_names = get_feature_names()
    
    df = pd.DataFrame([data])
    
    # Feature Engineering
    df["study_efficiency_ratio"] = (
        df["study_hours_per_week"].astype(float) /
        df["age"].replace(0, np.nan)
    ).round(4)
    
    df["attendance_x_study"] = (
    (df["attendance_rate"] / 100.0) * df["study_hours_per_week"]
    ).round(4)
    
    # Categorical Enconding
    df = pd.get_dummies(
        df,
        columns=["gender", "family_income"],
        drop_first=True,
        dtype=int
    )
    
    # Ensure all training features are present, fill missing dummies with 0, and match exact order
    for col in feature_names:
        if col not in df.columns:
            df[col] = 0
    
    return df[feature_names]
    
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
    feature_names = get_feature_names()

    return {
        "model_type":       type(regressor).__name__,
        "classifier_type":  type(classifier).__name__,
        "feature_count":    len(feature_names),
        "feature_order":    feature_names,
        "metadata":         metadata,
    }