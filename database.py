import sqlite3

DB_NAME = "adminpyme.db"

def conectar():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def crear_tablas():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS productos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT UNIQUE NOT NULL,
        nombre TEXT NOT NULL,
        descripcion TEXT,
        categoria TEXT,
        precio_compra REAL DEFAULT 0,
        precio_venta REAL DEFAULT 0,
        stock_actual INTEGER DEFAULT 0,
        stock_minimo INTEGER DEFAULT 5,
        activo INTEGER DEFAULT 1
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        cedula_rif TEXT,
        telefono TEXT,
        email TEXT,
        direccion TEXT,
        fecha_registro TEXT DEFAULT CURRENT_DATE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS proveedores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        cedula_rif TEXT,
        telefono TEXT,
        email TEXT,
        direccion TEXT,
        fecha_registro TEXT DEFAULT CURRENT_DATE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS facturas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        numero_factura TEXT UNIQUE NOT NULL,
        id_cliente INTEGER,
        fecha TEXT NOT NULL,
        subtotal REAL DEFAULT 0,
        impuesto REAL DEFAULT 0,
        total REAL DEFAULT 0,
        estado TEXT DEFAULT 'pagada',
        condicion_pago TEXT DEFAULT 'contado',
        metodo_pago TEXT DEFAULT '',
        FOREIGN KEY (id_cliente) REFERENCES clientes(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS factura_detalle (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_factura INTEGER NOT NULL,
        id_producto INTEGER NOT NULL,
        cantidad INTEGER NOT NULL,
        precio_unitario REAL NOT NULL,
        total_linea REAL NOT NULL,
        FOREIGN KEY (id_factura) REFERENCES facturas(id),
        FOREIGN KEY (id_producto) REFERENCES productos(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS compras (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        numero_factura TEXT UNIQUE NOT NULL,
        id_proveedor INTEGER,
        fecha TEXT NOT NULL,
        subtotal REAL DEFAULT 0,
        impuesto REAL DEFAULT 0,
        total REAL DEFAULT 0,
        estado TEXT DEFAULT 'pagada',
        condicion_pago TEXT DEFAULT 'contado',
        metodo_pago TEXT DEFAULT '',
        FOREIGN KEY (id_proveedor) REFERENCES proveedores(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS compra_detalle (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_compra INTEGER NOT NULL,
        id_producto INTEGER NOT NULL,
        cantidad INTEGER NOT NULL,
        precio_unitario REAL NOT NULL,
        total_linea REAL NOT NULL,
        FOREIGN KEY (id_compra) REFERENCES compras(id),
        FOREIGN KEY (id_producto) REFERENCES productos(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS creditos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_factura INTEGER NOT NULL,
        id_cliente INTEGER NOT NULL,
        monto_total REAL NOT NULL,
        monto_pagado REAL DEFAULT 0,
        saldo_pendiente REAL NOT NULL,
        fecha_credito TEXT DEFAULT CURRENT_DATE,
        estado TEXT DEFAULT 'pendiente',
        FOREIGN KEY (id_factura) REFERENCES facturas(id),
        FOREIGN KEY (id_cliente) REFERENCES clientes(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pagos_creditos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_credito INTEGER NOT NULL,
        monto_abonado REAL NOT NULL,
        fecha_pago TEXT DEFAULT CURRENT_DATE,
        metodo_pago TEXT DEFAULT 'Efectivo',
        FOREIGN KEY (id_credito) REFERENCES creditos(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cuentas_por_pagar (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_compra INTEGER NOT NULL,
        id_proveedor INTEGER NOT NULL,
        monto_total REAL NOT NULL,
        monto_pagado REAL DEFAULT 0,
        saldo_pendiente REAL NOT NULL,
        fecha_credito TEXT DEFAULT CURRENT_DATE,
        estado TEXT DEFAULT 'pendiente',
        FOREIGN KEY (id_compra) REFERENCES compras(id),
        FOREIGN KEY (id_proveedor) REFERENCES proveedores(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pagos_por_pagar (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_cuenta INTEGER NOT NULL,
        monto_abonado REAL NOT NULL,
        fecha_pago TEXT DEFAULT CURRENT_DATE,
        metodo_pago TEXT DEFAULT 'Efectivo',
        FOREIGN KEY (id_cuenta) REFERENCES cuentas_por_pagar(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS movimientos_inventario (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_producto INTEGER NOT NULL,
        tipo TEXT NOT NULL,
        cantidad INTEGER NOT NULL,
        fecha TEXT DEFAULT CURRENT_DATE,
        motivo TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS configuracion (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_negocio TEXT,
        rif TEXT,
        direccion TEXT,
        telefono TEXT,
        email TEXT,
        impuesto_porcentaje REAL DEFAULT 16.0,
        moneda TEXT DEFAULT 'USD',
        numero_factura_inicial INTEGER DEFAULT 1,
        numero_factura_actual INTEGER DEFAULT 0,
        codigo_admin TEXT DEFAULT 'Admin'
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        usuario TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        rol TEXT DEFAULT 'admin'
    )
    """)

    conn.commit()
    conn.close()

def insertar_datos_ejemplo():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM productos")
    count = cursor.fetchone()[0]

    if count == 0:
        productos = [
            ("P-001", "Laptop HP 14 pulgadas", "Laptop de uso diario", "Tecnología", 350, 499, 10, 3),
            ("P-002", "Mouse Inalámbrico Logitech", "Mouse ergonómico", "Tecnología", 12, 25, 50, 15),
            ("P-003", "Teclado Mecánico Redragon", "Teclado gamer RGB", "Tecnología", 35, 65, 25, 8),
            ("P-004", "Monitor LG 24 pulgadas", "Monitor Full HD", "Tecnología", 110, 180, 8, 4),
            ("P-005", "Impresora Epson EcoTank", "Impresora de tinta continua", "Oficina", 190, 280, 6, 2),
        ]
        for prod in productos:
            cursor.execute("""
            INSERT INTO productos (codigo, nombre, descripcion, categoria, precio_compra, precio_venta, stock_actual, stock_minimo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, prod)

        clientes = [
            ("Comercial El Sol C.A.", "J-12345678-9", "+58 414-1234567", "contacto@elsol.com", "Av. Principal, Caracas"),
            ("María Rodríguez", "V-87654321", "+58 412-9876543", "maria@gmail.com", "Calle 5, Valencia"),
            ("TechSolutions S.A.", "J-98765432-1", "+58 416-5554433", "info@techsol.com", "Centro Empresarial, Maracay"),
        ]
        for cli in clientes:
            cursor.execute("""
            INSERT INTO clientes (nombre, cedula_rif, telefono, email, direccion)
            VALUES (?, ?, ?, ?, ?)
            """, cli)

        proveedores = [
            ("Distribuidora La Sal. srl.", "J-11111111-1", "+58 414-1111111", "ventas@lasal.com", "Av. Los Pinos, Valencia"),
            ("Comercial El Zorro CA", "J-22222222-2", "+58 414-2222222", "info@elzorro.com", "Calle 10, Caracas"),
        ]
        for prov in proveedores:
            cursor.execute("""
            INSERT INTO proveedores (nombre, cedula_rif, telefono, email, direccion)
            VALUES (?, ?, ?, ?, ?)
            """, prov)

        cursor.execute("""
        INSERT INTO configuracion (nombre_negocio, direccion, telefono, impuesto_porcentaje, moneda)
        VALUES (?, ?, ?, ?, ?)
        """, ("Mi Negocio PYME", "Av. Principal, Local 15", "+58 000-0000000", 16.0, "USD"))

        cursor.execute("SELECT id FROM usuarios WHERE usuario = ?", ("admin",))
        if not cursor.fetchone():
            cursor.execute("""
            INSERT INTO usuarios (nombre, usuario, password_hash, rol)
            VALUES (?, ?, ?, ?)
            """, ("Administrador", "admin", "admin123", "admin"))

        conn.commit()
    conn.close()

def inicializar_si_vacia():
    """Crea las tablas y configuración mínima si la base está vacía."""
    crear_tablas()

    conn = conectar()
    cursor = conn.cursor()

    # Verificar si hay configuración
    cursor.execute("SELECT COUNT(*) FROM configuracion")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
        INSERT INTO configuracion 
        (nombre_negocio, codigo_admin, numero_factura_inicial, numero_factura_actual)
        VALUES ('AdminPyME Demo', 'Admin', 1, 0)
        """)
        conn.commit()
        print("✅ Configuración inicial creada")

    conn.close()
    print("✅ Base de datos inicializada")

if __name__ == "__main__":
    inicializar_si_vacia()