import { useState, useEffect } from 'react';
import { API } from '../services/api';

export default function DireccionesPage({ showToast }) {
  const [direcciones, setDirecciones] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({
    alias: '', linea1: '', linea2: '', ciudad: '', provincia: '', codigo_postal: '', es_principal: false,
  });
  const [editingId, setEditingId] = useState(null);

  async function loadDirecciones() {
    try {
      setLoading(true);
      const data = await API.direcciones.list();
      setDirecciones(Array.isArray(data) ? data : data?.data || []);
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { loadDirecciones(); }, []);

  function resetForm() {
    setForm({ alias: '', linea1: '', linea2: '', ciudad: '', provincia: '', codigo_postal: '', es_principal: false });
    setEditingId(null);
    setShowForm(false);
  }

  async function handleSubmit(e) {
    e.preventDefault();
    try {
      if (editingId) {
        await API.direcciones.update(editingId, form);
        showToast('Direccion actualizada');
      } else {
        await API.direcciones.create(form);
        showToast('Direccion creada');
      }
      resetForm();
      loadDirecciones();
    } catch (err) {
      showToast(err.message, 'error');
    }
  }

  async function handleDelete(id) {
    if (!confirm('Eliminar esta direccion?')) return;
    try {
      await API.direcciones.delete(id);
      showToast('Direccion eliminada');
      loadDirecciones();
    } catch (err) {
      showToast(err.message, 'error');
    }
  }

  function handleEdit(d) {
    setForm({
      alias: d.alias || '',
      linea1: d.linea1,
      linea2: d.linea2 || '',
      ciudad: d.ciudad,
      provincia: d.provincia || '',
      codigo_postal: d.codigo_postal || '',
      es_principal: d.es_principal,
    });
    setEditingId(d.id);
    setShowForm(true);
  }

  return (
    <div className="page">
      <div className="page-header">
        <h1>Direcciones</h1>
        <button className="btn btn-primary" onClick={() => { resetForm(); setShowForm(true); }}>
          + Nueva
        </button>
      </div>

      {showForm && (
        <div className="modal-overlay" onClick={() => setShowForm(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <h2>{editingId ? 'Editar' : 'Nueva'} Direccion</h2>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Alias</label>
                <input value={form.alias} onChange={e => setForm({ ...form, alias: e.target.value })} placeholder="Ej: Casa, Trabajo" />
              </div>
              <div className="form-group">
                <label>Linea 1 *</label>
                <input value={form.linea1} onChange={e => setForm({ ...form, linea1: e.target.value })} required />
              </div>
              <div className="form-group">
                <label>Linea 2</label>
                <input value={form.linea2} onChange={e => setForm({ ...form, linea2: e.target.value })} />
              </div>
              <div className="form-group">
                <label>Ciudad *</label>
                <input value={form.ciudad} onChange={e => setForm({ ...form, ciudad: e.target.value })} required />
              </div>
              <div className="form-group">
                <label>Provincia</label>
                <input value={form.provincia} onChange={e => setForm({ ...form, provincia: e.target.value })} />
              </div>
              <div className="form-group">
                <label>Codigo Postal</label>
                <input value={form.codigo_postal} onChange={e => setForm({ ...form, codigo_postal: e.target.value })} />
              </div>
              <div className="form-group">
                <label>
                  <input type="checkbox" checked={form.es_principal} onChange={e => setForm({ ...form, es_principal: e.target.checked })} />
                  {' '}Direccion principal
                </label>
              </div>
              <div className="form-actions">
                <button type="button" className="btn" onClick={() => setShowForm(false)}>Cancelar</button>
                <button type="submit" className="btn btn-primary">Guardar</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {loading ? (
        <div className="loading">Cargando...</div>
      ) : direcciones.length === 0 ? (
        <div className="empty-state">No hay direcciones registradas</div>
      ) : (
        <div className="grid">
          {direcciones.map(d => (
            <div key={d.id} className="card">
              <div className="card-header">
                <strong>{d.alias || `Direccion #${d.id}`}</strong>
                {d.es_principal && <span className="badge">Principal</span>}
              </div>
              <div className="card-body">
                <p>{d.linea1}</p>
                {d.linea2 && <p>{d.linea2}</p>}
                <p>{d.ciudad}{d.provincia ? `, ${d.provincia}` : ''}</p>
                {d.codigo_postal && <p>CP: {d.codigo_postal}</p>}
              </div>
              <div className="card-actions">
                <button className="btn btn-sm" onClick={() => handleEdit(d)}>Editar</button>
                <button className="btn btn-sm btn-danger" onClick={() => handleDelete(d.id)}>Eliminar</button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
