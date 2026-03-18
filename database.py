import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "taller.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            telefono TEXT,
            email TEXT,
            direccion TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vehiculos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            marca TEXT NOT NULL,
            modelo TEXT NOT NULL,
            anio INTEGER,
            placa TEXT UNIQUE,
            vin TEXT,
            kilometraje INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS repuestos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE NOT NULL,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            precio_unitario REAL NOT NULL,
            cantidad_stock INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ordenes_servicio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehiculo_id INTEGER NOT NULL,
            cliente_id INTEGER NOT NULL,
            fecha_ingreso TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_entrega TIMESTAMP,
            estado TEXT DEFAULT 'Pendiente',
            descripcion TEXT,
            observaciones TEXT,
            subtotal REAL DEFAULT 0,
            iva REAL DEFAULT 0,
            total REAL DEFAULT 0,
            kilometraje_ingreso INTEGER,
            kilometraje_salida INTEGER,
            FOREIGN KEY (vehiculo_id) REFERENCES vehiculos(id),
            FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS servicios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            orden_id INTEGER NOT NULL,
            descripcion TEXT NOT NULL,
            cantidad INTEGER DEFAULT 1,
            precio REAL NOT NULL,
            FOREIGN KEY (orden_id) REFERENCES ordenes_servicio(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orden_repuestos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            orden_id INTEGER NOT NULL,
            repuesto_id INTEGER NOT NULL,
            cantidad INTEGER DEFAULT 1,
            precio_unitario REAL NOT NULL,
            FOREIGN KEY (orden_id) REFERENCES ordenes_servicio(id),
            FOREIGN KEY (repuesto_id) REFERENCES repuestos(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventario_movimientos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            repuesto_id INTEGER NOT NULL,
            tipo TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (repuesto_id) REFERENCES repuestos(id)
        )
    """)

    conn.commit()
    conn.close()
    print("Base de datos inicializada correctamente")


if __name__ == "__main__":
    init_db()
