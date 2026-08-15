/**
 * A small reusable loading indicator. Pass `text` to customize the message
 * (e.g. "Loading students…" vs "Predicting…"); defaults to something generic.
 */
export default function Loader({ text = "Loading…" }) {
  return (
    <div className="loader">
      <span className="loader-spinner" aria-hidden="true" />
      <span>{text}</span>
    </div>
  );
}
