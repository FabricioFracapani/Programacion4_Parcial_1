const API_BASE = 'http://localhost:8000';

let currentView = 'productos';
let deleteTarget = null;
let debugLogs = [];

function toggleDebug() {
    const btn = document.getElementById('btn-toggle-debug');
    const logs = document.getElementById('debug-logs');
    logs.classList.toggle('hidden');
    btn.textContent = logs.classList.contains('hidden') ? 'Mostrar' : 'Ocultar';
}

const API = {
    async request(endpoint, options = {}) {
        const url = `${API_BASE}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
            ...options,
        };
        
        if (options.body && typeof options.body === 'object') {
            config.body = JSON.stringify(options.body);
        }
        
        debugLogs.push({ type: 'request', method: options.method || 'GET', endpoint, time: new Date().toLocaleTimeString() });
        
        try {
            const response = await fetch(url, config);
            if (!response.ok) {
                const error = await response.json().catch(() => ({ detail: 'Error desconocido' }));
                debugLogs.push({ type: 'error', message: error.detail || 'Error en la solicitud', time: new Date().toLocaleTimeString() });
                renderDebug();
                throw new Error(error.detail || 'Error en la solicitud');
            }
            
            if (response.status === 204) {
                debugLogs.push({ type: 'success', message: `${options.method || 'GET'} ${endpoint} - 204 OK`, time: new Date().toLocaleTimeString() });
                renderDebug();
                return null;
            }
            const result = await response.json();
            debugLogs.push({ type: 'success', message: `${options.method || 'GET'} ${endpoint}`, time: new Date().toLocaleTimeString() });
            renderDebug();
            return result;
        } catch (error) {
            console.log(error)
            const errorMsg = error.message === 'Failed to fetch' 
                ? 'No se puede conectar al backend. ¿Está corriendo en localhost:8000?' 
                : error.message;
            debugLogs.push({ type: 'error', message: errorMsg, time: new Date().toLocaleTimeString() });
            renderDebug();
            console.error('API Error:', error);
            throw error;
        }
    },
    
    productos: {
        getAll(offset = 0, limit = 20) {
            return API.request(`/productos?offset=${offset}&limit=${limit}`);
        },
        getById(id) {
            return API.request(`/productos/${id}`);
        },
        create(data) {
            return API.request('/productos', { method: 'POST', body: data });
        },
        update(id, data) {
            return API.request(`/productos/${id}`, { method: 'PATCH', body: data });
        },
        delete(id) {
            return API.request(`/productos/${id}/desactivar`, { method: 'DELETE' });
        },
        getCategorias() {
            return API.request('/productos/categorias');
        },
        getIngredientes() {
            return API.request('/productos/ingredientes');
        },
        asignarCategoria(productoId, categoriaId, esPrincipal = true) {
            return API.request('/productos/categorias', { 
                method: 'POST', 
                body: { producto_id: productoId, categoria_id: categoriaId, es_principal: esPrincipal } 
            });
        },
        asignarIngrediente(productoId, ingredienteId, esRemovible = false) {
            return API.request('/productos/ingredientes', { 
                method: 'POST', 
                body: { producto_id: productoId, ingrediente_id: ingredienteId, es_removible: esRemovible } 
            });
        },
        eliminarCategorias(productoId) {
            return API.request('/productos/categorias', { method: 'GET' });
        },
        eliminarIngredientes(productoId) {
            return API.request('/productos/ingredientes', { method: 'GET' });
        },
    },
    
    categorias: {
        getAll(offset = 0, limit = 20) {
            return API.request(`/categorias?offset=${offset}&limit=${limit}`);
        },
        getById(id) {
            return API.request(`/categorias/${id}`);
        },
        create(data) {
            return API.request('/categorias', { method: 'POST', body: data });
        },
        update(id, data) {
            return API.request(`/categorias/${id}`, { method: 'PATCH', body: data });
        },
        delete(id) {
            return API.request(`/categorias/${id}`, { method: 'DELETE' });
        },
        getForSelect() {
            return API.request('/categorias?offset=0&limit=100');
        },
    },
    
    ingredientes: {
        getAll(offset = 0, limit = 20) {
            return API.request(`/ingredientes?offset=${offset}&limit=${limit}`);
        },
        getById(id) {
            return API.request(`/ingredientes/${id}`);
        },
        create(data) {
            return API.request('/ingredientes', { method: 'POST', body: data });
        },
        update(id, data) {
            return API.request(`/ingredientes/${id}`, { method: 'PATCH', body: data });
        },
        delete(id) {
            return API.request(`/ingredientes/${id}`, { method: 'DELETE' });
        },
    },
};

function debugLog(type, message) {
    debugLogs.push({ type, message, time: new Date().toLocaleTimeString() });
    renderDebug();
}

function renderDebug() {
    const container = document.getElementById('debug-logs');
    const logsToShow = debugLogs.slice(-50).reverse();
    
    container.innerHTML = logsToShow.map(log => {
        const icon = log.type === 'error' ? '❌' : log.type === 'success' ? '✅' : '📤';
        const cssClass = log.type === 'error' ? 'log-error' : log.type === 'success' ? 'log-success' : 'log-request';
        return `<div class="debug-log ${cssClass}"><span class="log-icon">${icon}</span><span class="log-time">${log.time}</span><span class="log-message">${log.message}</span></div>`;
    }).join('');
}

function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type} show`;
    setTimeout(() => toast.classList.remove('show'), 3000);
}

function openModal(modalId) {
    document.getElementById(modalId).classList.add('open');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('open');
}

function closeAllModals() {
    document.querySelectorAll('.modal').forEach(modal => modal.classList.remove('open'));
}

function switchView(view) {
    currentView = view;
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
    document.getElementById(`${view}-view`).classList.add('active');
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.view === view);
    });
    loadData();
}

