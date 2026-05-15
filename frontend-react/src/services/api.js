const API_URL = 'http://localhost:8000';

// ==========================================
// 1. SISTEMA DE LOGS Y DEBUGGING
// ==========================================
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

// Función auxiliar para leer la cookie CSRF que requiere FastAPI
function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}

// ==========================================
// 2. MOTOR CENTRAL DE PETICIONES (Faltaba definirla)
// ==========================================
async function api(endpoint, options = {}) {
  const url = `${API_URL}${endpoint}`;
  
  // Configuración base de fetch
  const config = {
    method: options.method || 'GET',
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    // credentials: 'include' es VITAL para que el navegador 
    // envíe las cookies seguras (access_token) automáticamente al backend
    credentials: 'include', 
  };

  // Inyectar el token CSRF automáticamente en mutaciones
  if (config.method !== 'GET') {
    const csrfToken = getCookie('csrf_token');
    if (csrfToken) {
      config.headers['X-CSRF-Token'] = csrfToken;
    }
  }

  // Transformar el body a string si es un objeto (evitando romper FormData)
  if (options.body) {
    if (typeof options.body === 'object' && !(options.body instanceof FormData)) {
      config.body = JSON.stringify(options.body);
    } else {
      config.body = options.body;
    }
  }

  addDebugLog({ 
    type: 'request', 
    method: config.method, 
    endpoint, 
    time: new Date().toLocaleTimeString() 
  });

  try {
    const response = await fetch(url, config);

    // CONTROL DE ERRORES DE LA API
    if (!response.ok) {
      let errorMsg = `Error en la solicitud (${response.status})`;
      try {
        const errorData = await response.json();
        errorMsg = errorData.detail || errorMsg;
      } catch {
        // Si no es un JSON, nos quedamos con el error genérico
      }
      
      addDebugLog({ type: 'error', message: errorMsg, time: new Date().toLocaleTimeString() });
      throw new Error(errorMsg);
    }

    // MANEJO CORRECTO DEL STATUS 204 (No Content)
    if (response.status === 204) {
      addDebugLog({ type: 'response', status: 204, endpoint, time: new Date().toLocaleTimeString() });
      return null; 
    }

    // RESPUESTAS NORMALES CON CONTENIDO
    const data = await response.json();
    addDebugLog({ type: 'response', status: response.status, endpoint, time: new Date().toLocaleTimeString() });
    return data;

  } catch (error) {
    // Captura errores de red (ej: servidor apagado)
    addDebugLog({ type: 'error', message: error.message, time: new Date().toLocaleTimeString() });
    throw error;
  }
}

// ==========================================
// 3. MÓDULOS DE LA API (Tu estructura original impecable)
// ==========================================
export const API = {
  auth: {
    login(email, password) {
      return api('/auth/login', { method: 'POST', body: { email, password } });
    },
    register(nombre, apellido, email, password, celular) {
      return api('/auth/register', { method: 'POST', body: { nombre, apellido, email, password, celular } });
    },
    me() {
      return api('/auth/me');
    },
    refresh() {
      return api('/auth/refresh', { method: 'POST' });
    },
    logout() {
      return api('/auth/logout', { method: 'POST' });
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
    asignarIngrediente(productoId, ingredienteId, cantidad = 1, esRemovible = false) {
      return api('/productos/ingredientes', {
        method: 'POST',
        body: { producto_id: productoId, ingrediente_id: ingredienteId, cantidad, es_removible: esRemovible },
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
  },
  direcciones: {
    list() {
      return api('/direcciones/');
    },
    create(data) {
      return api('/direcciones/', { method: 'POST', body: data });
    },
    update(id, data) {
      return api(`/direcciones/${id}`, { method: 'PATCH', body: data });
    },
    delete(id) {
      return api(`/direcciones/${id}`, { method: 'DELETE' });
    },
  },
  pedidos: {
    list(offset = 0, limit = 50) {
      return api(`/pedidos/?offset=${offset}&limit=${limit}`);
    },
    create(data) {
      return api('/pedidos/', { method: 'POST', body: data });
    },
    getById(id) {
      return api(`/pedidos/${id}`);
    },
    avanzarEstado(id, estadoCodigo, motivo) {
      return api(`/pedidos/${id}/estado`, { method: 'PATCH', body: { estado_codigo: estadoCodigo, motivo } });
    },
    getHistorial(id) {
      return api(`/pedidos/${id}/historial`);
    },
  },
  unidades: {
    list() {
      return api('/unidades-medida/');
    },
    create(data) {
      return api('/unidades-medida/', { method: 'POST', body: data });
    },
    update(id, data) {
      return api(`/unidades-medida/${id}`, { method: 'PATCH', body: data });
    },
  },
  estados: {
    list() {
      return api('/estados-pedido/');
    },
  },
};