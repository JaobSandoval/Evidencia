from datetime import datetime
from .base_model import BaseModel

class Resena(BaseModel):
    collection_name = 'resenas'

    def __init__(self):
        super().__init__()
        # Crear índices necesarios
        self.collection.create_index([('usuarioId', 1), ('libroId', 1)])

    def create_resena(self, usuario_id, libro_id, calificacion, comentario):
        resena_data = {
            'usuarioId': self.to_object_id(usuario_id),
            'libroId': self.to_object_id(libro_id),
            'calificacion': calificacion,
            'comentario': comentario,
            'fecha': datetime.now()
        }
        return self.create(resena_data)

    def buscar_por_libro(self, libro_id):
        return self.find_many({'libroId': self.to_object_id(libro_id)})

    def buscar_por_usuario(self, usuario_id):
        return self.find_many({'usuarioId': self.to_object_id(usuario_id)})

    def calcular_promedio_libro(self, libro_id):
        pipeline = [
            {'$match': {'libroId': self.to_object_id(libro_id)}},
            {'$group': {
                '_id': '$libroId',
                'promedio': {'$avg': '$calificacion'},
                'total_resenas': {'$sum': 1}
            }}
        ]
        result = list(self.collection.aggregate(pipeline))
        return result[0] if result else {'promedio': 0, 'total_resenas': 0}