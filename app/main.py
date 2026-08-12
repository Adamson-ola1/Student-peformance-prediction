import time
from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

from app.model import PredictionInput, PredictionResponse
from app.ml_model import predict_performance, get_model_info, load_models
from app.routers import student


# ─────────────────────────────────────────────
# Load .env variables
# ─────────────────────────────────────────────
load_dotenv()


# ─────────────────────────────────────────────
# App Initialization
# ─────────────────────────────────────────────
app = FastAPI(
    title="Gworldsoft Student Performance Prediction API",
    description=(
        "A REST API for managing student records and predicting academic performance "
        "using a trained Machine Learning model. Built with FastAPI + SQL Server."
    ),
    version="1.0.0",
    contact={"name": "Gworldsoft Academy", "email": "admin@gworldsoft.com"},
)


# ─────────────────────────────────────────────
# CORS (allow all for development)
# ─────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────
# Startup Event
# ─────────────────────────────────────────────
@app.on_event("startup")
def on_startup():
    startup_start = time.time()

    print("\n" + "=" * 60)
    print("  Gworldsoft Student Performance API")
    print("=" * 60)

    load_models()

    elapsed = time.time() - startup_start
    print("=" * 60)
    print(f"  API ready in {elapsed:.2f}s")
    print("  Docs → http://127.0.0.1:8000/docs")
    print("=" * 60 + "\n")


# ─────────────────────────────────────────────
# GET /  → Health Check
# ─────────────────────────────────────────────
@app.get("/", tags=["Health"])
def health_check():
    return {
        "status": "ok",
        "message": "Gworldsoft Student Performance Prediction API is running.",
        "version": "1.0.0",
    }


# ─────────────────────────────────────────────
# Student CRUD routes
# ─────────────────────────────────────────────
app.include_router(student.router)

# ─────────────────────────────────────────────
#  POST /predict  → ML Prediction
# ─────────────────────────────────────────────
@app.post("/predict", response_model=PredictionResponse, tags=["ML Model"])
def predict(data: PredictionInput):
    """
    Accepts student features and returns:
    - predicted_gpa    (float)
    - pass_fail        (Pass / Fail)
    - pass_probability (float 0–1)
    - fail_probability (float 0–1)
    """
    result = predict_performance(data.model_dump())
    return result


# ─────────────────────────────────────────────
# GET /model-info  → Model Metrics
# ─────────────────────────────────────────────
@app.get("/model-info", tags=["ML Model"])
def model_info():
    """
    Returns:
    - Model type
    - Classifier type
    - Feature order used during training
    - Metadata from training run
    """
    return get_model_info()


# ─────────────────────────────────────────────
# Run directly: python app/main.py
# ─────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)