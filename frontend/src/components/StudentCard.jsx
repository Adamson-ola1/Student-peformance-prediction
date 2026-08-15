function PassFailBadge({ value }) {
  if (value === null || value === undefined) {
    return <span className="badge unknown">Not yet evaluated</span>;
  }
  return value === 1 ? (
    <span className="badge pass">Pass</span>
  ) : (
    <span className="badge fail">Fail</span>
  );
}

function Field({ label, value }) {
  return (
    <div className="card-field">
      <span className="card-field-label">{label}</span>
      <span className="card-field-value">{value}</span>
    </div>
  );
}

/**
 * A read-only card presentation of a single student — used on
 * StudentDetails.jsx. Distinct from StudentTable (a list of many rows) and
 * StudentForm (an editable form); this is just for viewing one record.
 */
export default function StudentCard({ student }) {
  return (
    <div className="student-card">
      <div className="student-card-header">
        <span className="student-card-id">Student #{student.student_id}</span>
        <PassFailBadge value={student.pass_fail} />
      </div>

      <div className="student-card-grid">
        <Field label="Age" value={student.age} />
        <Field label="Gender" value={student.gender} />
        <Field label="Attendance Rate" value={`${student.attendance_rate}%`} />
        <Field label="Study Hours / Week" value={student.study_hours_per_week} />
        <Field label="Previous GPA" value={student.previous_gpa} />
        <Field label="Extracurricular Score" value={`${student.extracurricular_score} / 5`} />
        <Field label="Family Income" value={student.family_income} />
        <Field label="Final GPA" value={student.final_gpa ?? "—"} />
      </div>
    </div>
  );
}
