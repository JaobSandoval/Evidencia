// app/static/js/categorias.js
function guardarCategoria() {
    // Obtener los valores directamente de los campos
    const nombre = document.getElementById('nombreCategoria').value.trim();
    const descripcion = document.getElementById('descripcionCategoria').value.trim();
    
    console.log('Valores a enviar:', { nombre, descripcion }); // Debug
    
    // Validación del lado del cliente
    if (!nombre) {
        showAlert('El nombre es requerido', 'danger');
        return;
    }
    
    const data = {
        nombre: nombre,
        descripcion: descripcion
    };
    
    console.log('Datos a enviar:', data); // Debug
    
    fetch('/categorias/', {
        method: 'POST',
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
        console.error('Error:', error);
        showAlert('Error al guardar la categoría', 'danger');
    });
}

function editarCategoria(id) {
    fetch(`/categorias/${id}`)
        .then(response => response.json())
        .then(categoria => {
            document.getElementById('categoria_id').value = categoria._id;
            document.getElementById('nombreCategoria').value = categoria.nombre;
            document.getElementById('descripcionCategoria').value = categoria.descripcion;
            
            document.getElementById('modalTitle').textContent = 'Editar Categoría';
            const modal = new bootstrap.Modal(document.getElementById('categoriaModal'));
            modal.show();
        })
        .catch(error => {
            showAlert('Error al cargar categoría', 'danger');
            console.error('Error:', error);
        });
}

function eliminarCategoria(id) {
    if (!confirmDelete('¿Está seguro de que desea eliminar esta categoría?')) {
        return;
    }

    fetch(`/categorias/${id}`, {
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
        showAlert('Error al eliminar categoría', 'danger');
        console.error('Error:', error);
    });
}

// Event Listener para limpiar el formulario cuando se abre el modal
document.getElementById('categoriaModal').addEventListener('show.bs.modal', function (event) {
    if (!event.relatedTarget || !event.relatedTarget.getAttribute('data-edit')) {
        document.getElementById('categoriaForm').reset();
        document.getElementById('categoria_id').value = '';
        document.getElementById('modalTitle').textContent = 'Nueva Categoría';
    }
});

// Prevenir envío normal del formulario
document.getElementById('categoriaForm').addEventListener('submit', function(e) {
    e.preventDefault();
});