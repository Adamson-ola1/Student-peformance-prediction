from sqlalchemy import create_engine
from dotenv import load_dotenv

# ─────────────────────────────────────────────────────────────
# IMPORT LIBRARIES
# ─────────────────────────────────────────────────────────────
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import warnings
import os

from sqlalchemy import create_engine
from dotenv import load_dotenv

warnings.filterwarnings("ignore")


# ─────────────────────────────────────────────────────────────
# LOAD ENVIRONMENT VARIABLES
# ─────────────────────────────────────────────────────────────
load_dotenv()

# Read database URL from .env
DATABASE_URL = os.getenv("DATABASE_URL")

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# ─────────────────────────────────────────────────────────────
# OUTPUT DIRECTORY FOR CHARTS
# ─────────────────────────────────────────────────────────────
os.makedirs("eda_charts", exist_ok=True)
CHART_DIR = "eda_charts"

# ─────────────────────────────────────────────────────────────
# PLOT STYLE
# ─────────────────────────────────────────────────────────────
sns.set_theme(style="whitegrid", palette="deep")

plt.rcParams.update({
    "figure.dpi": 150,
    "axes.titlesize": 13,
    "axes.labelsize": 11,
    "font.family": "Arial"
    })

# ════════════════════════════════════════════════════════════
# STEP 1 — LOAD DATA FROM SQL SERVER USING SQLALCHEMY
# ════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("EXPLORATORY DATA ANALYSIS")
print("=" * 60)

print("\n[1] Loading data from SQL Server...")

# Load StudentPerformance table
query_student = """
SELECT * 
FROM StudentPerformance
ORDER BY student_id
"""

df = pd.read_sql(query_student, engine)

# Load ML-ready view
query_ml = """
SELECT *
FROM vw_MLReadyDataset
ORDER BY student_id
"""

df_ml = pd.read_sql(query_ml, engine)

print(f"StudentPerformance shape : {df.shape}")
print(f"ML-Ready view shape      : {df_ml.shape}")

# Preview dataset
print("\nFirst 5 Rows")
print(df.head())

# ════════════════════════════════════════════════════════════════════════════
# STEP 2 — df.info() AND df.describe()
# ════════════════════════════════════════════════════════════════════════════

print("\n[2] Dataset Info (df.info())")
print("-" * 60)
df.info()

print("\n[3] Descriptive Statistics (df.describe())")
print("-" * 60)
print(df.describe(include="all").to_string())

# ════════════════════════════════════════════════════════════════════════════
# STEP 3 — MISSING VALUES & DUPLICATES
# ════════════════════════════════════════════════════════════════════════════

print("\n[4] Missing Values Check")
print("-" * 60)
null_counts = df.isnull().sum()
null_pct    = (null_counts / len(df) * 100).round(2)
null_df     = pd.DataFrame({"Missing Count": null_counts,
                             "Missing %":    null_pct})
print(null_df[null_df["Missing Count"] > 0] \
      if null_counts.any() else "No missing values found.")

print("\n[5] Duplicate Records Check")
print("-" * 60)
dupes = df.duplicated().sum()
print(f"  Duplicate rows: {dupes}")
if dupes > 0:
    df.drop_duplicates(inplace=True)
    print(f"Duplicates removed. New shape: {df.shape}")


# ════════════════════════════════════════════════════════════════════════════
# CHART 1 — Histograms of all numeric features
# ════════════════════════════════════════════════════════════════════════════

print("\n[6] Generating Chart 1 — Feature Distributions (Histograms) ...")

numeric_cols = ["age", "attendance_rate", "study_hours_per_week",
                "previous_gpa", "extracurricular_score", "final_gpa"]

fig, axes = plt.subplots(2, 3, figsize=(15, 8))
fig.suptitle("Chart 1: Distribution of All Numeric Features\n"
             "GworldsoftAcademy Student Performance Dataset",
             fontsize=14, fontweight="bold", y=1.01)

colours = ["#2563A8", "#1A6B3C", "#E67E22", "#C0392B", "#4A235A", "#1A6B6B"]

for ax, col, colour in zip(axes.flatten(), numeric_cols, colours):
    ax.hist(df[col].dropna(), bins=30, color=colour, edgecolor="white",
            linewidth=0.6, alpha=0.85)
    ax.set_title(col.replace("_", " ").title(), fontweight="bold")
    ax.set_xlabel("Value")
    ax.set_ylabel("Count")
    mean_val = df[col].mean()
    ax.axvline(mean_val, color="black", linestyle="--",
               linewidth=1.2, label=f"Mean: {mean_val:.2f}")
    ax.legend(fontsize=8)

