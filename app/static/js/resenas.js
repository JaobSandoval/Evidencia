// app/static/js/resenas.js
function guardarResena() {
    const form = document.getElementById('resenaForm');
    const resenaId = document.getElementById('resena_id').value;
    
    const data = {
        usuario_id: document.getElementById('usuario_modal_id').value,
        libro_id: document.getElementById('libro_modal_id').value,
        calificacion: document.querySelector('input[name="calificacion"]:checked').value,
        comentario: document.getElementById('comentario').value
    };

    const url = resenaId ? `/resenas/${resenaId}` : '/resenas';
    const method = resenaId ? 'PUT' : 'POST';

    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
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
        showAlert('Error al guardar reseña', 'danger');
        console.error('Error:', error);
    });
}

function editarResena(id) {
    fetch(`/resenas/${id}`)
        .then(response => response.json())
        .then(resena => {
            document.getElementById('resena_id').value = resena._id;
            document.getElementById('usuario_modal_id').value = resena.usuarioId;
            document.getElementById('libro_modal_id').value = resena.libroId;
            document.querySelector(`input[name="calificacion"][value="${resena.calificacion}"]`).checked = true;
            document.getElementById('comentario').value = resena.comentario;
            
            document.getElementById('modalTitle').textContent = 'Editar Reseña';
            const modal = new bootstrap.Modal(document.getElementById('resenaModal'));
            modal.show();
        })
        .catch(error => {
            showAlert('Error al cargar reseña', 'danger');
            console.error('Error:', error);
        });
}

function eliminarResena(id) {
    if (!confirmDelete('¿Está seguro de que desea eliminar esta reseña?')) {
        return;
    }

    fetch(`/resenas/${id}`, {
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
        showAlert('Error al eliminar reseña', 'danger');
        console.error('Error:', error);
    });
}

// Event Listeners
document.getElementById('searchForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const formData = new FormData(this);
    const params = new URLSearchParams();
    
    for (let pair of formData.entries()) {
        if (pair[1]) {
            params.append(pair[0], pair[1]);
        }
    }
    
    fetch(`/resenas/buscar?${params.toString()}`)
        .then(response => response.json())
        .then(resenas => {
            const tbody = document.querySelector('#resenasTable tbody');
            tbody.innerHTML = '';
            
            resenas.forEach(resena => {
                const estrellas = '★'.repeat(resena.calificacion) + '☆'.repeat(5 - resena.calificacion);
                tbody.innerHTML += `
                    <tr>
                        <td>${resena.libro_titulo}</td>
                        <td>${resena.usuario_nombre}</td>
                        <td>
                            <span class="text-warning">${estrellas}</span>
                        </td>
                        <td>${resena.comentario}</td>
                        <td>${formatDate(resena.fecha)}</td>
                        <td>
                            <div class="btn-group">
                                <button class="btn btn-sm btn-primary" onclick="editarResena('${resena._id}')">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button class="btn btn-sm btn-danger" onclick="eliminarResena('${resena._id}')">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </td>
                    </tr>
                `;
            });
        })
        .catch(error => {
            showAlert('Error al buscar reseñas', 'danger');
            console.error('Error:', error);
        });
});

// Limpiar formulario cuando se abre el modal para nueva reseña
document.getElementById('resenaModal').addEventListener('show.bs.modal', function (event) {
    if (!event.relatedTarget.getAttribute('data-edit')) {
        document.getElementById('resenaForm').reset();
        document.getElementById('resena_id').value = '';
        document.getElementById('modalTitle').textContent = 'Nueva Reseña';
    }
});