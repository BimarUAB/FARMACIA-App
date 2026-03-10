"""
Script para ejecutar el SQL directamente en MySQL
y luego verificar Flask-Migrate
"""
import pymysql
from app import create_app
from app.extensions import db

# SQL script proporcionado
SQL_SCRIPT = """
DROP DATABASE IF EXISTS gestion_ventas;
CREATE DATABASE gestion_ventas CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE gestion_ventas;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE,
    password VARCHAR(200) NOT NULL,
    role VARCHAR(50) DEFAULT 'usuario',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE categorias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) UNIQUE NOT NULL,
    descripcion VARCHAR(200),
    activa BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE productos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    precio FLOAT NOT NULL,
    stock INT DEFAULT 0,
    categoria_id INT,
    imagen VARCHAR(200),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (categoria_id) REFERENCES categorias(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE ventas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    total FLOAT NOT NULL,
    user_id INT NOT NULL,
    estado VARCHAR(50) DEFAULT 'completada',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE venta_detalles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    venta_id INT NOT NULL,
    producto_id INT NOT NULL,
    cantidad INT NOT NULL,
    precio_unitario FLOAT NOT NULL,
    FOREIGN KEY (venta_id) REFERENCES ventas(id) ON DELETE CASCADE,
    FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""

def execute_sql_directly():
    """Ejecuta el SQL directamente en MySQL"""
    print("=" * 50)
    print("EJECUTANDO SQL DIRECTAMENTE EN MYSQL")
    print("=" * 50)
    
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            port=3306,
            charset='utf8mb4'
        )
        
        print("✓ Conexión a MySQL establecida")
        
        statements = [s.strip() for s in SQL_SCRIPT.split(';') if s.strip()]
        
        with connection.cursor() as cursor:
            for statement in statements:
                if statement:
                    cursor.execute(statement)
            connection.commit()
        
        print("✓ Base de datos 'gestion_ventas' creada correctamente")
        print("✓ Tablas creadas: users, categorias, productos, ventas, venta_detalles")
        
        with connection.cursor() as cursor:
            cursor.execute("USE gestion_ventas")
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"\n📊 Tablas existentes: {len(tables)}")
            for table in tables:
                print(f"   - {table[0]}")
        
        connection.close()
        return True
        
    except pymysql.err.OperationalError as e:
        print(f"✗ Error de conexión: {e}")
        print("   Asegúrate de que MySQL esté ejecutándose en localhost:3306")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def verify_flask_migrate():
    """Verifica y ejecuta Flask-Migrate"""
    print("\n" + "=" * 50)
    print("VERIFICANDO FLASK-MIGRATE")
    print("=" * 50)
    
    app = create_app()
    
    with app.app_context():
        print("\n📋 Verificando tablas con SQLAlchemy...")
        
        from app.models import User, Categoria, Producto, Venta, VentaDetalle
        from sqlalchemy import inspect
        
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"   Tablas en la base de datos: {len(tables)}")
        for t in tables:
            print(f"   - {t}")
        
        users = User.query.all()
        print(f"\n👥 Usuarios en la base de datos: {len(users)}")
        for u in users:
            print(f"   - {u.username} ({u.role}) - {u.email}")
        
        categorias = Categoria.query.all()
        print(f"\n📁 Categorías: {len(categorias)}")
        
        productos = Producto.query.all()
        print(f"📦 Productos: {len(productos)}")
        
        ventas = Venta.query.all()
        print(f"💰 Ventas: {len(ventas)}")

def main():
    print("\n🚀 INICIANDO CONFIGURACIÓN DE BASE DE DATOS\n")
    
    sql_success = execute_sql_directly()
    
    if sql_success:
        verify_flask_migrate()
        
        print("\n" + "=" * 50)
        print("✅ CONFIGURACIÓN COMPLETA")
        print("=" * 50)
    else:
        print("\n⚠️ No se pudo ejecutar SQL directamente")
        print("   Intentando solo con Flask-Migrate...")
        verify_flask_migrate()

if __name__ == "__main__":
    main()

