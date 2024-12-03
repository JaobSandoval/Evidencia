from datetime import datetime
from .base_model import BaseModel
from bson import ObjectId

class Usuario(BaseModel):
    collection_name = 'usuarios'

    def __init__(self):
        super().__init__()
        # Crear índice único para email
        self.collection.create_index('email', unique=True)

    def create_usuario(self, nombre, email, direccion, telefono):
        try:
            # Verificar si el email ya existe
            if self.buscar_por_email(email):
                raise ValueError('El email ya está registrado')

            usuario_data = {
                'nombre': nombre.strip(),
                'email': email.lower().strip(),
                'direccion': direccion.strip(),
                'telefono': telefono.strip(),
                'fechaRegistro': datetime.now(),
                'activo': True
            }
            
            # Usar directamente collection.insert_one
            result = self.collection.insert_one(usuario_data)
            return result.inserted_id
            
        except Exception as e:
            print(f"Error al crear usuario: {str(e)}")
            raise

    def buscar_por_email(self, email):
        if not email:
            return None
        return self.find_one({'email': email.lower().strip()})

    def find_many(self, query=None):
        if query is None:
            query = {}
        try:
            result = list(self.collection.find(query))
            # Convertir ObjectId a string
            for doc in result:
                if '_id' in doc:
                    doc['_id'] = str(doc['_id'])
            return result
        except Exception as e:
            print(f"Error en find_many: {str(e)}")
            return []

    def update_one(self, query, update_data):
        try:
            # Asegurarse de que los datos están limpios
            if 'email' in update_data:
                update_data['email'] = update_data['email'].lower().strip()
            if 'nombre' in update_data:
                update_data['nombre'] = update_data['nombre'].strip()
            if 'telefono' in update_data:
                update_data['telefono'] = update_data['telefono'].strip()
            if 'direccion' in update_data:
                update_data['direccion'] = update_data['direccion'].strip()

            return self.collection.update_one(query, {'$set': update_data})
        except Exception as e:
            print(f"Error en update_one: {str(e)}")
            raise

    def delete_one(self, query):
        try:
            return self.collection.delete_one(query)
        except Exception as e:
            print(f"Error en delete_one: {str(e)}")
            raise

    @staticmethod
    def to_object_id(id):
        try:
            return ObjectId(id)
        except Exception as e:
            print(f"Error al convertir a ObjectId: {str(e)}")
            raise ValueError('ID inválido')