plt.tight_layout()
plt.savefig(f"{CHART_DIR}/chart1_histograms.png", bbox_inches="tight")
plt.close()
print(f"Saved: {CHART_DIR}/chart1_histograms.png")


# ════════════════════════════════════════════════════════════════════════════
# CHART 2 — Boxplots by pass/fail
# ════════════════════════════════════════════════════════════════════════════

print("[7] Generating Chart 2 — Boxplots: Features vs Pass/Fail ...")

# Create readable labels
df["pass_fail_label"] = df["pass_fail"].map({
    1: "Pass",
    0: "Fail"
})

# Create figure
fig, axes = plt.subplots(2, 3, figsize=(15, 9))

fig.suptitle(
    "Chart 2: Feature Distributions by Pass / Fail Outcome",
    fontsize=14,
    fontweight="bold"
)

# Loop through numeric columns
for ax, col in zip(axes.flatten(), numeric_cols):

    # Separate data
    pass_data = df[df["pass_fail_label"] == "Pass"][col].dropna()
    fail_data = df[df["pass_fail_label"] == "Fail"][col].dropna()

    # Create boxplot
    bp = ax.boxplot(
        [pass_data, fail_data],
        labels=["Pass", "Fail"],
        patch_artist=True,
        widths=0.5,
        flierprops=dict(
            marker='o',
            markersize=3,
            alpha=0.4
        )
    )

    # Set colors
    colors = ["#1A6B3C", "#C0392B"]

    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)

    # Titles and labels
    ax.set_title(
        col.replace("_", " ").title(),
        fontweight="bold"
    )

    ax.set_xlabel("Outcome")
    ax.set_ylabel(
        col.replace("_", " ").title()
    )

# Adjust layout
plt.tight_layout()

# Save figure
plt.savefig(
    f"{CHART_DIR}/chart2_boxplots_pass_fail.png",
    bbox_inches="tight"
)

plt.close()

print(f"Saved: {CHART_DIR}/chart2_boxplots_pass_fail.png")

# ════════════════════════════════════════════════════════════════════════════
# CHART 3 — Correlation Heatmap
# ════════════════════════════════════════════════════════════════════════════

print("[8] Generating Chart 3 — Correlation Heatmap ...")

corr_cols = ["age", "attendance_rate", "study_hours_per_week",
             "previous_gpa", "extracurricular_score", "final_gpa", "pass_fail"]
corr_matrix = df[corr_cols].corr()

fig, ax = plt.subplots(figsize=(10, 7))
mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
sns.heatmap(
    corr_matrix, mask=mask, annot=True, fmt=".2f",
    cmap="RdYlGn", center=0, vmin=-1, vmax=1,
    linewidths=0.5, linecolor="white",
    annot_kws={"size": 9}, ax=ax
)
ax.set_title("Chart 3: Correlation Heatmap — All Numeric Features\n"
             "(lower triangle; 1.0 = perfect positive correlation)",
             fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig(f"{CHART_DIR}/chart3_correlation_heatmap.png", bbox_inches="tight")
plt.close()
print(f"Saved: {CHART_DIR}/chart3_correlation_heatmap.png")


# ════════════════════════════════════════════════════════════════════════════
# CHART 4 — Scatter: previous_gpa vs final_gpa (coloured by pass/fail)
# ════════════════════════════════════════════════════════════════════════════

print("[9] Generating Chart 4 — Scatter: previous_gpa vs final_gpa ...")

fig, ax = plt.subplots(figsize=(9, 6))
colours_pf = df["pass_fail_label"].map({"Pass": "#1A6B3C", "Fail": "#C0392B"})

ax.scatter(df["previous_gpa"], df["final_gpa"],
           c=colours_pf, alpha=0.45, s=20, edgecolors="none")

# Regression line
m, b = np.polyfit(df["previous_gpa"].dropna(),
                  df["final_gpa"].dropna(), 1)
x_line = np.linspace(0.5, 4.0, 100)
ax.plot(x_line, m * x_line + b, color="black",
        linewidth=1.5, linestyle="--", label=f"OLS line: y = {m:.2f}x + {b:.2f}")

from matplotlib.lines import Line2D
legend_elements = [
    Line2D([0], [0], marker="o", color="w",
           markerfacecolor="#1A6B3C", markersize=8, label="Pass"),
    Line2D([0], [0], marker="o", color="w",
           markerfacecolor="#C0392B", markersize=8, label="Fail"),
    Line2D([0], [0], color="black", linestyle="--", label=f"OLS: y={m:.2f}x+{b:.2f}"),
]
ax.legend(handles=legend_elements, fontsize=9)
ax.set_xlabel("Previous GPA")
ax.set_ylabel("Final GPA")
ax.set_title("Chart 4: Previous GPA vs Final GPA\n"
             "(green = Pass, red = Fail)", fontweight="bold")
corr_val = df["previous_gpa"].corr(df["final_gpa"])
ax.text(0.05, 0.92, f"Pearson r = {corr_val:.3f}",
        transform=ax.transAxes, fontsize=10,
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.8))
plt.tight_layout()
plt.savefig(f"{CHART_DIR}/chart4_scatter_prev_vs_final_gpa.png", bbox_inches="tight")
plt.close()
print(f"Saved: {CHART_DIR}/chart4_scatter_prev_vs_final_gpa.png")


