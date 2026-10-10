import streamlit as st
import pandas as pd
import database as db

def mostrar():
    st.title("👥 Clientes")
    st.markdown("Gestiona los datos de tus clientes")

    tab1, tab2, tab3 = st.tabs(["📄 Ver Clientes", "➕ Agregar Cliente", "🔍 Buscar"])

    with tab1:
        st.subheader("Listado de Clientes")
        conn = db.conectar()
        df_clientes = pd.read_sql_query("""
            SELECT id, nombre, cedula_rif, telefono, email, direccion, fecha_registro
            FROM clientes ORDER BY nombre
        """, conn)
        conn.close()
        if df_clientes.empty:
            st.info("No hay clientes registrados.")
        else:
            st.dataframe(df_clientes, use_container_width=True, height=400)
            st.metric("Total Clientes", len(df_clientes))

    with tab2:
        st.subheader("Registrar Nuevo Cliente")
        with st.form("form_cliente_mod"):
            col1, col2 = st.columns(2)
            with col1:
                nombre = st.text_input("Nombre del cliente *")
                cedula_rif = st.text_input("Cédula / RIF")
                telefono = st.text_input("Teléfono")
            with col2:
                email = st.text_input("Correo electrónico")
                direccion = st.text_area("Dirección")
            submit = st.form_submit_button("💾 Guardar Cliente", type="primary")
            if submit:
                if not nombre:
                    st.error("El nombre es obligatorio.")
                else:
                    conn = db.conectar()
                    cursor = conn.cursor()
                    try:
                        cursor.execute("""
                        INSERT INTO clientes (nombre, cedula_rif, telefono, email, direccion)
                        VALUES (?, ?, ?, ?, ?)
                        """, (nombre, cedula_rif, telefono, email, direccion))
                        conn.commit()
                        st.success(f"✅ Cliente '{nombre}' guardado correctamente.")
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
                    finally:
                        conn.close()

    with tab3:
        st.subheader("Buscar Cliente")
        busqueda = st.text_input("Buscar por nombre, cédula o RIF")
        if busqueda:
            conn = db.conectar()
            df_busqueda = pd.read_sql_query("""
                SELECT * FROM clientes WHERE nombre LIKE ? OR cedula_rif LIKE ?
            """, conn, params=(f"%{busqueda}%", f"%{busqueda}%"))
            conn.close()
            if df_busqueda.empty:
                st.warning("Sin resultados.")
            else:
                st.dataframe(df_busqueda, use_container_width=True)