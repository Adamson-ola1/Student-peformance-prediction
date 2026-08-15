/*
 * StudentContext.jsx
 * ------------------
 * Holds the student list, pagination state, and CRUD actions in one place
 * so that Students.jsx, AddStudent.jsx, EditStudent.jsx, and
 * StudentDetails.jsx can all share the same data instead of each page
 * fetching (and re-fetching) its own copy.
 *
 * Pages don't import this file directly — they call the useStudents()
 * hook (src/hooks/useStudents.js), which reads from this context.
 */
import { createContext, useCallback, useEffect, useState } from "react";
import {
  listStudents,
  createStudent as apiCreateStudent,
  updateStudent as apiUpdateStudent,
  deleteStudent as apiDeleteStudent,
} from "../api/studentApi.js";

const PAGE_SIZE = 10;

export const StudentContext = createContext(null);

export function StudentProvider({ children }) {
  const [students, setStudents] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(PAGE_SIZE);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const refresh = useCallback(async (targetPage = page) => {
    setLoading(true);
    setError(null);
    try {
      const data = await listStudents(targetPage, pageSize);
      setStudents(data.students);
      setTotal(data.total);
      setPage(data.page);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pageSize]);

  useEffect(() => {
    refresh(1);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function addStudent(payload) {
    const created = await apiCreateStudent(payload);
    await refresh(1); // new student is easiest to find by going back to page 1
    return created;
  }

  async function editStudent(studentId, payload) {
    const updated = await apiUpdateStudent(studentId, payload);
    await refresh(page);
    return updated;
  }

  async function removeStudent(studentId) {
    await apiDeleteStudent(studentId);
    await refresh(page);
  }

  const value = {
    students,
    total,
    page,
    pageSize,
    loading,
    error,
    refresh,
    addStudent,
    editStudent,
    removeStudent,
  };

  return <StudentContext.Provider value={value}>{children}</StudentContext.Provider>;
}
