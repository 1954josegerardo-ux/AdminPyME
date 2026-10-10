import streamlit as st
import pandas as pd
import database as db
from modules import inventario, facturacion, cobrar, pagar, clientes, reportes, configuracion

# ==================== CONFIGURACIÓN DE PÁGINA (PRIMERO) ====================
st.set_page_config(
    page_title="AdminPyME",
    page_icon="📦",
    layout="wide"
)

# ==================== INICIALIZAR BASE DE DATOS ====================

db.crear_tablas()

# Garantizar que exista una configuración por defecto con código Admin
conn = db.conectar()
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM configuracion")
if cursor.fetchone()[0] == 0:
    cursor.execute("""
    INSERT INTO configuracion (nombre_negocio, codigo_admin, numero_factura_inicial, numero_factura_actual)
    VALUES ('Mi Negocio', 'Admin', 1, 0)
    """)
    conn.commit()
conn.close()
# ==================== MENÚ LATERAL ====================
with st.sidebar:
    st.title("📦 AdminPyME")
    st.markdown("### Menú Principal")
    opcion = st.radio(
        "Selecciona un módulo:",
        ["📊 Dashboard", "📦 Inventario", "🧾 Facturación", "💰 Cuentas por Cobrar", "🧾 Cuentas por Pagar", "👥 Clientes", "📈 Reportes", "⚙️ Configuración"],
        label_visibility="collapsed",
        key="menu_principal"
    )

    # Detectar cambio de módulo y limpiar estado
    if 'modulo_actual' not in st.session_state:
        st.session_state.modulo_actual = opcion
    elif st.session_state.modulo_actual != opcion:
    # Cambió de módulo: limpiar estados temporales
        for key in list(st.session_state.keys()):
            if key not in ['modulo_actual', 'menu_principal']:
                del st.session_state[key]
        st.session_state.modulo_actual = opcion
        st.rerun()
    st.markdown("---")
    st.markdown("© 2026 - AdminPyME v1.0")

# ==================== NAVEGACIÓN ====================
if opcion == "📊 Dashboard":
    st.title("📊 Dashboard")
    conn = db.conectar()
    prod = pd.read_sql_query("SELECT COUNT(*) as n FROM productos WHERE activo = 1", conn)["n"][0]
    cli = pd.read_sql_query("SELECT COUNT(*) as n FROM clientes", conn)["n"][0]
    fac = pd.read_sql_query("SELECT COUNT(*) as n FROM facturas", conn)["n"][0]
    conn.close()

    c1, c2, c3 = st.columns(3)
    c1.metric("📦 Productos Activos", prod)
    c2.metric("👥 Clientes", cli)
    c3.metric("🧾 Facturas", fac)

elif opcion == "📦 Inventario":
    inventario.mostrar()

elif opcion == "🧾 Facturación":
    facturacion.mostrar()

elif opcion == "💰 Cuentas por Cobrar":
    cobrar.mostrar()

elif opcion == "🧾 Cuentas por Pagar":
    pagar.mostrar()

elif opcion == "👥 Clientes":
    clientes.mostrar()

elif opcion == "📈 Reportes":
    reportes.mostrar()

elif opcion == "⚙️ Configuración":
    configuracion.mostrar()