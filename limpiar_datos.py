import sqlite3
import os

DB_NAME = 'adminpyme.db'

if not os.path.exists(DB_NAME):
    print(f"❌ No se encontró {DB_NAME}")
    exit()

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

cursor.execute("PRAGMA foreign_keys = OFF")

# Lista completa de tablas
tablas = [
    "pagos_creditos",
    "pagos_por_pagar",
    "creditos",
    "cuentas_por_pagar",
    "factura_detalle",
    "compra_detalle",
    "facturas",
    "compras",
    "movimientos_inventario",
    "clientes",
    "proveedores",
    "productos",
    "usuarios",
    "configuracion"
]

for tabla in tablas:
    try:
        cursor.execute(f"DELETE FROM {tabla}")
        filas_borradas = cursor.rowcount
        cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{tabla}'")
        print(f"✅ {tabla}: {filas_borradas} registros eliminados")
    except Exception as e:
        print(f"⚠️ {tabla}: {e}")

cursor.execute("PRAGMA foreign_keys = ON")
conn.commit()

# Verificación posterior
print("\n=== Verificación ===")
for tabla in tablas:
    cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
    count = cursor.fetchone()[0]
    estado = "✅ vacía" if count == 0 else f"⚠️ {count} registros"
    print(f"  {tabla}: {estado}")

conn.close()
print("\n🎉 Base de datos limpiada. Lista para comenzar de cero.")