# ════════════════════════════════════════════════════════════════════════════
# CHART 5 — Average GPA by Family Income (grouped bar)
# ════════════════════════════════════════════════════════════════════════════

print("[10] Generating Chart 5 — Avg GPA by Family Income ...")

income_order = ["Low", "Medium", "High"]
income_stats = (df.groupby("family_income")["final_gpa"]
                  .agg(["mean", "std", "count"])
                  .reindex(income_order)
                  .reset_index())
income_stats.columns = ["family_income", "mean_gpa", "std_gpa", "count"]

fig, ax = plt.subplots(figsize=(8, 5))
colours_income = ["#C0392B", "#E67E22", "#1A6B3C"]
bars = ax.bar(income_stats["family_income"],
              income_stats["mean_gpa"],
              yerr=income_stats["std_gpa"],
              color=colours_income, edgecolor="white",
              linewidth=0.7, capsize=5, alpha=0.88, width=0.5)

for bar, (_, row) in zip(bars, income_stats.iterrows()):
    ax.text(bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.05,
            f"{row['mean_gpa']:.3f}\n(n={int(row['count'])})",
            ha="center", va="bottom", fontsize=9, fontweight="bold")

ax.set_xlabel("Family Income Category")
ax.set_ylabel("Mean Final GPA")
ax.set_title("Chart 5: Average Final GPA by Family Income\n"
             "(error bars = ±1 std dev)", fontweight="bold")
ax.set_ylim(0, 4.0)
ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.1f"))
plt.tight_layout()
plt.savefig(f"{CHART_DIR}/chart5_gpa_by_income.png", bbox_inches="tight")
plt.close()
print(f"Saved: {CHART_DIR}/chart5_gpa_by_income.png")


# ════════════════════════════════════════════════════════════════════════════
# CHART 6 — Pass/Fail distribution by Gender
# ════════════════════════════════════════════════════════════════════════════

print("[11] Generating Chart 6 — Pass/Fail by Gender ...")

# Ensure pass_fail_label exists
df["pass_fail_label"] = df["pass_fail"].map({
    1: "Pass",
    0: "Fail"
})

# Remove missing rows if any
df_chart = df.dropna(subset=["gender", "pass_fail_label"])

# Create grouped count table
gender_pf = (
    df_chart.groupby(["gender", "pass_fail_label"])
    .size()
    .unstack(fill_value=0)
)

# Convert to numeric
gender_pf = gender_pf.astype(int)

# Create percentage table
gender_pf_pct = (
    gender_pf.div(gender_pf.sum(axis=1), axis=0)
    * 100
).round(1)

# Create figure
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# ─────────────────────────────
# Chart 6A — Absolute Counts
# ─────────────────────────────
x = np.arange(len(gender_pf.index))
width = 0.35

axes[0].bar(
    x - width/2,
    gender_pf.get("Fail", pd.Series(0, index=gender_pf.index)),
    width,
    label="Fail",
)

axes[0].bar(
    x + width/2,
    gender_pf.get("Pass", pd.Series(0, index=gender_pf.index)),
    width,
    label="Pass",
)

axes[0].set_xticks(x)
axes[0].set_xticklabels(gender_pf.index)

axes[0].set_title(
    "Chart 6a: Pass/Fail Counts by Gender",
    fontweight="bold"
)

axes[0].set_xlabel("Gender")
axes[0].set_ylabel("Number of Students")
axes[0].legend(title="Outcome")

