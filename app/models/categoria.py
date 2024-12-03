from .base_model import BaseModel

class Categoria(BaseModel):
    collection_name = 'categorias'

    def create_categoria(self, nombre, descripcion):
        categoria_data = {
            'nombre': nombre,
            'descripcion': descripcion
        }
        return self.create(categoria_data)

    def buscar_por_nombre(self, nombre):
        return self.find_one({'nombre': nombre})

    def listar_todas(self):
        return self.find_many()

    def actualizar_categoria(self, categoria_id, nombre=None, descripcion=None):
        update_data = {}
        if nombre is not None:
            update_data['nombre'] = nombre
        if descripcion is not None:
            update_data['descripcion'] = descripcion
            
        if update_data:
            return self.update_one(
                {'_id': self.to_object_id(categoria_id)},
                update_data
            )