import streamlit as st
import pandas as pd
import database as db
import time

def obtener_codigo_admin():
    """Obtiene el código de administrador desde la base de datos."""
    conn = db.conectar()
    df = pd.read_sql_query("SELECT codigo_admin FROM configuracion ORDER BY id DESC LIMIT 1", conn)
    conn.close()
    if df.empty:
        return "Admin"
    return str(df.iloc[0]["codigo_admin"])

def mostrar():
    st.title("⚙️ Configuración del Sistema")
    st.markdown("Datos de la empresa y parámetros del sistema")

    # ==================== CONTROL DE ACCESO ====================
    st.warning("🔐 Esta sección requiere código de administrador.")

    codigo_ingresado = st.text_input("Código de administrador:", type="password", key="admin_config")

    codigo_correcto = obtener_codigo_admin()

    if codigo_ingresado != codigo_correcto:
        if codigo_ingresado:
            st.error("❌ Código incorrecto.")
        return

    st.success("✅ Acceso concedido.")

    # ==================== FORMULARIO DE CONFIGURACIÓN ====================
    conn = db.conectar()
    df_config = pd.read_sql_query("SELECT * FROM configuracion ORDER BY id DESC LIMIT 1", conn)
    conn.close()

    if df_config.empty:
        st.info("📌 Primera configuración: ingresa los datos de tu negocio.")
        config = None
    else:
        config = df_config.iloc[0]

    with st.form("form_configuracion"):
        st.markdown("### 🏢 Datos del Negocio")

        col1, col2 = st.columns(2)
        with col1:
            nombre_negocio = st.text_input(
                "Nombre del negocio *",
                value=str(config["nombre_negocio"]) if config is not None and config["nombre_negocio"] else ""
            )
            rif = st.text_input(
                "RIF / Cédula",
                value=str(config["rif"]) if config is not None and config["rif"] else ""
            )
            telefono = st.text_input(
                "Teléfono",
                value=str(config["telefono"]) if config is not None and config["telefono"] else ""
            )
        with col2:
            direccion = st.text_input(
                "Dirección",
                value=str(config["direccion"]) if config is not None and config["direccion"] else ""
            )
            email = st.text_input(
                "Correo electrónico",
                value=str(config["email"]) if config is not None and config["email"] else ""
            )

        st.markdown("### 💰 Parámetros Fiscales")
        col3, col4 = st.columns(2)
        with col3:
            impuesto = st.number_input(
                "Porcentaje de impuesto (%)",
                min_value=0.0,
                max_value=50.0,
                step=0.5,
                value=float(config["impuesto_porcentaje"]) if config is not None else 16.0
            )
        with col4:
            monedas = ["USD", "VES", "COP", "EUR", "MXN", "PEN", "ARS"]
            indice_moneda = monedas.index(str(config["moneda"])) if config is not None and str(config["moneda"]) in monedas else 0
            moneda = st.selectbox("Moneda", monedas, index=indice_moneda)

        st.markdown("### 🧾 Numeración de Facturas")
        st.caption("Define el número inicial de facturación. El sistema incrementará automáticamente.")

        col5, col6 = st.columns(2)
        with col5:
            numero_inicial = st.number_input(
                "Número inicial de factura",
                min_value=1,
                step=1,
                value=int(config["numero_factura_inicial"]) if config is not None else 1
            )
        with col6:
            numero_actual = st.number_input(
                "Último número usado",
                min_value=0,
                step=1,
                value=int(config["numero_factura_actual"]) if config is not None else 0,
                disabled=True,
                help="Este campo se actualiza automáticamente"
            )

        st.markdown("### 🔐 Código de Acceso al Sistema")
        st.caption("Este código protege las secciones de Configuración y Administración de Inventario.")

        col7, col8 = st.columns(2)
        with col7:
            nuevo_codigo = st.text_input(
                "Nuevo código de administrador",
                value=str(config["codigo_admin"]) if config is not None and config["codigo_admin"] else "Admin",
                help="Cámbialo por uno que solo tú conozcas"
            )
        with col8:
            confirmar_codigo = st.text_input(
                "Confirmar nuevo código",
                value=str(config["codigo_admin"]) if config is not None and config["codigo_admin"] else "Admin"
            )

        st.markdown("---")

        guardar = st.form_submit_button("💾 Guardar Configuración", type="primary", use_container_width=True)

        if guardar:
            if not nombre_negocio:
                st.error("El nombre del negocio es obligatorio.")
            elif not nuevo_codigo:
                st.error("El código de administrador no puede estar vacío.")
            elif nuevo_codigo != confirmar_codigo:
                st.error("Los códigos no coinciden. Verifica ambos campos.")
            else:
                conn = db.conectar()
                cursor = conn.cursor()
                try:
                    if config is None:
                        cursor.execute("""
                        INSERT INTO configuracion 
                        (nombre_negocio, rif, direccion, telefono, email, impuesto_porcentaje, moneda, 
                         numero_factura_inicial, numero_factura_actual, codigo_admin)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (nombre_negocio, rif, direccion, telefono, email, impuesto, moneda, 
                              numero_inicial, numero_inicial - 1, nuevo_codigo))
                    else:
                        cursor.execute("""
                        UPDATE configuracion 
                        SET nombre_negocio = ?, rif = ?, direccion = ?, telefono = ?, email = ?,
                            impuesto_porcentaje = ?, moneda = ?, numero_factura_inicial = ?, codigo_admin = ?
                        WHERE id = ?
                        """, (nombre_negocio, rif, direccion, telefono, email, impuesto, moneda, 
                              numero_inicial, nuevo_codigo, int(config["id"])))
                    conn.commit()
                    st.success("✅ Configuración guardada correctamente.")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {e}")
                finally:
                    conn.close()