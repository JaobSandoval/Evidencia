from flask import Blueprint, render_template, request, jsonify
from app.models.prestamo import Prestamo
from app.models.libro import Libro
from app.models.usuario import Usuario
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime, timedelta

prestamo_bp = Blueprint('prestamos', __name__)
prestamo_model = Prestamo()
libro_model = Libro()
usuario_model = Usuario()

@prestamo_bp.route('/')
def index():
    # Convertir cursores a lista para asegurar que los datos están disponibles
    usuarios = list(usuario_model.buscar_activos())
    libros = list(libro_model.find_many({'activo': True}))
    
    print(f"Usuarios disponibles: {len(usuarios)}")  # Debug
    print(f"Libros disponibles: {len(libros)}")     # Debug
    
    return render_template('prestamos/index.html',
                         usuarios=usuarios,
                         libros=libros,
                         today=datetime.now().strftime('%Y-%m-%d'))
@prestamo_bp.route('/buscar')
def buscar():
    # Parámetros de búsqueda
    usuario_id = request.args.get('usuario_id')
    libro_id = request.args.get('libro_id')
    estado = request.args.get('estado')
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    
    # Construir filtro
    filtro = {}
    if usuario_id:
        filtro['usuarioId'] = ObjectId(usuario_id)
    if libro_id:
        filtro['libroId'] = ObjectId(libro_id)
    if estado:
        filtro['estado'] = estado
    if fecha_inicio and fecha_fin:
        filtro['fechaPrestamo'] = {
            '$gte': datetime.strptime(fecha_inicio, '%Y-%m-%d'),
            '$lte': datetime.strptime(fecha_fin, '%Y-%m-%d')
        }
    
    prestamos = prestamo_model.find_many(filtro)
    
    # Enriquecer datos
    for prestamo in prestamos:
        usuario = usuario_model.find_one({'_id': prestamo['usuarioId']})
        libro = libro_model.find_one({'_id': prestamo['libroId']})
        
        prestamo['usuario_nombre'] = usuario['nombre'] if usuario else 'Usuario no encontrado'
        prestamo['libro_titulo'] = libro['titulo'] if libro else 'Libro no encontrado'
        prestamo['_id'] = str(prestamo['_id'])
        prestamo['usuarioId'] = str(prestamo['usuarioId'])
        prestamo['libroId'] = str(prestamo['libroId'])
    
    return jsonify(prestamos)

@prestamo_bp.route('/', methods=['POST'])
def crear_prestamo():
    try:
        datos = request.get_json()
        
        # Validación de datos recibidos
        if not datos:
            return jsonify({
                'error': 'No se recibieron datos para crear el préstamo'
            }), 400
        
        # Validar campos requeridos
        campos_requeridos = ['usuario_id', 'libro_id', 'dias_prestamo']
        for campo in campos_requeridos:
            if campo not in datos or not datos[campo]:
                return jsonify({
                    'error': f'El campo {campo} es requerido'
                }), 400

        # Validar y obtener usuario
        try:
            usuario = usuario_model.find_one({'_id': ObjectId(datos['usuario_id'])})
            if not usuario:
                return jsonify({'error': 'Usuario no encontrado'}), 404
            if not usuario.get('activo', False):
                return jsonify({'error': 'El usuario no está activo'}), 400
        except InvalidId:
            return jsonify({'error': 'ID de usuario inválido'}), 400

        # Validar y obtener libro
        try:
            libro = libro_model.find_one({'_id': ObjectId(datos['libro_id'])})
            if not libro:
                return jsonify({'error': 'Libro no encontrado'}), 404
            if not libro.get('activo', False):
                return jsonify({'error': 'El libro no está disponible'}), 400
            if libro.get('disponibles', 0) <= 0:
                return jsonify({'error': 'No hay ejemplares disponibles de este libro'}), 400
        except InvalidId:
            return jsonify({'error': 'ID de libro inválido'}), 400

        # Validar días de préstamo
        dias_prestamo = int(datos.get('dias_prestamo', 14))
        if dias_prestamo < 1 or dias_prestamo > 30:
            return jsonify({
                'error': 'Los días de préstamo deben estar entre 1 y 30'
            }), 400

        # Verificar si el usuario tiene préstamos vencidos
        prestamos_vencidos = prestamo_model.find_many({
            'usuarioId': ObjectId(datos['usuario_id']),
            'estado': 'ACTIVO',
            'fechaDevolucion': {'$lt': datetime.now()}
        })
        
        if prestamos_vencidos:
            return jsonify({
                'error': 'El usuario tiene préstamos vencidos pendientes'
            }), 400

        # Verificar límite de préstamos activos del usuario
        prestamos_activos = prestamo_model.find_many({
            'usuarioId': ObjectId(datos['usuario_id']),
            'estado': 'ACTIVO'
        })
        
        if len(list(prestamos_activos)) >= 3:  # Límite de 3 préstamos activos
            return jsonify({
                'error': 'El usuario ha alcanzado el límite de préstamos activos'
            }), 400

        # Crear el préstamo
        prestamo_id = prestamo_model.create_prestamo(
            datos['usuario_id'],
            datos['libro_id'],
            dias_prestamo
        )
        
        if not prestamo_id:
            return jsonify({
                'error': 'Error al crear el préstamo'
            }), 500

        # Actualizar disponibilidad del libro
        libro_model.actualizar_disponibilidad(
            datos['libro_id'],
            libro['disponibles'] - 1
        )

        return jsonify({
            'id': str(prestamo_id),
            'mensaje': 'Préstamo creado exitosamente'
        }), 201

    except Exception as e:
        # Log del error para debugging
        print(f"Error al crear préstamo: {str(e)}")
        
        return jsonify({
            'error': 'Error interno del servidor al procesar la solicitud'
        }), 500

