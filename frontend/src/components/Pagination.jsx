/**
 * Reusable pagination control. Purely presentational — the parent owns
 * `page`/`total`/`pageSize` state and passes down `onPageChange`.
 */
export default function Pagination({ page, total, pageSize, onPageChange }) {
  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  return (
    <div className="pagination">
      <span>
        {total} result{total === 1 ? "" : "s"} total — page {page} of {totalPages}
      </span>
      <div className="pagination-controls">
        <button
          className="btn-secondary btn-small"
          onClick={() => onPageChange(page - 1)}
          disabled={page <= 1}
        >
          ← Prev
        </button>
        <button
          className="btn-secondary btn-small"
          onClick={() => onPageChange(page + 1)}
          disabled={page >= totalPages}
        >
          Next →
        </button>
      </div>
    </div>
  );
}
