from datetime import datetime, timedelta
from .base_model import BaseModel

class Prestamo(BaseModel):
    collection_name = 'prestamos'

    def __init__(self):
        super().__init__()
        # Crear índices necesarios
        self.collection.create_index([('usuarioId', 1), ('libroId', 1)])

    def create_prestamo(self, usuario_id, libro_id, dias_prestamo=14):
        fecha_prestamo = datetime.now()
        fecha_devolucion = fecha_prestamo + timedelta(days=dias_prestamo)
        
        prestamo_data = {
            'usuarioId': self.to_object_id(usuario_id),
            'libroId': self.to_object_id(libro_id),
            'fechaPrestamo': fecha_prestamo,
            'fechaDevolucion': fecha_devolucion,
            'fechaDevuelto': None,
            'multa': 0,
            'estado': 'ACTIVO'
        }
        return self.create(prestamo_data)

    def registrar_devolucion(self, prestamo_id):
        fecha_devuelto = datetime.now()
        prestamo = self.find_one({'_id': self.to_object_id(prestamo_id)})
        
        # Calcular multa si hay retraso
        multa = 0
        if fecha_devuelto > prestamo['fechaDevolucion']:
            dias_retraso = (fecha_devuelto - prestamo['fechaDevolucion']).days
            multa = dias_retraso * 10  # 10 pesos por día de retraso

        return self.update_one(
            {'_id': self.to_object_id(prestamo_id)},
            {
                'fechaDevuelto': fecha_devuelto,
                'multa': multa,
                'estado': 'DEVUELTO'
            }
        )

    def buscar_prestamos_usuario(self, usuario_id):
        return self.find_many({'usuarioId': self.to_object_id(usuario_id)})

    def buscar_prestamos_activos(self):
        return self.find_many({'estado': 'ACTIVO'})

    def buscar_prestamos_vencidos(self):
        return self.find_many({
            'estado': 'ACTIVO',
            'fechaDevolucion': {'$lt': datetime.now()}
        })