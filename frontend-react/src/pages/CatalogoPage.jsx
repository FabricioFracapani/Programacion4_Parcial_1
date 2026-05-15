import { useState, useEffect } from 'react';
import { API } from '../services/api';

const PLACEHOLDER = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMzAwIiBoZWlnaHQ9IjIwMCIgZmlsbD0iI2YzZjRmNiIvPjx0ZXh0IHg9IjE1MCIgeT0iMTAwIiBmb250LXNpemU9IjIwIiBmaWxsPSIjOTk5IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkeT0iLjNlbSI+U2luIEltYWdlbjwvdGV4dD48L3N2Zz4=';

export default function CatalogoPage({ showToast }) {
  const [productos, setProductos] = useState([]);
  const [categorias, setCategorias] = useState([]);
  const [relCategorias, setRelCategorias] = useState([]);
  const [relIngredientes, setRelIngredientes] = useState([]);
  const [filtroCat, setFiltroCat] = useState('');

  async function loadData() {
    try {
      const p = await API.productos.list(0, 50);
      setProductos(p.data);
      const c = await API.categorias.list(0, 50);
      setCategorias(c.data);
      const rc = await API.productos.getCategorias();
      setRelCategorias(rc.data);
      const ri = await API.productos.getIngredientes();
      setRelIngredientes(ri.data);
    } catch (err) {
      showToast(err.message, 'error');
    }
  }

  useEffect(() => { loadData(); }, []);

  const filtrados = filtroCat
    ? productos.filter(p => relCategorias.some(r => r.producto_id === p.id && String(r.categoria_id) === filtroCat))
    : productos;

  return (
    <div className="page">
      <div className="section-header">
        <h2>Catálogo de Productos</h2>
        <select value={filtroCat} onChange={e => setFiltroCat(e.target.value)}>
          <option value="">Todas las categorías</option>
          {categorias.map(c => (<option key={c.id} value={c.id}>{c.nombre}</option>))}
        </select>
      </div>
      <div className="catalogo-grid">
        {filtrados.map(p => {
          const imgUrl = p.imagenes_url?.[0] || PLACEHOLDER;
          const catsProd = relCategorias.filter(r => r.producto_id === p.id);
          const catsNombres = catsProd.map(r => {
            const cat = categorias.find(c => c.id === r.categoria_id);
            return cat?.nombre || `Cat ${r.categoria_id}`;
          }).join(', ');
          const ingCount = relIngredientes.filter(r => r.producto_id === p.id).length;
          return (
            <div key={p.id} className="catalogo-card">
              <img src={imgUrl} alt={p.nombre} className="catalogo-img"
                onError={e => { e.target.src = PLACEHOLDER; }} />
              <div className="catalogo-content">
                <h3>{p.nombre}</h3>
                <p className="catalogo-desc">{p.descripcion || 'Sin descripción'}</p>
                <p className="catalogo-precio">${p.precio_base.toFixed(2)}</p>
                <div className="catalogo-tags">
                  <span className="catalogo-cat">{catsNombres || 'Sin categoría'}</span>
                  {ingCount > 0 && <span className="catalogo-ing">{ingCount} ingrediente(s)</span>}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
