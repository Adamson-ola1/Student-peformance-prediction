import { GENDER_OPTIONS, FAMILY_INCOME_OPTIONS } from "./StudentForm.jsx";

export default function PredictionForm({ formState, onChange, onSubmit, onLoadExample, submitting }) {
  function handleFieldChange(e) {
    const { name, value } = e.target;
    onChange({ ...formState, [name]: value });
  }

  return (
    <form onSubmit={onSubmit} className="app-form">
      <div className="grid-2">
        <label>
          Age
          <input type="number" name="age" value={formState.age} min="10" max="100" onChange={handleFieldChange} required />
        </label>
        <label>
          Gender
          <select name="gender" value={formState.gender} onChange={handleFieldChange} required>
            {GENDER_OPTIONS.map((g) => <option key={g} value={g}>{g}</option>)}
          </select>
        </label>
        <label>
          Attendance rate (%)
          <input type="number" name="attendance_rate" value={formState.attendance_rate} min="0" max="100" step="0.1" onChange={handleFieldChange} required />
        </label>
        <label>
          Study hours / week
          <input type="number" name="study_hours_per_week" value={formState.study_hours_per_week} min="0" step="0.5" onChange={handleFieldChange} required />
        </label>
        <label>
          Previous GPA
          <input type="number" name="previous_gpa" value={formState.previous_gpa} min="0" max="4" step="0.01" onChange={handleFieldChange} required />
        </label>
        <label>
          Extracurricular score (0-5)
          <input type="number" name="extracurricular_score" value={formState.extracurricular_score} min="0" max="5" step="1" onChange={handleFieldChange} required />
        </label>
        <label>
          Family income
          <select name="family_income" value={formState.family_income} onChange={handleFieldChange} required>
            {FAMILY_INCOME_OPTIONS.map((f) => <option key={f} value={f}>{f}</option>)}
          </select>
        </label>
      </div>

      <div className="form-actions">
        <button type="submit" className="btn-primary" disabled={submitting}>
          {submitting ? "Predicting…" : "Predict Performance"}
        </button>
        <button type="button" className="btn-secondary" onClick={onLoadExample}>
          Load weak example
        </button>
      </div>
    </form>
  );
}
