import pickle
import os
import json
import numpy as np

print("\n" + "="*60)
print("SAVE MODEL METADATA & FINAL ARTIFACTS")
print("="*60)


# ════════════════════════════════════════════════════════════════════════════
# PATH CONFIGURATION
# ════════════════════════════════════════════════════════════════════════════

# Always resolve paths relative to THIS file's location (project root)
# so the script works regardless of where you call it from.
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")

os.makedirs(MODELS_DIR, exist_ok=True)


# ════════════════════════════════════════════════════════════════════════════
# HELPER
# ════════════════════════════════════════════════════════════════════════════

def load_pkl(filename):
    path = os.path.join(MODELS_DIR, filename)
    with open(path, "rb") as f:
        return pickle.load(f)

def save_pkl(obj, filename):
    path = os.path.join(MODELS_DIR, filename)
    with open(path, "wb") as f:
        pickle.dump(obj, f)
    print(f"Saved: {path}")


# ════════════════════════════════════════════════════════════════════════════
# STEP 1 — LOAD TRAINED MODELS & SUPPORTING FILES
# ════════════════════════════════════════════════════════════════════════════

print("\n[1] Loading trained models from models/ ...")

try:
    rf_reg        = load_pkl("rf_regressor.pkl")
    rf_cls        = load_pkl("rf_classifier.pkl")
    scaler        = load_pkl("scaler.pkl")
    feature_names = load_pkl("feature_names.pkl")
    X_test_reg    = load_pkl("X_test_reg.pkl")
    X_test_cls    = load_pkl("X_test_cls.pkl")
    y_test_reg    = load_pkl("y_test_reg.pkl")
    y_test_cls    = load_pkl("y_test_cls.pkl")
    print("All models and supporting files loaded successfully.")
except FileNotFoundError as e:
    print(f"\n  [ERROR] Missing file: {e}")
    print("  Run train_model.py first: python train_model.py")
    raise


# ════════════════════════════════════════════════════════════════════════════
# STEP 2 — RECOMPUTE METRICS FOR METADATA
# ════════════════════════════════════════════════════════════════════════════

print("\n[2] Recomputing metrics for metadata ...")

from sklearn.metrics import (
    r2_score, mean_squared_error, mean_absolute_error,
    accuracy_score, roc_auc_score
)

preds_reg      = rf_reg.predict(X_test_reg)
preds_cls      = rf_cls.predict(X_test_cls)
preds_cls_prob = rf_cls.predict_proba(X_test_cls)[:, 1]

r2       = r2_score(y_test_reg, preds_reg)
rmse     = np.sqrt(mean_squared_error(y_test_reg, preds_reg))
mae      = mean_absolute_error(y_test_reg, preds_reg)
accuracy = accuracy_score(y_test_cls, preds_cls)
auc_roc  = roc_auc_score(y_test_cls, preds_cls_prob)

print(f"  R²       : {r2:.4f}")
print(f"  RMSE     : {rmse:.4f}")
print(f"  MAE      : {mae:.4f}")
print(f"  Accuracy : {accuracy:.4f}")
print(f"  AUC-ROC  : {auc_roc:.4f}")


# ════════════════════════════════════════════════════════════════════════════
# STEP 3 — SAVE MODEL METADATA AS JSON
# ════════════════════════════════════════════════════════════════════════════

print("\n[3] Saving model_metadata.json ...")

metadata = {
    "regression_model": {
        "type":          "RandomForestRegressor",
        "target":        "final_gpa",
        "n_estimators":  rf_reg.n_estimators,
        "r2_score":      round(r2, 4),
        "rmse":          round(rmse, 4),
        "mae":           round(mae, 4),
        "oob_score":     round(rf_reg.oob_score_, 4),
        "feature_importances": {
            name: round(float(imp), 6)
            for name, imp in zip(
                feature_names,
                rf_reg.feature_importances_
            )
        },
    },
    "classification_model": {
        "type":         "RandomForestClassifier",
        "target":       "pass_fail",
        "n_estimators": rf_cls.n_estimators,
        "accuracy":     round(accuracy, 4),
        "auc_roc":      round(auc_roc, 4),
        "oob_score":    round(rf_cls.oob_score_, 4),
    },
    "feature_names":  feature_names,
    "feature_count":  len(feature_names),
}

# Save JSON to project root (next to save_model.py)
metadata_path = os.path.join(BASE_DIR, "model_metadata.json")
with open(metadata_path, "w") as f:
    json.dump(metadata, f, indent=2)
print(f"Saved: {metadata_path}")


# ════════════════════════════════════════════════════════════════════════════
# STEP 4 — SAVE NAMED COPIES FOR LEGACY COMPATIBILITY
# ════════════════════════════════════════════════════════════════════════════
# These are the filenames the old code and ml_model.py may reference.

print("\n[4] Saving named copies for API / legacy compatibility ...")

save_pkl(rf_reg,        "student_performance_model.pkl")
save_pkl(rf_cls,        "student_performance_classifier.pkl")
save_pkl(
    {
        "r2_score":            round(r2, 4),
        "rmse":                round(rmse, 4),
        "mae":                 round(mae, 4),
        "accuracy":            round(accuracy, 4),
        "auc_roc":             round(auc_roc, 4),
        "feature_names":       feature_names,
        "regression_model":    "RandomForestRegressor",
        "classification_model":"RandomForestClassifier",
    },
    "student_performance_model_meta.pkl"
)


# ════════════════════════════════════════════════════════════════════════════
# STEP 5 — FINAL SUMMARY
# ════════════════════════════════════════════════════════════════════════════

print("\n" + "="*60)
print("  SAVE MODEL COMPLETE")
print("="*60)
print(f"""
  ── ALL FILES SAVED TO: {MODELS_DIR} ──

  rf_regressor.pkl                    ← primary regression model
  rf_classifier.pkl                   ← primary classification model
  scaler.pkl                          ← StandardScaler
  feature_names.pkl                   ← feature column names
  student_performance_model.pkl       ← legacy copy (regression)
  student_performance_classifier.pkl  ← legacy copy (classification)
  student_performance_model_meta.pkl  ← legacy copy (metadata)

  ── PROJECT ROOT ──
  model_metadata.json                 ← human-readable metrics & importances

""")
print("="*60)

