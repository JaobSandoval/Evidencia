// prestamos.js
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar elementos del formulario
    initializeFormElements();
    
    // Inicializar eventos
    initializeEventListeners();
});

// Inicialización de elementos del formulario
function initializeFormElements() {
    // Inicializar fecha actual
    const fechaPrestamo = document.getElementById('fecha_prestamo');
    if (fechaPrestamo) {
        const today = new Date().toISOString().split('T')[0];
        fechaPrestamo.value = today;
        fechaPrestamo.min = today;
    }

    // Inicializar select de días de préstamo
    const diasPrestamo = document.getElementById('dias_prestamo');
    if (diasPrestamo) {
        actualizarFechaDevolucion();
    }
}

// Inicialización de event listeners
function initializeEventListeners() {
    // Event listener para el formulario de préstamo
    const prestamoForm = document.getElementById('prestamoForm');
    if (prestamoForm) {
        prestamoForm.addEventListener('submit', function(e) {
            e.preventDefault();
            guardarPrestamo();
        });
    }

    // Event listener para días de préstamo
    const diasPrestamo = document.getElementById('dias_prestamo');
    if (diasPrestamo) {
        diasPrestamo.addEventListener('change', actualizarFechaDevolucion);
    }

    // Event listener para cerrar modal
    const prestamoModal = document.getElementById('prestamoModal');
    if (prestamoModal) {
        prestamoModal.addEventListener('hidden.bs.modal', function() {
            resetForm();
        });
    }

    // Event listeners para selects
    const usuarioSelect = document.getElementById('usuario_id');
    const libroSelect = document.getElementById('libro_id');

    if (usuarioSelect) {
        usuarioSelect.addEventListener('change', validarSeleccion);
    }

    if (libroSelect) {
        libroSelect.addEventListener('change', validarSeleccion);
    }
}

// Función para guardar préstamo
function guardarPrestamo() {
    // Obtener los valores del formulario
    const usuario_id = document.getElementById('usuario_id').value.trim();
    const libro_id = document.getElementById('libro_id').value.trim();
    const dias_prestamo = document.getElementById('dias_prestamo').value;

    // Debug: Imprimir valores
    console.log('Valores del formulario:', {
        usuario_id,
        libro_id,
        dias_prestamo
    });

    // Validaciones
    if (!usuario_id || usuario_id === '') {
        mostrarWarning('Debe seleccionar un usuario');
        return;
    }

    if (!libro_id || libro_id === '') {
        mostrarWarning('Debe seleccionar un libro');
        return;
    }

    if (!dias_prestamo) {
        mostrarWarning('Debe seleccionar los días de préstamo');
        return;
    }

    // Crear objeto de datos
    const data = {
        usuario_id: usuario_id,
        libro_id: libro_id,
        dias_prestamo: parseInt(dias_prestamo)
    };

    // Realizar la petición
    fetch('/prestamos/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            mostrarWarning(data.error);
        } else {
            showAlert('Préstamo registrado exitosamente', 'success');
            setTimeout(() => {
                window.location.reload();
            }, 1500);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('Error al registrar el préstamo', 'danger');
    });
}

// Función para mostrar warnings en el formulario
function mostrarWarning(mensaje) {
    const warningsDiv = document.getElementById('warnings');
    if (warningsDiv) {
        warningsDiv.innerHTML = mensaje;
        warningsDiv.style.display = 'block';
        setTimeout(() => {
            warningsDiv.style.display = 'none';
        }, 3000);
    }
}

// Función para mostrar alertas generales
function showAlert(message, type = 'success') {
    const alertsContainer = document.getElementById('alerts-container') || createAlertsContainer();
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.role = 'alert';
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;

    alertsContainer.appendChild(alert);
    setTimeout(() => alert.remove(), 3000);
}

function createAlertsContainer() {
    const container = document.createElement('div');
    container.id = 'alerts-container';
    container.style.position = 'fixed';
    container.style.top = '20px';
    container.style.right = '20px';
    container.style.zIndex = '1050';
    document.body.appendChild(container);
    return container;
}

