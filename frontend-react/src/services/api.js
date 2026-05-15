const API_URL = '/api';

let debugLogs = [];
let onDebugUpdate = () => {};

export function setDebugCallback(cb) {
  onDebugUpdate = cb;
}

function addDebugLog(entry) {
  debugLogs.push(entry);
  if (debugLogs.length > 100) debugLogs.shift();
  onDebugUpdate([...debugLogs]);
}

export function getDebugLogs() {
  return [...debugLogs];
}

export function clearDebugLogs() {
  debugLogs = [];
  onDebugUpdate([]);
}

function getToken() {
  return localStorage.getItem('token');
}

async function api(endpoint, options = {}) {
  const url = `${API_URL}${endpoint}`;
  const token = getToken();
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
    ...options,
  };

  if (options.body && typeof options.body === 'object') {
    config.body = JSON.stringify(options.body);
  }

  addDebugLog({ type: 'request', method: options.method || 'GET', endpoint, time: new Date().toLocaleTimeString() });

  const response = await fetch(url, config);

  if (!response.ok) {
    let errorMsg = 'Error en la solicitud';
    try {
      const error = await response.json();
      errorMsg = error.detail || errorMsg;
    } catch {}
    addDebugLog({ type: 'error', message: errorMsg, time: new Date().toLocaleTimeString() });
    throw new Error(errorMsg);
  }

  if (response.status === 204) {
    addDebugLog({ type: 'response', status: 204, endpoint, time: new Date().toLocaleTimeString() });
    return null;
  }

  const data = await response.json();
  addDebugLog({ type: 'response', status: response.status, endpoint, time: new Date().toLocaleTimeString() });
  return data;
}

export const API = {
  auth: {
    login(username, password) {
      return api('/auth/login', { method: 'POST', body: { username, password } });
    },
    register(username, password) {
      return api('/auth/register', { method: 'POST', body: { username, password } });
    },
    me() {
      return api('/auth/me');
    },
  },
  productos: {
    list(offset = 0, limit = 50) {
      return api(`/productos/?offset=${offset}&limit=${limit}`);
    },
    create(data) {
      return api('/productos/', { method: 'POST', body: data });
    },
    update(id, data) {
      return api(`/productos/${id}`, { method: 'PATCH', body: data });
    },
    delete(id) {
      return api(`/productos/${id}/desactivar`, { method: 'DELETE' });
    },
    getCategorias() {
      return api('/productos/categorias');
    },
    getIngredientes() {
      return api('/productos/ingredientes');
    },
    asignarCategoria(productoId, categoriaId, esPrincipal = true) {
      return api('/productos/categorias', {
        method: 'POST',
        body: { producto_id: productoId, categoria_id: categoriaId, es_principal: esPrincipal },
      });
    },
    asignarIngrediente(productoId, ingredienteId, esRemovible = false) {
      return api('/productos/ingredientes', {
        method: 'POST',
        body: { producto_id: productoId, ingrediente_id: ingredienteId, es_removible: esRemovible },
      });
    },
  },
  categorias: {
    list(offset = 0, limit = 50) {
      return api(`/categorias/?offset=${offset}&limit=${limit}`);
    },
    create(data) {
      return api('/categorias/', { method: 'POST', body: data });
    },
    update(id, data) {
      return api(`/categorias/${id}`, { method: 'PATCH', body: data });
    },
    delete(id) {
      return api(`/categorias/${id}`, { method: 'DELETE' });
    },
  },
  ingredientes: {
    list(offset = 0, limit = 50) {
      return api(`/ingredientes/?offset=${offset}&limit=${limit}`);
    },
    create(data) {
      return api('/ingredientes/', { method: 'POST', body: data });
    },
    update(id, data) {
      return api(`/ingredientes/${id}`, { method: 'PATCH', body: data });
    },
    delete(id) {
      return api(`/ingredientes/${id}`, { method: 'DELETE' });
    },
    getRelaciones(productoId) {
      return api(`/ingredientes/producto/${productoId}`);
    },
  },
};
