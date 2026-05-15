import { NavLink } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Sidebar({ isOpen, onClose, darkMode, onToggleDark, debugVisible, onToggleDebug, onLogout }) {
  const { user } = useAuth();

  return (
    <>
      {isOpen && <div className="sidebar-overlay" onClick={onClose} />}
      <aside className={`sidebar ${isOpen ? 'sidebar-open' : ''}`}>
        <div className="sidebar-header">
          <h2>PlanViejo</h2>
          <button className="sidebar-close" onClick={onClose}>×</button>
        </div>

        <div className="sidebar-user">
          <div className="sidebar-avatar">{user?.sub?.[0]?.toUpperCase() || '?'}</div>
          <div className="sidebar-user-info">
            <span className="sidebar-username">{user?.sub || 'Invitado'}</span>
            <span className="sidebar-role">{user?.rol || 'USER'}</span>
          </div>
        </div>

        <nav className="sidebar-nav">
          <NavLink to="/productos" className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`} onClick={onClose}>
            <span className="sidebar-icon">📦</span>
            Productos
          </NavLink>
          <NavLink to="/categorias" className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`} onClick={onClose}>
            <span className="sidebar-icon">📁</span>
            Categorías
          </NavLink>
          <NavLink to="/ingredientes" className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`} onClick={onClose}>
            <span className="sidebar-icon">🥚</span>
            Ingredientes
          </NavLink>
          <NavLink to="/catalogo" className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`} onClick={onClose}>
            <span className="sidebar-icon">🛒</span>
            Catálogo
          </NavLink>
        </nav>

        <div className="sidebar-footer">
          <label className="switch-dark">
            <span>🌙 Modo Oscuro</span>
            <input type="checkbox" checked={darkMode} onChange={onToggleDark} />
            <span className="slider"></span>
          </label>
          <label className="switch-dark">
            <span>🪲 Debug</span>
            <input type="checkbox" checked={debugVisible} onChange={onToggleDebug} />
            <span className="slider"></span>
          </label>
          <button onClick={onLogout} className="btn btn-danger btn-full">Cerrar Sesión</button>
        </div>
      </aside>
    </>
  );
}
