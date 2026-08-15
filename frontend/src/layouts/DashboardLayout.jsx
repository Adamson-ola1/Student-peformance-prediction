import { Outlet } from "react-router-dom";
import Navbar from "../components/Navbar.jsx";
import Sidebar from "../components/Sidebar.jsx";
import Footer from "../components/Footer.jsx";

/**
 * The shared shell every page renders inside. `<Outlet />` is where
 * react-router injects whichever page component matched the current route
 * (see src/routes.jsx) — Dashboard, Students, Prediction, etc.
 */
export default function DashboardLayout() {
  return (
    <div className="app-shell">
      <Navbar />
      <div className="layout-body">
        <Sidebar />
        <main className="content-area">
          <Outlet />
        </main>
      </div>
      <Footer />
    </div>
  );
}
