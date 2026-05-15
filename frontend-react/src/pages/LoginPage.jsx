import { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { API } from '../services/api';

export default function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const message = location.state?.message;

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    try {
      const data = await API.auth.login(username, password);
      login(data.access_token);
      navigate('/', { replace: true });
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1>PlanViejo</h1>
        <h2>Iniciar Sesión</h2>
        {message && <div className="auth-message success">{message}</div>}
        {error && <div className="auth-message error">{error}</div>}
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Usuario</label>
            <input type="text" value={username} onChange={e => setUsername(e.target.value)} required autoFocus />
          </div>
          <div className="form-group">
            <label>Contraseña</label>
            <input type="password" value={password} onChange={e => setPassword(e.target.value)} required />
          </div>
          <button type="submit" className="btn btn-primary btn-full">Ingresar</button>
        </form>
        <div className="auth-links">
          <Link to="/register">Crear una cuenta</Link>
        </div>
      </div>
    </div>
  );
}
