from flask import Flask, render_template  # Agregamos render_template aquí
from flask_pymongo import PyMongo
from config import Config

mongo = PyMongo()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Inicializar extensiones
    mongo.init_app(app)
    
    # Registrar blueprints
    from app.controllers.libro_controller import libro_bp
    from app.controllers.usuario_controller import usuario_bp
    from app.controllers.prestamo_controller import prestamo_bp
    from app.controllers.autor_controller import autor_bp
    from app.controllers.resena_controller import resena_bp
    from app.controllers.categoria_controller import categoria_bp
    
    app.register_blueprint(libro_bp, url_prefix='/libros')
    app.register_blueprint(usuario_bp, url_prefix='/usuarios')
    app.register_blueprint(prestamo_bp, url_prefix='/prestamos')
    app.register_blueprint(autor_bp, url_prefix='/autores')
    app.register_blueprint(resena_bp, url_prefix='/resenas')
    app.register_blueprint(categoria_bp, url_prefix='/categorias')
    
    # Ruta principal
    @app.route('/')
    def index():
        return render_template('index.html')
    
    return app