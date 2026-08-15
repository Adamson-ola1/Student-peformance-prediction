import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { getStudent } from "../api/studentApi.js";
import { useStudents } from "../hooks/useStudents.js";
import StudentCard from "../components/StudentCard.jsx";
import ConfirmDelete from "../components/ConfirmDelete.jsx";
import Loader from "../components/Loader.jsx";

export default function StudentDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { removeStudent } = useStudents();

  const [student, setStudent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [deleteError, setDeleteError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    getStudent(id)
      .then((data) => !cancelled && setStudent(data))
      .catch((err) => !cancelled && setError(err.message))
      .finally(() => !cancelled && setLoading(false));
    return () => {
      cancelled = true;
    };
  }, [id]);

  async function handleConfirmDelete() {
    setConfirmOpen(false);
    try {
      await removeStudent(id);
      navigate("/students");
    } catch (err) {
      setDeleteError(err.message);
    }
  }

  return (
    <div className="page">
      <section className="panel">
        <div className="panel-head-row">
          <div className="panel-head">
            <h1>Student Details</h1>
            <p>Full profile for this student record.</p>
          </div>
          <Link className="btn-secondary btn-small" to="/students">
            ← Back to Students
          </Link>
        </div>

        {error && <div className="error-banner">Could not load student #{id}: {error}</div>}
        {deleteError && <div className="error-banner">Could not delete: {deleteError}</div>}

        {loading && <Loader text="Loading student record…" />}

        {!loading && student && (
          <>
            <StudentCard student={student} />
            <div className="form-actions">
              <Link className="btn-primary" to={`/students/${id}/edit`}>
                Edit
              </Link>
              <button className="btn-danger-solid" onClick={() => setConfirmOpen(true)}>
                Delete
              </button>
            </div>
          </>
        )}
      </section>

      <ConfirmDelete
        isOpen={confirmOpen}
        itemLabel={`Student #${id}`}
        onConfirm={handleConfirmDelete}
        onCancel={() => setConfirmOpen(false)}
      />
    </div>
  );
}
