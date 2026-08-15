import { RouterProvider } from "react-router-dom";
import { StudentProvider } from "./context/StudentContext.jsx";
import router from "./routes.jsx";

export default function App() {
  return (
    <StudentProvider>
      <RouterProvider router={router} />
    </StudentProvider>
  );
}
