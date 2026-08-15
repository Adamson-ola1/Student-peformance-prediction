export default function PredictionResult({ result, error }) {
  if (error) {
    return <div className="result-error">Could not generate a prediction: {error}</div>;
  }

  if (!result) {
    return (
      <div className="result-empty">
        Fill in the student's profile and click <strong>Predict Performance</strong> to
        see the predicted GPA and pass/fail outcome.
      </div>
    );
  }

  const isPass = result.pass_fail === "Pass";

  return (
    <div className="prediction-result">
      <span className="gpa-label">Predicted Final GPA</span>
      <span className="gpa-readout">{result.predicted_gpa.toFixed(2)}</span>

      <div className={`pass-fail-badge ${isPass ? "pass" : "fail"}`}>
        {result.pass_fail}
      </div>

      <div className="prob-bars">
        <div className="prob-row">
          <span className="prob-name">Pass</span>
          <span className="prob-track">
            <span
              className="prob-fill pass"
              style={{ width: `${result.pass_probability * 100}%` }}
            />
          </span>
          <span className="prob-value">{(result.pass_probability * 100).toFixed(1)}%</span>
        </div>
        <div className="prob-row">
          <span className="prob-name">Fail</span>
          <span className="prob-track">
            <span
              className="prob-fill fail"
              style={{ width: `${result.fail_probability * 100}%` }}
            />
          </span>
          <span className="prob-value">{(result.fail_probability * 100).toFixed(1)}%</span>
        </div>
      </div>
    </div>
  );
}
