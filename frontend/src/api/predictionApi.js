/*
 * predictionApi.js
 * ----------------
 * ML-related calls, matching app/main.py:
 *   POST /predict       -> predicted GPA + pass/fail + probabilities
 *   GET  /model-info     -> model type, metrics, feature order
 */
import api from "./axios.js";

export async function predictPerformance(payload) {
  const { data } = await api.post("/predict", payload);
  return data;
}

export async function getModelInfo() {
  const { data } = await api.get("/model-info");
  return data;
}

export async function healthCheck() {
  const { data } = await api.get("/");
  return data;
}