@prestamo_bp.route('/<id>', methods=['PUT'])
def actualizar_prestamo(id):
    datos = request.get_json()
    prestamo = prestamo_model.find_one({'_id': ObjectId(id)})
    
    if not prestamo:
        return jsonify({'error': 'Préstamo no encontrado'}), 404
    
    # Si se está actualizando el estado a DEVUELTO
    if datos.get('estado') == 'DEVUELTO' and prestamo['estado'] != 'DEVUELTO':
        # Registrar la devolución
        prestamo_model.registrar_devolucion(id)
        
        # Actualizar disponibilidad del libro
        libro = libro_model.find_one({'_id': prestamo['libroId']})
        if libro:
            libro_model.actualizar_disponibilidad(
                str(libro['_id']),
                libro['disponibles'] + 1
            )
    else:
        # Para otras actualizaciones
        prestamo_model.update_one({'_id': ObjectId(id)}, datos)
    
    return jsonify({'mensaje': 'Préstamo actualizado exitosamente'})

@prestamo_bp.route('/<id>', methods=['DELETE'])
def eliminar_prestamo(id):
    prestamo = prestamo_model.find_one({'_id': ObjectId(id)})
    if not prestamo:
        return jsonify({'error': 'Préstamo no encontrado'}), 404
    
    # Solo permitir eliminar préstamos devueltos
    if prestamo['estado'] != 'DEVUELTO':
        return jsonify({
            'error': 'No se puede eliminar un préstamo activo'
        }), 400
    
    prestamo_model.delete_one({'_id': ObjectId(id)})
    return jsonify({'mensaje': 'Préstamo eliminado exitosamente'})

@prestamo_bp.route('/vencidos')
def prestamos_vencidos():
    prestamos = prestamo_model.buscar_prestamos_vencidos()
    
    # Enriquecer datos
    for prestamo in prestamos:
        usuario = usuario_model.find_one({'_id': prestamo['usuarioId']})
        libro = libro_model.find_one({'_id': prestamo['libroId']})
        
        dias_retraso = (datetime.now() - prestamo['fechaDevolucion']).days
        multa = dias_retraso * 10  # 10 pesos por día de retraso
        
        prestamo['usuario_nombre'] = usuario['nombre'] if usuario else 'Usuario no encontrado'
        prestamo['libro_titulo'] = libro['titulo'] if libro else 'Libro no encontrado'
        prestamo['dias_retraso'] = dias_retraso
        prestamo['multa'] = multa
        
        # Convertir ObjectId a string para JSON
        prestamo['_id'] = str(prestamo['_id'])
        prestamo['usuarioId'] = str(prestamo['usuarioId'])
        prestamo['libroId'] = str(prestamo['libroId'])
    
    return jsonify(prestamos)

@prestamo_bp.route('/estadisticas')
def estadisticas():
    # Total de préstamos activos
    prestamos_activos = len(prestamo_model.buscar_prestamos_activos())
    
    # Total de préstamos vencidos
    prestamos_vencidos = len(prestamo_model.buscar_prestamos_vencidos())
    
    # Usuarios con más préstamos
    pipeline = [
        {'$group': {
            '_id': '$usuarioId',
            'total_prestamos': {'$sum': 1}
        }},
        {'$sort': {'total_prestamos': -1}},
        {'$limit': 5}
    ]
    
    top_usuarios = []
    for item in prestamo_model.collection.aggregate(pipeline):
        usuario = usuario_model.find_one({'_id': item['_id']})
        if usuario:
            top_usuarios.append({
                'usuario': usuario['nombre'],
                'total_prestamos': item['total_prestamos']
            })
    
    # Total de multas pendientes
    total_multas = sum(
        prestamo['multa'] 
        for prestamo in prestamo_model.buscar_prestamos_vencidos()
    )
    
    return jsonify({
        'prestamos_activos': prestamos_activos,
        'prestamos_vencidos': prestamos_vencidos,
        'top_usuarios': top_usuarios,
        'total_multas': total_multas
    })

@prestamo_bp.route('/usuario/<usuario_id>')
def prestamos_usuario(usuario_id):
    usuario = usuario_model.find_one({'_id': ObjectId(usuario_id)})
    if not usuario:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    
    # Obtener todos los préstamos del usuario
    prestamos = prestamo_model.buscar_prestamos_usuario(usuario_id)
    
    # Enriquecer datos
    for prestamo in prestamos:
        libro = libro_model.find_one({'_id': prestamo['libroId']})
        prestamo['libro_titulo'] = libro['titulo'] if libro else 'Libro no encontrado'
        
        # Calcular multa si está vencido
        if prestamo['estado'] == 'ACTIVO' and prestamo['fechaDevolucion'] < datetime.now():
            dias_retraso = (datetime.now() - prestamo['fechaDevolucion']).days
            prestamo['multa'] = dias_retraso * 10
        
        # Convertir ObjectId a string
        prestamo['_id'] = str(prestamo['_id'])
        prestamo['usuarioId'] = str(prestamo['usuarioId'])
        prestamo['libroId'] = str(prestamo['libroId'])
    
    return jsonify({
        'usuario': {
            'nombre': usuario['nombre'],
            'email': usuario['email']
        },
        'prestamos': prestamos
    })