import streamlit as st
import pandas as pd
import database as db
import time

def mostrar():
    st.title("📦 Inventario")
    st.markdown("Gestiona productos, stock y precios")

    tab1, tab2, tab3, tab4 = st.tabs(["📄 Ver Productos", "➕ Agregar Producto", "🔍 Buscar", "🔐 Admin"])

    with tab1:
        st.subheader("Listado de Productos")
        conn = db.conectar()
        df = pd.read_sql_query("""
            SELECT id, codigo, nombre, categoria, precio_compra, precio_venta, stock_actual, stock_minimo
            FROM productos
            WHERE activo = 1
            ORDER BY nombre
        """, conn)
        conn.close()

        if df.empty:
            st.info("No hay productos registrados.")
        else:
            st.dataframe(df, use_container_width=True, height=400)
            total_productos = len(df)
            total_stock = df["stock_actual"].sum()
            productos_bajos = len(df[df["stock_actual"] <= df["stock_minimo"]])

            col1, col2, col3 = st.columns(3)
            col1.metric("Total Productos", total_productos)
            col2.metric("Unidades en Stock", total_stock)
            col3.metric("⚠️ Stock Bajo", productos_bajos)

    with tab2:
        st.subheader("Registrar Nuevo Producto")
        st.caption("💡 Completa los datos y pulsa **Aceptar y Guardar**. El formulario se limpiará automáticamente para el siguiente producto.")

        # Contador para forzar limpieza del formulario
        if 'form_producto_key' not in st.session_state:
            st.session_state.form_producto_key = 0

        with st.form(f"form_producto_{st.session_state.form_producto_key}"):
            col1, col2 = st.columns(2)
            with col1:
                codigo = st.text_input("Código *")
                nombre = st.text_input("Nombre del producto *")
                descripcion = st.text_area("Descripción")
            with col2:
                categoria = st.text_input("Categoría")
                precio_compra = st.number_input("Precio de compra", min_value=0.0, step=0.01)
                precio_venta = st.number_input("Precio de venta", min_value=0.0, step=0.01)

            col3, col4 = st.columns(2)
            with col3:
                stock_actual = st.number_input("Stock inicial", min_value=0, step=1)
            with col4:
                stock_minimo = st.number_input("Stock mínimo", min_value=0, step=1, value=5)

            col_aceptar, col_cancelar = st.columns(2)

            with col_aceptar:
                submit = st.form_submit_button("✅ Aceptar y Guardar", type="primary", use_container_width=True)

            with col_cancelar:
                cancelar = st.form_submit_button("❌ Cancelar", use_container_width=True)

            if submit:
                if not codigo or not nombre:
                    st.error("Código y nombre son obligatorios.")
                else:
                    conn = db.conectar()
                    cursor = conn.cursor()
                    try:
                        cursor.execute("""
                        INSERT INTO productos (codigo, nombre, descripcion, categoria, precio_compra, precio_venta, stock_actual, stock_minimo)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (codigo, nombre, descripcion, categoria, precio_compra, precio_venta, stock_actual, stock_minimo))
                        conn.commit()
                        st.success(f"✅ Producto '{nombre}' guardado correctamente. Listo para el siguiente.")
                        st.session_state.form_producto_key += 1
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
                    finally:
                        conn.close()

            if cancelar:
                st.session_state.form_producto_key += 1
                st.warning("Operación cancelada. Formulario limpio.")
                time.sleep(0.5)
                st.rerun()

    with tab3:
        st.subheader("Buscar Producto")
        busqueda = st.text_input("Buscar por nombre o código")
        if busqueda:
            conn = db.conectar()
            df_busqueda = pd.read_sql_query("""
                SELECT * FROM productos
                WHERE nombre LIKE ? OR codigo LIKE ? AND activo = 1
            """, conn, params=(f"%{busqueda}%", f"%{busqueda}%"))
            conn.close()
            if df_busqueda.empty:
                st.warning("Sin resultados.")
            else:
                st.dataframe(df_busqueda, use_container_width=True)

    with tab4:
        st.subheader("🔐 Administración de Inventario")
        st.warning("Esta sección requiere código de administrador.")

        codigo_admin = st.text_input("Código de administrador:", type="password", key="admin_codigo")

        # Obtener código desde la configuración
        conn = db.conectar()
        df_conf = pd.read_sql_query("SELECT codigo_admin FROM configuracion ORDER BY id DESC LIMIT 1", conn)
        conn.close()
        codigo_correcto = str(df_conf.iloc[0]["codigo_admin"]) if not df_conf.empty else "Admin"

        if codigo_admin == codigo_correcto:
            st.success("✅ Acceso concedido.")

            sub_opcion = st.radio(
                "Selecciona una acción:",
                ["✏️ Modificar productos activos", "♻️ Recuperar productos eliminados"],
                horizontal=True,
                key="admin_sub_opcion"
            )

            # ==================== MODIFICAR PRODUCTOS ACTIVOS ====================
            if sub_opcion == "✏️ Modificar productos activos":
                conn = db.conectar()
                df_admin = pd.read_sql_query("""
                    SELECT id, codigo, nombre, categoria, precio_compra, precio_venta, stock_actual, stock_minimo
                    FROM productos
                    WHERE activo = 1
                    ORDER BY nombre
                """, conn)
                conn.close()

                if df_admin.empty:
                    st.info("No hay productos registrados.")
                else:
                    st.caption("👆 Haz clic en una fila para modificar o eliminar el producto")

                    evento = st.dataframe(
                        df_admin,
                        use_container_width=True,
                        height=300,
                        hide_index=True,
                        on_select="rerun",
                        selection_mode="single-row",
                        key=f"tabla_admin_{st.session_state.get('refresh_admin', 0)}",
                        column_config={
                            "id": None,
                            "codigo": st.column_config.TextColumn("Código", width="small"),
                            "nombre": st.column_config.TextColumn("Nombre", width="large"),
                            "categoria": st.column_config.TextColumn("Categoría", width="medium"),
                            "precio_compra": st.column_config.NumberColumn("Costo", format="$ %.2f"),
                            "precio_venta": st.column_config.NumberColumn("Precio Venta", format="$ %.2f"),
                            "stock_actual": st.column_config.NumberColumn("Stock", width="small"),
                            "stock_minimo": st.column_config.NumberColumn("Stock Mín.", width="small"),
                        }
                    )

                    filas_seleccionadas = evento.selection.rows if hasattr(evento, "selection") else []

                    if filas_seleccionadas:
                        indice = filas_seleccionadas[0]
                        fila = df_admin.iloc[indice]
                        producto_id = int(fila["id"])

                        conn = db.conectar()
                        df_fresco = pd.read_sql_query("""
                            SELECT id, codigo, nombre, descripcion, categoria, precio_compra, precio_venta, stock_actual, stock_minimo
                            FROM productos WHERE id = ?
                        """, conn, params=(producto_id,))
                        conn.close()

                        if not df_fresco.empty:
                            p = df_fresco.iloc[0]

                            st.markdown("---")
                            st.markdown(f"### ✏️ Modificar Producto: **{p['nombre']}**")

                            if 'form_admin_key' not in st.session_state:
                                st.session_state.form_admin_key = 0

                            with st.form(f"form_admin_{st.session_state.form_admin_key}"):
                                col1, col2 = st.columns(2)
                                with col1:
                                    nuevo_codigo = st.text_input("Código", value=str(p["codigo"]))
                                    nuevo_nombre = st.text_input("Nombre", value=str(p["nombre"]))
                                    nueva_descripcion = st.text_area("Descripción", value=str(p["descripcion"]) if p["descripcion"] else "")
                                with col2:
                                    nueva_categoria = st.text_input("Categoría", value=str(p["categoria"]) if p["categoria"] else "")
                                    nuevo_precio_compra = st.number_input("Precio de Compra (Costo)", min_value=0.0, step=0.01, value=float(p["precio_compra"]))
                                    nuevo_precio_venta = st.number_input("Precio de Venta", min_value=0.0, step=0.01, value=float(p["precio_venta"]))

                                col3, col4 = st.columns(2)
                                with col3:
                                    nuevo_stock = st.number_input("Stock Actual", min_value=0, step=1, value=int(p["stock_actual"]))
                                with col4:
                                    nuevo_stock_min = st.number_input("Stock Mínimo", min_value=0, step=1, value=int(p["stock_minimo"]))

                                st.markdown("---")

                                col_guardar, col_eliminar, col_cancelar = st.columns(3)

                                with col_guardar:
                                    guardar = st.form_submit_button("✅ Guardar Cambios", type="primary", use_container_width=True)

                                with col_eliminar:
                                    eliminar = st.form_submit_button("🗑️ Eliminar Producto", use_container_width=True)

                                with col_cancelar:
                                    cancelar = st.form_submit_button("↩️ Cancelar Modificaciones", use_container_width=True)

                                if guardar:
                                    conn = db.conectar()
                                    cursor = conn.cursor()
                                    try:
                                        cursor.execute("""
                                        UPDATE productos
                                        SET codigo = ?, nombre = ?, descripcion = ?, categoria = ?,
                                            precio_compra = ?, precio_venta = ?, stock_actual = ?, stock_minimo = ?
                                        WHERE id = ?
                                        """, (nuevo_codigo, nuevo_nombre, nueva_descripcion, nueva_categoria,
                                              nuevo_precio_compra, nuevo_precio_venta, nuevo_stock, nuevo_stock_min, producto_id))
                                        conn.commit()
                                        st.success(f"✅ Producto '{nuevo_nombre}' actualizado correctamente.")
                                        st.session_state.form_admin_key += 1
                                        st.session_state.refresh_admin = st.session_state.get('refresh_admin', 0) + 1
                                        time.sleep(1)
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"❌ Error: {e}")
                                    finally:
                                        conn.close()

                                if eliminar:
                                    conn = db.conectar()
                                    cursor = conn.cursor()
                                    try:
                                        cursor.execute("UPDATE productos SET activo = 0 WHERE id = ?", (producto_id,))
                                        conn.commit()
                                        st.success(f"🗑️ Producto '{p['nombre']}' eliminado correctamente.")
                                        st.session_state.form_admin_key += 1
                                        st.session_state.refresh_admin = st.session_state.get('refresh_admin', 0) + 1
                                        time.sleep(1)
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"❌ Error: {e}")
                                    finally:
                                        conn.close()

                                if cancelar:
                                    st.session_state.form_admin_key += 1
                                    st.info("Modificaciones descartadas. El formulario vuelve a los valores originales.")
                                    time.sleep(0.5)
                                    st.rerun()
                    else:
                        st.info("👆 Selecciona un producto de la tabla para modificarlo o eliminarlo.")

            # ==================== RECUPERAR PRODUCTOS ELIMINADOS ====================
            else:
                st.markdown("### ♻️ Productos Eliminados")
                st.caption("Selecciona un producto para reactivarlo en el inventario")

                conn = db.conectar()
                df_inactivos = pd.read_sql_query("""
                    SELECT id, codigo, nombre, categoria, precio_compra, precio_venta, stock_actual
                    FROM productos
                    WHERE activo = 0
                    ORDER BY nombre
                """, conn)
                conn.close()

                if df_inactivos.empty:
                    st.info("No hay productos eliminados para recuperar.")
                else:
                    evento_inact = st.dataframe(
                        df_inactivos,
                        use_container_width=True,
                        height=300,
                        hide_index=True,
                        on_select="rerun",
                        selection_mode="single-row",
                        key=f"tabla_inactivos_{st.session_state.get('refresh_admin', 0)}",
                        column_config={
                            "id": None,
                            "codigo": st.column_config.TextColumn("Código", width="small"),
                            "nombre": st.column_config.TextColumn("Nombre", width="large"),
                            "categoria": st.column_config.TextColumn("Categoría", width="medium"),
                            "precio_compra": st.column_config.NumberColumn("Costo", format="$ %.2f"),
                            "precio_venta": st.column_config.NumberColumn("Precio Venta", format="$ %.2f"),
                            "stock_actual": st.column_config.NumberColumn("Stock", width="small"),
                        }
                    )

                    filas_inact = evento_inact.selection.rows if hasattr(evento_inact, "selection") else []

                    if filas_inact:
                        indice_inact = filas_inact[0]
                        prod_inact = df_inactivos.iloc[indice_inact]
                        prod_id_inact = int(prod_inact["id"])
                        prod_nombre_inact = str(prod_inact["nombre"])

                        st.markdown("---")
                        st.info(f"Producto seleccionado: **{prod_nombre_inact}**")

                        if st.button("♻️ Reactivar Producto", type="primary", use_container_width=True):
                            conn = db.conectar()
                            cursor = conn.cursor()
                            try:
                                cursor.execute("UPDATE productos SET activo = 1 WHERE id = ?", (prod_id_inact,))
                                conn.commit()
                                st.success(f"✅ Producto '{prod_nombre_inact}' reactivado correctamente.")
                                st.session_state.refresh_admin = st.session_state.get('refresh_admin', 0) + 1
                                time.sleep(1)
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error: {e}")
                            finally:
                                conn.close()
                    else:
                        st.info("👆 Selecciona un producto para reactivarlo.")

        elif codigo_admin:
            st.error("❌ Código incorrecto.")    