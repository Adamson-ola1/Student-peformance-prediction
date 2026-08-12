import pickle
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import (
    mean_squared_error, r2_score, mean_absolute_error,
    accuracy_score, classification_report, confusion_matrix,
    roc_auc_score, roc_curve
)

print("\n" + "="*60)
print("ML MODEL TRAINING & EVALUATION")
print("="*60)

# ════════════════════════════════════════════════════════════════════════════
# PATH CONFIGURATION
# ════════════════════════════════════════════════════════════════════════════
 
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")
CHARTS_DIR = os.path.join(BASE_DIR, "eda_charts")
 
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(CHARTS_DIR, exist_ok=True)
 
sns.set_theme(style="whitegrid")
plt.rcParams.update({"figure.dpi": 150, "font.family": "Arial"})
 
 
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
 
def save_chart(filename):
    path = os.path.join(CHARTS_DIR, filename)
    plt.savefig(path, bbox_inches="tight")
    plt.close()
    print(f"Saved: {path}")


# ════════════════════════════════════════════════════════════════════════════
# STEP 1 — LOAD PREPROCESSED DATA
# ════════════════════════════════════════════════════════════════════════════

print("\n[1] Loading preprocessed data from models/ ...")

def load_pkl(path):
    with open(path, "rb") as f:
        return pickle.load(f)

try:
    X_train_reg  = load_pkl("models/X_train_reg.pkl")
    X_test_reg   = load_pkl("models/X_test_reg.pkl")
    y_train_reg  = load_pkl("models/y_train_reg.pkl")
    y_test_reg   = load_pkl("models/y_test_reg.pkl")
    X_train_cls  = load_pkl("models/X_train_cls.pkl")
    X_test_cls   = load_pkl("models/X_test_cls.pkl")
    y_train_cls  = load_pkl("models/y_train_cls.pkl")
    y_test_cls   = load_pkl("models/y_test_cls.pkl")
    feature_names = load_pkl("models/feature_names.pkl")
    print(f"Train size : {X_train_reg.shape[0]:,} rows")
    print(f"Test size  : {X_test_reg.shape[0]:,} rows")
    print(f"Features   : {len(feature_names)} columns")
except FileNotFoundError:
    print("\n  [ERROR] Preprocessed data not found.")
    print("  Run preprocessing.py first: python preprocessing.py")
    raise


# ════════════════════════════════════════════════════════════════════════════
# STEP 2 — MODEL A: RandomForestRegressor (predict final_gpa)
# ════════════════════════════════════════════════════════════════════════════

print("\n[2] Training Model A — RandomForestRegressor (predict final_gpa) ...")

rf_reg = RandomForestRegressor(
    n_estimators=200,    # 200 decision trees
    max_depth=None,      # Trees grow fully — let the forest decide
    min_samples_split=5, # Minimum samples to split an internal node
    min_samples_leaf=2,  # Minimum samples at a leaf node
    max_features="sqrt", # Features to consider per split (sqrt = default)
    random_state=42,     # Reproducibility
    n_jobs=-1,           # Use all CPU cores
    oob_score=True,      # Out-of-bag error estimate (free validation)
)

rf_reg.fit(X_train_reg, y_train_reg)
print("Model trained.")
print(f"OOB R² score (training estimate): {rf_reg.oob_score_:.4f}")

# Evaluate on held-out test set
preds_reg = rf_reg.predict(X_test_reg)

mse  = mean_squared_error(y_test_reg, preds_reg)
rmse = np.sqrt(mse)
mae  = mean_absolute_error(y_test_reg, preds_reg)
r2   = r2_score(y_test_reg, preds_reg)

print("\n  ── REGRESSION EVALUATION METRICS ──")
print(f"  R²   (coefficient of determination) : {r2:.4f}")
print(f"  MSE  (mean squared error)            : {mse:.4f}")
print(f"  RMSE (root mean squared error)       : {rmse:.4f}")
print(f"  MAE  (mean absolute error)           : {mae:.4f}")

# Phase 5 deliverable check
TARGET_R2 = 0.85
if r2 >= TARGET_R2:
    print(f"\n DELIVERABLE MET — R² = {r2:.4f} (≥ {TARGET_R2} required)")
else:
    print(f"\n R² = {r2:.4f} is below target {TARGET_R2}.")
    print(" Consider: more data, deeper trees, or additional features.")

# Save model
with open("models/rf_regressor.pkl", "wb") as f:
    pickle.dump(rf_reg, f)
print("\n Saved: models/rf_regressor.pkl")


# ════════════════════════════════════════════════════════════════════════════
# STEP 3 — MODEL B: RandomForestClassifier (predict pass/fail)
# ════════════════════════════════════════════════════════════════════════════

print("\n[3] Training Model B — RandomForestClassifier (predict pass_fail) ...")

