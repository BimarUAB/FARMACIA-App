USE gestion_ventas;

-- Eliminar tablas en PLURAL (las que creaste manualmente)
DROP TABLE IF EXISTS venta_detalles;
DROP TABLE IF EXISTS ventas;
DROP TABLE IF EXISTS productos;
DROP TABLE IF EXISTS categorias;
DROP TABLE IF EXISTS users;

-- Verificar que solo queden las tablas en singular
SHOW TABLES;

-- Eliminar base de datos completa
DROP DATABASE IF EXISTS gestion_ventas;

-- Crear base de datos
CREATE DATABASE gestion_ventas CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE gestion_ventas;

-- Tablas en SINGULAR (como las crea Flask)
CREATE TABLE user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE,
    password VARCHAR(200) NOT NULL,
    role VARCHAR(50) DEFAULT 'usuario',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE categoria (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) UNIQUE NOT NULL,
    descripcion VARCHAR(200),
    activa BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE producto (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    precio FLOAT NOT NULL,
    stock INT DEFAULT 0,
    categoria_id INT,
    imagen VARCHAR(200),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (categoria_id) REFERENCES categoria(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE venta (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    total FLOAT NOT NULL,
    user_id INT NOT NULL,
    estado VARCHAR(50) DEFAULT 'completada',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE venta_detalle (
    id INT AUTO_INCREMENT PRIMARY KEY,
    venta_id INT NOT NULL,
    producto_id INT NOT NULL,
    cantidad INT NOT NULL,
    precio_unitario FLOAT NOT NULL,
    FOREIGN KEY (venta_id) REFERENCES venta(id) ON DELETE CASCADE,
    FOREIGN KEY (producto_id) REFERENCES producto(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

SHOW TABLES;

select * from user;
select * from categoria;
select * from producto;
select * from venta;
select * from venta_detalle;