# ─────────────────────────────
# Chart 6B — Percentage
# ─────────────────────────────
axes[1].bar(
    x - width/2,
    gender_pf_pct.get("Fail", pd.Series(0, index=gender_pf_pct.index)),
    width,
    label="Fail",
)

axes[1].bar(
    x + width/2,
    gender_pf_pct.get("Pass", pd.Series(0, index=gender_pf_pct.index)),
    width,
    label="Pass",
)

axes[1].set_xticks(x)
axes[1].set_xticklabels(gender_pf_pct.index)

axes[1].set_title(
    "Chart 6b: Pass/Fail Rate (%) by Gender",
    fontweight="bold"
)

axes[1].set_xlabel("Gender")
axes[1].set_ylabel("Percentage (%)")
axes[1].set_ylim(0, 100)
axes[1].legend(title="Outcome")

# Add labels
for ax in axes:
    for container in ax.containers:
        ax.bar_label(container, fmt="%.0f", fontsize=8)

# Save chart
plt.tight_layout()

plt.savefig(
    f"{CHART_DIR}/chart6_passfail_by_gender.png",
    bbox_inches="tight"
)

plt.close()

print(f"Saved: {CHART_DIR}/chart6_passfail_by_gender.png")

# ════════════════════════════════════════════════════════════════════════════
# CHART 7 — Attendance rate vs Final GPA (scatter + density)
# ════════════════════════════════════════════════════════════════════════════

print("[12] Generating Chart 7 — Attendance vs Final GPA ...")

fig, ax = plt.subplots(figsize=(9, 6))
ax.scatter(df["attendance_rate"], df["final_gpa"],
           c=colours_pf, alpha=0.35, s=18, edgecolors="none")

m2, b2 = np.polyfit(df["attendance_rate"], df["final_gpa"], 1)
x2 = np.linspace(0, 100, 200)
ax.plot(x2, m2 * x2 + b2, color="black",
        linewidth=1.5, linestyle="--",
        label=f"OLS: y = {m2:.4f}x + {b2:.2f}")

corr2 = df["attendance_rate"].corr(df["final_gpa"])
ax.text(0.05, 0.92, f"Pearson r = {corr2:.3f}",
        transform=ax.transAxes, fontsize=10,
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.8))
ax.set_xlabel("Attendance Rate (%)")
ax.set_ylabel("Final GPA")
ax.set_title("Chart 7: Attendance Rate vs Final GPA\n"
             "(green = Pass, red = Fail)", fontweight="bold")
ax.legend(fontsize=9)
plt.tight_layout()
plt.savefig(f"{CHART_DIR}/chart7_attendance_vs_gpa.png", bbox_inches="tight")
plt.close()
print(f"Saved: {CHART_DIR}/chart7_attendance_vs_gpa.png")


# ════════════════════════════════════════════════════════════════════════════
# CHART 8 — Study hours vs Final GPA (scatter)
# ════════════════════════════════════════════════════════════════════════════

print("[13] Generating Chart 8 — Study Hours vs Final GPA ...")

fig, ax = plt.subplots(figsize=(9, 6))
ax.scatter(df["study_hours_per_week"], df["final_gpa"],
           c=colours_pf, alpha=0.4, s=18, edgecolors="none")

m3, b3 = np.polyfit(df["study_hours_per_week"], df["final_gpa"], 1)
x3 = np.linspace(5, 49, 200)
ax.plot(x3, m3 * x3 + b3, color="black", linewidth=1.5, linestyle="--",
        label=f"OLS: y = {m3:.4f}x + {b3:.2f}")

corr3 = df["study_hours_per_week"].corr(df["final_gpa"])
ax.text(0.05, 0.92, f"Pearson r = {corr3:.3f}",
        transform=ax.transAxes, fontsize=10,
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.8))
ax.set_xlabel("Study Hours per Week")
ax.set_ylabel("Final GPA")
ax.set_title("Chart 8: Study Hours per Week vs Final GPA\n"
             "(green = Pass, red = Fail)", fontweight="bold")
ax.legend(fontsize=9)
plt.tight_layout()
plt.savefig(f"{CHART_DIR}/chart8_studyhours_vs_gpa.png", bbox_inches="tight")
plt.close()
print(f"Saved: {CHART_DIR}/chart8_studyhours_vs_gpa.png")


# ════════════════════════════════════════════════════════════════════════════
# CHART 9 — Extracurricular Score vs Final GPA (violin)
# ════════════════════════════════════════════════════════════════════════════

