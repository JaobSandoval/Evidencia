from pymongo import MongoClient
import json
from datetime import datetime

client = MongoClient('mongodb://localhost:27017/')
db = client['BibliotecaDigital']

with open('database/sample_data.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

for collection_name, items in data.items():
    collection = db[collection_name]
    for item in items:
        for key, value in item.items():
            if isinstance(value, str) and ('fecha' in key.lower()):
                item[key] = datetime.strptime(value, '%Y-%m-%d')
    
    if items:
        collection.insert_many(items)
        print(f"Insertados {len(items)} documentos en {collection_name}")

print("Datos insertados correctamente")
client.close()