async function renderTable(view, data) {
    const container = document.getElementById(`${view}-table-container`);
    
    if (!data || data.data.length === 0) {
        container.innerHTML = `<div class="table-empty">No hay datos disponibles</div>`;
        return;
    }
    
    switch (view) {
        case 'productos':
            container.innerHTML = renderProductosTable(data);
            break;
        case 'categorias':
            container.innerHTML = renderCategoriasTable(data);
            break;
        case 'ingredientes':
            container.innerHTML = renderIngredientesTable(data);
            break;
    }
}

function renderProductosTable(data) {
    let html = `<div class="table-container"><table>
        <thead>
            <tr>
                <th>ID</th>
                <th>Nombre</th>
                <th>Precio</th>
                <th>Stock</th>
                <th>Estado</th>
                <th>Acciones</th>
            </tr>
        </thead>
        <tbody>`;
    
    data.data.forEach(p => {
        html += `<tr>
            <td>${p.id}</td>
            <td>${p.nombre}</td>
            <td>$${p.precio_base.toFixed(2)}</td>
            <td>${p.stock_cantidad}</td>
            <td><span class="badge ${p.disponible ? 'badge-success' : 'badge-danger'}">${p.disponible ? 'Activo' : 'Inactivo'}</span></td>
            <td class="actions-cell">
                <button class="btn btn-sm btn-secondary" onclick="editProducto(${p.id})">Editar</button>
                <button class="btn btn-sm btn-danger" onclick="confirmDelete('producto', ${p.id}, '${p.nombre}')">Eliminar</button>
            </td>
        </tr>`;
    });
    
    html += `</tbody></table></div>`;
    return html;
}

