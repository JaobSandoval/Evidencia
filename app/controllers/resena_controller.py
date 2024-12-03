from flask import Blueprint, render_template, request, jsonify
from app.models.resena import Resena
from app.models.libro import Libro
from app.models.usuario import Usuario
from app.models.prestamo import Prestamo
from bson import ObjectId
from datetime import datetime

resena_bp = Blueprint('resenas', __name__)
resena_model = Resena()
libro_model = Libro()
usuario_model = Usuario()
prestamo_model = Prestamo()

@resena_bp.route('/')
def index():
    # Obtener usuarios y libros para los filtros
    usuarios = usuario_model.buscar_activos()
    libros = libro_model.find_many({'activo': True})
    resenas = resena_model.find_many()
    
    # Enriquecer datos de reseñas
    for resena in resenas:
        usuario = usuario_model.find_one({'_id': resena['usuarioId']})
        libro = libro_model.find_one({'_id': resena['libroId']})
        
        resena['usuario_nombre'] = usuario['nombre'] if usuario else 'Usuario no encontrado'
        resena['libro_titulo'] = libro['titulo'] if libro else 'Libro no encontrado'
    
    return render_template('resenas/index.html',
                         resenas=resenas,
                         usuarios=usuarios,
                         libros=libros)

@resena_bp.route('/buscar')
def buscar():
    # Parámetros de búsqueda
    usuario_id = request.args.get('usuario_id')
    libro_id = request.args.get('libro_id')
    calificacion_min = request.args.get('calificacion_min')
    calificacion_max = request.args.get('calificacion_max')
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    
    # Construir filtro
    filtro = {}
    if usuario_id:
        filtro['usuarioId'] = ObjectId(usuario_id)
    if libro_id:
        filtro['libroId'] = ObjectId(libro_id)
    if calificacion_min or calificacion_max:
        filtro['calificacion'] = {}
        if calificacion_min:
            filtro['calificacion']['$gte'] = int(calificacion_min)
        if calificacion_max:
            filtro['calificacion']['$lte'] = int(calificacion_max)
    if fecha_inicio and fecha_fin:
        filtro['fecha'] = {
            '$gte': datetime.strptime(fecha_inicio, '%Y-%m-%d'),
            '$lte': datetime.strptime(fecha_fin, '%Y-%m-%d')
        }
    
    resenas = resena_model.find_many(filtro)
    
    # Enriquecer datos
    for resena in resenas:
        usuario = usuario_model.find_one({'_id': resena['usuarioId']})
        libro = libro_model.find_one({'_id': resena['libroId']})
        
        resena['usuario_nombre'] = usuario['nombre'] if usuario else 'Usuario no encontrado'
        resena['libro_titulo'] = libro['titulo'] if libro else 'Libro no encontrado'
        resena['_id'] = str(resena['_id'])
        resena['usuarioId'] = str(resena['usuarioId'])
        resena['libroId'] = str(resena['libroId'])
    
    return jsonify(resenas)

@resena_bp.route('/', methods=['POST'])
def crear_resena():
    datos = request.get_json()
    
    # Validar usuario y libro
    usuario = usuario_model.find_one({'_id': ObjectId(datos['usuario_id'])})
    if not usuario:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    
    libro = libro_model.find_one({'_id': ObjectId(datos['libro_id'])})
    if not libro:
        return jsonify({'error': 'Libro no encontrado'}), 404
    
    # Verificar si el usuario ha prestado el libro
    prestamos = prestamo_model.find_many({
        'usuarioId': ObjectId(datos['usuario_id']),
        'libroId': ObjectId(datos['libro_id']),
        'estado': 'DEVUELTO'
    })
    
    if not prestamos:
        return jsonify({
            'error': 'El usuario debe haber leído el libro para poder reseñarlo'
        }), 400
    
    # Verificar si el usuario ya ha reseñado este libro
    resena_existente = resena_model.find_one({
        'usuarioId': ObjectId(datos['usuario_id']),
        'libroId': ObjectId(datos['libro_id'])
    })
    
    if resena_existente:
        return jsonify({
            'error': 'El usuario ya ha reseñado este libro'
        }), 400
    
    # Crear la reseña
    resena_id = resena_model.create_resena(
        datos['usuario_id'],
        datos['libro_id'],
        datos['calificacion'],
        datos['comentario']
    )
    
    return jsonify({
        'id': str(resena_id),
        'mensaje': 'Reseña creada exitosamente'
    })

@resena_bp.route('/<id>', methods=['PUT'])
def actualizar_resena(id):
    datos = request.get_json()
    resena = resena_model.find_one({'_id': ObjectId(id)})
    
    if not resena:
        return jsonify({'error': 'Reseña no encontrada'}), 404
    
    # Validar que solo el usuario que creó la reseña pueda modificarla
    if str(resena['usuarioId']) != datos.get('usuario_id'):
        return jsonify({
            'error': 'No tiene permiso para modificar esta reseña'
        }), 403
    
    # Actualizar solo los campos permitidos
    campos_actualizables = ['calificacion', 'comentario']
    datos_actualizacion = {
        k: v for k, v in datos.items() 
        if k in campos_actualizables
    }
    
    resena_model.update_one(
        {'_id': ObjectId(id)},
        datos_actualizacion
    )
    
    return jsonify({'mensaje': 'Reseña actualizada exitosamente'})

@resena_bp.route('/<id>', methods=['DELETE'])
def eliminar_resena(id):
    resena = resena_model.find_one({'_id': ObjectId(id)})
    if not resena:
        return jsonify({'error': 'Reseña no encontrada'}), 404
    
    resena_model.delete_one({'_id': ObjectId(id)})
    return jsonify({'mensaje': 'Reseña eliminada exitosamente'})

@resena_bp.route('/libro/<libro_id>')
def resenas_libro(libro_id):
    libro = libro_model.find_one({'_id': ObjectId(libro_id)})
    if not libro:
        return jsonify({'error': 'Libro no encontrado'}), 404
    
    resenas = resena_model.buscar_por_libro(libro_id)
    stats = resena_model.calcular_promedio_libro(libro_id)
    
    # Enriquecer datos de reseñas
    for resena in resenas:
        usuario = usuario_model.find_one({'_id': resena['usuarioId']})
        resena['usuario_nombre'] = usuario['nombre'] if usuario else 'Usuario no encontrado'
        resena['_id'] = str(resena['_id'])
        resena['usuarioId'] = str(resena['usuarioId'])
        resena['libroId'] = str(resena['libroId'])
    
    return jsonify({
        'libro': {
            'titulo': libro['titulo'],
            'promedio_calificacion': stats['promedio'],
            'total_resenas': stats['total_resenas']
        },
        'resenas': resenas
    })

@resena_bp.route('/usuario/<usuario_id>')
def resenas_usuario(usuario_id):
    usuario = usuario_model.find_one({'_id': ObjectId(usuario_id)})
    if not usuario:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    
    resenas = resena_model.buscar_por_usuario(usuario_id)
    
    # Enriquecer datos
    for resena in resenas:
        libro = libro_model.find_one({'_id': resena['libroId']})
        resena['libro_titulo'] = libro['titulo'] if libro else 'Libro no encontrado'
        resena['_id'] = str(resena['_id'])
        resena['usuarioId'] = str(resena['usuarioId'])
        resena['libroId'] = str(resena['libroId'])
    
    return jsonify({
        'usuario': {
            'nombre': usuario['nombre'],
            'email': usuario['email']
        },
        'resenas': resenas
    })