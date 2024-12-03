from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from app.models.libro import Libro
from app.models.autor import Autor
from app.models.categoria import Categoria
from app.models.prestamo import Prestamo
from app.models.resena import Resena
from bson import ObjectId

libro_bp = Blueprint('libros', __name__)
libro_model = Libro()
autor_model = Autor()
categoria_model = Categoria()

@libro_bp.route('/')
def index():
    # Obtener las listas para los filtros
    autores = autor_model.find_many({'activo': True})
    categorias = categoria_model.listar_todas()
    libros = libro_model.find_many({'activo': True})
    
    # Enriquecer los datos de libros con información de autor y categoría
    for libro in libros:
        if 'autorId' in libro:
            autor = autor_model.find_one({'_id': libro['autorId']})
            libro['autor_nombre'] = autor['nombre'] if autor else 'Autor no encontrado'
        if 'categoriaId' in libro:
            categoria = categoria_model.find_one({'_id': libro['categoriaId']})
            libro['categoria_nombre'] = categoria['nombre'] if categoria else 'Sin categoría'
    
    return render_template('libros/index.html', 
                         libros=libros, 
                         autores=autores, 
                         categorias=categorias)

@libro_bp.route('/buscar')
def buscar():
    # Obtener parámetros de búsqueda
    titulo = request.args.get('titulo')
    autor_id = request.args.get('autor_id')
    categoria_id = request.args.get('categoria_id')
    isbn = request.args.get('isbn')
    disponibilidad = request.args.get('disponibilidad')
    
    # Construir filtro
    filtro = {'activo': True}
    if titulo:
        filtro['titulo'] = {'$regex': titulo, '$options': 'i'}
    if autor_id:
        filtro['autorId'] = ObjectId(autor_id)
    if categoria_id:
        filtro['categoriaId'] = ObjectId(categoria_id)
    if isbn:
        filtro['isbn'] = isbn
    if disponibilidad:
        filtro['disponibles'] = {'$gt': 0} if disponibilidad == 'disponible' else 0
    
    libros = libro_model.find_many(filtro)
    
    # Enriquecer datos
    for libro in libros:
        # Obtener información del autor
        if 'autorId' in libro:
            autor = autor_model.find_one({'_id': libro['autorId']})
            libro['autor_nombre'] = autor['nombre'] if autor else 'Autor no encontrado'
        
        # Obtener información de la categoría
        if 'categoriaId' in libro:
            categoria = categoria_model.find_one({'_id': libro['categoriaId']})
            libro['categoria_nombre'] = categoria['nombre'] if categoria else 'Sin categoría'
        
        # Obtener promedio de reseñas
        resena_model = Resena()
        stats = resena_model.calcular_promedio_libro(libro['_id'])
        libro['calificacion_promedio'] = stats['promedio']
        libro['total_resenas'] = stats['total_resenas']
        
        # Convertir ObjectId a string para JSON
        libro['_id'] = str(libro['_id'])
        if 'autorId' in libro:
            libro['autorId'] = str(libro['autorId'])
        if 'categoriaId' in libro:
            libro['categoriaId'] = str(libro['categoriaId'])
    
    return jsonify(libros)

@libro_bp.route('/<id>', methods=['GET'])
def obtener_libro(id):
    libro = libro_model.find_one({'_id': ObjectId(id)})
    if libro:
        # Convertir ObjectIds a strings
        libro['_id'] = str(libro['_id'])
        if 'autorId' in libro:
            libro['autorId'] = str(libro['autorId'])
            # Obtener nombre del autor
            autor = autor_model.find_one({'_id': ObjectId(libro['autorId'])})
            libro['autor_nombre'] = autor['nombre'] if autor else 'Autor no encontrado'
        
        if 'categoriaId' in libro:
            libro['categoriaId'] = str(libro['categoriaId'])
            # Obtener nombre de la categoría
            categoria = categoria_model.find_one({'_id': ObjectId(libro['categoriaId'])})
            libro['categoria_nombre'] = categoria['nombre'] if categoria else 'Sin categoría'
        
        # Obtener reseñas del libro
        resena_model = Resena()
        resenas = resena_model.buscar_por_libro(libro['_id'])
        for resena in resenas:
            resena['_id'] = str(resena['_id'])
            resena['usuarioId'] = str(resena['usuarioId'])
            resena['libroId'] = str(resena['libroId'])
        
        # Obtener préstamos activos
        prestamo_model = Prestamo()
        prestamos_activos = prestamo_model.find_many({
            'libroId': ObjectId(libro['_id']),
            'estado': 'ACTIVO'
        })
        
        libro['resenas'] = resenas
        libro['prestamos_activos'] = len(prestamos_activos)
        
        return jsonify(libro)
    return jsonify({'error': 'Libro no encontrado'}), 404