function renderCategoriasTable(data) {
    const categorias = data.data;
    const categoriasMap = {};
    categorias.forEach(c => {
        categoriasMap[c.id] = { ...c, hijos: [] };
    });
    categoriasMap[null] = { id: null, hijos: [] };
    categorias.forEach(c => {
        const padreId = c.parent_id || null;
        if (categoriasMap[padreId]) {
            categoriasMap[padreId].hijos.push(categoriasMap[c.id]);
        }
    });
    
    function renderArbol(cat, nivel = 0) {
        let html = '';
        const paddingLeft = nivel * 20 + 10;
        const tieneHijos = cat.hijos && cat.hijos.length > 0;
        const esPrincipal = cat.es_principal !== undefined ? cat.es_principal : true;
        
        const expandBtn = tieneHijos ? `<button class="tree-expand" onclick="toggleArbol(this)">▶</button>` : '<span class="tree-expand-spacer"></span>';
        
        html += `<div class="tree-item" style="padding-left: ${paddingLeft}px">
            <div class="tree-content">
                ${expandBtn}
                <span class="tree-nombre">${cat.nombre}</span>
                <span class="tree-desc">${cat.descripcion || ''}</span>
                <span class="badge ${esPrincipal ? 'badge-success' : 'badge-danger'}">${esPrincipal ? 'Principal' : 'Secundaria'}</span>
            </div>
            <div class="tree-actions">
                <button class="btn btn-sm btn-secondary" onclick="editCategoria(${cat.id})">Editar</button>
                <button class="btn btn-sm btn-danger" onclick="confirmDelete('categoria', ${cat.id}, '${cat.nombre}')">Eliminar</button>
            </div>
        </div>`;
        
        if (tieneHijos) {
            html += `<div class="tree-hijos" style="display: none;">`;
            for (const hijo of cat.hijos) {
                html += renderArbol(hijo, nivel + 1);
            }
            html += `</div>`;
        }
        
        return html;
    }
    
    let html = `<div class="tree-container">`;
    const raiz = categoriasMap[null];
    for (const cat of raiz.hijos) {
        html += renderArbol(cat, 0);
    }
    
    if (categorias.length === 0) {
        html += `<div class="table-empty">No hay categorías</div>`;
    }
    
    html += `</div>`;
    return html;
}

function renderIngredientesTable(data) {
    let html = `<div class="table-container"><table>
        <thead>
            <tr>
                <th>ID</th>
                <th>Nombre</th>
                <th>Descripción</th>
                <th>Alérgeno</th>
                <th>Acciones</th>
            </tr>
        </thead>
        <tbody>`;
    
    data.data.forEach(i => {
        html += `<tr>
            <td>${i.id}</td>
            <td>${i.nombre}</td>
            <td>${i.descripcion || '-'}</td>
            <td><span class="badge ${i.es_alergeno ? 'badge-danger' : 'badge-success'}">${i.es_alergeno ? 'Sí' : 'No'}</span></td>
            <td class="actions-cell">
                <button class="btn btn-sm btn-secondary" onclick="editIngrediente(${i.id})">Editar</button>
                <button class="btn btn-sm btn-danger" onclick="confirmDelete('ingrediente', ${i.id}, '${i.nombre}')">Eliminar</button>
            </td>
        </tr>`;
    });
    
    html += `</tbody></table></div>`;
    return html;
}

async function loadData() {
    try {
        let data;
        switch (currentView) {
            case 'productos':
                data = await API.productos.getAll();
                renderTable('productos', data);
                break;
            case 'categorias':
                data = await API.categorias.getAll();
                renderTable('categorias', data);
                break;
            case 'ingredientes':
                data = await API.ingredientes.getAll();
                renderTable('ingredientes', data);
                break;
            case 'catalogo':
                await loadCatalogo();
                break;
        }
    } catch (error) {
        showToast(error.message, 'error');
    }
}

