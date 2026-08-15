from pathlib import Path

# ----------------------------------------------------------------------
# Project paths
# ----------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent


MODELS_DIR = PROJECT_ROOT / "models"


for _d in (
    MODELS_DIR
):
    _d.mkdir(parents=True, exist_ok=True)
    

for result in results:
    model_name = result["Model"]
    with open(REPORTS_DIR / f"{model_name}_classification_report.txt", "w") as f:
        f.write(result["Classification Report"])

results_df_display.to_csv(REPORTS_DIR / "model_report.csv", index=False)
print("Saved model_report.csv and per-model classification reports to reports/")