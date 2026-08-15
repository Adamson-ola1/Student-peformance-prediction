import { createBrowserRouter } from "react-router-dom";
import DashboardLayout from "./layouts/DashboardLayout.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import Students from "./pages/Students.jsx";
import AddStudent from "./pages/AddStudent.jsx";
import EditStudent from "./pages/EditStudent.jsx";
import StudentDetails from "./pages/StudentDetails.jsx";
import Prediction from "./pages/Prediction.jsx";
import ModelInfo from "./pages/ModelInfo.jsx";
import NotFound from "./pages/NotFound.jsx";

/**
 * Every route renders inside <DashboardLayout> (Navbar + Sidebar + Footer),
 * via its <Outlet /> — see src/layouts/DashboardLayout.jsx.
 */
const router = createBrowserRouter([
  {
    path: "/",
    element: <DashboardLayout />,
    children: [
      { index: true, element: <Dashboard /> },
      { path: "students", element: <Students /> },
      { path: "students/add", element: <AddStudent /> },
      { path: "students/:id", element: <StudentDetails /> },
      { path: "students/:id/edit", element: <EditStudent /> },
      { path: "predict", element: <Prediction /> },
      { path: "model-info", element: <ModelInfo /> },
      { path: "*", element: <NotFound /> },
    ],
  },
]);

export default router;