async function editProducto(id) {
    try {
        const producto = await API.productos.getById(id);
        document.getElementById('producto-id').value = producto.id;
        document.getElementById('producto-nombre').value = producto.nombre;
        document.getElementById('producto-descripcion').value = producto.descripcion || '';
        document.getElementById('producto-precio').value = producto.precio_base;
        document.getElementById('producto-stock').value = producto.stock_cantidad;
        document.getElementById('producto-imagen').value = producto.imagen_url?.[0] || '';
        document.getElementById('producto-disponible').checked = producto.disponible;
        
        const categorias = await API.categorias.getForSelect();
        const relacionesCategorias = await API.productos.getCategorias();
        const relacionesIngredientes = await API.productos.getIngredientes();
        
        const select = document.getElementById('producto-categoria');
        select.innerHTML = '<option value="">Seleccionar categoría...</option>';
        categorias.data.forEach(c => {
            const option = document.createElement('option');
            option.value = c.id;
            option.textContent = c.nombre;
            select.appendChild(option);
        });
        
        const catsProducto = relacionesCategorias.data.filter(r => r.producto_id === id);
        const catPrincipal = catsProducto.find(r => r.es_principal);
        if (catPrincipal) {
            select.value = catPrincipal.categoria_id;
        }
        
        const catsAdic = document.getElementById('categorias-adicionales');
        catsAdic.innerHTML = '';
        categorias.data.forEach(c => {
            const isChecked = catsProducto.some(r => r.categoria_id === c.id && !r.es_principal);
            catsAdic.innerHTML += `<div class="checkbox-item">
                <input type="checkbox" id="cat-adic-${c.id}" value="${c.id}" ${isChecked ? 'checked' : ''}>
                <label for="cat-adic-${c.id}">${c.nombre}</label>
            </div>`;
        });
        
        const ingredientes = await API.ingredientes.getAll(0, 100);
        const ingProducto = relacionesIngredientes.data.filter(r => r.producto_id === id);
        const ingDisp = document.getElementById('ingredientes-disponibles');
        ingDisp.innerHTML = '';
        ingredientes.data.forEach(i => {
            const isChecked = ingProducto.some(r => r.ingrediente_id === i.id);
            ingDisp.innerHTML += `<div class="checkbox-item">
                <input type="checkbox" id="ing-${i.id}" value="${i.id}" ${isChecked ? 'checked' : ''}>
                <label for="ing-${i.id}">${i.nombre}</label>
            </div>`;
        });
        
        document.getElementById('modal-producto-title').textContent = `Editar Producto: ${producto.nombre}`;
        openModal('modal-producto');
    } catch (error) {
        showToast(error.message, 'error');
    }
}

async function editCategoria(id) {
    try {
        const categoria = await API.categorias.getById(id);
        document.getElementById('categoria-id').value = categoria.id;
        document.getElementById('categoria-nombre').value = categoria.nombre;
        document.getElementById('categoria-descripcion').value = categoria.descripcion || '';
        document.getElementById('categoria-padre').value = categoria.parent_id || '';
        document.getElementById('categoria-principal').checked = categoria.es_principal !== undefined ? categoria.es_principal : true;
        document.getElementById('modal-categoria-title').textContent = `Editar Categoría: ${categoria.nombre}`;
        
        const categorias = await API.categorias.getForSelect();
        const select = document.getElementById('categoria-padre');
        select.innerHTML = '<option value="">Ninguna</option>';
        categorias.data.forEach(c => {
            if (c.id !== categoria.id) {
                const option = document.createElement('option');
                option.value = c.id;
                option.textContent = c.nombre;
                select.appendChild(option);
            }
        });
        select.value = categoria.parent_id || '';
        
        openModal('modal-categoria');
    } catch (error) {
        showToast(error.message, 'error');
    }
}

async function editIngrediente(id) {
    try {
        const ingrediente = await API.ingredientes.getById(id);
        document.getElementById('ingrediente-id').value = ingrediente.id;
        document.getElementById('ingrediente-nombre').value = ingrediente.nombre;
        document.getElementById('ingrediente-descripcion').value = ingrediente.descripcion || '';
        document.getElementById('ingrediente-precio').value = 0;
        document.getElementById('ingrediente-disponible').checked = true;
        document.getElementById('modal-ingrediente-title').textContent = `Editar Ingrediente: ${ingrediente.nombre}`;
        openModal('modal-ingrediente');
    } catch (error) {
        showToast(error.message, 'error');
    }
}

function confirmDelete(type, id, name) {
    const typeLabels = { producto: 'producto', categoria: 'categoría', ingrediente: 'ingrediente' };
    document.getElementById('mensaje-eliminar').textContent = `¿Estás seguro de eliminar el ${typeLabels[type]} "${name}"?`;
    deleteTarget = { type, id };
    openModal('modal-confirmar');
}

