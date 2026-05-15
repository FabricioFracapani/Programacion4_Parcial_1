import { useState, useEffect } from 'react';
import { API } from '../services/api';
import ConfirmModal from '../components/ConfirmModal';

export default function ProductosPage({ showToast }) {
  const [productos, setProductos] = useState([]);
  const [filterText, setFilterText] = useState('');
  const [total, setTotal] = useState(0);
  const [categorias, setCategorias] = useState([]);
  const [ingredientes, setIngredientes] = useState([]);
  const [relCategorias, setRelCategorias] = useState([]);
  const [relIngredientes, setRelIngredientes] = useState([]);
  const [editId, setEditId] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [confirm, setConfirm] = useState(null);

  const [form, setForm] = useState({
    nombre: '', descripcion: '', categoria_principal: '',
    categorias_adicionales: [], ingredientes_seleccionados: [],
    precio_base: '', stock_cantidad: '0', imagen_url: '', disponible: true,
  });

  async function loadData() {
    try {
      const p = await API.productos.list(0, 50);
      setProductos(p.data);
      setTotal(p.total);
      const c = await API.categorias.list(0, 50);
      setCategorias(c.data);
      const i = await API.ingredientes.list(0, 50);
      setIngredientes(i.data);
      const rc = await API.productos.getCategorias();
      setRelCategorias(rc.data);
      const ri = await API.productos.getIngredientes();
      setRelIngredientes(ri.data);
    } catch (err) {
      showToast(err.message, 'error');
    }
  }

  useEffect(() => { loadData(); }, []);

  const productosFiltrados = filterText
    ? productos.filter(p => p.nombre.toLowerCase().includes(filterText.toLowerCase()))
    : productos;

  function openCreate() {
    setEditId(null);
    setForm({
      nombre: '', descripcion: '', categoria_principal: '',
      categorias_adicionales: [], ingredientes_seleccionados: [],
      precio_base: '', stock_cantidad: '0', imagen_url: '', disponible: true,
    });
    setShowModal(true);
  }

  async function openEdit(id) {
    const p = productos.find(x => x.id === id);
    const catsProd = relCategorias.filter(r => r.producto_id === id);
    const principal = catsProd.find(r => r.es_principal);
    const adicionales = catsProd.filter(r => !r.es_principal).map(r => r.categoria_id);
    const ingsProd = relIngredientes.filter(r => r.producto_id === id).map(r => r.ingrediente_id);
    setEditId(id);
    setForm({
      nombre: p.nombre, descripcion: p.descripcion || '',
      categoria_principal: principal ? String(principal.categoria_id) : '',
      categorias_adicionales: adicionales,
      ingredientes_seleccionados: ingsProd,
      precio_base: String(p.precio_base), stock_cantidad: String(p.stock_cantidad || 0),
      imagen_url: p.imagen_url?.[0] || '', disponible: p.disponible,
    });
    setShowModal(true);
  }

  async function handleSubmit(e) {
    e.preventDefault();
    if (!form.categoria_principal) {
      showToast('Debe seleccionar una categoría principal', 'error');
      return;
    }
    const data = {
      nombre: form.nombre,
      descripcion: form.descripcion || null,
      precio_base: parseFloat(form.precio_base),
      stock_cantidad: parseInt(form.stock_cantidad) || 0,
      imagen_url: form.imagen_url ? [form.imagen_url] : [],
      disponible: form.disponible,
    };
    try {
      let producto;
      if (editId) {
        producto = await API.productos.update(editId, data);
      } else {
        producto = await API.productos.create(data);
      }
      const pid = editId || producto.id;
      const allCatIds = [parseInt(form.categoria_principal), ...form.categorias_adicionales.map(Number)];
      await Promise.all(allCatIds.map(cid =>
        API.productos.asignarCategoria(pid, cid, cid === parseInt(form.categoria_principal))
      ));
      await Promise.all(form.ingredientes_seleccionados.map(iid =>
        API.productos.asignarIngrediente(pid, parseInt(iid))
      ));
      showToast(editId ? 'Producto actualizado' : 'Producto creado');
      setShowModal(false);
      loadData();
    } catch (err) {
      showToast(err.message, 'error');
    }
  }

  function handleDelete(id, nombre) {
    setConfirm({
      title: 'Eliminar Producto',
      message: `¿Estás seguro de eliminar el producto "${nombre}"?`,
      onConfirm: async () => {
        try {
          await API.productos.delete(id);
          showToast('Producto eliminado');
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
        <h2>Gestión de Productos ({productosFiltrados.length}/{total})</h2>
        <button onClick={openCreate} className="btn btn-primary">+ Nuevo Producto</button>
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
            <tr><th>ID</th><th>Nombre</th><th>Precio</th><th>Stock</th><th>Acciones</th></tr>
          </thead>
          <tbody>
            {productosFiltrados.map(p => (
              <tr key={p.id}>
                <td>{p.id}</td>
                <td>{p.nombre}</td>
                <td>${p.precio_base.toFixed(2)}</td>
                <td>{p.stock_cantidad}</td>
                <td className="actions-cell">
                  <button onClick={() => openEdit(p.id)} className="btn btn-sm btn-secondary">Editar</button>
                  <button onClick={() => handleDelete(p.id, p.nombre)} className="btn btn-sm btn-danger">Eliminar</button>
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
            <h3>{editId ? 'Editar Producto' : 'Nuevo Producto'}</h3>
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
                <label>Categoría Principal *</label>
                <select value={form.categoria_principal} onChange={e => setForm({...form, categoria_principal: e.target.value})} required>
                  <option value="">Seleccionar...</option>
                  {categorias.map(c => (<option key={c.id} value={c.id}>{c.nombre}</option>))}
                </select>
              </div>
              <div className="form-group">
                <label>Categorías Adicionales</label>
                <div className="checkbox-list">
                  {categorias.map(c => (
                    <label key={c.id} className="checkbox-item">
                      <input type="checkbox" checked={form.categorias_adicionales.includes(c.id)}
                        onChange={e => {
                          const val = parseInt(e.target.value);
                          setForm(f => ({
                            ...f,
                            categorias_adicionales: e.target.checked
                              ? [...f.categorias_adicionales, val]
                              : f.categorias_adicionales.filter(x => x !== val),
                          }));
                        }} value={c.id} />
                      {c.nombre}
                    </label>
                  ))}
                </div>
              </div>
              <div className="form-group">
                <label>Ingredientes</label>
                <div className="checkbox-list">
                  {ingredientes.map(i => (
                    <label key={i.id} className="checkbox-item">
                      <input type="checkbox" checked={form.ingredientes_seleccionados.includes(i.id)}
                        onChange={e => {
                          const val = parseInt(e.target.value);
                          setForm(f => ({
                            ...f,
                            ingredientes_seleccionados: e.target.checked
                              ? [...f.ingredientes_seleccionados, val]
                              : f.ingredientes_seleccionados.filter(x => x !== val),
                          }));
                        }} value={i.id} />
                      {i.nombre}
                    </label>
                  ))}
                </div>
              </div>
              <div className="form-group">
                <label>Precio Base *</label>
                <input type="number" step="0.01" min="0.01" value={form.precio_base}
                  onChange={e => setForm({...form, precio_base: e.target.value})} required />
              </div>
              <div className="form-group">
                <label>Stock</label>
                <input type="number" min="0" value={form.stock_cantidad}
                  onChange={e => setForm({...form, stock_cantidad: e.target.value})} />
              </div>
              <div className="form-group">
                <label>URL de Imagen</label>
                <input value={form.imagen_url} onChange={e => setForm({...form, imagen_url: e.target.value})}
                  placeholder="https://ejemplo.com/imagen.jpg" />
              </div>
              <div className="form-group checkbox-group">
                <input type="checkbox" id="prod-disponible" checked={form.disponible}
                  onChange={e => setForm({...form, disponible: e.target.checked})} />
                <label htmlFor="prod-disponible">Disponible</label>
              </div>
              <div className="form-actions">
                <button type="submit" className="btn btn-primary">Guardar</button>
                <button type="button" onClick={() => setShowModal(false)} className="btn btn-secondary">Cancelar</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {confirm && (
        <ConfirmModal {...confirm} onCancel={() => setConfirm(null)} />
      )}
    </div>
  );
}
