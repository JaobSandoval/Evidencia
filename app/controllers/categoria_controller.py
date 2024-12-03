from flask import Blueprint, render_template, request, jsonify
from app.models.categoria import Categoria
from app.models.libro import Libro
from bson import ObjectId

categoria_bp = Blueprint('categorias', __name__)
categoria_model = Categoria()
libro_model = Libro()

@categoria_bp.route('/')
def index():
    categorias = categoria_model.listar_todas()
    
    # Enriquecer con el total de libros por categoría
    for categoria in categorias:
        libros = libro_model.find_many({'categoriaId': categoria['_id']})
        categoria['total_libros'] = len(libros)
    
    return render_template('categorias/index.html', categorias=categorias)

@categoria_bp.route('/buscar')
def buscar():
    nombre = request.args.get('nombre')
    
    # Construir filtro
    filtro = {}
    if nombre:
        filtro['nombre'] = {'$regex': nombre, '$options': 'i'}
    
    categorias = categoria_model.find_many(filtro)
    
    # Enriquecer datos
    for categoria in categorias:
        libros = libro_model.find_many({'categoriaId': categoria['_id']})
        categoria['total_libros'] = len(libros)
        categoria['_id'] = str(categoria['_id'])
    
    return jsonify(categorias)

@categoria_bp.route('/', methods=['POST'])
def crear_categoria():
    try:
        print("Headers:", request.headers)
        print("Raw Data:", request.get_data())
        
        datos = request.get_json()
        print("Datos parseados:", datos)
        
        if not datos:
            print("No se recibieron datos JSON")
            return jsonify({'error': 'No se recibieron datos'}), 400

        nombre = datos.get('nombre', '').strip()
        if not nombre:
            print("Nombre está vacío después de strip")
            return jsonify({'error': 'El nombre es requerido'}), 400

        descripcion = datos.get('descripcion', '').strip()
        
        print(f"Creando categoría: nombre='{nombre}', descripcion='{descripcion}'")
        
        categoria_id = categoria_model.create_categoria(
            nombre=nombre,
            descripcion=descripcion
        )

        return jsonify({
            'id': str(categoria_id),
            'mensaje': 'Categoría creada exitosamente'
        })

    except Exception as e:
        print("Error:", str(e))
        import traceback
        print("Traceback:", traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@categoria_bp.route('/<id>', methods=['PUT'])
def actualizar_categoria(id):
    datos = request.get_json()
    categoria = categoria_model.find_one({'_id': ObjectId(id)})
    
    if not categoria:
        return jsonify({'error': 'Categoría no encontrada'}), 404
    
    # Si se está actualizando el nombre, verificar que no exista
    if 'nombre' in datos and datos['nombre'] != categoria['nombre']:
        categoria_existente = categoria_model.find_one({'nombre': datos['nombre']})
        if categoria_existente:
            return jsonify({'error': 'Ya existe una categoría con ese nombre'}), 400
    
    categoria_model.update_one({'_id': ObjectId(id)}, datos)
    return jsonify({'mensaje': 'Categoría actualizada exitosamente'})

@categoria_bp.route('/<id>', methods=['DELETE'])
def eliminar_categoria(id):
    # Verificar si existen libros con esta categoría
    libros = libro_model.find_many({'categoriaId': ObjectId(id)})
    
    if libros:
        return jsonify({
            'error': 'No se puede eliminar la categoría porque tiene libros asociados'
        }), 400
    
    categoria_model.delete_one({'_id': ObjectId(id)})
    return jsonify({'mensaje': 'Categoría eliminada exitosamente'})

@categoria_bp.route('/<id>/libros')
def libros_categoria(id):
    categoria = categoria_model.find_one({'_id': ObjectId(id)})
    if not categoria:
        return jsonify({'error': 'Categoría no encontrada'}), 404
    
    libros = libro_model.find_many({'categoriaId': ObjectId(id)})
    
    # Enriquecer datos de libros
    for libro in libros:
        libro['_id'] = str(libro['_id'])
        if 'autorId' in libro:
            libro['autorId'] = str(libro['autorId'])
        if 'categoriaId' in libro:
            libro['categoriaId'] = str(libro['categoriaId'])
    
    return jsonify({
        'categoria': {
            'nombre': categoria['nombre'],
            'descripcion': categoria['descripcion']
        },
        'libros': libros
    })