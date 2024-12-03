// Función para mostrar alertas - evita redefinición
if (typeof showAlert === 'undefined') {
    function showAlert(message, type = 'success') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        const container = document.querySelector('.container');
        container.insertBefore(alertDiv, container.firstChild);
        
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }
}




const formatCurrency = (amount) => {
    return new Intl.NumberFormat('es-MX', {
        style: 'currency',
        currency: 'MXN'
    }).format(amount);
};

// Validación del formulario
function validarFormulario() {
    try {
        const nombre = document.getElementById('nombre_usuario').value.trim();
        const email = document.getElementById('email_usuario').value.trim();
        const telefono = document.getElementById('telefono_usuario').value.trim();
        const direccion = document.getElementById('direccion_usuario').value.trim();
        
        
        
        if (!nombre || !email || !telefono || !direccion) {
            throw new Error('No se encontraron todos los campos del formulario');
        }
        
        const errores = [];
        
        if (nombre.value.trim().length < 2) {
            errores.push('El nombre debe tener al menos 2 caracteres');
        }
        
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email.value.trim())) {
            errores.push('Por favor ingrese un email válido');
        }
        
        const telefonoRegex = /^\+?[0-9]{8,15}$/;
        if (!telefonoRegex.test(telefono.value.trim())) {
            errores.push('El teléfono debe tener entre 8 y 15 dígitos');
        }
        
        if (direccion.value.trim().length < 5) {
            errores.push('La dirección debe tener al menos 5 caracteres');
        }
        
        return errores;
    } catch (error) {
        console.error('Error en validación:', error);
        return ['Error en la validación del formulario'];
    }
}
// Función para guardar usuario
async function guardarUsuario() {
    try {
        const errores = validarFormulario();
        if (errores.length > 0) {
            showAlert(errores.join('<br>'), 'danger');
            return;
        }

        const usuarioId = document.getElementById('usuario_id').value;
        
        const data = {
            nombre: document.getElementById('nombre_usuario').value.trim(),
            email: document.getElementById('email_usuario').value.trim(),
            direccion: document.getElementById('direccion_usuario').value.trim(),
            telefono: document.getElementById('telefono_usuario').value.trim()
        };

        // Mostrar loading
        const saveButton = document.querySelector('#usuarioModal .btn-primary');
        const originalText = saveButton.innerHTML;
        saveButton.disabled = true;
        saveButton.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Guardando...';

        const url = usuarioId ? `/usuarios/${usuarioId}` : '/usuarios';
        const method = usuarioId ? 'PUT' : 'POST';

        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });

        const responseData = await response.json();

        if (!response.ok) {
            throw new Error(responseData.error || 'Error al guardar usuario');
        }

        showAlert(responseData.mensaje || 'Usuario guardado exitosamente', 'success');
        
        // Cerrar el modal y recargar
        const modal = bootstrap.Modal.getInstance(document.getElementById('usuarioModal'));
        modal.hide();
        
        setTimeout(() => {
            window.location.reload();
        }, 1000);

    } catch (error) {
        console.error('Error:', error);
        showAlert(error.message || 'Error al guardar usuario', 'danger');
    } finally {
        const saveButton = document.querySelector('#usuarioModal .btn-primary');
        if (saveButton) {
            saveButton.disabled = false;
            saveButton.innerHTML = '<i class="fas fa-save me-2"></i>Guardar';
        }
    }
}
// Inicialización cuando el DOM está listo
document.addEventListener('DOMContentLoaded', () => {
    // Inicializar el formulario
    const usuarioForm = document.getElementById('usuarioForm');
    if (usuarioForm) {
        usuarioForm.addEventListener('submit', guardarUsuario);
    }

    // Inicializar el modal
    const usuarioModal = document.getElementById('usuarioModal');
    if (usuarioModal) {
        usuarioModal.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            if (!button || !button.getAttribute('data-edit')) {
                document.getElementById('usuarioForm').reset();
                document.getElementById('usuario_id').value = '';
                document.getElementById('modalTitle').textContent = 'Nuevo Usuario';
                document.getElementById('estadoContainer').style.display = 'none';
            }
        });

        usuarioModal.addEventListener('hidden.bs.modal', function () {
            document.getElementById('usuarioForm').reset();
            document.getElementById('usuario_id').value = '';
        });
    }

    // Inicializar tooltips
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltips.forEach(tooltip => new bootstrap.Tooltip(tooltip));

    // Inicializar DataTable
    const usuariosTable = document.getElementById('usuariosTable');
    if (usuariosTable && typeof $.fn.DataTable !== 'undefined') {
        initializeDataTable();
    }
});

