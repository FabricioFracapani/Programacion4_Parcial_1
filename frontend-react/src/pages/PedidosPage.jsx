import { useState, useEffect } from 'react';
import { API } from '../services/api';

export default function PedidosPage({ showToast }) {
  const [pedidos, setPedidos] = useState([]);
  const [loading, setLoading] = useState(true);

  async function loadPedidos() {
    try {
      setLoading(true);
      const data = await API.pedidos.list(0, 100);
      setPedidos(data?.data || []);
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { loadPedidos(); }, []);

  const estadosColor = {
    PENDIENTE: '#f59e0b',
    CONFIRMADO: '#3b82f6',
    EN_PREP: '#8b5cf6',
    EN_CAMINO: '#06b6d4',
    ENTREGADO: '#10b981',
    CANCELADO: '#ef4444',
  };

  return (
    <div className="page">
      <div className="page-header">
        <h1>Pedidos</h1>
      </div>
      {loading ? (
        <div className="loading">Cargando pedidos...</div>
      ) : pedidos.length === 0 ? (
        <div className="empty-state">No hay pedidos aun</div>
      ) : (
        <div className="table-container">
          <table className="table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Estado</th>
                <th>Subtotal</th>
                <th>Total</th>
                <th>Fecha</th>
              </tr>
            </thead>
            <tbody>
              {pedidos.map(p => (
                <tr key={p.id}>
                  <td>#{p.id}</td>
                  <td>
                    <span className="badge" style={{ background: estadosColor[p.estado_codigo] || '#6b7280' }}>
                      {p.estado_codigo}
                    </span>
                  </td>
                  <td>S/. {p.subtotal?.toFixed(2)}</td>
                  <td>S/. {p.total?.toFixed(2)}</td>
                  <td>{new Date(p.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
