import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev')
    MONGO_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/BibliotecaDigital')
    DB_NAME = os.getenv('DB_NAME', 'BibliotecaDigital')