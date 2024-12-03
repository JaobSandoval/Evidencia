from datetime import datetime
from .base_model import BaseModel

class Libro(BaseModel):
    collection_name = 'libros'
    def delete_many(self, filter_dict):
        """Elimina múltiples documentos que coincidan con el filtro"""
        return self.collection.delete_many(filter_dict)
    
    def __init__(self):
        super().__init__()
        # Crear índices necesarios
        self.collection.create_index('isbn', unique=True)
        self.collection.create_index('autorId')
        self.collection.create_index('categoriaId')

    def create_libro(self, titulo, autor_id, categoria_id, isbn, copias, fecha_publicacion, editorial):
        libro_data = {
            'titulo': titulo,
            'autorId': self.to_object_id(autor_id),
            'categoriaId': self.to_object_id(categoria_id),
            'isbn': isbn,
            'copias': copias,
            'disponibles': copias,
            'fechaPublicacion': fecha_publicacion,
            'editorial': editorial,
            'activo': True
        }
        result = self.collection.insert_one(libro_data)  # Usar collection.insert_one directamente
        return result  # Esto devolverá un objeto con inserted_id

    def buscar_por_isbn(self, isbn):
        return self.find_one({'isbn': isbn})

    def buscar_por_autor(self, autor_id):
        return self.find_many({'autorId': self.to_object_id(autor_id)})

    def buscar_por_categoria(self, categoria_id):
        return self.find_many({'categoriaId': self.to_object_id(categoria_id)})

    def actualizar_disponibilidad(self, libro_id, cantidad_disponible):
        return self.update_one(
            {'_id': self.to_object_id(libro_id)},
            {'disponibles': cantidad_disponible}
        )

    def desactivar_libro(self, libro_id):
        return self.update_one(
            {'_id': self.to_object_id(libro_id)},
            {'activo': False}
        )