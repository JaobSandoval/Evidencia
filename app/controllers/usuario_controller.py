from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from app.models.usuario import Usuario
from app.models.prestamo import Prestamo
from app.models.resena import Resena
from bson import ObjectId
from datetime import datetime
import math

usuario_bp = Blueprint('usuarios', __name__)
usuario_model = Usuario()
prestamo_model = Prestamo()
resena_model = Resena()

@usuario_bp.route('/')
def index():
    try:
        # Obtener parámetros de paginación
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        # Obtener todos los usuarios activos
        query = {'activo': True}
        skip = (page - 1) * per_page
        usuarios = usuario_model.find_many(query)
        
        # Log para debugging
        print("Total usuarios en la base de datos:", len(usuarios))

        # Enriquecer datos con estadísticas
        for usuario in usuarios:
            # Convertir _id a string si es necesario
            if '_id' in usuario:
                usuario['_id'] = str(usuario['_id'])
            
            # Obtener préstamos del usuario
            prestamos = prestamo_model.buscar_prestamos_usuario(str(usuario['_id']))
            prestamos_activos = [p for p in prestamos if p['estado'] == 'ACTIVO']
            
            # Agregar estadísticas
            usuario['total_prestamos'] = len(prestamos)
            usuario['prestamos_activos'] = len(prestamos_activos)
            
            # Calcular multas pendientes
            multa_total = sum(
                prestamo.get('multa', 0)
                for prestamo in prestamos_activos
                if prestamo['fechaDevolucion'] < datetime.now()
            )
            usuario['multas_pendientes'] = multa_total

        # Calcular total de páginas
        total_usuarios = len(usuarios)
        total_pages = math.ceil(total_usuarios / per_page)

        return render_template(
            'usuarios/index.html',
            usuarios=usuarios[(page-1)*per_page:page*per_page],
            current_page=page,
            total_pages=total_pages,
            per_page=per_page
        )

    except Exception as e:
        print(f"Error en index: {str(e)}")
        return render_template(
            'usuarios/index.html',
            error=f'Error al cargar usuarios: {str(e)}',
            usuarios=[],
            current_page=1,
            total_pages=1,
            per_page=10
        )

@usuario_bp.route('/buscar')
def buscar():
    try:
        # Parámetros de búsqueda
        nombre = request.args.get('nombre')
        email = request.args.get('email')
        activo = request.args.get('activo')
        
        # Construir filtro
        filtro = {}
        if nombre:
            filtro['nombre'] = {'$regex': nombre.strip(), '$options': 'i'}
        if email:
            filtro['email'] = {'$regex': email.strip(), '$options': 'i'}
        if activo is not None:
            filtro['activo'] = activo.lower() == 'true'
        
        # Obtener usuarios
        usuarios = usuario_model.find_many(filtro)
        
        # Enriquecer datos con estadísticas
        for usuario in usuarios:
            prestamos = prestamo_model.buscar_prestamos_usuario(str(usuario['_id']))
            resenas = resena_model.buscar_por_usuario(str(usuario['_id']))
            
            usuario['total_prestamos'] = len(prestamos)
            usuario['prestamos_activos'] = len([p for p in prestamos if p['estado'] == 'ACTIVO'])
            usuario['total_resenas'] = len(resenas)
        
        return jsonify(usuarios)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@usuario_bp.route('/<id>', methods=['GET'])
def obtener_usuario(id):
    try:
        usuario = usuario_model.find_one({'_id': ObjectId(id)})
        if not usuario:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        # Convertir _id a string
        usuario['_id'] = str(usuario['_id'])
        
        # Obtener préstamos del usuario
        prestamos = prestamo_model.buscar_prestamos_usuario(id)
        prestamos_activos = [p for p in prestamos if p['estado'] == 'ACTIVO']
        
        # Obtener reseñas del usuario
        resenas = resena_model.buscar_por_usuario(id)
        
        # Agregar información adicional
        usuario['prestamos'] = [{
            '_id': str(p['_id']),
            'libroId': str(p['libroId']),
            'fechaPrestamo': p['fechaPrestamo'],
            'fechaDevolucion': p['fechaDevolucion'],
            'estado': p['estado']
        } for p in prestamos_activos]
        
        usuario['resenas'] = [{
            '_id': str(r['_id']),
            'libroId': str(r['libroId']),
            'calificacion': r['calificacion'],
            'comentario': r.get('comentario', '')
        } for r in resenas]
        
        return jsonify(usuario)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@usuario_bp.route('/<id>', methods=['PUT'])
def actualizar_usuario(id):
    try:
        datos = request.get_json()
        usuario = usuario_model.find_one({'_id': ObjectId(id)})
        
        if not usuario:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        # Si se está actualizando el email, verificar que no exista
        if 'email' in datos and datos['email'] != usuario['email']:
            if usuario_model.buscar_por_email(datos['email']):
                return jsonify({'error': 'El email ya está registrado'}), 400
        
        usuario_model.update_one({'_id': ObjectId(id)}, datos)
        return jsonify({'mensaje': 'Usuario actualizado exitosamente'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@usuario_bp.route('/<id>', methods=['DELETE'])
def eliminar_usuario(id):
    try:
        usuario = usuario_model.find_one({'_id': ObjectId(id)})
        if not usuario:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        # Verificar si tiene préstamos activos
        prestamos_activos = prestamo_model.find_many({
            'usuarioId': ObjectId(id),
            'estado': 'ACTIVO'
        })
        
        if prestamos_activos:
            return jsonify({
                'error': 'No se puede eliminar el usuario porque tiene préstamos activos'
            }), 400
        
        # Desactivar usuario en lugar de eliminarlo
        usuario_model.update_one({'_id': ObjectId(id)}, {'activo': False})
        return jsonify({'mensaje': 'Usuario desactivado exitosamente'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@usuario_bp.route('/', methods=['POST'])
def crear_usuario():
    try:
        datos = request.get_json()
        if not datos:
            return jsonify({'error': 'No se recibieron datos'}), 400
        
        # Validar datos requeridos
        campos_requeridos = ['nombre', 'email', 'direccion', 'telefono']
        for campo in campos_requeridos:
            if not datos.get(campo) or not str(datos[campo]).strip():
                return jsonify({'error': f'El campo {campo} es requerido y no puede estar vacío'}), 400
        
        # Verificar si el email ya existe
        if usuario_model.buscar_por_email(datos['email']):
            return jsonify({'error': 'El email ya está registrado'}), 400
        
        # Crear usuario
        resultado = usuario_model.create_usuario(
            nombre=datos['nombre'].strip(),
            email=datos['email'].strip(),
            direccion=datos['direccion'].strip(),
            telefono=datos['telefono'].strip()
        )
        
        return jsonify({
            'id': str(resultado),
            'mensaje': 'Usuario creado exitosamente'
        }), 201
        
    except Exception as e:
        print(f"Error al crear usuario: {str(e)}")
        return jsonify({'error': 'Error al crear el usuario'}), 500