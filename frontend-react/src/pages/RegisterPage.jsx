import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function RegisterPage() {
  const [nombre, setNombre] = useState('');
  const [apellido, setApellido] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [celular, setCelular] = useState('');
  const [error, setError] = useState('');
  const { register } = useAuth();
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    try {
      await register(nombre, apellido, email, password, celular || undefined);
      navigate('/', { replace: true });
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1>Food Store</h1>
        <h2>Registrarse</h2>
        {error && <div className="auth-message error">{error}</div>}
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Nombre</label>
            <input type="text" value={nombre} onChange={e => setNombre(e.target.value)} required autoFocus />
          </div>
          <div className="form-group">
            <label>Apellido</label>
            <input type="text" value={apellido} onChange={e => setApellido(e.target.value)} required />
          </div>
          <div className="form-group">
            <label>Email</label>
            <input type="email" value={email} onChange={e => setEmail(e.target.value)} required />
          </div>
          <div className="form-group">
            <label>Contrasena</label>
            <input type="password" value={password} onChange={e => setPassword(e.target.value)} required />
          </div>
          <div className="form-group">
            <label>Celular (opcional)</label>
            <input type="text" value={celular} onChange={e => setCelular(e.target.value)} />
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
