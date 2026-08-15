import { useEffect, useState } from "react";
import { useNavigate, useParams, Link } from "react-router-dom";
import { getStudent } from "../api/studentApi.js";
import { useStudents } from "../hooks/useStudents.js";
import StudentForm from "../components/StudentForm.jsx";
import Loader from "../components/Loader.jsx";

export default function EditStudent() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { editStudent } = useStudents();

  const [formState, setFormState] = useState(null); // null while the record is still loading
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    getStudent(id)
      .then((student) => {
        if (cancelled) return;
        setFormState({
          age: student.age,
          gender: student.gender,
          attendance_rate: student.attendance_rate,
          study_hours_per_week: student.study_hours_per_week,
          previous_gpa: student.previous_gpa,
          extracurricular_score: student.extracurricular_score,
          family_income: student.family_income,
        });
      })
      .catch((err) => !cancelled && setLoadError(err.message))
      .finally(() => !cancelled && setLoading(false));
    return () => {
      cancelled = true;
    };
  }, [id]);

  async function handleSubmit(e) {
    e.preventDefault();
    setSubmitting(true);
    setSubmitError(null);

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
      await editStudent(id, payload);
      navigate(`/students/${id}`);
    } catch (err) {
      setSubmitError(err.message);
      setSubmitting(false);
    }
  }

  return (
    <div className="page">
      <section className="panel">
        <div className="panel-head">
          <h1>Edit Student #{id}</h1>
          <p>Update this student's record.</p>
        </div>

        {loadError && (
          <div className="error-banner">
            Could not load student #{id}: {loadError} —{" "}
            <Link to="/students">back to Students</Link>
          </div>
        )}
        {submitError && <div className="error-banner">Could not save: {submitError}</div>}

        {loading && <Loader text="Loading student record…" />}

        {!loading && formState && (
          <StudentForm
            formState={formState}
            onChange={setFormState}
            onSubmit={handleSubmit}
            onCancel={() => navigate(`/students/${id}`)}
            submitting={submitting}
            submitLabel="Save Changes"
          />
        )}
      </section>
    </div>
  );
}
