import { Link } from "react-router-dom";
import { useStudents } from "../hooks/useStudents.js";

export default function Dashboard() {
  const { total, students, loading } = useStudents();

  const passCount = students.filter((s) => s.pass_fail === 1).length;
  const failCount = students.filter((s) => s.pass_fail === 0).length;

  return (
    <div className="page">
      <section className="panel">
        <div className="panel-head">
          <h1>Dashboard</h1>
          <p>Overview of the Gworldsoft Student Performance system.</p>
        </div>

        <div className="metric-grid">
          <div className="metric-card">
            <div className="metric-value">{loading ? "…" : total}</div>
            <div className="metric-label">Total Students</div>
          </div>
          <div className="metric-card">
            <div className="metric-value">{loading ? "…" : passCount}</div>
            <div className="metric-label">Passing (this page)</div>
          </div>
          <div className="metric-card">
            <div className="metric-value">{loading ? "…" : failCount}</div>
            <div className="metric-label">Failing (this page)</div>
          </div>
        </div>
      </section>

      <section className="panel">
        <div className="panel-head">
          <h1>Quick Actions</h1>
          <p>Jump straight to the most common tasks.</p>
        </div>

        <div className="quick-links">
          <Link className="quick-link-card" to="/students">
            <strong>View Students</strong>
            <span>Browse, edit, and delete student records.</span>
          </Link>
          <Link className="quick-link-card" to="/students/add">
            <strong>Add Student</strong>
            <span>Register a new student in the database.</span>
          </Link>
          <Link className="quick-link-card" to="/predict">
            <strong>Predict Performance</strong>
            <span>Forecast a GPA and pass/fail outcome for any profile.</span>
          </Link>
          <Link className="quick-link-card" to="/model-info">
            <strong>Model Info</strong>
            <span>Inspect the currently loaded model's metrics.</span>
          </Link>
        </div>
      </section>
    </div>
  );
}
