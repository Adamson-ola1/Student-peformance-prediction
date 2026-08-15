import { useEffect, useState } from "react";
import { getModelInfo } from "../api/predictionApi.js";
import Loader from "../components/Loader.jsx";

function MetricCard({ label, value }) {
  return (
    <div className="metric-card">
      <div className="metric-value">{value}</div>
      <div className="metric-label">{label}</div>
    </div>
  );
}

export default function ModelInfo() {
  const [info, setInfo] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getModelInfo()
      .then(setInfo)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="page">
      <section className="panel">
        <div className="panel-head">
          <h1>Model Info</h1>
          <p>Details about the currently loaded regression + classification models.</p>
        </div>

        {loading && <Loader text="Loading model info…" />}
        {error && <div className="error-banner">Could not load model info: {error}</div>}

        {info && (
          <>
            <div className="metric-grid">
              <MetricCard label="Regression Model" value={info.model_type} />
              <MetricCard label="Classifier" value={info.classifier_type} />
              <MetricCard label="Feature Count" value={info.feature_count} />
            </div>

            {info.metadata && (
              <div className="metric-grid">
                {info.metadata.r2_score !== undefined && (
                  <MetricCard label="R² (GPA)" value={info.metadata.r2_score} />
                )}
                {info.metadata.rmse !== undefined && (
                  <MetricCard label="RMSE (GPA)" value={info.metadata.rmse} />
                )}
                {info.metadata.mae !== undefined && (
                  <MetricCard label="MAE (GPA)" value={info.metadata.mae} />
                )}
                {info.metadata.accuracy !== undefined && (
                  <MetricCard label="Accuracy (Pass/Fail)" value={info.metadata.accuracy} />
                )}
                {info.metadata.auc_roc !== undefined && (
                  <MetricCard label="AUC-ROC" value={info.metadata.auc_roc} />
                )}
              </div>
            )}
          </>
        )}
      </section>

      {info && (
        <section className="panel">
          <div className="panel-head">
            <h1>Feature Order</h1>
            <p>The exact column order the model expects on every prediction request.</p>
          </div>
          <ol className="feature-order-list">
            {info.feature_order.map((f) => (
              <li key={f}>{f}</li>
            ))}
          </ol>
        </section>
      )}
    </div>
  );
}
