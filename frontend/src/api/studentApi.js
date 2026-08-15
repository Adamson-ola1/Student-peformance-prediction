import api from "./axios.js";

export async function checkHealth() {
  const { data } = await api.get("/");
  return data;
}

export async function listStudents(page = 1, pageSize = 10) {
  const { data } = await api.get("/students", {
    params: { page, page_size: pageSize },
  });
  return data;
}

export async function getStudent(studentId) {
  const { data } = await api.get(`/students/${studentId}`);
  return data;
}

export async function createStudent(payload) {
  const { data } = await api.post("/students", payload);
  return data;
}

export async function updateStudent(studentId, payload) {
  const { data } = await api.put(`/students/${studentId}`, payload);
  return data;
}

export async function deleteStudent(studentId) {
  // 204 No Content -> axios gives us an empty body, nothing to return
  await api.delete(`/students/${studentId}`);
}