rf_cls = RandomForestClassifier(
    n_estimators=200,
    max_depth=None,
    min_samples_split=5,
    min_samples_leaf=2,
    max_features="sqrt",
    class_weight="balanced",  # Handle class imbalance automatically
    random_state=42,
    n_jobs=-1,
    oob_score=True,
)

rf_cls.fit(X_train_cls, y_train_cls)
print("Model trained.")
print(f"OOB accuracy (training estimate): {rf_cls.oob_score_:.4f}")

preds_cls      = rf_cls.predict(X_test_cls)
preds_cls_prob = rf_cls.predict_proba(X_test_cls)[:, 1]

accuracy = accuracy_score(y_test_cls, preds_cls)
auc_roc  = roc_auc_score(y_test_cls, preds_cls_prob)

print("\n ── CLASSIFICATION EVALUATION METRICS ──")
print(f"Accuracy       : {accuracy:.4f}")
print(f"AUC-ROC        : {auc_roc:.4f}")
print("\nClassification Report:")
print(classification_report(y_test_cls, preds_cls,
                             target_names=["Fail (0)", "Pass (1)"]))

with open("models/rf_classifier.pkl", "wb") as f:
    pickle.dump(rf_cls, f)
print("Saved: models/rf_classifier.pkl")


# ════════════════════════════════════════════════════════════════════════════
# STEP 4 — BASELINE COMPARISON (Linear Regression + Logistic Regression)
# ════════════════════════════════════════════════════════════════════════════

print("\n[4] Baseline model comparison ...")

# Baseline regression
lr_reg = LinearRegression()
lr_reg.fit(X_train_reg, y_train_reg)
lr_reg_preds = lr_reg.predict(X_test_reg)
lr_r2 = r2_score(y_test_reg, lr_reg_preds)

# Baseline classification
lr_cls = LogisticRegression(max_iter=1000, random_state=42)
lr_cls.fit(X_train_cls, y_train_cls)
lr_cls_preds = lr_cls.predict(X_test_cls)
lr_acc = accuracy_score(y_test_cls, lr_cls_preds)

print("\n  ── MODEL COMPARISON TABLE ──")
print(f"  {'Model':<35} {'Metric':<12} {'Score':<10}")
print(f"  {'-'*55}")
print(f"  {'RandomForestRegressor':<35} {'R²':<12} {r2:.4f}")
print(f"  {'LinearRegression (baseline)':<35} {'R²':<12} {lr_r2:.4f}")
print(f"  {'RandomForestClassifier':<35} {'Accuracy':<12} {accuracy:.4f}")
print(f"  {'LogisticRegression (baseline)':<35} {'Accuracy':<12} {lr_acc:.4f}")
improvement_r2  = r2 - lr_r2
improvement_acc = accuracy - lr_acc
print(f"\n  RF improvement over Linear Regression   : +{improvement_r2:.4f} R²")
print(f"  RF improvement over Logistic Regression : +{improvement_acc:.4f} Accuracy")


# ════════════════════════════════════════════════════════════════════════════
# CHARTS — Evaluation Visuals
# ════════════════════════════════════════════════════════════════════════════

print("\n[5] Generating evaluation charts ...")

# ── Chart A: Actual vs Predicted GPA ─────────────────────────────────────────
fig, ax = plt.subplots(figsize=(8, 6))
ax.scatter(y_test_reg, preds_reg, alpha=0.4, s=18,
           color="#2563A8", edgecolors="none", label="Predictions")
min_val = min(y_test_reg.min(), preds_reg.min())
max_val = max(y_test_reg.max(), preds_reg.max())
ax.plot([min_val, max_val], [min_val, max_val],
        "r--", linewidth=1.5, label="Perfect prediction line")
ax.set_xlabel("Actual Final GPA")
ax.set_ylabel("Predicted Final GPA")
ax.set_title(f"Actual vs Predicted Final GPA\n"
             f"RandomForestRegressor (R² = {r2:.4f}, RMSE = {rmse:.4f})",
             fontweight="bold")
ax.legend()
ax.text(0.05, 0.92, f"R² = {r2:.4f}", transform=ax.transAxes,
        fontsize=11, bbox=dict(boxstyle="round", facecolor="white", alpha=0.8))
plt.tight_layout()
plt.savefig("eda_charts/chart11_actual_vs_predicted_gpa.png", bbox_inches="tight")
plt.close()
print("Saved: eda_charts/chart11_actual_vs_predicted_gpa.png")

# ── Chart B: Residuals plot ───────────────────────────────────────────────────
residuals = y_test_reg - preds_reg
fig, ax = plt.subplots(figsize=(8, 5))
ax.scatter(preds_reg, residuals, alpha=0.4, s=18,
           color="#E67E22", edgecolors="none")
