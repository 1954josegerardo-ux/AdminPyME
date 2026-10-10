import sqlite3

conn = sqlite3.connect('adminpyme.db')
c = conn.cursor()

print("=== PRODUCTOS ===")
c.execute("SELECT id, codigo, nombre, precio_compra, precio_venta, stock_actual FROM productos")
for r in c.fetchall():
    print(f"  ID:{r[0]} | {r[1]} | {r[2]} | Costo:${r[3]} | Venta:${r[4]} | Stock:{r[5]}")

print("\n=== CLIENTES ===")
c.execute("SELECT id, nombre FROM clientes")
for r in c.fetchall():
    print(f"  ID:{r[0]} | {r[1]}")

print("\n=== PROVEEDORES ===")
c.execute("SELECT id, nombre FROM proveedores")
for r in c.fetchall():
    print(f"  ID:{r[0]} | {r[1]}")

conn.close()