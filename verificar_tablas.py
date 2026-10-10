import sqlite3

conn = sqlite3.connect('adminpyme.db')
c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tablas = [r[0] for r in c.fetchall()]
conn.close()

print("=== Tablas existentes ===")
for t in tablas:
    print(f"✅ {t}")