async function executeDelete() {
    if (!deleteTarget) return;
    
    try {
        switch (deleteTarget.type) {
            case 'producto':
                await API.productos.delete(deleteTarget.id);
                break;
            case 'categoria':
                await API.categorias.delete(deleteTarget.id);
                break;
            case 'ingrediente':
                await API.ingredientes.delete(deleteTarget.id);
                break;
        }
        showToast('Eliminado correctamente');
        closeAllModals();
        loadData();
    } catch (error) {
        showToast(error.message, 'error');
    }
    deleteTarget = null;
}

async function populateCategoriaSelect() {
    try {
        const categorias = await API.categorias.getForSelect();
        const select = document.getElementById('categoria-padre');
        select.innerHTML = '<option value="">Ninguna</option>';
        categorias.data.forEach(c => {
            const option = document.createElement('option');
            option.value = c.id;
            option.textContent = c.nombre;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error cargando categorías:', error);
    }
}

async function populateProductoCategoriaSelect() {
    try {
        const categorias = await API.categorias.getForSelect();
        const select = document.getElementById('producto-categoria');
        select.innerHTML = '<option value="">Seleccionar categoría...</option>';
        categorias.data.forEach(c => {
            const option = document.createElement('option');
            option.value = c.id;
            option.textContent = c.nombre;
            select.appendChild(option);
        });
        
        const catsAdic = document.getElementById('categorias-adicionales');
        catsAdic.innerHTML = '';
        categorias.data.forEach(c => {
            catsAdic.innerHTML += `<div class="checkbox-item">
                <input type="checkbox" id="cat-adic-${c.id}" value="${c.id}">
                <label for="cat-adic-${c.id}">${c.nombre}</label>
            </div>`;
        });
        
        const ingredientes = await API.ingredientes.getAll(0, 100);
        const ingDisp = document.getElementById('ingredientes-disponibles');
        ingDisp.innerHTML = '';
        ingredientes.data.forEach(i => {
            ingDisp.innerHTML += `<div class="checkbox-item">
                <input type="checkbox" id="ing-${i.id}" value="${i.id}">
                <label for="ing-${i.id}">${i.nombre}</label>
            </div>`;
        });
    } catch (error) {
        console.error('Error cargando categorías/ingredientes:', error);
    }
}

async function loadCatalogo() {
    try {
        const productos = await API.productos.getAll(0, 100);
        const categorias = await API.categorias.getAll(0, 100);
        const relacionesCategorias = await API.productos.getCategorias();
        const relacionesIngredientes = await API.productos.getIngredientes();
        
        const select = document.getElementById('filtro-categoria');
        select.innerHTML = '<option value="">Todas las categorías</option>';
        categorias.data.forEach(c => {
            const option = document.createElement('option');
            option.value = c.id;
            option.textContent = c.nombre;
            select.appendChild(option);
        });
        
        renderCatalogo(productos, categorias, relacionesCategorias, relacionesIngredientes);
    } catch (error) {
        console.error('Error cargando catálogo:', error);
    }
}

function renderCatalogo(productos, categorias, relacionesCategorias, relacionesIngredientes) {
    const container = document.getElementById('catalogo-grid');
    const filtroCategoria = document.getElementById('filtro-categoria').value;
    
    let productosFiltrados = productos.data;
    
    if (filtroCategoria) {
        const idsProductos = relacionesCategorias.data
            .filter(r => r.categoria_id === parseInt(filtroCategoria))
            .map(r => r.producto_id);
        productosFiltrados = productos.data.filter(p => idsProductos.includes(p.id));
    }
    
    if (productosFiltrados.length === 0) {
        container.innerHTML = '<div class="table-empty">No hay productos en el catálogo</div>';
        return;
    }
    
    const PLACEHOLDER_SIN_IMAGEN = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMzAwIiBoZWlnaHQ9IjIwMCIgZmlsbD0iI2YzZjRmNiIvPjx0ZXh0IHg9IjE1MCIgeT0iMTAwIiBmb250LXNpemU9IjIwIiBmaWxsPSIjOTk5IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkeT0iLjNlbSI+U2luIEltYWdlbjwvdGV4dD48L3N2Zz4=';
    
    let html = '<div class="catalogo-grid">';
    
    productosFiltrados.forEach(p => {
        const imgUrl = p.imagen_url && p.imagen_url.length > 0 
            ? p.imagen_url[0] 
            : PLACEHOLDER_SIN_IMAGEN;
        
        const catsIds = relacionesCategorias.data
            .filter(r => r.producto_id === p.id)
            .map(r => r.categoria_id);
        
        const catsNombres = catsIds.map(catId => {
            const cat = categorias.data.find(c => c.id === catId);
            return cat ? cat.nombre : `Cat ${catId}`;
        }).join(', ');
        
        const ingIds = relacionesIngredientes.data
            .filter(r => r.producto_id === p.id)
            .map(r => r.ingrediente_id);
        
        html += `<div class="catalogo-card">
            <img src="${imgUrl}" alt="${p.nombre}" class="catalogo-img" onerror="this.src='${PLACEHOLDER_SIN_IMAGEN}'">
            <div class="catalogo-content">
                <h3>${p.nombre}</h3>
                <p class="catalogo-desc">${p.descripcion || 'Sin descripción'}</p>
                <p class="catalogo-precio">$${p.precio_base.toFixed(2)}</p>
                <div class="catalogo-tags">
                    <span class="catalogo-cat">${catsNombres || 'Sin categoría'}</span>
                    ${ingIds.length > 0 ? `<span class="catalogo-ing">${ingIds.length} ingrediente(s)</span>` : ''}
                </div>
            </div>
        </div>`;
    });
    
    html += '</div>';
    container.innerHTML = html;
}

function toggleArbol(btn) {
    const treeItem = btn.closest('.tree-item');
    const hijos = treeItem.nextElementSibling;
    if (hijos && hijos.classList.contains('tree-hijos')) {
        if (hijos.style.display === 'none') {
            hijos.style.display = 'block';
            btn.textContent = '▼';
            btn.classList.add('expanded');
        } else {
            hijos.style.display = 'none';
            btn.textContent = '▶';
            btn.classList.remove('expanded');
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.addEventListener('click', () => switchView(btn.dataset.view));
    });
    
    document.getElementById('btn-crear-producto').addEventListener('click', async () => {
        document.getElementById('form-producto').reset();
        document.getElementById('producto-id').value = '';
        document.getElementById('modal-producto-title').textContent = 'Nuevo Producto';
        await populateProductoCategoriaSelect();
        openModal('modal-producto');
    });
    
    document.getElementById('btn-crear-categoria').addEventListener('click', async () => {
        document.getElementById('form-categoria').reset();
        document.getElementById('categoria-id').value = '';
        document.getElementById('modal-categoria-title').textContent = 'Nueva Categoría';
        await populateCategoriaSelect();
        openModal('modal-categoria');
    });
    
    document.getElementById('btn-crear-ingrediente').addEventListener('click', () => {
        document.getElementById('form-ingrediente').reset();
        document.getElementById('ingrediente-id').value = '';
        document.getElementById('modal-ingrediente-title').textContent = 'Nuevo Ingrediente';
        openModal('modal-ingrediente');
    });
    
    document.querySelectorAll('.modal-close, .modal-cancel').forEach(btn => {
        btn.addEventListener('click', closeAllModals);
    });
    
    document.getElementById('modal-confirmar').addEventListener('click', (e) => {
        if (e.target.id === 'modal-confirmar') closeAllModals();
    });
    
    document.getElementById('btn-confirmar-eliminar').addEventListener('click', executeDelete);
    
    document.getElementById('btn-clear-debug').addEventListener('click', () => {
        debugLogs = [];
        renderDebug();
    });
    
    document.getElementById('form-producto').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const categoriaPrincipalId = document.getElementById('producto-categoria').value;
        if (!categoriaPrincipalId) {
            showToast('Debe seleccionar una categoría principal', 'error');
            return;
        }
        
        const id = document.getElementById('producto-id').value;
        const data = {
            nombre: document.getElementById('producto-nombre').value,
            descripcion: document.getElementById('producto-descripcion').value || null,
            precio_base: parseFloat(document.getElementById('producto-precio').value),
            stock_cantidad: parseInt(document.getElementById('producto-stock').value) || 0,
            imagen_url: document.getElementById('producto-imagen').value ? [document.getElementById('producto-imagen').value] : [],
            disponible: document.getElementById('producto-disponible').checked,
        };
        
        const catsAdicionales = [];
        document.querySelectorAll('#categorias-adicionales input[type="checkbox"]:checked').forEach(cb => {
            if (cb.value !== categoriaPrincipalId) {
                catsAdicionales.push(parseInt(cb.value));
            }
        });
        
        const ingredientes = [];
        document.querySelectorAll('#ingredientes-disponibles input[type="checkbox"]:checked').forEach(cb => {
            ingredientes.push(parseInt(cb.value));
        });
        
        try {
            let productoId;
            if (id) {
                await API.productos.update(id, data);
                productoId = id;
                showToast('Producto actualizado');
                
                await API.productos.eliminarCategorias(productoId);
                await API.productos.asignarCategoria(productoId, parseInt(categoriaPrincipalId), true);
                for (const catId of catsAdicionales) {
                    await API.productos.asignarCategoria(productoId, catId, false);
                }
                
                await API.productos.eliminarIngredientes(productoId);
                for (const ingId of ingredientes) {
                    await API.productos.asignarIngrediente(productoId, ingId, false);
                }
            } else {
                const result = await API.productos.create(data);
                productoId = result.id;
                showToast('Producto creado');
                
                await API.productos.asignarCategoria(productoId, parseInt(categoriaPrincipalId), true);
                for (const catId of catsAdicionales) {
                    await API.productos.asignarCategoria(productoId, catId, false);
                }
                for (const ingId of ingredientes) {
                    await API.productos.asignarIngrediente(productoId, ingId, false);
                }
            }
            
            closeAllModals();
            loadData();
        } catch (error) {
            showToast(error.message, 'error');
        }
    });
    
    document.getElementById('form-categoria').addEventListener('submit', async (e) => {
        e.preventDefault();
        const id = document.getElementById('categoria-id').value;
        const data = {
            nombre: document.getElementById('categoria-nombre').value,
            descripcion: document.getElementById('categoria-descripcion').value || null,
            parent_id: document.getElementById('categoria-padre').value ? parseInt(document.getElementById('categoria-padre').value) : null,
            es_principal: document.getElementById('categoria-principal').checked,
        };
        
        try {
            if (id) {
                await API.categorias.update(id, data);
                showToast('Categoría actualizada');
            } else {
                await API.categorias.create(data);
                showToast('Categoría creada');
            }
            closeAllModals();
            loadData();
        } catch (error) {
            showToast(error.message, 'error');
        }
    });
    
    document.getElementById('form-ingrediente').addEventListener('submit', async (e) => {
        e.preventDefault();
        const id = document.getElementById('ingrediente-id').value;
        const data = {
            nombre: document.getElementById('ingrediente-nombre').value,
            descripcion: document.getElementById('ingrediente-descripcion').value || null,
            es_alergeno: false,
        };
        
        try {
            if (id) {
                await API.ingredientes.update(id, data);
                showToast('Ingrediente actualizado');
            } else {
                await API.ingredientes.create(data);
                showToast('Ingrediente creado');
            }
            closeAllModals();
            loadData();
        } catch (error) {
            showToast(error.message, 'error');
        }
    });
    
    document.getElementById('filtro-categoria').addEventListener('change', () => {
        if (currentView === 'catalogo') {
            loadCatalogo();
        }
    });
    
    document.getElementById('switch-dark-mode').addEventListener('change', (e) => {
        document.body.classList.toggle('dark-mode', e.target.checked);
    });
    
    debugLog('info', 'Aplicación iniciada');
    loadData();
});