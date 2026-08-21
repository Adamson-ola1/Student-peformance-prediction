import sys
from pathlib import Path
import warnings

import pandas as pd
import numpy as np
import pickle
import os

from sqlalchemy import text
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

sys.path.append(str(Path(__file__).resolve().parent.parent))

# Import central config
from config import CHARTS_DIR, MODEL_DIR, MODELS_DIR, ROOT_DIR
warnings.filterwarnings("ignore")

# Import SQLAlchemy engine
from database import engine

print("\n" + "=" * 60)
print("DATA PREPROCESSING & FEATURE ENGINEERING")
print("=" * 60)


# ════════════════════════════════════════════════════════════════════════════
# LOAD RAW DATA USING SQLALCHEMY
# ════════════════════════════════════════════════════════════════════════════

print("\n[1] Loading StudentPerformance from database using SQLAlchemy ...")

query = text("SELECT * FROM StudentPerformance ORDER BY student_id")

# Load data into DataFrame
df = pd.read_sql(query, engine)

print(f"Loaded: {df.shape[0]:,} rows × {df.shape[1]} columns")


# ════════════════════════════════════════════════════════════════════════════
# STEP 2 — DROP NON-FEATURE COLUMNS
# ════════════════════════════════════════════════════════════════════════════

print("\n[2] Dropping non-feature columns ...")

# Remove unnecessary columns
cols_to_drop = ["student_id", "created_at"]

# Only drop if column exists
df.drop(
    columns=[col for col in cols_to_drop if col in df.columns],
    inplace=True
)

print(f"Dropped: {cols_to_drop}")
print(f"Remaining columns:")
print(df.columns.tolist())


# ════════════════════════════════════════════════════════════════════════════
# STEP 3 — HANDLE MISSING VALUES
# ════════════════════════════════════════════════════════════════════════════

print("\n[3] Handling missing values ...")

# TARGET VARIABLES
target_columns = ["final_gpa", "pass_fail"]

# Count rows before dropping missing target values
before = len(df)

# Drop rows where target values are missing
df.dropna(subset=target_columns, inplace=True)

after = len(df)

print(f"Rows before : {before:,}")
print(f"Rows after  : {after:,}")
print(f"Rows dropped: {before - after:,}")


# ════════════════════════════════════════════════════════════════════════════
# STEP 4 — IMPUTE FEATURE NULLS
# ════════════════════════════════════════════════════════════════════════════

print("\n[4] Imputing missing feature values with median ...")

numeric_features = [
    "age",
    "attendance_rate",
    "study_hours_per_week",
    "previous_gpa",
    "extracurricular_score"
]

for col in numeric_features:
    
    # Check if column exists
    if col in df.columns:
        
        # Check for null values
        if df[col].isnull().sum() > 0:
            
            median_val = df[col].median()

            # Replace missing values
            df[col] = df[col].fillna(median_val)

            print(
                f"{col}: missing values filled "
                f"with median ({median_val:.2f})"
            )


# ════════════════════════════════════════════════════════════════════════════
# STEP 5 — CHECK REMAINING NULLS
# ════════════════════════════════════════════════════════════════════════════

print("\n[5] Final Missing Value Check ...")

null_summary = df.isnull().sum()

remaining_nulls = null_summary[null_summary > 0]

if len(remaining_nulls) == 0:
    print("No missing values remaining.")
else:
    print(remaining_nulls)



# ════════════════════════════════════════════════════════════════════════════
# STEP 6 — OUTLIER DETECTION (IQR method — cap, don't remove)
# ════════════════════════════════════════════════════════════════════════════

print("\n[6] Outlier handling (IQR capping) ...")

# We CAP (Winsorise) rather than remove outliers.
# Removing rows loses training data; capping retains it and reduces skew.
outlier_cols = ["attendance_rate", "study_hours_per_week",
                "previous_gpa", "extracurricular_score", "final_gpa"]

total_capped = 0
for col in outlier_cols:
    Q1  = df[col].quantile(0.25)
    Q3  = df[col].quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR
    n_outliers = ((df[col] < lower) | (df[col] > upper)).sum()
    if n_outliers > 0:
        df[col] = df[col].clip(lower=lower, upper=upper)
        print(f"  Capped {n_outliers} outliers in '{col}' "
              f"[{lower:.2f}, {upper:.2f}]")
        total_capped += n_outliers

if total_capped == 0:
    print("No significant outliers detected (data was generated with constraints).")


# ════════════════════════════════════════════════════════════════════════════
# STEP 7 — CATEGORICAL ENCODING (pd.get_dummies)
# ════════════════════════════════════════════════════════════════════════════

print("\n[7] Encoding categorical variables ...")

print("Before encoding — columns:", list(df.columns))

# One-hot encode 'gender' and 'family_income'
# drop_first=True avoids the dummy variable trap (multicollinearity)
df = pd.get_dummies(df,
                    columns=["gender", "family_income"],
                    drop_first=True,
                    dtype=int)

