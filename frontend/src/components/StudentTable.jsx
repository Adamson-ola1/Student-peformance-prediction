import { Link } from "react-router-dom";

function PassFailBadge({ value }) {
  if (value === null || value === undefined) {
    return <span className="badge unknown">—</span>;
  }
  return value === 1 ? (
    <span className="badge pass">Pass</span>
  ) : (
    <span className="badge fail">Fail</span>
  );
}

export default function StudentTable({ students, onDeleteRequest }) {
  if (students.length === 0) {
    return <p className="empty-text">No students yet — add one to get started.</p>;
  }

  return (
    <table className="student-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>Age</th>
          <th>Gender</th>
          <th>Attendance</th>
          <th>Study hrs/wk</th>
          <th>Prev. GPA</th>
          <th>Final GPA</th>
          <th>Outcome</th>
          <th />
        </tr>
      </thead>
      <tbody>
        {students.map((s) => (
          <tr key={s.student_id}>
            <td>{s.student_id}</td>
            <td>{s.age}</td>
            <td>{s.gender}</td>
            <td>{s.attendance_rate}%</td>
            <td>{s.study_hours_per_week}</td>
            <td>{s.previous_gpa}</td>
            <td>{s.final_gpa ?? "—"}</td>
            <td><PassFailBadge value={s.pass_fail} /></td>
            <td>
              <div className="row-actions">
                <Link className="btn-secondary btn-small" to={`/students/${s.student_id}`}>
                  View
                </Link>
                <Link className="btn-secondary btn-small" to={`/students/${s.student_id}/edit`}>
                  Edit
                </Link>
                <button className="btn-danger" onClick={() => onDeleteRequest(s)}>
                  Delete
                </button>
              </div>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
