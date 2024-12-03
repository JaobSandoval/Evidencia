// app/static/js/libros.js
function guardarLibro() {
    const libroId = document.getElementById('libro_id').value;
    
    // Obtener y validar los datos del formulario
    const data = {
        titulo: document.getElementById('tituloLibro').value.trim(),
        autorId: document.getElementById('autorLibro').value,
        categoriaId: document.getElementById('categoriaLibro').value,
        isbn: document.getElementById('isbnLibro').value.trim(),
        copias: parseInt(document.getElementById('copiasLibro').value),
        fechaPublicacion: document.getElementById('fechaLibro').value,
        editorial: document.getElementById('editorialLibro').value.trim()
    };

    // Validación mejorada
    if (!data.titulo) {
        showAlert('El título es requerido', 'danger');
        return;
    }
    if (!data.autorId) {
        showAlert('Debe seleccionar un autor', 'danger');
        return;
    }
    if (!data.categoriaId) {
        showAlert('Debe seleccionar una categoría', 'danger');
        return;
    }
    if (!data.isbn) {
        showAlert('El ISBN es requerido', 'danger');
        return;
    }
    if (!data.copias || data.copias < 1) {
        showAlert('El número de copias debe ser mayor a 0', 'danger');
        return;
    }
    if (!data.fechaPublicacion) {
        showAlert('La fecha de publicación es requerida', 'danger');
        return;
    }
    if (!data.editorial) {
        showAlert('La editorial es requerida', 'danger');
        return;
    }

    const url = libroId ? `/libros/${libroId}` : '/libros';
    const method = libroId ? 'PUT' : 'POST';

    // Mostrar indicador de carga
    const saveButton = document.querySelector('#libroModal .btn-primary');
    const originalText = saveButton.innerHTML;
    saveButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Guardando...';
    saveButton.disabled = true;

    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json().then(data => ({status: response.status, body: data})))
    .then(({status, body}) => {
        if (status >= 400) {
            throw new Error(body.error || 'Error al guardar el libro');
        }
        showAlert(body.mensaje || 'Libro guardado exitosamente', 'success');
        window.location.reload();
    })
    .catch(error => {
        showAlert(error.message, 'danger');
    })
    .finally(() => {
        // Restaurar botón
        saveButton.innerHTML = originalText;
        saveButton.disabled = false;
    });
}

function editarLibro(id) {
    console.log('Editando libro:', id); // Debug
    fetch(`/libros/${id}`)
        .then(response => response.json())
        .then(libro => {
            console.log('Datos del libro:', libro); // Debug
            document.getElementById('libro_id').value = libro._id;
            document.getElementById('tituloLibro').value = libro.titulo;
            document.getElementById('autorLibro').value = libro.autorId;
            document.getElementById('categoriaLibro').value = libro.categoriaId;
            document.getElementById('isbnLibro').value = libro.isbn;
            document.getElementById('copiasLibro').value = libro.copias;
            document.getElementById('fechaLibro').value = formatDate(libro.fechaPublicacion);
            document.getElementById('editorialLibro').value = libro.editorial;
            
            document.getElementById('modalTitle').textContent = 'Editar Libro';
            const modal = new bootstrap.Modal(document.getElementById('libroModal'));
            modal.show();
        })
        .catch(error => {
            console.error('Error completo:', error);
            showAlert('Error al cargar libro', 'danger');
        });
}

function eliminarLibro(id) {
    if (!confirmDelete('¿Está seguro de que desea eliminar este libro?')) {
        return;
    }

    fetch(`/libros/${id}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showAlert(data.error, 'danger');
        } else {
            showAlert(data.mensaje);
            window.location.reload();
        }
    })
    .catch(error => {
        console.error('Error completo:', error);
        showAlert('Error al eliminar libro', 'danger');
    });
}

function verLibro(id) {
    console.log('Viendo libro:', id); // Debug
    fetch(`/libros/${id}`)
        .then(response => {
            console.log('Status:', response.status); // Debug
            return response.json();
        })
        .then(libro => {
            console.log('Datos del libro:', libro); // Debug
            document.getElementById('detalle-titulo').textContent = libro.titulo || 'N/A';
            document.getElementById('detalle-autor').textContent = libro.autor_nombre || 'Sin autor';
            document.getElementById('detalle-categoria').textContent = libro.categoria_nombre || 'Sin categoría';
            document.getElementById('detalle-isbn').textContent = libro.isbn || 'N/A';
            document.getElementById('detalle-editorial').textContent = libro.editorial || 'N/A';
            document.getElementById('detalle-copias').textContent = `${libro.copias || 0} totales`;
            document.getElementById('detalle-disponibles').textContent = `${libro.disponibles || 0} disponibles`;
            
            const modal = new bootstrap.Modal(document.getElementById('detallesModal'));
            modal.show();
        })
        .catch(error => {
            console.error('Error completo:', error);
            showAlert('Error al cargar detalles del libro', 'danger');
        });
}

// Buscar libros
document.getElementById('searchForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const params = new URLSearchParams();
    if (document.getElementById('tituloBusqueda').value) {
        params.append('titulo', document.getElementById('tituloBusqueda').value);
    }
    if (document.getElementById('autorBusqueda').value) {
        params.append('autor_id', document.getElementById('autorBusqueda').value);
    }
    if (document.getElementById('categoriaBusqueda').value) {
        params.append('categoria_id', document.getElementById('categoriaBusqueda').value);
    }
    if (document.getElementById('disponibilidad').value) {
        params.append('disponibilidad', document.getElementById('disponibilidad').value);
    }
    
    fetch(`/libros/buscar?${params.toString()}`)
        .then(response => response.json())
        .then(libros => {
            const tbody = document.querySelector('#librosTable tbody');
            tbody.innerHTML = '';
            
            libros.forEach(libro => {
                tbody.innerHTML += `
                    <tr>
                        <td>${libro.titulo}</td>
                        <td>${libro.autor_nombre || 'Sin autor'}</td>
                        <td>${libro.categoria_nombre || 'Sin categoría'}</td>
                        <td>${libro.isbn}</td>
                        <td>
                            <span class="badge ${libro.disponibles > 0 ? 'bg-success' : 'bg-danger'}">
                                ${libro.disponibles}/${libro.copias}
                            </span>
                        </td>
                        <td>
                            <div class="btn-group">
                                <button class="btn btn-sm btn-info" onclick="verLibro('${libro._id}')">
                                    <i class="fas fa-eye"></i>
                                </button>
                                <button class="btn btn-sm btn-primary" onclick="editarLibro('${libro._id}')">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button class="btn btn-sm btn-danger" onclick="eliminarLibro('${libro._id}')">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </td>
                    </tr>
                `;
            });
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('Error al buscar libros', 'danger');
        });
});

// Limpiar formulario al abrir modal para nuevo libro
document.getElementById('libroModal').addEventListener('show.bs.modal', function (event) {
    if (!event.relatedTarget || !event.relatedTarget.getAttribute('data-edit')) {
        document.getElementById('libroForm').reset();
        document.getElementById('libro_id').value = '';
        document.getElementById('modalTitle').textContent = 'Nuevo Libro';
    }
});