@libro_bp.route('/<id>', methods=['PUT'])
def actualizar_libro(id):
    datos = request.get_json()
    libro = libro_model.find_one({'_id': ObjectId(id)})
    if not libro:
        return jsonify({'error': 'Libro no encontrado'}), 404

    # Actualizar relaciones si cambian
    if 'autorId' in datos and datos['autorId'] != str(libro.get('autorId')):
        autor = autor_model.find_one({'_id': ObjectId(datos['autorId'])})
        if not autor:
            return jsonify({'error': 'Autor no encontrado'}), 404

    if 'categoriaId' in datos and datos['categoriaId'] != str(libro.get('categoriaId')):
        categoria = categoria_model.find_one({'_id': ObjectId(datos['categoriaId'])})
        if not categoria:
            return jsonify({'error': 'Categoría no encontrada'}), 404

    # Convertir IDs de string a ObjectId
    if 'autorId' in datos:
        datos['autorId'] = ObjectId(datos['autorId'])
    if 'categoriaId' in datos:
        datos['categoriaId'] = ObjectId(datos['categoriaId'])

    libro_model.update_one({'_id': ObjectId(id)}, datos)
    return jsonify({'mensaje': 'Libro actualizado exitosamente'})

@libro_bp.route('/<id>', methods=['DELETE'])
def eliminar_libro(id):
    try:
        libro = libro_model.find_one({'_id': ObjectId(id)})
        if not libro:
            return jsonify({'error': 'Libro no encontrado'}), 404

        # Verificar si hay préstamos activos
        prestamo_model = Prestamo()
        prestamos_activos = prestamo_model.find_many({
            'libroId': ObjectId(id),
            'estado': 'ACTIVO'
        })

        if prestamos_activos:
            return jsonify({
                'error': 'No se puede eliminar el libro porque tiene préstamos activos'
            }), 400

        # Eliminar el libro permanentemente
        resultado = libro_model.delete_one({'_id': ObjectId(id)})
        
        if resultado.deleted_count > 0:
            return jsonify({'mensaje': 'Libro eliminado exitosamente'})
        else:
            return jsonify({'error': 'No se pudo eliminar el libro'}), 500
            
    except Exception as e:
        print(f"Error al eliminar libro: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
@libro_bp.route('/por-autor/<autor_id>')
def libros_por_autor(autor_id):
    autor = autor_model.find_one({'_id': ObjectId(autor_id)})
    if not autor:
        return jsonify({'error': 'Autor no encontrado'}), 404

    libros = libro_model.buscar_por_autor(autor_id)
    return jsonify({
        'autor': {
            'nombre': autor['nombre'],
            'nacionalidad': autor['nacionalidad']
        },
        'libros': libros
    })

@libro_bp.route('/estadisticas')
def estadisticas():
    # Total de libros
    total_libros = len(libro_model.find_many({'activo': True}))
    
    # Libros por categoría
    libros_por_categoria = []
    categorias = categoria_model.listar_todas()
    for categoria in categorias:
        count = len(libro_model.buscar_por_categoria(str(categoria['_id'])))
        libros_por_categoria.append({
            'categoria': categoria['nombre'],
            'cantidad': count
        })
    
    # Libros más prestados
    prestamo_model = Prestamo()
    libros_prestados = prestamo_model.collection.aggregate([
        {'$group': {
            '_id': '$libroId',
            'total_prestamos': {'$sum': 1}
        }},
        {'$sort': {'total_prestamos': -1}},
        {'$limit': 5}
    ])
    
    top_libros = []
    for item in libros_prestados:
        libro = libro_model.find_one({'_id': item['_id']})
        if libro:
            top_libros.append({
                'titulo': libro['titulo'],
                'total_prestamos': item['total_prestamos']
            })
    
    return jsonify({
        'total_libros': total_libros,
        'libros_por_categoria': libros_por_categoria,
        'libros_mas_prestados': top_libros
    })
@libro_bp.route('/', methods=['POST'])
@libro_bp.route('/', methods=['POST'])
def crear_libro():
    try:
        datos = request.get_json()
        
        resultado = libro_model.create_libro(
            titulo=datos['titulo'],
            autor_id=datos['autorId'],
            categoria_id=datos['categoriaId'],
            isbn=datos['isbn'],
            copias=int(datos['copias']),
            fecha_publicacion=datos['fechaPublicacion'],
            editorial=datos['editorial']
        )
        
        return jsonify({
            'mensaje': 'Libro creado exitosamente',
            'id': str(resultado.inserted_id)
        }), 201
        
    except Exception as e:
        print(f"Error al crear libro: {str(e)}")
        return jsonify({'error': 'Error al crear el libro'}), 500