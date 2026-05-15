export default function ConfirmModal({ title, message, onConfirm, onCancel, confirmText = 'Eliminar' }) {
  return (
    <div className="modal-overlay" onClick={onCancel}>
      <div className="modal-content modal-small" onClick={e => e.stopPropagation()}>
        <span className="modal-close" onClick={onCancel}>&times;</span>
        <h3>{title}</h3>
        <p>{message}</p>
        <div className="form-actions">
          <button onClick={onConfirm} className="btn btn-danger">{confirmText}</button>
          <button onClick={onCancel} className="btn btn-secondary">Cancelar</button>
        </div>
      </div>
    </div>
  );
}
