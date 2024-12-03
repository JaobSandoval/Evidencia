from bson import ObjectId
from app.database.connection import DatabaseConnection

class BaseModel:
    collection_name = None

    def __init__(self):
        if self.collection_name is None:
            raise NotImplementedError("collection_name debe ser definido en la clase hija")
        self.db = DatabaseConnection.get_instance().get_database()
        self.collection = self.db[self.collection_name]

    def find_one(self, query):
        try:
            result = self.collection.find_one(query)
            if result and '_id' in result:
                result['_id'] = str(result['_id'])
            return result
        except Exception as e:
            print(f"Error en find_one: {str(e)}")
            return None

    def find_many(self, query=None):
        if query is None:
            query = {}
        try:
            cursor = self.collection.find(query)
            result = list(cursor)
            # Convertir ObjectId a string
            for doc in result:
                if '_id' in doc:
                    doc['_id'] = str(doc['_id'])
            return result
        except Exception as e:
            print(f"Error en find_many: {str(e)}")
            return []

    def create(self, data):
        try:
            result = self.collection.insert_one(data)
            return result.inserted_id
        except Exception as e:
            print(f"Error en create: {str(e)}")
            raise

    def update_one(self, query, update_data):
        try:
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
        except:
            raise ValueError('ID inválido')