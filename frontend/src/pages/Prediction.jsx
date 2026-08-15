import { useState } from "react";
import { predictPerformance } from "../api/predictionApi.js";
import PredictionForm from "../components/PredictionForm.jsx";
import PredictionResult from "../components/PredictionResult.jsx";

const DEFAULT_STUDENT = {
  age: 20,
  gender: "Male",
  attendance_rate: 85.5,
  study_hours_per_week: 12,
  previous_gpa: 3.2,
  extracurricular_score: 3,
  family_income: "Medium",
};

const WEAK_EXAMPLE = {
  age: 19,
  gender: "Female",
  attendance_rate: 55.0,
  study_hours_per_week: 3,
  previous_gpa: 1.8,
  extracurricular_score: 0,
  family_income: "Low",
};

export default function Prediction() {
  const [formState, setFormState] = useState(DEFAULT_STUDENT);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);

    const payload = {
      age: Number(formState.age),
      gender: formState.gender,
      attendance_rate: Number(formState.attendance_rate),
      study_hours_per_week: Number(formState.study_hours_per_week),
      previous_gpa: Number(formState.previous_gpa),
      extracurricular_score: Number(formState.extracurricular_score),
      family_income: formState.family_income,
    };

    try {
      const data = await predictPerformance(payload);
      setResult(data);
    } catch (err) {
      setResult(null);
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  function handleLoadExample() {
    setFormState(WEAK_EXAMPLE);
    setResult(null);
    setError(null);
  }

  return (
    <div className="page">
      <div className="two-col">
        <section className="panel">
          <div className="panel-head">
            <h1>Predict Performance</h1>
            <p>Enter a student's profile to predict their final GPA and pass/fail outcome.</p>
          </div>
          <PredictionForm
            formState={formState}
            onChange={setFormState}
            onSubmit={handleSubmit}
            onLoadExample={handleLoadExample}
            submitting={submitting}
          />
        </section>

        <section className="panel">
          <div className="panel-head">
            <h1>Prediction</h1>
            <p>Model-generated GPA forecast and pass/fail probability.</p>
          </div>
          <PredictionResult result={result} error={error} />
        </section>
      </div>
    </div>
  );
}