// Inicialización cuando el DOM está listo
document.addEventListener('DOMContentLoaded', function() {
    // Debug: Verificar selects
    const usuarioSelect = document.getElementById('usuario_id');
    const libroSelect = document.getElementById('libro_id');

    console.log('Estado inicial de selects:', {
        usuarioSelect: usuarioSelect ? {
            value: usuarioSelect.value,
            options: Array.from(usuarioSelect.options).map(o => ({value: o.value, text: o.text}))
        } : null,
        libroSelect: libroSelect ? {
            value: libroSelect.value,
            options: Array.from(libroSelect.options).map(o => ({value: o.value, text: o.text}))
        } : null
    });

    // Prevenir envío del formulario
    const form = document.getElementById('prestamoForm');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
        });
    }
});
// Función para registrar devolución
function registrarDevolucion(id) {
    if (!confirm('¿Está seguro de registrar la devolución?')) return;

    fetch(`/prestamos/${id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            estado: 'DEVUELTO',
            fechaDevuelto: new Date().toISOString()
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showAlert(data.error, 'danger');
        } else {
            showAlert('Devolución registrada exitosamente', 'success');
            setTimeout(() => window.location.reload(), 1500);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('Error al registrar la devolución', 'danger');
    });
}

// Función para actualizar la fecha de devolución
function actualizarFechaDevolucion() {
    const fechaPrestamo = new Date(document.getElementById('fecha_prestamo').value);
    const diasPrestamo = parseInt(document.getElementById('dias_prestamo').value);
    
    if (!isNaN(fechaPrestamo.getTime()) && !isNaN(diasPrestamo)) {
        const fechaDevolucion = new Date(fechaPrestamo);
        fechaDevolucion.setDate(fechaDevolucion.getDate() + diasPrestamo);
        
        const infoDiv = document.getElementById('fecha-devolucion-info');
        if (infoDiv) {
            infoDiv.textContent = `Fecha de devolución: ${fechaDevolucion.toLocaleDateString()}`;
            infoDiv.classList.remove('text-danger');
        }
    }
}

// Función para validar el formulario
function validarFormulario() {
    const campos = ['usuario_id', 'libro_id', 'dias_prestamo'];
    const warnings = [];

    campos.forEach(campo => {
        const elemento = document.getElementById(campo);
        if (!elemento || !elemento.value) {
            warnings.push(`El campo ${campo.replace('_', ' ')} es requerido`);
        }
    });

    if (warnings.length > 0) {
        showAlert(warnings.join('<br>'), 'danger');
        return false;
    }

    return true;
}

// Función para validar selección
function validarSeleccion() {
    const warningsDiv = document.getElementById('warnings');
    warningsDiv.style.display = 'none';
    warningsDiv.innerHTML = '';
}

// Función para mostrar alertas
function showAlert(message, type = 'success') {
    const alertsContainer = document.getElementById('alerts-container') || createAlertsContainer();
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.role = 'alert';
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;

    alertsContainer.appendChild(alert);

    setTimeout(() => alert.remove(), 5000);
}

// Función para crear el contenedor de alertas
function createAlertsContainer() {
    const container = document.createElement('div');
    container.id = 'alerts-container';
    container.style.position = 'fixed';
    container.style.top = '20px';
    container.style.right = '20px';
    container.style.zIndex = '1050';
    document.body.appendChild(container);
    return container;
}

// Función para cerrar modal y recargar
function cerrarModalYRecargar() {
    const modal = bootstrap.Modal.getInstance(document.getElementById('prestamoModal'));
    if (modal) {
        modal.hide();
    }
    setTimeout(() => window.location.reload(), 1500);
}

// Función para resetear el formulario
function resetForm() {
    const form = document.getElementById('prestamoForm');
    if (form) {
        form.reset();
        const warningsDiv = document.getElementById('warnings');
        if (warningsDiv) {
            warningsDiv.style.display = 'none';
            warningsDiv.innerHTML = '';
        }
        initializeFormElements();
    }
}

// Función para ver detalles del préstamo
function verPrestamo(id) {
    fetch(`/prestamos/${id}`)
        .then(response => response.json())
        .then(prestamo => {
            // Llenar datos básicos
            document.getElementById('detalle-usuario').textContent = prestamo.usuario_nombre;
            document.getElementById('detalle-libro').textContent = prestamo.libro_titulo;
            document.getElementById('detalle-fecha-prestamo').textContent = new Date(prestamo.fechaPrestamo).toLocaleDateString();
            document.getElementById('detalle-fecha-devolucion').textContent = new Date(prestamo.fechaDevolucion).toLocaleDateString();
            
            // Estado del préstamo
            const estadoSpan = document.getElementById('detalle-estado-prestamo');
            estadoSpan.textContent = prestamo.estado;
            estadoSpan.className = `badge bg-${prestamo.estado === 'ACTIVO' ? 'primary' : 
                                              prestamo.estado === 'DEVUELTO' ? 'success' : 'danger'}`;
            
            // Mostrar el modal
            const modal = new bootstrap.Modal(document.getElementById('detallesPrestamoModal'));
            modal.show();
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('Error al cargar los detalles del préstamo', 'danger');
        });
}

// Función para formatear fechas
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString('es-ES', options);
}