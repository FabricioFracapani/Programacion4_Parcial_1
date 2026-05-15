import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { API } from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const checkAuth = useCallback(async () => {
    try {
      const data = await API.auth.me();
      if (data?.user) {
        setUser(data.user);
      } else {
        setUser(null);
      }
    } catch {
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  async function login(email, password) {
    const data = await API.auth.login(email, password);
    if (data?.user) {
      setUser(data.user);
    }
    return data;
  }

  async function register(nombre, apellido, email, password, celular) {
    const data = await API.auth.register(nombre, apellido, email, password, celular);
    if (data?.user) {
      setUser(data.user);
    }
    return data;
  }

  async function logout() {
    try {
      await API.auth.logout();
    } catch {}
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, checkAuth }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
}