print("[14] Generating Chart 9 — Extracurricular Score vs Final GPA (Violin) ...")

fig, ax = plt.subplots(figsize=(10, 6))
sns.violinplot(data=df, x="extracurricular_score", y="final_gpa",
               palette="deep", ax=ax, inner="box", cut=0)
ax.set_xlabel("Extracurricular Score (0 = None, 5 = Highest)")
ax.set_ylabel("Final GPA")
ax.set_title("Chart 9: Final GPA Distribution by Extracurricular Score\n"
             "(violin = distribution shape; box = IQR)", fontweight="bold")
means = df.groupby("extracurricular_score")["final_gpa"].mean()
for score, mean_val in means.items():
    ax.text(score, mean_val + 0.08, f"{mean_val:.2f}",
            ha="center", va="bottom", fontsize=8, color="black", fontweight="bold")
plt.tight_layout()
plt.savefig(f"{CHART_DIR}/chart9_extracurricular_violin.png", bbox_inches="tight")
plt.close()
print(f"Saved: {CHART_DIR}/chart9_extracurricular_violin.png")


# ════════════════════════════════════════════════════════════════════════════
# CHART 10 — Feature Importance (Correlation with final_gpa)
# ════════════════════════════════════════════════════════════════════════════

print("[15] Generating Chart 10 — Feature Correlation with Final GPA ...")

feature_cols = ["age", "attendance_rate", "study_hours_per_week",
                "previous_gpa", "extracurricular_score"]
correlations  = df[feature_cols + ["final_gpa"]].corr()["final_gpa"].drop("final_gpa")
correlations  = correlations.sort_values(ascending=True)

fig, ax = plt.subplots(figsize=(9, 5))
bar_cols = ["#1A6B3C" if v > 0 else "#C0392B" for v in correlations.values]
bars = ax.barh(correlations.index, correlations.values,
               color=bar_cols, edgecolor="white", height=0.55)
ax.axvline(0, color="black", linewidth=0.8)
ax.set_xlabel("Pearson Correlation Coefficient (r)")
ax.set_title("Chart 10: Feature Correlation with Final GPA\n"
             "(green = positive, red = negative relationship)", fontweight="bold")
for bar, val in zip(bars, correlations.values):
    ax.text(val + (0.005 if val >= 0 else -0.005),
            bar.get_y() + bar.get_height() / 2,
            f"{val:.3f}",
            va="center", ha="left" if val >= 0 else "right",
            fontsize=9, fontweight="bold")
nice_labels = {
    "previous_gpa":          "Previous GPA",
    "attendance_rate":       "Attendance Rate",
    "study_hours_per_week":  "Study Hours/Week",
    "extracurricular_score": "Extracurricular Score",
    "age":                   "Age",
}
ax.set_yticklabels([nice_labels.get(l, l)
                    for l in correlations.index])
plt.tight_layout()
plt.savefig(f"{CHART_DIR}/chart10_feature_correlations.png", bbox_inches="tight")
plt.close()
print(f"Saved: {CHART_DIR}/chart10_feature_correlations.png")


# ════════════════════════════════════════════════════════════════════════════
# EDA CONCLUSIONS SUMMARY
# ════════════════════════════════════════════════════════════════════════════

print("\n" + "="*60)
print("  EDA CONCLUSIONS SUMMARY")
print("="*60)

pass_rate = df["pass_fail"].mean() * 100
corr_prev = df["previous_gpa"].corr(df["final_gpa"])
corr_att  = df["attendance_rate"].corr(df["final_gpa"])
corr_hrs  = df["study_hours_per_week"].corr(df["final_gpa"])

print(f"""
  Dataset              : {df.shape[0]:,} students × {df.shape[1]} columns
  Pass rate            : {pass_rate:.1f}%
  Avg final GPA        : {df['final_gpa'].mean():.3f}
  Missing values       : {df.isnull().sum().sum()}
  Duplicate rows       : {dupes}

  Top Correlations with final_gpa:
    previous_gpa          r = {corr_prev:.3f}  ← strongest predictor
    attendance_rate       r = {corr_att:.3f}
    study_hours_per_week  r = {corr_hrs:.3f}

  GPA by Income:
    Low    : {df[df['family_income']=='Low']['final_gpa'].mean():.3f}
    Medium : {df[df['family_income']=='Medium']['final_gpa'].mean():.3f}
    High   : {df[df['family_income']=='High']['final_gpa'].mean():.3f}

  All 10 charts saved to: ./{CHART_DIR}/

  """)
print("="*60)