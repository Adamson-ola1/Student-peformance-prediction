/**
 * A small confirmation modal, used before any destructive action (deleting
 * a student). Replaces window.confirm() with something that matches the
 * app's own styling and is easier to test/extend later (e.g. adding a
 * reason field).
 *
 * Controlled entirely by the parent: pass `isOpen`, and the parent decides
 * what happens on confirm/cancel.
 */
export default function ConfirmDelete({ isOpen, itemLabel, onConfirm, onCancel }) {
  if (!isOpen) return null;

  return (
    <div className="modal-overlay" role="dialog" aria-modal="true">
      <div className="modal-box">
        <h2>Confirm Deletion</h2>
        <p>
          Are you sure you want to delete <strong>{itemLabel}</strong>? This
          action cannot be undone.
        </p>
        <div className="modal-actions">
          <button className="btn-danger-solid" onClick={onConfirm}>
            Delete
          </button>
          <button className="btn-secondary" onClick={onCancel}>
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}
