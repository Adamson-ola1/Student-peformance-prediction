/*
 * useStudents.js
 * --------------
 * Thin convenience hook around StudentContext. Pages call `useStudents()`
 * instead of importing `useContext(StudentContext)` directly — if we ever
 * need to change how the context is structured, only this file needs to
 * change, not every page that uses it.
 */
import { useContext } from "react";
import { StudentContext } from "../context/StudentContext.jsx";

export function useStudents() {
  const context = useContext(StudentContext);
  if (!context) {
    throw new Error("useStudents() must be used inside a <StudentProvider>.");
  }
  return context;
}
