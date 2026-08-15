import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useStudents } from "../hooks/useStudents.js";
import StudentForm from "../components/StudentForm.jsx";

const DEFAULT_STUDENT = {
  age: 20,
  gender: "Male",
  attendance_rate: 85.5,
  study_hours_per_week: 12,
  previous_gpa: 3.2,
  extracurricular_score: 3,
  family_income: "Medium",
};

export default function AddStudent() {
  const { addStudent } = useStudents();
  const navigate = useNavigate();

  const [formState, setFormState] = useState(DEFAULT_STUDENT);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

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
      await addStudent(payload);
      navigate("/students");
    } catch (err) {
      setError(err.message);
      setSubmitting(false);
    }
  }

  return (
    <div className="page">
      <section className="panel">
        <div className="panel-head">
          <h1>Add Student</h1>
          <p>Register a new student in the database.</p>
        </div>

        {error && <div className="error-banner">Could not save: {error}</div>}

        <StudentForm
          formState={formState}
          onChange={setFormState}
          onSubmit={handleSubmit}
          submitting={submitting}
          submitLabel="Add Student"
        />
      </section>
    </div>
  );
}
