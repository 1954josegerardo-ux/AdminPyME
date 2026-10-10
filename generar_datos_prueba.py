# ============================================================================
#  GENERADOR DE DATOS DE PRUEBA - AdminPyME
#  Crea productos, clientes, proveedores, compras y facturas coherentes
# ============================================================================
import sqlite3
import random
import datetime

DB_NAME = 'adminpyme.db'

conn = sqlite3.connect(DB_NAME)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# ==================== LIMPIAR TODO ====================
print("🧹 Limpiando base de datos...")
cursor.execute("PRAGMA foreign_keys = OFF")
tablas = ["pagos_creditos", "pagos_por_pagar", "creditos", "cuentas_por_pagar",
          "factura_detalle", "compra_detalle", "facturas", "compras",
          "movimientos_inventario", "clientes", "proveedores", "productos"]
for t in tablas:
    cursor.execute(f"DELETE FROM {t}")
    cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{t}'")
cursor.execute("PRAGMA foreign_keys = ON")
conn.commit()

# ==================== PRODUCTOS ====================
print("📦 Insertando productos...")
productos_data = [
    ("P-001", "Laptop HP 14 pulgadas", "Tecnología", 350, 499, 15, 3),
    ("P-002", "Mouse Inalámbrico Logitech", "Tecnología", 12, 25, 80, 15),
    ("P-003", "Teclado Mecánico Redragon", "Tecnología", 35, 65, 40, 8),
    ("P-004", "Monitor LG 24 pulgadas", "Tecnología", 110, 180, 20, 4),
    ("P-005", "Impresora Epson EcoTank", "Oficina", 190, 280, 12, 2),
    ("P-006", "Silla Ergonómica Oficina", "Mobiliario", 120, 220, 8, 2),
    ("P-007", "Escritorio Moderno", "Mobiliario", 150, 280, 6, 2),
    ("P-008", "Lámpara LED Escritorio", "Oficina", 25, 55, 30, 5),
    ("P-009", "Cafetera Oster", "Electrodomésticos", 45, 85, 18, 4),
    ("P-010", "Microondas LG 20L", "Electrodomésticos", 120, 210, 10, 3),
    ("P-011", "Disco Duro Externo 1TB", "Tecnología", 55, 95, 25, 6),
    ("P-012", "Memoria USB 64GB", "Tecnología", 8, 18, 100, 20),
    ("P-013", "Webcam Logitech HD", "Tecnología", 40, 75, 22, 5),
    ("P-014", "Audífonos Sony Bluetooth", "Tecnología", 60, 110, 15, 4),
    ("P-015", "Papel Bond Resma", "Papelería", 5, 12, 200, 30),
]
for p in productos_data:
    cursor.execute("""
    INSERT INTO productos (codigo, nombre, categoria, precio_compra, precio_venta, stock_actual, stock_minimo)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, p)

# ==================== CLIENTES ====================
print("👥 Insertando clientes...")
clientes_data = [
    ("Comercial El Sol C.A.", "J-12345678-9", "+58 414-1234567", "contacto@elsol.com", "Av. Principal, Caracas"),
    ("María Rodríguez", "V-87654321", "+58 412-9876543", "maria@gmail.com", "Calle 5, Valencia"),
    ("TechSolutions S.A.", "J-98765432-1", "+58 416-5554433", "info@techsol.com", "Centro Empresarial, Maracay"),
    ("Pedro Martínez", "V-11223344", "+58 414-7778899", "pedro@email.com", "Av. Bolívar, Barquisimeto"),
    ("Inversiones La Económica", "J-55555555-5", "+58 412-3334455", "ventas@laeconomica.com", "Zona Industrial, Valencia"),
    ("Ana Gómez", "V-99887766", "+58 414-2223344", "ana.gomez@gmail.com", "Urb. Los Chaguaramos, Caracas"),
    ("Carlos Pérez", "V-44556677", "+58 416-8889900", "carlos.p@email.com", "Av. Las Delicias, Maracay"),
    ("Farmacia San Rafael", "J-77777777-7", "+58 412-1112233", "admin@sanrafael.com", "Calle Comercio, Valencia"),
    ("Juan Fernández", "V-22334455", "+58 414-6667788", "juanf@email.com", "Res. Los Pinos, Barquisimeto"),
    ("Servicios Múltiples C.A.", "J-33333333-3", "+58 416-4445566", "info@smultiples.com", "Av. Libertador, Caracas"),
]
for c in clientes_data:
    cursor.execute("""
    INSERT INTO clientes (nombre, cedula_rif, telefono, email, direccion)
    VALUES (?, ?, ?, ?, ?)
    """, c)

# ==================== PROVEEDORES ====================
print("🏢 Insertando proveedores...")
proveedores_data = [
    ("Distribuidora La Sal. srl.", "J-11111111-1", "+58 414-1111111", "ventas@lasal.com", "Av. Los Pinos, Valencia"),
    ("Comercial El Zorro CA", "J-22222222-2", "+58 414-2222222", "info@elzorro.com", "Calle 10, Caracas"),
    ("Importadora Global Tech", "J-44444444-4", "+58 416-3333322", "compras@globaltech.com", "Zona Franca, Margarita"),
    ("Distribuidora Nacional", "J-66666666-6", "+58 412-5556677", "pedidos@dnacional.com", "Av. Industrial, Valencia"),
]
for p in proveedores_data:
    cursor.execute("""
    INSERT INTO proveedores (nombre, cedula_rif, telefono, email, direccion)
    VALUES (?, ?, ?, ?, ?)
    """, p)

conn.commit()

# Obtener IDs
cursor.execute("SELECT id, precio_venta FROM productos")
productos = cursor.fetchall()
cursor.execute("SELECT id FROM clientes")
clientes = cursor.fetchall()
cursor.execute("SELECT id FROM proveedores")
proveedores = cursor.fetchall()

# ==================== COMPRAS (para abastecer inventario) ====================
print("🛒 Generando compras...")
fecha_base = datetime.date.today() - datetime.timedelta(days=90)

for i in range(15):
    proveedor_id = random.choice(proveedores)["id"]
    dias_atras = random.randint(1, 90)
    fecha_compra = (datetime.date.today() - datetime.timedelta(days=dias_atras)).isoformat()
    numero = f"C-{i+1:06d}"
    condicion = random.choice(["contado", "credito"])
    estado = "pagada" if condicion == "contado" else "credito"

    subtotal = 0
    items = []
    for _ in range(random.randint(1, 4)):
        prod = random.choice(productos)
        cantidad = random.randint(5, 30)
        costo = round(random.uniform(10, 200), 2)
        total_linea = round(cantidad * costo, 2)
        subtotal += total_linea
        items.append((prod["id"], cantidad, costo, total_linea))

    subtotal = round(subtotal, 2)
    impuesto = round(subtotal * 0.16, 2)
    total = round(subtotal + impuesto, 2)
    cursor.execute("""
    INSERT INTO compras (numero_factura, id_proveedor, fecha, subtotal, impuesto, total, estado, condicion_pago, metodo_pago)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (numero, proveedor_id, fecha_compra, subtotal, impuesto, total, estado, condicion, "Efectivo" if condicion == "contado" else ""))

    compra_id = cursor.lastrowid

    for item in items:
        cursor.execute("""
        INSERT INTO compra_detalle (id_compra, id_producto, cantidad, precio_unitario, total_linea)
        VALUES (?, ?, ?, ?, ?)
        """, (compra_id, item[0], item[1], item[2], item[3]))

    if condicion == "credito":
        cursor.execute("""
        INSERT INTO cuentas_por_pagar (id_compra, id_proveedor, monto_total, saldo_pendiente, estado)
        VALUES (?, ?, ?, ?, 'pendiente')
        """, (compra_id, proveedor_id, total, total))

