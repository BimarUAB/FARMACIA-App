import pymysql
pymysql.install_as_MySQLdb()

from flask import Flask
from config import Config
from .extensions import db, login_manager, admin, migrate

def create_app():
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
    
    configuracion_admin()
    app.register_blueprint(auth_bp)
    app.register_blueprint(productos_bp, url_prefix='/productos')  
    
    return app