ax.axhline(0, color="black", linewidth=1.2, linestyle="--")
ax.set_xlabel("Predicted Final GPA")
ax.set_ylabel("Residual (Actual − Predicted)")
ax.set_title("Residuals Plot — RandomForestRegressor\n"
             "(random scatter around 0 = good model)",
             fontweight="bold")
plt.tight_layout()
plt.savefig("eda_charts/chart12_residuals.png", bbox_inches="tight")
plt.close()
print("Saved: eda_charts/chart12_residuals.png")

# ── Chart C: Feature Importance (Regression model) ───────────────────────────
importances = pd.Series(rf_reg.feature_importances_, index=feature_names)
importances = importances.sort_values(ascending=True)

fig, ax = plt.subplots(figsize=(9, 6))
colours = ["#2563A8" if i >= len(importances) - 3 else "#BDD7EE"
           for i in range(len(importances))]
ax.barh(importances.index, importances.values,
        color=colours, edgecolor="white", height=0.6)
ax.set_xlabel("Feature Importance (Mean Decrease in Impurity)")
ax.set_title("Feature Importance — RandomForestRegressor\n"
             "(top 3 highlighted in dark blue)", fontweight="bold")
for i, (val, label) in enumerate(zip(importances.values, importances.index)):
    ax.text(val + 0.002, i, f"{val:.4f}", va="center", fontsize=8)
plt.tight_layout()
plt.savefig("eda_charts/chart13_feature_importance.png", bbox_inches="tight")
plt.close()
print("Saved: eda_charts/chart13_feature_importance.png")

# ── Chart D: Confusion Matrix (Classification) ───────────────────────────────
cm = confusion_matrix(y_test_cls, preds_cls)
fig, ax = plt.subplots(figsize=(6, 5))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
            xticklabels=["Fail (0)", "Pass (1)"],
            yticklabels=["Fail (0)", "Pass (1)"],
            linewidths=0.5, ax=ax)
ax.set_xlabel("Predicted")
ax.set_ylabel("Actual")
ax.set_title(f"Confusion Matrix — RandomForestClassifier\n"
             f"Accuracy = {accuracy:.4f} | AUC-ROC = {auc_roc:.4f}",
             fontweight="bold")
plt.tight_layout()
plt.savefig("eda_charts/chart14_confusion_matrix.png", bbox_inches="tight")
plt.close()
print("Saved: eda_charts/chart14_confusion_matrix.png")

# ── Chart E: ROC Curve ───────────────────────────────────────────────────────
fpr, tpr, _ = roc_curve(y_test_cls, preds_cls_prob)
fig, ax = plt.subplots(figsize=(7, 6))
ax.plot(fpr, tpr, color="#1A6B3C", linewidth=2.0,
        label=f"RF Classifier (AUC = {auc_roc:.4f})")
ax.plot([0, 1], [0, 1], "r--", linewidth=1.0, label="Random guess (AUC = 0.50)")
ax.fill_between(fpr, tpr, alpha=0.15, color="#1A6B3C")
ax.set_xlabel("False Positive Rate (1 − Specificity)")
ax.set_ylabel("True Positive Rate (Sensitivity)")
ax.set_title("ROC Curve — RandomForestClassifier\n"
             "(Pass / Fail classification)", fontweight="bold")
ax.legend(loc="lower right")
plt.tight_layout()
plt.savefig("eda_charts/chart15_roc_curve.png", bbox_inches="tight")
plt.close()
print("Saved: eda_charts/chart15_roc_curve.png")


# ════════════════════════════════════════════════════════════════════════════
# STEP 5 — FINAL SUMMARY
# ════════════════════════════════════════════════════════════════════════════

print("\n" + "="*60)
print("TRAIN MODEL SUMMARY")
print("="*60)
print(f"""
  ── REGRESSION MODEL (RandomForestRegressor) ──
  R²   : {r2:.4f}    {'DELIVERABLE MET' if r2 >= 0.85 else '✗ Below target 0.85'}
  RMSE : {rmse:.4f}
  MAE  : {mae:.4f}

  ── CLASSIFICATION MODEL (RandomForestClassifier) ──
  Accuracy : {accuracy:.4f}
  AUC-ROC  : {auc_roc:.4f}

  ── SAVED MODELS ──
  models/rf_regressor.pkl     ← regression model
  models/rf_classifier.pkl    ← classification model
  models/scaler.pkl           ← StandardScaler (for SVM / LinearReg)
  models/feature_names.pkl    ← column names for inference

  ── CHARTS SAVED ──
  eda_charts/chart11_actual_vs_predicted_gpa.png
  eda_charts/chart12_residuals.png
  eda_charts/chart13_feature_importance.png
  eda_charts/chart14_confusion_matrix.png
  eda_charts/chart15_roc_curve.png

""")
print("="*60)