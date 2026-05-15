import { NavLink } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Sidebar({ isOpen, onClose, darkMode, onToggleDark, debugVisible, onToggleDebug, onLogout }) {
  const { user } = useAuth();

  const displayName = user ? `${user.nombre} ${user.apellido}` : 'Invitado';
  const displayRole = user?.roles?.[0] || 'CLIENT';
  const avatarLetter = user?.nombre?.[0]?.toUpperCase() || '?';

  return (
    <>
      {isOpen && <div className="sidebar-overlay" onClick={onClose} />}
      <aside className={`sidebar ${isOpen ? 'sidebar-open' : ''}`}>
        <div className="sidebar-header">
          <h2>Food Store</h2>
          <button className="sidebar-close" onClick={onClose}>x</button>
        </div>

        <div className="sidebar-user">
          <div className="sidebar-avatar">{avatarLetter}</div>
          <div className="sidebar-user-info">
            <span className="sidebar-username">{displayName}</span>
            <span className="sidebar-role">{displayRole}</span>
          </div>
        </div>

        <nav className="sidebar-nav">
          <NavLink to="/productos" className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`} onClick={onClose}>
            <span className="sidebar-icon">📦</span>
            Productos
          </NavLink>
          <NavLink to="/categorias" className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`} onClick={onClose}>
            <span className="sidebar-icon">📁</span>
            Categorias
          </NavLink>
          <NavLink to="/ingredientes" className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`} onClick={onClose}>
            <span className="sidebar-icon">🥚</span>
            Ingredientes
          </NavLink>
          <NavLink to="/catalogo" className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`} onClick={onClose}>
            <span className="sidebar-icon">🛒</span>
            Catalogo
          </NavLink>
          <NavLink to="/pedidos" className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`} onClick={onClose}>
            <span className="sidebar-icon">📋</span>
            Pedidos
          </NavLink>
          <NavLink to="/direcciones" className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`} onClick={onClose}>
            <span className="sidebar-icon">📍</span>
            Direcciones
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
          <button onClick={onLogout} className="btn btn-danger btn-full">Cerrar Sesion</button>
        </div>
      </aside>
    </>
  );
}
