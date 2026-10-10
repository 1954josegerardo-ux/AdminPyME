import sqlite3

conn = sqlite3.connect('adminpyme.db')
cursor = conn.cursor()

# Redondear campos monetarios en todas las tablas
tablas_campos = {
    "productos": ["precio_compra", "precio_venta"],
    "facturas": ["subtotal", "impuesto", "total"],
    "factura_detalle": ["precio_unitario", "total_linea"],
    "compras": ["subtotal", "impuesto", "total"],
    "compra_detalle": ["precio_unitario", "total_linea"],
    "creditos": ["monto_total", "monto_pagado", "saldo_pendiente"],
    "pagos_creditos": ["monto_abonado"],
    "cuentas_por_pagar": ["monto_total", "monto_pagado", "saldo_pendiente"],
    "pagos_por_pagar": ["monto_abonado"],
}

for tabla, campos in tablas_campos.items():
    for campo in campos:
        cursor.execute(f"UPDATE {tabla} SET {campo} = ROUND({campo}, 2)")
        print(f"✅ {tabla}.{campo} redondeado")

# Corregir saldos pendientes que quedaron casi en cero
cursor.execute("""
UPDATE cuentas_por_pagar 
SET saldo_pendiente = 0, estado = 'pagado'
WHERE saldo_pendiente < 0.01
""")
print(f"✅ Cuentas por pagar casi en cero corregidas: {cursor.rowcount}")

cursor.execute("""
UPDATE creditos 
SET saldo_pendiente = 0, estado = 'pagado'
WHERE saldo_pendiente < 0.01
""")
print(f"✅ Créditos casi en cero corregidos: {cursor.rowcount}")

conn.commit()
conn.close()
print("\n🎉 Redondeo completo.")