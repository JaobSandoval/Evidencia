from connection import DatabaseConnection

def init_database():
    db = DatabaseConnection.get_instance().get_database()
    
    # Crear colecciones
    db.create_collection('usuarios')
    db.create_collection('libros')
    db.create_collection('autores')
    db.create_collection('prestamos')
    db.create_collection('resenas')
    db.create_collection('categorias')
    
    # Crear indices
    db.usuarios.create_index('email', unique=True)
    db.libros.create_index('isbn', unique=True)
    db.libros.create_index('autorId')
    db.libros.create_index('categoriaId')
    db.prestamos.create_index([('usuarioId', 1), ('libroId', 1)])
    db.resenas.create_index([('usuarioId', 1), ('libroId', 1)])
    
    print("Base de datos inicializada correctamente")

if __name__ == "__main__":
    init_database()