print("After encoding  — columns:", list(df.columns))
print(f"New shape: {df.shape}")


# ════════════════════════════════════════════════════════════════════════════
# STEP 8 — FEATURE ENGINEERING (derived features)
# ════════════════════════════════════════════════════════════════════════════

print("\n[8] Feature engineering — adding derived features ...")

# study_efficiency_ratio: study intensity relative to age
# Mirrors the derived feature in vw_MLReadyDataset SQL view
df["study_efficiency_ratio"] = (
    df["study_hours_per_week"].astype(float) /
    df["age"].replace(0, np.nan)
).round(4)

# attendance_x_study: interaction feature — both attendance and effort matter
df["attendance_x_study"] = (
    (df["attendance_rate"] / 100) * df["study_hours_per_week"]
).round(4)

print("Added: 'study_efficiency_ratio'")
print("Added: 'attendance_x_study' (interaction feature)")
print(f"Final shape: {df.shape}")


# ════════════════════════════════════════════════════════════════════════════
# STEP 9 — DEFINE FEATURE MATRIX (X) AND TARGETS (y)
# ════════════════════════════════════════════════════════════════════════════

print("\n[9] Defining feature matrix X and target variables ...")

# Drop BOTH target variables from the feature matrix
X = df.drop(["final_gpa", "pass_fail"], axis=1)

# Regression target  → predict exact final GPA (continuous)
y_regression     = df["final_gpa"]

# Classification target → predict pass (1) or fail (0) (binary)
y_classification = df["pass_fail"].astype(int)

print(f"X shape          : {X.shape}  (features)")
print(f"y_regression     : {y_regression.shape}  (continuous — final_gpa)")
print(f"y_classification : {y_classification.shape}  (binary — pass_fail)")
print(f"Feature columns  : {list(X.columns)}")


# ════════════════════════════════════════════════════════════════════════════
# STEP 10 — TRAIN / TEST SPLIT (80 / 20)
# ════════════════════════════════════════════════════════════════════════════

print("\n[10] Train/test split (80% train, 20% test, random_state=42) ...")

# Regression split
X_train_reg, X_test_reg, y_train_reg, y_test_reg = train_test_split(
    X, y_regression,
    test_size=0.2,
    random_state=42
)

# Classification split (same indices via random_state for reproducibility)
X_train_cls, X_test_cls, y_train_cls, y_test_cls = train_test_split(
    X, y_classification,
    test_size=0.2,
    random_state=42
)

print(f"Regression   → Train: {X_train_reg.shape} | Test: {X_test_reg.shape}")
print(f"Classification → Train: {X_train_cls.shape} | Test: {X_test_cls.shape}")
print(f"Pass rate in train : {y_train_cls.mean()*100:.1f}%")
print(f"Pass rate in test  : {y_test_cls.mean()*100:.1f}%")


# ════════════════════════════════════════════════════════════════════════════
# STEP 11 — FEATURE SCALING (StandardScaler)
# ════════════════════════════════════════════════════════════════════════════

print("\n[11] Feature scaling (StandardScaler) ...")
print("NOTE: Tree-based models (RandomForest) do not require scaling.")
print("Scaled versions are saved separately for SVM/LinearReg use.")

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train_reg)   # fit on TRAIN only
X_test_scaled  = scaler.transform(X_test_reg)         # apply same scale to TEST

print(" Scaler fitted on training data only (no data leakage).")
print(f"X_train_scaled shape : {X_train_scaled.shape}")
print(f"X_test_scaled shape  : {X_test_scaled.shape}")


# ════════════════════════════════════════════════════════════════════════════
# STEP 12 — SAVE ALL PREPROCESSED OBJECTS
# ════════════════════════════════════════════════════════════════════════════

print("\n[12] Saving preprocessed data and scaler as .pkl files ...")

os.makedirs(MODELS_DIR, exist_ok=True)
objects_to_save = {
    "X_train_reg.pkl":    X_train_reg,
    "X_test_reg.pkl":     X_test_reg,
    "y_train_reg.pkl":    y_train_reg,
    "y_test_reg.pkl":     y_test_reg,
    "X_train_cls.pkl":    X_train_cls,
    "X_test_cls.pkl":     X_test_cls,
    "y_train_cls.pkl":    y_train_cls,
    "y_test_cls.pkl":     y_test_cls,
    "X_train_scaled.pkl": X_train_scaled,
    "X_test_scaled.pkl":  X_test_scaled,
    "scaler.pkl":         scaler,
    "feature_names.pkl":  list(X.columns),
}

for filename, obj in objects_to_save.items():
    path = os.path.join(MODELS_DIR, filename)
    with open(path, "wb") as f:
        pickle.dump(obj, f)
    print(f"Saved: {path}")

