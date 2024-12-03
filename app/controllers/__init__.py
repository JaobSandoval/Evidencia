# Similar al de models, puede estar vacío o exportar los blueprints
from .libro_controller import libro_bp
from .usuario_controller import usuario_bp
from .prestamo_controller import prestamo_bp
from .autor_controller import autor_bp
from .resena_controller import resena_bp
from .categoria_controller import categoria_bp

__all__ = ['libro_bp', 'usuario_bp', 'prestamo_bp', 'autor_bp', 'resena_bp', 'categoria_bp']