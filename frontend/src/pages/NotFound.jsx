import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <div className="page">
      <section className="panel not-found-panel">
        <h1>404</h1>
        <p>The page you're looking for doesn't exist.</p>
        <Link className="btn-primary" to="/">
          ← Back to Dashboard
        </Link>
      </section>
    </div>
  );
}
