import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
  headers: {
    "Content-Type": "application/json",
  },
});

// ===============================
// Request Interceptor
// ===============================
api.interceptors.request.use(
  (config) => {
    console.log(
      `[API REQUEST] ${config.method?.toUpperCase()} ${config.url}`
    );
    return config;
  },
  (error) => Promise.reject(error)
);


// ===============================
// Response Interceptor
// ===============================
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const detail = error.response?.data?.detail;
    let message = error.message;

    if (typeof detail === "string") {
      message = detail;
    } else if (Array.isArray(detail)) {
      message = detail.map((d) => d.msg || JSON.stringify(d)).join("; ");
    } else if (error.code === "ECONNABORTED") {
      message = "Request timed out — is the backend running?";
    } else if (!error.response) {
      message = "Could not reach the API — is the backend running?";
    }

    return Promise.reject(new Error(message));
  }
);

export default api;
export { API_BASE_URL };
