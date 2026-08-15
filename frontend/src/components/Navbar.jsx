import { useEffect, useState } from "react";
import { checkHealth } from "../api/studentApi.js";

export default function Navbar() {
  const [status, setStatus] = useState({ online: null, text: "Checking API…" });

  useEffect(() => {
    let cancelled = false;

    checkHealth()
      .then((data) => {
        if (!cancelled) {
          setStatus({ online: true, text: data.message || "API online" });
        }
      })
      .catch(() => {
        if (!cancelled) {
          setStatus({ online: false, text: "API offline — start the backend" });
        }
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const dotClass =
    status.online === null ? "dot" : status.online ? "dot online" : "dot offline";

  return (
    <header className="navbar">
      <div className="brand">
        <span className="brand-mark">&#9679;</span>
        <div className="brand-text">
          <span className="brand-name">Gworldsoft Academy</span>
          <span className="brand-sub">Student Performance Console</span>
        </div>
      </div>
      <div className="api-status">
        <span className={dotClass} />
        <span>{status.text}</span>
      </div>
    </header>
  );
}
