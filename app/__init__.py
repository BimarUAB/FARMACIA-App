import pymysql
pymysql.install_as_MySQLdb()
from flask import Flask
from config import Config
from .extensions import db, login_manager, admin, migrate

def create_app():
    # ✅ CORREGIDO: __name__ en lugar de name
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    admin.init_app(app)

    from .models import User, Producto, Categoria
    from .admin import configuracion_admin
    from .auth import auth_bp
    from .productos import productos_bp
    from .categorias import categorias_bp
    from .usuarios import usuarios_bp
    from .ventas import ventas_bp
    from .ventas_admin import ventas_admin_bp
    from .chat_routes import chat_bp
    from .routes import reportes_bp

    # Configurar panel admin
    configuracion_admin(app)

    # ✅ REGISTRAR TODOS LOS BLUEPRINTS
    app.register_blueprint(auth_bp)
    app.register_blueprint(productos_bp, url_prefix='/productos')
    app.register_blueprint(categorias_bp, url_prefix='/categorias')
    app.register_blueprint(usuarios_bp, url_prefix='/usuarios')
    app.register_blueprint(ventas_bp, url_prefix='/ventas')
    app.register_blueprint(ventas_admin_bp, url_prefix='/ventas')
    app.register_blueprint(chat_bp, url_prefix='/chatbot')
    app.register_blueprint(reportes_bp, url_prefix='/reportes')

    return app