import { useState, useEffect } from 'react';
import { API } from '../services/api';
import ConfirmModal from '../components/ConfirmModal';

export default function CategoriasPage({ showToast }) {
  const [categorias, setCategorias] = useState([]);
  const [tree, setTree] = useState([]);
  const [filterText, setFilterText] = useState('');
  const [expanded, setExpanded] = useState({});
  const [editId, setEditId] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [confirm, setConfirm] = useState(null);
  const [form, setForm] = useState({
    nombre: '', descripcion: '', parent_id: '', es_principal: true,
  });

  async function loadData() {
    try {
      const c = await API.categorias.list(0, 50);
      setCategorias(c.data);
      buildTree(c.data);
    } catch (err) {
      showToast(err.message, 'error');
    }
  }

  function buildTree(data) {
    const map = {};
    data.forEach(c => { map[c.id] = { ...c, hijos: [] }; });
    const roots = [];
    data.forEach(c => {
      if (c.parent_id && map[c.parent_id]) {
        map[c.parent_id].hijos.push(map[c.id]);
      } else {
        roots.push(map[c.id]);
      }
    });
    setTree(roots);
  }

  useEffect(() => { loadData(); }, []);

  function filterTree(nodes, text) {
    if (!text) return nodes;
    const t = text.toLowerCase();
    return nodes.reduce((acc, node) => {
      const hijosFiltrados = node.hijos ? filterTree(node.hijos, t) : [];
      if (node.nombre.toLowerCase().includes(t) || hijosFiltrados.length > 0) {
        acc.push({ ...node, hijos: hijosFiltrados });
      }
      return acc;
    }, []);
  }

  const treeFiltrado = filterText ? filterTree(tree, filterText) : tree;

  function toggleExpand(id) {
    setExpanded(e => ({ ...e, [id]: !e[id] }));
  }

  function openCreate(parentId = '') {
    setEditId(null);
    setForm({ nombre: '', descripcion: '', parent_id: parentId, es_principal: true });
    setShowModal(true);
  }

  function openEdit(id) {
    const c = categorias.find(x => x.id === id);
    setEditId(id);
    setForm({
      nombre: c.nombre, descripcion: c.descripcion || '',
      parent_id: c.parent_id ? String(c.parent_id) : '',
      es_principal: c.es_principal !== false,
    });
    setShowModal(true);
  }

  async function handleSubmit(e) {
    e.preventDefault();
    const data = {
      nombre: form.nombre,
      descripcion: form.descripcion || null,
      parent_id: form.parent_id ? parseInt(form.parent_id) : null,
      es_principal: form.es_principal,
    };
    try {
      if (editId) {
        await API.categorias.update(editId, data);
      } else {
        await API.categorias.create(data);
      }
      showToast(editId ? 'Categoría actualizada' : 'Categoría creada');
      setShowModal(false);
      loadData();
    } catch (err) {
      showToast(err.message, 'error');
    }
  }

  function handleDelete(id, nombre) {
    setConfirm({
      title: 'Eliminar Categoría',
      message: `¿Estás seguro de eliminar la categoría "${nombre}"?`,
      onConfirm: async () => {
        try {
          await API.categorias.delete(id);
          showToast('Categoría eliminada');
          setConfirm(null);
          loadData();
        } catch (err) {
          showToast(err.message, 'error');
        }
      },
    });
  }

  function renderTreeNode(node, nivel = 0) {
    const hasChildren = node.hijos?.length > 0;
    const isExpanded = expanded[node.id];
    return (
      <div key={node.id}>
        <div className="tree-item" style={{ paddingLeft: nivel * 20 + 10 }}>
          <div className="tree-content">
            {hasChildren ? (
              <button className="tree-expand" onClick={() => toggleExpand(node.id)}>
                {isExpanded ? '▼' : '▶'}
              </button>
            ) : <span className="tree-expand-spacer" />}
            <span className="tree-nombre">{node.nombre}</span>
            <span className="tree-desc">{node.descripcion || ''}</span>
            <span className={`badge ${node.es_principal !== false ? 'badge-success' : 'badge-danger'}`}>
              {node.es_principal !== false ? 'Principal' : 'Secundaria'}
            </span>
          </div>
          <div className="tree-actions">
            <button onClick={() => openEdit(node.id)} className="btn btn-sm btn-secondary">Editar</button>
            <button onClick={() => handleDelete(node.id, node.nombre)} className="btn btn-sm btn-danger">Eliminar</button>
          </div>
        </div>
        {hasChildren && isExpanded && (
          <div className="tree-hijos">
            {node.hijos.map(h => renderTreeNode(h, nivel + 1))}
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="page">
      <div className="section-header">
        <h2>Gestión de Categorías ({categorias.length})</h2>
        <button onClick={() => openCreate()} className="btn btn-primary">+ Nueva Categoría</button>
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
      <div className="tree-container">
        {treeFiltrado.length === 0 && <div className="table-empty">No hay categorías</div>}
        {treeFiltrado.map(node => renderTreeNode(node))}
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <span className="modal-close" onClick={() => setShowModal(false)}>&times;</span>
            <h3>{editId ? 'Editar Categoría' : 'Nueva Categoría'}</h3>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Nombre *</label>
                <input value={form.nombre} onChange={e => setForm({...form, nombre: e.target.value})} required />
              </div>
              <div className="form-group">
                <label>Descripción</label>
                <textarea value={form.descripcion} onChange={e => setForm({...form, descripcion: e.target.value})} />
              </div>
              <div className="form-group">
                <label>Categoría Padre</label>
                <select value={form.parent_id} onChange={e => setForm({...form, parent_id: e.target.value})}>
                  <option value="">Ninguna</option>
                  {categorias.filter(c => c.id !== editId).map(c => (
                    <option key={c.id} value={c.id}>{c.nombre}</option>
                  ))}
                </select>
              </div>
              <div className="form-group checkbox-group">
                <input type="checkbox" id="cat-principal" checked={form.es_principal}
                  onChange={e => setForm({...form, es_principal: e.target.checked})} />
                <label htmlFor="cat-principal">Es categoría principal</label>
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
