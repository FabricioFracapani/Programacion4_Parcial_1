import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { API } from '../services/api';

export default function RegisterPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    try {
      await API.auth.register(username, password);
      navigate('/login', { replace: true, state: { message: 'Usuario creado correctamente' } });
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1>PlanViejo</h1>
        <h2>Registrarse</h2>
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
          <button type="submit" className="btn btn-primary btn-full">Registrarse</button>
        </form>
        <div className="auth-links">
          <Link to="/login">Ya tengo cuenta</Link>
        </div>
      </div>
    </div>
  );
}
