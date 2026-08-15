import { NavLink } from "react-router-dom";

const LINKS = [
  { to: "/", label: "Dashboard", end: true },
  { to: "/students", label: "Students" },
  { to: "/predict", label: "Predict Performance" },
  { to: "/model-info", label: "Model Info" },
];

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <nav>
        {LINKS.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            end={link.end}
            className={({ isActive }) => `sidebar-link ${isActive ? "active" : ""}`}
          >
            {link.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
