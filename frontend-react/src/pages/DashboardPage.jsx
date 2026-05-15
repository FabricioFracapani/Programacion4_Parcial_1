import { useState, useEffect } from 'react';
import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { setDebugCallback } from '../services/api';
import TopBar from '../components/Navbar';
import Sidebar from '../components/Sidebar';
import DebugPanel from '../components/DebugPanel';
import Toast from '../components/Toast';
import ProductosPage from './ProductosPage';
import CategoriasPage from './CategoriasPage';
import IngredientesPage from './IngredientesPage';
import CatalogoPage from './CatalogoPage';

export default function DashboardPage() {
  const { logout } = useAuth();
  const [toast, setToast] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [darkMode, setDarkMode] = useState(() => localStorage.getItem('darkMode') === 'true');
  const [debugVisible, setDebugVisible] = useState(true);
  const location = useLocation();

  function showToast(message, type = 'success') {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3000);
  }

  function toggleDarkMode() {
    const next = !darkMode;
    setDarkMode(next);
    localStorage.setItem('darkMode', String(next));
  }

  function toggleSidebar() {
    setSidebarOpen(o => !o);
  }

  function closeSidebar() {
    setSidebarOpen(false);
  }

  useEffect(() => {
    document.documentElement.classList.toggle('dark', darkMode);
  }, [darkMode]);

  useEffect(() => {
    setDebugCallback(() => {});
  }, []);

  useEffect(() => {
    closeSidebar();
  }, [location]);

  return (
    <div className={`app-layout ${darkMode ? 'dark' : ''}`}>
      <TopBar onMenuToggle={toggleSidebar} />
      <Sidebar
        isOpen={sidebarOpen}
        onClose={closeSidebar}
        darkMode={darkMode}
        onToggleDark={toggleDarkMode}
        debugVisible={debugVisible}
        onToggleDebug={() => setDebugVisible(v => !v)}
        onLogout={logout}
      />
      <main className="main-content">
        <Routes>
          <Route index element={<Navigate to="productos" replace />} />
          <Route path="productos" element={<ProductosPage showToast={showToast} />} />
          <Route path="categorias" element={<CategoriasPage showToast={showToast} />} />
          <Route path="ingredientes" element={<IngredientesPage showToast={showToast} />} />
          <Route path="catalogo" element={<CatalogoPage showToast={showToast} />} />
        </Routes>
      </main>
      {/* <DebugPanel visible={debugVisible} /> */}
      {toast && <Toast message={toast.message} type={toast.type} />}
    </div>
  );
}
