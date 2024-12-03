// app/static/js/autores.js
function guardarAutor() {
    // Debug
    console.log('Iniciando guardarAutor');
    
    const autorId = document.getElementById('autor_id').value;
    const nombre = document.getElementById('nombreAutor').value.trim();
    const nacionalidad = document.getElementById('nacionalidadAutor').value.trim();
    const biografia = document.getElementById('biografia').value.trim();
    const fechaNacimiento = document.getElementById('fechaNacimiento').value;
    
    // Debug
    console.log('Valores obtenidos:', { nombre, nacionalidad, biografia, fechaNacimiento });
    
    // Validación
    if (!nombre || !nacionalidad || !biografia || !fechaNacimiento) {
        showAlert('Todos los campos son requeridos', 'danger');
        return;
    }

    const data = {
        nombre: nombre,
        nacionalidad: nacionalidad,
        biografia: biografia,
        fechaNacimiento: fechaNacimiento
    };

    // Si es edición, incluir el estado
    if (autorId) {
        data.activo = document.getElementById('activo').value === 'true';
    }

    // Debug
    console.log('Datos a enviar:', data);

    const url = autorId ? `/autores/${autorId}` : '/autores';
    const method = autorId ? 'PUT' : 'POST';

    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        console.log('Status:', response.status); // Debug
        return response.json();
    })
    .then(data => {
        console.log('Respuesta:', data); // Debug
        if (data.error) {
            showAlert(data.error, 'danger');
        } else {
            showAlert(data.mensaje);
            window.location.reload();
        }
    })
    .catch(error => {
        console.error('Error completo:', error);
        showAlert('Error al guardar autor', 'danger');
    });
}


function editarAutor(id) {
    fetch(`/autores/${id}`)
        .then(response => response.json())
        .then(autor => {
            document.getElementById('autor_id').value = autor._id;
            document.getElementById('nombreAutor').value = autor.nombre;
            document.getElementById('nacionalidadAutor').value = autor.nacionalidad;
            document.getElementById('biografia').value = autor.biografia;
            document.getElementById('fechaNacimiento').value = formatDate(autor.fechaNacimiento);
            
            // Mostrar campo de estado en edición
            document.getElementById('estadoContainer').style.display = 'block';
            if (document.getElementById('activo')) {
                document.getElementById('activo').value = autor.activo;
            }
            
            document.getElementById('modalTitle').textContent = 'Editar Autor';
            const modal = new bootstrap.Modal(document.getElementById('autorModal'));
            modal.show();
        })
        .catch(error => {
            showAlert('Error al cargar autor', 'danger');
            console.error('Error:', error);
        });
}
function eliminarAutor(id) {
    if (!confirm('¿Está seguro de que desea eliminar este autor? Esta acción eliminará también todos los libros asociados a este autor y no se puede deshacer.')) {
        return;
    }

    fetch(`/autores/${id}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showAlert(data.error, 'danger');
        } else {
            showAlert(data.mensaje, 'success');
            window.location.reload();
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('Error al eliminar autor y sus libros', 'danger');
    });
}
function verLibros(id) {
    fetch(`/autores/${id}/libros`)
        .then(response => response.json())
        .then(data => {
            const tbody = document.querySelector('#librosAutor tbody');
            tbody.innerHTML = '';
            
            data.libros.forEach(libro => {
                tbody.innerHTML += `
                    <tr>
                        <td>${libro.titulo}</td>
                        <td>${libro.isbn}</td>
                        <td>${libro.editorial}</td>
                        <td>
                            <span class="badge ${libro.disponibles > 0 ? 'bg-success' : 'bg-danger'}">
                                ${libro.disponibles}/${libro.copias}
                            </span>
                        </td>
                    </tr>
                `;
            });
            
            document.getElementById('autorLibrosTitle').textContent = `Libros de: ${data.autor.nombre}`;
            const modal = new bootstrap.Modal(document.getElementById('librosModal'));
            modal.show();
        })
        .catch(error => {
            showAlert('Error al cargar libros del autor', 'danger');
            console.error('Error:', error);
        });
}

// Event Listeners
document.getElementById('searchForm')?.addEventListener('submit', function(e) {
    e.preventDefault();
    const formData = new FormData(this);
    const params = new URLSearchParams();
    
    for (let pair of formData.entries()) {
        if (pair[1]) {
            params.append(pair[0], pair[1]);
        }
    }
    
    fetch(`/autores/buscar?${params.toString()}`)
        .then(response => response.json())
        .then(autores => {
            const tbody = document.querySelector('#autoresTable tbody');
            tbody.innerHTML = '';
            
            autores.forEach(autor => {
                tbody.innerHTML += `
                    <tr>
                        <td>${autor.nombre}</td>
                        <td>${autor.nacionalidad}</td>
                        <td>
                            <span class="badge bg-info">${autor.total_libros || 0}</span>
                        </td>
                        <td>
                            <div class="btn-group">
                                <button class="btn btn-sm btn-primary" onclick="editarAutor('${autor._id}')">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button class="btn btn-sm btn-warning" onclick="verLibros('${autor._id}')">
                                    <i class="fas fa-book"></i>
                                </button>
                                <button class="btn btn-sm btn-danger" onclick="eliminarAutor('${autor._id}')">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </td>
                    </tr>
                `;
            });
        })
        .catch(error => {
            showAlert('Error al buscar autores', 'danger');
            console.error('Error:', error);
        });
});

// Limpiar formulario cuando se abre el modal para nuevo autor
document.getElementById('autorModal')?.addEventListener('show.bs.modal', function (event) {
    if (!event.relatedTarget || !event.relatedTarget.getAttribute('data-edit')) {
        document.getElementById('autorForm').reset();
        document.getElementById('autor_id').value = '';
        document.getElementById('modalTitle').textContent = 'Nuevo Autor';
        document.getElementById('estadoContainer').style.display = 'none';
    }
});

