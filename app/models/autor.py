from datetime import datetime
from .base_model import BaseModel
from bson import ObjectId

class Autor(BaseModel):
    collection_name = 'autores'

    def create_autor(self, nombre, nacionalidad, biografia, fecha_nacimiento):
        autor_data = {
            'nombre': nombre,
            'nacionalidad': nacionalidad,
            'biografia': biografia,
            'fechaNacimiento': fecha_nacimiento,
            'activo': True
        }
        return self.create(autor_data)

    def buscar_por_nombre(self, nombre):
        return self.find_many({
            'nombre': {'$regex': nombre, '$options': 'i'},
            'activo': True
        })

    def buscar_por_nacionalidad(self, nacionalidad):
        return self.find_many({
            'nacionalidad': nacionalidad,
            'activo': True
        })

    def buscar_activos(self):
        return self.find_many({'activo': True})

    def desactivar_autor(self, autor_id):
        # Al desactivar un autor, marcamos sus libros como sin autor
        from .libro import Libro
        libro_model = Libro()
        
        # Primero desactivamos el autor
        self.update_one(
            {'_id': self.to_object_id(autor_id)},
            {'activo': False}
        )
        
        # Luego actualizamos los libros
        libro_model.update_many(
            {'autorId': self.to_object_id(autor_id)},
            {'autorId': None}
        )
    
    def obtener_estadisticas(self, autor_id):
        from .libro import Libro
        from .resena import Resena
        
        libro_model = Libro()
        resena_model = Resena()
        
        # Obtener todos los libros del autor
        libros = libro_model.buscar_por_autor(autor_id)
        
        # Calcular estadísticas
        total_libros = len(libros)
        total_copias = sum(libro.get('copias', 0) for libro in libros)
        
        # Calcular promedio de calificaciones de todos sus libros
        calificaciones_totales = 0
        numero_resenas = 0
        
        for libro in libros:
            stats = resena_model.calcular_promedio_libro(str(libro['_id']))
            if stats['total_resenas'] > 0:
                calificaciones_totales += stats['promedio'] * stats['total_resenas']
                numero_resenas += stats['total_resenas']
        
        promedio_general = calificaciones_totales / numero_resenas if numero_resenas > 0 else 0
        
        return {
            'total_libros': total_libros,
            'total_copias': total_copias,
            'promedio_calificacion': round(promedio_general, 2),
            'total_resenas': numero_resenas
        }
    