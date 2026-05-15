import { useState, useEffect } from 'react';
import { API } from '../services/api';
import ConfirmModal from '../components/ConfirmModal';

export default function IngredientesPage({ showToast }) {
  const [ingredientes, setIngredientes] = useState([]);
  const [filterText, setFilterText] = useState('');
  const [editId, setEditId] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [confirm, setConfirm] = useState(null);
  const [form, setForm] = useState({
    nombre: '', descripcion: '', es_alergeno: false,
  });

  async function loadData() {
    try {
      const i = await API.ingredientes.list(0, 50);
      setIngredientes(i.data);
    } catch (err) {
      showToast(err.message, 'error');
    }
  }

  useEffect(() => { loadData(); }, []);

  const ingredientesFiltrados = filterText
    ? ingredientes.filter(i => i.nombre.toLowerCase().includes(filterText.toLowerCase()))
    : ingredientes;

  function openCreate() {
    setEditId(null);
    setForm({ nombre: '', descripcion: '', es_alergeno: false });
    setShowModal(true);
  }

  function openEdit(id) {
    const i = ingredientes.find(x => x.id === id);
    setEditId(id);
    setForm({
      nombre: i.nombre, descripcion: i.descripcion || '',
      es_alergeno: i.es_alergeno || false,
    });
    setShowModal(true);
  }

  async function handleSubmit(e) {
    e.preventDefault();
    const data = {
      nombre: form.nombre,
      descripcion: form.descripcion || null,
      es_alergeno: form.es_alergeno,
    };
    try {
      if (editId) {
        await API.ingredientes.update(editId, data);
      } else {
        await API.ingredientes.create(data);
      }
      showToast(editId ? 'Ingrediente actualizado' : 'Ingrediente creado');
      setShowModal(false);
      loadData();
    } catch (err) {
      showToast(err.message, 'error');
    }
  }

  function handleDelete(id, nombre) {
    setConfirm({
      title: 'Eliminar Ingrediente',
      message: `¿Estás seguro de eliminar el ingrediente "${nombre}"?`,
      onConfirm: async () => {
        try {
          await API.ingredientes.delete(id);
          showToast('Ingrediente eliminado');
          setConfirm(null);
          loadData();
        } catch (err) {
          showToast(err.message, 'error');
        }
      },
    });
  }

  return (
    <div className="page">
      <div className="section-header">
        <h2>Gestión de Ingredientes ({ingredientesFiltrados.length}/{ingredientes.length})</h2>
        <button onClick={openCreate} className="btn btn-primary">+ Nuevo Ingrediente</button>
      </div>
      <div className="filter-bar">
        <input
          type="text"
          placeholder="Filtrar por nombre..."
          value={filterText}
          onChange={e => setFilterText(e.target.value)}
          className="filter-input"
        />
      </div>
      <div className="table-container">
        <table>
          <thead>
            <tr><th>ID</th><th>Nombre</th><th>Descripción</th><th>Alérgeno</th><th>Acciones</th></tr>
          </thead>
          <tbody>
            {ingredientesFiltrados.map(i => (
              <tr key={i.id}>
                <td>{i.id}</td>
                <td>{i.nombre}</td>
                <td>{i.descripcion || '-'}</td>
                <td><span className={`badge ${i.es_alergeno ? 'badge-danger' : 'badge-success'}`}>{i.es_alergeno ? 'Sí' : 'No'}</span></td>
                <td className="actions-cell">
                  <button onClick={() => openEdit(i.id)} className="btn btn-sm btn-secondary">Editar</button>
                  <button onClick={() => handleDelete(i.id, i.nombre)} className="btn btn-sm btn-danger">Eliminar</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <span className="modal-close" onClick={() => setShowModal(false)}>&times;</span>
            <h3>{editId ? 'Editar Ingrediente' : 'Nuevo Ingrediente'}</h3>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Nombre *</label>
                <input value={form.nombre} onChange={e => setForm({...form, nombre: e.target.value})} required />
              </div>
              <div className="form-group">
                <label>Descripción</label>
                <textarea value={form.descripcion} onChange={e => setForm({...form, descripcion: e.target.value})} />
              </div>
              <div className="form-group checkbox-group">
                <input type="checkbox" id="ing-alergeno" checked={form.es_alergeno}
                  onChange={e => setForm({...form, es_alergeno: e.target.checked})} />
                <label htmlFor="ing-alergeno">Es alérgeno</label>
              </div>
              <div className="form-actions">
                <button type="submit" className="btn btn-primary">Guardar</button>
                <button type="button" onClick={() => setShowModal(false)} className="btn btn-secondary">Cancelar</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {confirm && <ConfirmModal {...confirm} onCancel={() => setConfirm(null)} />}
    </div>
  );
}
