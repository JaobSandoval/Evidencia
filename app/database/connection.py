from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

class DatabaseConnection:
    _instance = None

    @staticmethod
    def get_instance():
        if DatabaseConnection._instance is None:
            DatabaseConnection()
        return DatabaseConnection._instance

    def __init__(self):
        if DatabaseConnection._instance is not None:
            raise Exception("Esta clase es un Singleton!")
        else:
            self.client = MongoClient(os.getenv('MONGODB_URI'))
            self.db = self.client[os.getenv('DB_NAME')]
            DatabaseConnection._instance = self

    def get_database(self):
        return self.db

    def close_connection(self):
        self.client.close()