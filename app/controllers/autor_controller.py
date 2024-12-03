from flask import Blueprint, render_template, request, jsonify
from app.models.autor import Autor
from app.models.libro import Libro
from bson import ObjectId
from datetime import datetime

autor_bp = Blueprint('autores', __name__)
autor_model = Autor()
libro_model = Libro()

@autor_bp.route('/')
def index():
    autores = autor_model.buscar_activos()
    return render_template('autores/index.html', autores=autores)

@autor_bp.route('/buscar')
def buscar():
    # Parámetros de búsqueda
    nombre = request.args.get('nombre')
    nacionalidad = request.args.get('nacionalidad')
    
    # Construir filtro
    filtro = {'activo': True}
    if nombre:
        filtro['nombre'] = {'$regex': nombre, '$options': 'i'}
    if nacionalidad:
        filtro['nacionalidad'] = nacionalidad
    
    autores = autor_model.find_many(filtro)
    
    # Enriquecer datos con estadísticas
    for autor in autores:
        stats = autor_model.obtener_estadisticas(str(autor['_id']))
        autor.update(stats)
        autor['_id'] = str(autor['_id'])
    
    return jsonify(autores)

@autor_bp.route('/', methods=['POST'])
def crear_autor():
    datos = request.get_json()
    
    # Validar datos requeridos
    campos_requeridos = ['nombre', 'nacionalidad', 'biografia', 'fechaNacimiento']
    for campo in campos_requeridos:
        if campo not in datos:
            return jsonify({'error': f'El campo {campo} es requerido'}), 400
    
    # Convertir la fecha de string a datetime
    try:
        fecha_nacimiento = datetime.strptime(datos['fechaNacimiento'], '%Y-%m-%d')
    except ValueError:
        return jsonify({'error': 'Formato de fecha inválido. Use YYYY-MM-DD'}), 400
    
    autor_id = autor_model.create_autor(
        nombre=datos['nombre'],
        nacionalidad=datos['nacionalidad'],
        biografia=datos['biografia'],
        fecha_nacimiento=fecha_nacimiento
    )
    
    return jsonify({
        'id': str(autor_id),
        'mensaje': 'Autor creado exitosamente'
    })

@autor_bp.route('/<id>', methods=['GET'])
def obtener_autor(id):
    autor = autor_model.find_one({'_id': ObjectId(id)})
    if not autor:
        return jsonify({'error': 'Autor no encontrado'}), 404
    
    # Obtener libros del autor
    libros = libro_model.buscar_por_autor(id)
    
    # Obtener estadísticas
    stats = autor_model.obtener_estadisticas(id)
    
    autor['_id'] = str(autor['_id'])
    autor['libros'] = [{
        '_id': str(libro['_id']),
        'titulo': libro['titulo'],
        'isbn': libro['isbn'],
        'editorial': libro['editorial']
    } for libro in libros]
    autor.update(stats)
    
    return jsonify(autor)

@autor_bp.route('/<id>', methods=['PUT'])
def actualizar_autor(id):
    datos = request.get_json()
    autor = autor_model.find_one({'_id': ObjectId(id)})
    
    if not autor:
        return jsonify({'error': 'Autor no encontrado'}), 404
    
    # Si se incluye fecha de nacimiento, convertirla
    if 'fechaNacimiento' in datos:
        try:
            datos['fechaNacimiento'] = datetime.strptime(
                datos['fechaNacimiento'],
                '%Y-%m-%d'
            )
        except ValueError:
            return jsonify({'error': 'Formato de fecha inválido. Use YYYY-MM-DD'}), 400
    
    autor_model.update_one({'_id': ObjectId(id)}, datos)
    return jsonify({'mensaje': 'Autor actualizado exitosamente'})

@autor_bp.route('/<id>', methods=['DELETE'])
def eliminar_autor(id):
    try:
        autor = autor_model.find_one({'_id': ObjectId(id)})
        if not autor:
            return jsonify({'error': 'Autor no encontrado'}), 404
        
        # Eliminamos todos los libros que tengan este autorId
        libro_model.delete_many({'autorId': ObjectId(id)})
        
        # Luego eliminamos el autor
        resultado = autor_model.delete_one({'_id': ObjectId(id)})
        
        if resultado.deleted_count > 0:
            return jsonify({
                'mensaje': 'Autor y sus libros asociados fueron eliminados exitosamente'
            })
        else:
            return jsonify({'error': 'No se pudo eliminar el autor'}), 500
        
    except Exception as e:
        print(f"Error al eliminar autor: {str(e)}")
        return jsonify({'error': str(e)}), 500

@autor_bp.route('/<id>/libros')
def libros_autor(id):
    autor = autor_model.find_one({'_id': ObjectId(id)})
    if not autor:
        return jsonify({'error': 'Autor no encontrado'}), 404
    
    libros = libro_model.buscar_por_autor(id)
    
    # Enriquecer datos de libros
    for libro in libros:
        libro['_id'] = str(libro['_id'])
        if 'autorId' in libro:
            libro['autorId'] = str(libro['autorId'])
        if 'categoriaId' in libro:
            libro['categoriaId'] = str(libro['categoriaId'])
    
    return jsonify({
        'autor': {
            'nombre': autor['nombre'],
            'nacionalidad': autor['nacionalidad']
        },
        'libros': libros
    })

@autor_bp.route('/<id>/estadisticas')
def estadisticas_autor(id):
    autor = autor_model.find_one({'_id': ObjectId(id)})
    if not autor:
        return jsonify({'error': 'Autor no encontrado'}), 404
    
    stats = autor_model.obtener_estadisticas(id)
    
    return jsonify({
        'autor': {
            'nombre': autor['nombre'],
            'nacionalidad': autor['nacionalidad']
        },
        'estadisticas': stats
    })