conn.commit()

# ==================== FACTURAS DE VENTA ====================
print("🧾 Generando facturas de venta...")
cursor.execute("UPDATE configuracion SET numero_factura_actual = 0, numero_factura_inicial = 1")

for i in range(50):
    cliente_id = random.choice(clientes)["id"]
    dias_atras = random.randint(0, 90)
    fecha = (datetime.date.today() - datetime.timedelta(days=dias_atras)).isoformat()
    numero = f"F-{i+1:06d}"
    condicion = random.choice(["contado", "credito", "contado", "contado"])
    estado = "pagada" if condicion == "contado" else "credito"
    metodo = random.choice(["Efectivo", "Tarjeta de débito", "Tarjeta de crédito", "Transferencia"]) if condicion == "contado" else ""

    subtotal = 0
    items = []
    for _ in range(random.randint(1, 5)):
        prod = random.choice(productos)
        cantidad = random.randint(1, 4)
        precio = round(prod["precio_venta"], 2)
        total_linea = round(cantidad * precio, 2)
        subtotal += total_linea
        items.append((prod["id"], cantidad, precio, total_linea))

    subtotal = round(subtotal, 2)
    impuesto = round(subtotal * 0.16, 2)
    total = round(subtotal + impuesto, 2)    cursor.execute("""
    INSERT INTO facturas (numero_factura, id_cliente, fecha, subtotal, impuesto, total, estado, condicion_pago, metodo_pago)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (numero, cliente_id, fecha, subtotal, impuesto, total, estado, condicion, metodo))

    factura_id = cursor.lastrowid

    for item in items:
        cursor.execute("""
        INSERT INTO factura_detalle (id_factura, id_producto, cantidad, precio_unitario, total_linea)
        VALUES (?, ?, ?, ?, ?)
        """, (factura_id, item[0], item[1], item[2], item[3]))

    if condicion == "credito":
        cursor.execute("""
        INSERT INTO creditos (id_factura, id_cliente, monto_total, saldo_pendiente, estado)
        VALUES (?, ?, ?, ?, 'pendiente')
        """, (factura_id, cliente_id, total, total))

cursor.execute("UPDATE configuracion SET numero_factura_actual = 50")

conn.commit()

# ==================== RESUMEN ====================
print("\n" + "=" * 50)
print("✅ DATOS DE PRUEBA GENERADOS")
print("=" * 50)
for tabla in ["productos", "clientes", "proveedores", "compras", "facturas", "creditos", "cuentas_por_pagar"]:
    cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
    print(f"  {tabla}: {cursor.fetchone()[0]} registros")

conn.close()
print("\n🎉 Listo para probar los reportes.")