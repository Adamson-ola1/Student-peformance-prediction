import { useState } from "react";
import { Link } from "react-router-dom";
import { useStudents } from "../hooks/useStudents.js";
import StudentTable from "../components/StudentTable.jsx";
import Pagination from "../components/Pagination.jsx";
import ConfirmDelete from "../components/ConfirmDelete.jsx";
import Loader from "../components/Loader.jsx";

export default function Students() {
  const { students, total, page, pageSize, loading, error, refresh, removeStudent } = useStudents();
  const [pendingDelete, setPendingDelete] = useState(null); // the student row being confirmed
  const [banner, setBanner] = useState(null);

  async function handleConfirmDelete() {
    const student = pendingDelete;
    setPendingDelete(null);
    try {
      await removeStudent(student.student_id);
      setBanner({ type: "success", text: `Student #${student.student_id} deleted.` });
    } catch (err) {
      setBanner({ type: "error", text: `Could not delete: ${err.message}` });
    }
  }

  return (
    <div className="page">
      <section className="panel">
        <div className="panel-head-row">
          <div className="panel-head">
            <h1>Students</h1>
            <p>All student records currently in the database.</p>
          </div>
          <Link className="btn-primary" to="/students/add">
            + Add Student
          </Link>
        </div>

        {banner && (
          <div className={banner.type === "success" ? "success-banner" : "error-banner"}>
            {banner.text}
          </div>
        )}
        {error && <div className="error-banner">Could not load students: {error}</div>}

        {loading ? (
          <Loader text="Loading students…" />
        ) : (
          <>
            <StudentTable students={students} onDeleteRequest={setPendingDelete} />
            <Pagination
              page={page}
              total={total}
              pageSize={pageSize}
              onPageChange={(newPage) => refresh(newPage)}
            />
          </>
        )}
      </section>

      <ConfirmDelete
        isOpen={pendingDelete !== null}
        itemLabel={pendingDelete ? `Student #${pendingDelete.student_id}` : ""}
        onConfirm={handleConfirmDelete}
        onCancel={() => setPendingDelete(null)}
      />
    </div>
  );
}