// Resto del código actual se mantiene igual...
// (incluye las funciones editarUsuario, eliminarUsuario, verUsuario, etc.)
const eliminarUsuario = async (id) => {
    if (!confirmDelete('¿Está seguro de que desea eliminar este usuario? Esta acción no se puede deshacer.')) {
        return;
    }

    try {
        const response = await fetch(`/usuarios/${id}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Error al eliminar usuario');
        }
        
        showAlert(data.mensaje, 'success');
        window.location.reload();
        
    } catch (error) {
        showAlert(error.message, 'danger');
        console.error('Error:', error);
    }
};

const verUsuario = async (id) => {
    try {
        const response = await fetch(`/usuarios/${id}`);
        if (!response.ok) {
            throw new Error('Error al cargar usuario');
        }
        
        const usuario = await response.json();
        
        // Información básica
        document.getElementById('detalle-nombre').textContent = usuario.nombre;
        document.getElementById('detalle-email').textContent = usuario.email;
        document.getElementById('detalle-direccion').textContent = usuario.direccion;
        document.getElementById('detalle-telefono').textContent = usuario.telefono;
        
        // Estado
        const estado = document.getElementById('detalle-estado');
        estado.textContent = usuario.activo ? 'Activo' : 'Inactivo';
        estado.className = `badge ${usuario.activo ? 'bg-success' : 'bg-danger'}`;
        
        // Estadísticas
        document.getElementById('detalle-total-prestamos').textContent = usuario.estadisticas.total_prestamos;
        document.getElementById('detalle-prestamos-activos').textContent = usuario.estadisticas.prestamos_activos;
        document.getElementById('detalle-total-resenas').textContent = usuario.estadisticas.total_resenas;
        document.getElementById('detalle-multas').textContent = formatCurrency(usuario.estadisticas.multas_pendientes);
        
        const modal = new bootstrap.Modal(document.getElementById('detallesModal'));
        modal.show();
        
    } catch (error) {
        showAlert(error.message, 'danger');
        console.error('Error:', error);
    }
};

const verPrestamos = async (id) => {
    try {
        const response = await fetch(`/usuarios/${id}/prestamos`);
        if (!response.ok) {
            throw new Error('Error al cargar préstamos');
        }
        
        const data = await response.json();
        
        // Cargar préstamos activos
        const activosBody = document.getElementById('prestamos-activos-body');
        activosBody.innerHTML = '';
        
        data.prestamos
            .filter(p => p.estado === 'ACTIVO')
            .forEach(prestamo => {
                activosBody.innerHTML += `
                    <tr>
                        <td>${prestamo.libro_titulo}</td>
                        <td>${formatDate(prestamo.fechaPrestamo)}</td>
                        <td>${formatDate(prestamo.fechaDevolucion)}</td>
                        <td>
                            <span class="badge bg-primary">Activo</span>
                        </td>
                        <td>
                            <button class="btn btn-sm btn-success" onclick="registrarDevolucion('${prestamo._id}')">
                                <i class="fas fa-check"></i> Devolver
                            </button>
                        </td>
                    </tr>
                `;
            });
        
        // Cargar historial
        const historialBody = document.getElementById('historial-prestamos-body');
        historialBody.innerHTML = '';
        
        data.prestamos
            .filter(p => p.estado === 'DEVUELTO')
            .forEach(prestamo => {
                historialBody.innerHTML += `
                    <tr>
                        <td>${prestamo.libro_titulo}</td>
                        <td>${formatDate(prestamo.fechaPrestamo)}</td>
                        <td>${formatDate(prestamo.fechaDevolucion)}</td>
                        <td>${formatDate(prestamo.fechaDevuelto)}</td>
                        <td>${prestamo.multa ? formatCurrency(prestamo.multa) : '-'}</td>
                    </tr>
                `;
            });
        
        const modal = new bootstrap.Modal(document.getElementById('prestamosModal'));
        modal.show();
        
    } catch (error) {
        showAlert(error.message, 'danger');
        console.error('Error:', error);
    }
};

const verMultas = async (id) => {
    try {
        const response = await fetch(`/usuarios/${id}/multas`);
        if (!response.ok) {
            throw new Error('Error al cargar multas');
        }
        
        const data = await response.json();
        
        // Actualizar tabla de multas
        const multasBody = document.getElementById('multas-body');
        multasBody.innerHTML = '';
        
        data.multas.forEach(multa => {
            multasBody.innerHTML += `
                <tr>
                    <td>${multa.libro_titulo}</td>
                    <td>${formatDate(multa.fecha_devolucion)}</td>
                    <td>${multa.dias_retraso}</td>
                    <td>${formatCurrency(multa.multa)}</td>
                </tr>
            `;
        });
        
        // Actualizar total
        document.getElementById('multas-total').textContent = formatCurrency(data.total_multa);
        
        const modal = new bootstrap.Modal(document.getElementById('multasModal'));
        modal.show();
        
    } catch (error) {
        showAlert(error.message, 'danger');
        console.error('Error:', error);
    }
};

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    // Formulario de búsqueda
    const searchForm = document.getElementById('searchForm');
    if (searchForm) {
        searchForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(searchForm);
            const params = new URLSearchParams();
            
            for (let [key, value] of formData.entries()) {
                if (value) {
                    params.append(key, value);
                }
            }
            
            try {
                const response = await fetch(`/usuarios/buscar?${params.toString()}`);
                if (!response.ok) {
                    throw new Error('Error en la búsqueda');
                }
                
                const data = await response.json();
                actualizarTablaUsuarios(data.usuarios);
                
            } catch (error) {
                showAlert(error.message, 'danger');
                console.error('Error:', error);
            }
        });

        searchForm.addEventListener('reset', () => {
            window.location.reload();
        });
    }

    // Modal de usuario
    const usuarioModal = document.getElementById('usuarioModal');
    if (usuarioModal) {
        usuarioModal.addEventListener('show.bs.modal', function (event) {
            if (!event.relatedTarget || !event.relatedTarget.getAttribute('data-edit')) {
                document.getElementById('usuarioForm').reset();
                document.getElementById('usuario_id').value = '';
                document.getElementById('modalTitle').textContent = 'Nuevo Usuario';
                document.getElementById('estadoContainer').style.display = 'none';
            }
        });

        usuarioModal.addEventListener('hidden.bs.modal', function () {
            document.getElementById('usuarioForm').reset();
            document.getElementById('usuario_id').value = '';
        });
    }

    // Inicializar DataTable si está presente
    const usuariosTable = document.getElementById('usuariosTable');
    if (usuariosTable && $.fn.DataTable) {
        const table = $(usuariosTable).DataTable({
            language: {
                url: '//cdn.datatables.net/plug-ins/1.10.24/i18n/Spanish.json'
            },
            pageLength: 10,
            responsive: true,
            dom: 'Bfrtip',
            buttons: [
                {
                    extend: 'collection',
                    text: 'Exportar',
                    buttons: ['copy', 'excel', 'pdf']
                }
            ],
            order: [[0, 'asc']]
        });

        // Refresh DataTable después de búsqueda
        searchForm.addEventListener('submit', () => {
            table.draw();
        });
    }
});

// Función auxiliar para actualizar la tabla
const actualizarTablaUsuarios = (usuarios) => {
    const tbody = document.querySelector('#usuariosTable tbody');
    tbody.innerHTML = '';
    
    usuarios.forEach(usuario => {
        tbody.innerHTML += `
            <tr>
                <td>${usuario.nombre}</td>
                <td>${usuario.email}</td>
                <td>${usuario.telefono}</td>
                <td>
                    <span class="badge bg-info">${usuario.prestamos_activos}</span>
                </td>
                <td>
                    <span class="badge ${usuario.activo ? 'bg-success' : 'bg-danger'}">
                        ${usuario.activo ? 'Activo' : 'Inactivo'}
                    </span>
                </td>
                <td>
                    <div class="btn-group">
                        <button class="btn btn-sm btn-info" onclick="verUsuario('${usuario._id}')" title="Ver detalles">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-sm btn-primary" onclick="editarUsuario('${usuario._id}')" title="Editar">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-warning" onclick="verPrestamos('${usuario._id}')" title="Ver préstamos">
                            <i class="fas fa-book-reader"></i>
                        </button>
                        <button class="btn btn-sm btn-info" onclick="verMultas('${usuario._id}')" title="Ver multas">
                            <i class="fas fa-dollar-sign"></i>
                        </button>
                        ${usuario.prestamos_activos === 0 ? 
                            `<button class="btn btn-sm btn-danger" onclick="eliminarUsuario('${usuario._id}')" title="Eliminar">
                                <i class="fas fa-trash"></i>
                            </button>` : 
                            `<button class="btn btn-sm btn-danger" disabled title="No se puede eliminar usuario con préstamos activos">
                                <i class="fas fa-trash"></i>
                            </button>`
                        }
                    </div>
                </td>
            </tr>
        `;
    });

    // Si estamos usando DataTable, refrescar la tabla
    if ($.fn.DataTable.isDataTable('#usuariosTable')) {
        $('#usuariosTable').DataTable().destroy();
        initializeDataTable();
    }
};
function editarUsuario(id) {
    fetch(`/usuarios/${id}`)
        .then(response => response.json())
        .then(usuario => {
            document.getElementById('usuario_id').value = usuario._id;
            document.getElementById('nombreUsuario').value = usuario.nombre;
            document.getElementById('emailUsuario').value = usuario.email;
            document.getElementById('direccionUsuario').value = usuario.direccion;
            document.getElementById('telefonoUsuario').value = usuario.telefono;
            
            // Mostrar campo de estado en edición
            document.getElementById('estadoContainer').style.display = 'block';
            document.getElementById('activoUsuario').value = usuario.activo;
            
            document.getElementById('modalTitle').textContent = 'Editar Usuario';
            const modal = new bootstrap.Modal(document.getElementById('usuarioModal'));
            modal.show();
        })
        .catch(error => {
            showAlert('Error al cargar usuario', 'danger');
            console.error('Error:', error);
        });
}
// Función para registrar devolución de préstamo
const registrarDevolucion = async (prestamoId) => {
    if (!confirmDelete('¿Confirma la devolución del libro?')) {
        return;
    }

    try {
        const response = await fetch(`/prestamos/${prestamoId}/devolver`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.error || 'Error al registrar devolución');
        }

        const data = await response.json();
        showAlert(data.mensaje, 'success');
        
        // Recargar modal de préstamos
        const usuarioId = document.querySelector('[data-usuario-id]').dataset.usuarioId;
        await verPrestamos(usuarioId);

    } catch (error) {
        showAlert(error.message, 'danger');
        console.error('Error:', error);
    }
};

function initializeDataTable() {
    const table = $('#usuariosTable');
    
    // Destruir la tabla si ya está inicializada
    if ($.fn.DataTable.isDataTable(table)) {
        table.DataTable().destroy();
    }
    
    table.DataTable({
        language: {
            url: '//cdn.datatables.net/plug-ins/1.10.24/i18n/Spanish.json'
        },
        responsive: true,
        pageLength: 10,
        dom: 'Bfrtip',
        buttons: [
            {
                extend: 'collection',
                text: '<span>Exportar</span>',
                buttons: [
                    {
                        extend: 'copy',
                        text: '<span>Copiar</span>',
                        className: 'btn btn-primary',
                        exportOptions: {
                            columns: [0, 1, 2, 3, 4]
                        }
                    },
                    {
                        extend: 'excel',
                        text: '<span>Excel</span>',
                        className: 'btn btn-success',
                        exportOptions: {
                            columns: [0, 1, 2, 3, 4]
                        }
                    },
                    {
                        extend: 'pdf',
                        text: '<span>PDF</span>',
                        className: 'btn btn-danger',
                        exportOptions: {
                            columns: [0, 1, 2, 3, 4]
                        }
                    }
                ],
                className: 'btn btn-secondary'
            }
        ],
        order: [[0, 'asc']],
        columnDefs: [
            {
                targets: -1,
                orderable: false
            }
        ]
    });
}

// Función para manejar la paginación
const manejarPaginacion = (pagina) => {
    const searchParams = new URLSearchParams(window.location.search);
    searchParams.set('page', pagina);
    window.location.search = searchParams.toString();
};

// Función para exportar datos
const exportarDatos = async (formato) => {
    try {
        const response = await fetch('/usuarios/exportar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ formato })
        });

        if (!response.ok) {
            throw new Error('Error al exportar datos');
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `usuarios_${new Date().toISOString().split('T')[0]}.${formato}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        a.remove();

    } catch (error) {
        showAlert(error.message, 'danger');
        console.error('Error:', error);
    }
};

// Inicialización al cargar la página
document.addEventListener('DOMContentLoaded', () => {
    // Inicializar tooltips de Bootstrap
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));

    // Inicializar DataTable si existe la tabla
    const usuariosTable = document.getElementById('usuariosTable');
    if (usuariosTable) {
        initializeDataTable();
    }
});