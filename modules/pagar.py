import streamlit as st
import pandas as pd
import database as db
import datetime
import time

def mostrar():
    st.title("🧾 Cuentas por Pagar")
    st.markdown("Registra compras a proveedores y abona a tus deudas")

    tab1, tab2, tab3 = st.tabs(["➕ Nueva Compra", "📄 Compras Guardadas", "💵 Registrar Abono"])

    # ==================== NUEVA COMPRA ====================
    with tab1:
        st.subheader("Registrar Compra a Proveedor")

        conn = db.conectar()
        df_proveedores = pd.read_sql_query("SELECT id, nombre FROM proveedores ORDER BY nombre", conn)
        conn.close()

        id_proveedor = None

        st.markdown("#### Proveedor")
        lista_proveedores = ["➕ Registrar nuevo proveedor"] + df_proveedores["nombre"].tolist()
        seleccion_proveedor = st.selectbox("Selecciona o crea un proveedor:", lista_proveedores, key="select_proveedor_compra_mod")

        if seleccion_proveedor == "➕ Registrar nuevo proveedor":
            with st.form("form_nuevo_proveedor_compra_mod"):
                col1, col2 = st.columns(2)
                with col1:
                    nombre_prov = st.text_input("Nombre del proveedor *")
                    cedula_prov = st.text_input("Cédula / RIF")
                    telefono_prov = st.text_input("Teléfono")
                with col2:
                    email_prov = st.text_input("Correo electrónico")
                    direccion_prov = st.text_input("Dirección")

                submit_prov = st.form_submit_button("💾 Guardar Proveedor", type="primary")
                if submit_prov:
                    if not nombre_prov:
                        st.error("El nombre es obligatorio.")
                    else:
                        conn = db.conectar()
                        cursor = conn.cursor()
                        cursor.execute("""
                        INSERT INTO proveedores (nombre, cedula_rif, telefono, email, direccion)
                        VALUES (?, ?, ?, ?, ?)
                        """, (nombre_prov, cedula_prov, telefono_prov, email_prov, direccion_prov))
                        conn.commit()
                        id_proveedor = cursor.lastrowid
                        conn.close()
                        st.session_state.id_proveedor_temporal = id_proveedor
                        st.success(f"Proveedor **{nombre_prov}** registrado correctamente.")
        else:
            id_proveedor = df_proveedores.loc[df_proveedores["nombre"] == seleccion_proveedor, "id"].iloc[0]
            st.session_state.id_proveedor_temporal = id_proveedor
            st.success(f"Proveedor seleccionado: **{seleccion_proveedor}**")

        if 'id_proveedor_temporal' in st.session_state:
            id_proveedor = st.session_state.id_proveedor_temporal

        # ==================== PRODUCTOS ====================
        if id_proveedor is not None:
            st.markdown("#### Productos comprados")

            if 'items_compra' not in st.session_state:
                st.session_state.items_compra = []

            conn = db.conectar()
            df_productos_inv = pd.read_sql_query("SELECT id, nombre FROM productos WHERE activo = 1 ORDER BY nombre", conn)
            conn.close()

            lista_productos = ["➕ Nuevo producto"] + df_productos_inv["nombre"].tolist()
            seleccion_producto = st.selectbox("Selecciona o crea un producto:", lista_productos, key="select_producto_compra_mod")

            if seleccion_producto == "➕ Nuevo producto":
                with st.form("form_nuevo_producto_compra_mod"):
                    col1, col2 = st.columns(2)
                    with col1:
                        codigo_nuevo = st.text_input("Código del producto *")
                        nombre_nuevo = st.text_input("Nombre del producto *")
                        categoria_nueva = st.text_input("Categoría")
                    with col2:
                        costo_nuevo = st.number_input("Costo unitario", min_value=0.01, step=0.01, value=0.01)
                        precio_venta_nuevo = st.number_input("Precio de venta", min_value=0.0, step=0.01, value=0.0)
                        stock_inicial_nuevo = st.number_input("Cantidad comprada", min_value=1, step=1, value=1)

                    submit_nuevo = st.form_submit_button("💾 Crear y agregar", type="primary")
                    if submit_nuevo:
                        if not codigo_nuevo or not nombre_nuevo:
                            st.error("Código y nombre son obligatorios.")
                        else:
                            conn = db.conectar()
                            cursor = conn.cursor()
                            cursor.execute("SELECT id FROM productos WHERE codigo = ?", (codigo_nuevo,))
                            existente = cursor.fetchone()
                            if existente:
                                st.error(f"Ya existe un producto con el código '{codigo_nuevo}'.")
                            else:
                                cursor.execute("""
                                INSERT INTO productos (codigo, nombre, categoria, precio_compra, precio_venta, stock_actual, stock_minimo)
                                VALUES (?, ?, ?, ?, ?, ?, 5)
                                """, (codigo_nuevo, nombre_nuevo, categoria_nueva, costo_nuevo, precio_venta_nuevo, stock_inicial_nuevo))
                                conn.commit()
                                id_nuevo = cursor.lastrowid
                                conn.close()

                                item = {
                                    "id_producto": int(id_nuevo),
                                    "nombre": nombre_nuevo,
                                    "cantidad": int(stock_inicial_nuevo),
                                    "costo": float(costo_nuevo),
                                    "total_linea": float(stock_inicial_nuevo * costo_nuevo)
                                }
                                st.session_state.items_compra.append(item)
                                st.success(f"Producto '{nombre_nuevo}' creado y agregado.")
           
            else:
                # Obtener datos completos del producto
                conn = db.conectar()
                df_prod_sel = pd.read_sql_query("""
                    SELECT id, codigo, nombre, precio_compra, precio_venta, stock_actual
                    FROM productos WHERE nombre = ?
                """, conn, params=(seleccion_producto,))
                conn.close()

                if not df_prod_sel.empty:
                    p = df_prod_sel.iloc[0]
                    id_producto = int(p["id"])
                    precio_compra_actual = float(p["precio_compra"])
                    precio_venta_actual = float(p["precio_venta"])
                    stock_actual = int(p["stock_actual"])

                    st.info(f"📦 Stock actual: **{stock_actual}** unidades | Costo actual: **${precio_compra_actual:.2f}** | Precio venta: **${precio_venta_actual:.2f}**")

                    col_cant, col_cost, col_pv, col_btn = st.columns([1, 1, 1, 1])
                    
                    with col_cant:
                        cantidad = st.number_input(
                            "Cantidad a sumar",
                            min_value=1,
                            step=1,
                            value=1,
                            key=f"cant_compra_{id_producto}"
                        )
                    with col_cost:
                        costo = st.number_input(
                            "Nuevo costo unitario",
                            min_value=0.01,
                            step=0.01,
                            value=precio_compra_actual if precio_compra_actual > 0 else 0.01,
                            key=f"costo_compra_{id_producto}"
                        )
                    with col_pv:
                        precio_venta_nuevo = st.number_input(
                            "Nuevo precio venta",
                            min_value=0.0,
                            step=0.01,
                            value=precio_venta_actual,
                            key=f"pv_compra_{id_producto}"
                        )
                    with col_btn:
                        st.markdown("")
                        if st.button("➕ Agregar", key="btn_agregar_compra_mod", use_container_width=True):
                            item = {
                                "id_producto": id_producto,
                                "nombre": seleccion_producto,
                                "cantidad": int(cantidad),
                                "costo": float(costo),
                                "precio_venta": float(precio_venta_nuevo),
                                "total_linea": float(cantidad * costo)
                            }
                            st.session_state.items_compra.append(item)
                            st.success(f"Agregado: {seleccion_producto} x{cantidad}")

            if st.session_state.items_compra:
                st.markdown("#### Detalle de la compra")
                df_items = pd.DataFrame(st.session_state.items_compra)
                st.dataframe(df_items, use_container_width=True)

                subtotal = sum(i["total_linea"] for i in st.session_state.items_compra)
                impuesto = subtotal * 0.16
                total = subtotal + impuesto

                col1, col2, col3 = st.columns(3)
                col1.metric("Subtotal", f"${subtotal:.2f}")
                col2.metric("Impuesto (16%)", f"${impuesto:.2f}")
                col3.metric("TOTAL", f"${total:.2f}")

                st.markdown("#### Datos de la factura del proveedor")
                numero_factura_proveedor = st.text_input("Número de factura del proveedor *", key="num_fact_prov_mod")

                st.markdown("#### Condición de pago")
                condicion_pago = st.radio("Forma de pago:", ["Contado", "Crédito"], horizontal=True, key="condicion_compra_mod")
                metodo_pago = ""
                if condicion_pago == "Contado":
                    metodo_pago = st.selectbox("Método de pago:", ["Efectivo", "Tarjeta de débito", "Tarjeta de crédito", "Transferencia", "Otros"], key="metodo_compra_mod")

                col_guardar, col_cancelar = st.columns(2)

                with col_guardar:
                    if st.button("💾 Guardar Compra", type="primary", use_container_width=True):
                        if id_proveedor is None:
                            st.error("Selecciona o registra un proveedor.")
                        elif not numero_factura_proveedor:
                            st.error("Debes ingresar el número de factura del proveedor.")
                        else:
                            conn = db.conectar()
                            cursor = conn.cursor()
                            try:
                                ahora = datetime.datetime.now()
                                estado_compra = "credito" if condicion_pago == "Crédito" else "pagada"

                                cursor.execute("""
                                INSERT INTO compras (numero_factura, id_proveedor, fecha, subtotal, impuesto, total, estado, condicion_pago, metodo_pago)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                                """, (numero_factura_proveedor.strip(), int(id_proveedor), ahora.strftime('%Y-%m-%d'), subtotal, impuesto, total, estado_compra, condicion_pago.lower(), metodo_pago))
                                id_compra = cursor.lastrowid

                                for item in st.session_state.items_compra:
                                    cursor.execute("""
                                    UPDATE productos 
                                    SET stock_actual = stock_actual + ?, 
                                        precio_compra = ?,
                                        precio_venta = ?
                                    WHERE id = ?
                                    """, (item["cantidad"], item["costo"], item.get("precio_venta", item["costo"]), item["id_producto"]))

                                    cursor.execute("""
                                    INSERT INTO compra_detalle (id_compra, id_producto, cantidad, precio_unitario, total_linea)
                                    VALUES (?, ?, ?, ?, ?)
                                    """, (id_compra, item["id_producto"], item["cantidad"], item["costo"], item["total_linea"]))

                                if condicion_pago == "Crédito":
                                    cursor.execute("""
                                    INSERT INTO cuentas_por_pagar (id_compra, id_proveedor, monto_total, saldo_pendiente, estado)
                                    VALUES (?, ?, ?, ?, 'pendiente')
                                    """, (id_compra, int(id_proveedor), total, total))

                                conn.commit()
                                st.session_state.items_compra = []
                                st.session_state.id_proveedor_temporal = None
                                st.success(f"Compra {numero_factura_proveedor} guardada. Inventario actualizado.")
                            except Exception as e:
                                st.error(f"Error: {e}")
                            finally:
                                conn.close()

                with col_cancelar:
                    if st.button("❌ Cancelar Compra", use_container_width=True):
                        st.session_state.items_compra = []
                        st.session_state.id_proveedor_temporal = None
                        st.warning("Compra cancelada. No se guardaron cambios.")
                        st.rerun()

                    if id_proveedor is None:
                        st.error("Selecciona o registra un proveedor.")
                    elif not numero_factura_proveedor:
                        st.error("Debes ingresar el número de factura del proveedor.")
                    else:
                        conn = db.conectar()
                        cursor = conn.cursor()
                        try:
                            ahora = datetime.datetime.now()
                            estado_compra = "credito" if condicion_pago == "Crédito" else "pagada"

                            cursor.execute("""
                            INSERT INTO compras (numero_factura, id_proveedor, fecha, subtotal, impuesto, total, estado, condicion_pago, metodo_pago)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (numero_factura_proveedor.strip(), int(id_proveedor), ahora.strftime('%Y-%m-%d'), subtotal, impuesto, total, estado_compra, condicion_pago.lower(), metodo_pago))
                            id_compra = cursor.lastrowid

                            for item in st.session_state.items_compra:
                                cursor.execute("""
                                UPDATE productos 
                                SET stock_actual = stock_actual + ?, 
                                    precio_compra = ?,
                                    precio_venta = ?
                                WHERE id = ?
                                """, (item["cantidad"], item["costo"], item.get("precio_venta", item["costo"]), item["id_producto"]))

                                cursor.execute("""
                                INSERT INTO compra_detalle (id_compra, id_producto, cantidad, precio_unitario, total_linea)
                                VALUES (?, ?, ?, ?, ?)
                                """, (id_compra, item["id_producto"], item["cantidad"], item["costo"], item["total_linea"]))

                            if condicion_pago == "Crédito":
                                cursor.execute("""
                                INSERT INTO cuentas_por_pagar (id_compra, id_proveedor, monto_total, saldo_pendiente, estado)
                                VALUES (?, ?, ?, ?, 'pendiente')
                                """, (id_compra, int(id_proveedor), total, total))

                            conn.commit()
                            st.session_state.items_compra = []
                            st.success(f"Compra {numero_factura_proveedor} guardada. Inventario actualizado.")
                        except Exception as e:
                            st.error(f"Error: {e}")
                        finally:
                            conn.close()

          # ==================== COMPRAS GUARDADAS ====================
    with tab2:
        st.subheader("Compras Registradas")

        col_fecha1, col_fecha2 = st.columns(2)
        with col_fecha1:
            fecha_inicio = st.date_input("Desde:", datetime.date.today().replace(day=1), key="fecha_inicio_compras_mod")
        with col_fecha2:
            fecha_fin = st.date_input("Hasta:", datetime.date.today(), key="fecha_fin_compras_mod")

        conn = db.conectar()
        df_compras = pd.read_sql_query("""
            SELECT c.id as compra_id, c.numero_factura, p.nombre as proveedor, c.fecha, 
                   c.total, c.estado, c.condicion_pago, c.metodo_pago
            FROM compras c
            LEFT JOIN proveedores p ON c.id_proveedor = p.id
            WHERE date(c.fecha) BETWEEN date(?) AND date(?)
            ORDER BY c.fecha DESC
        """, conn, params=(fecha_inicio.isoformat(), fecha_fin.isoformat()))
        conn.close()

        if df_compras.empty:
            st.info("No hay compras registradas en ese período.")
        else:
            st.caption("👆 Haz clic en una fila para ver el detalle de productos")

            evento = st.dataframe(
                df_compras,
                use_container_width=True,
                height=300,
                hide_index=True,
                on_select="rerun",
                selection_mode="single-row",
                column_config={
                    "compra_id": None,
                    "numero_factura": st.column_config.TextColumn("N° Factura", width="medium"),
                    "proveedor": st.column_config.TextColumn("Proveedor", width="large"),
                    "fecha": st.column_config.DateColumn("Fecha"),
                    "total": st.column_config.NumberColumn("Total", format="$ %.2f"),
                    "estado": st.column_config.TextColumn("Estado", width="small"),
                    "condicion_pago": st.column_config.TextColumn("Condición", width="small"),
                    "metodo_pago": st.column_config.TextColumn("Método", width="small"),
                }
            )

            filas_seleccionadas = evento.selection.rows if hasattr(evento, "selection") else []

            if filas_seleccionadas:
                indice = filas_seleccionadas[0]
                fila = df_compras.iloc[indice]
                compra_id = int(fila["compra_id"])
                numero_factura = str(fila["numero_factura"])

                st.markdown("---")
                st.markdown(f"### 🧾 Detalle de la Compra **{numero_factura}**")

                conn = db.conectar()
                df_detalle = pd.read_sql_query("""
                    SELECT p.nombre as producto, cd.cantidad, cd.precio_unitario, cd.total_linea
                    FROM compra_detalle cd
                    JOIN productos p ON cd.id_producto = p.id
                    WHERE cd.id_compra = ?
                """, conn, params=(compra_id,))
                conn.close()

                if df_detalle.empty:
                    st.info("Esta compra no tiene productos registrados.")
                else:
                    st.dataframe(
                        df_detalle,
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "producto": st.column_config.TextColumn("Producto", width="large"),
                            "cantidad": st.column_config.NumberColumn("Cantidad", width="small"),
                            "precio_unitario": st.column_config.NumberColumn("Costo Unit.", format="$ %.2f"),
                            "total_linea": st.column_config.NumberColumn("Total", format="$ %.2f"),
                        }
                    )

                    total_calculado = df_detalle["total_linea"].sum()
                    st.metric("Total del detalle", f"${total_calculado:.2f}")
            else:
                st.info("👆 Selecciona una compra de la tabla para ver sus productos.")  
    # ==================== REGISTRAR ABONO ====================
      # ==================== REGISTRAR ABONO ====================
    with tab3:
        st.subheader("Abonar a Cuenta por Pagar")
        st.caption("👆 Haz clic en una factura de la tabla para registrar un abono")

        conn = db.conectar()
        df_deudas = pd.read_sql_query("""
            SELECT 
                cpp.id as cuenta_id,
                p.nombre as proveedor,
                c.numero_factura,
                cpp.monto_total,
                cpp.monto_pagado,
                cpp.saldo_pendiente,
                cpp.fecha_credito,
                cpp.estado
            FROM cuentas_por_pagar cpp
            JOIN proveedores p ON cpp.id_proveedor = p.id
            JOIN compras c ON cpp.id_compra = c.id
            WHERE cpp.estado = 'pendiente' AND cpp.saldo_pendiente > 0
            ORDER BY cpp.fecha_credito DESC
        """, conn)
        conn.close()

        if df_deudas.empty:
            st.info("No hay cuentas por pagar pendientes.")
            return

        # Métricas
        total_pendiente = df_deudas["saldo_pendiente"].sum()
        total_deudas = len(df_deudas)
        col1, col2 = st.columns(2)
        col1.metric("Deudas Activas", total_deudas)
        col2.metric("Saldo Total Pendiente", f"${total_pendiente:.2f}")

        st.markdown("---")

        # Tabla con selección
        evento = st.dataframe(
            df_deudas,
            use_container_width=True,
            height=300,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row",
            key="tabla_deudas_fija",
            column_config={
                "cuenta_id": None,
                "proveedor": st.column_config.TextColumn("Proveedor", width="large"),
                "numero_factura": st.column_config.TextColumn("N° Factura", width="medium"),
                "monto_total": st.column_config.NumberColumn("Monto Total", format="$ %.2f"),
                "monto_pagado": st.column_config.NumberColumn("Pagado", format="$ %.2f"),
                "saldo_pendiente": st.column_config.NumberColumn("Saldo Pendiente", format="$ %.2f"),
                "fecha_credito": st.column_config.DateColumn("Fecha Crédito"),
                "estado": st.column_config.TextColumn("Estado", width="small"),
            }
        ) 

        filas_seleccionadas = evento.selection.rows if hasattr(evento, "selection") else []

        if not filas_seleccionadas:
            st.info("👆 Selecciona una factura de la tabla para continuar.")
            return

        # Datos de la fila seleccionada
        indice = filas_seleccionadas[0]
        fila = df_deudas.iloc[indice]
        cuenta_id = int(fila["cuenta_id"])
        numero_factura = str(fila["numero_factura"])

        # CONSULTA FRESCA a la base de datos para evitar datos cacheados
        conn = db.conectar()
        df_fresco = pd.read_sql_query("""
            SELECT cpp.saldo_pendiente, p.nombre as proveedor
            FROM cuentas_por_pagar cpp
            JOIN proveedores p ON cpp.id_proveedor = p.id
            WHERE cpp.id = ?
        """, conn, params=(cuenta_id,))
        conn.close()

        if not df_fresco.empty:
            saldo_actual = float(df_fresco.iloc[0]["saldo_pendiente"])
            proveedor_nombre = str(df_fresco.iloc[0]["proveedor"])
        else:
            saldo_actual = float(fila["saldo_pendiente"])
            proveedor_nombre = str(fila["proveedor"])

        st.markdown("---") 
        st.markdown(f"### 💵 Abonar a la Factura **{numero_factura}**")

        col_info1, col_info2 = st.columns(2)
        col_info1.info(f"**Proveedor:** {proveedor_nombre}")
        col_info2.info(f"**Saldo pendiente:** ${saldo_actual:.2f}")

        # Mostrar productos de la factura seleccionada
        conn = db.conectar()
        df_productos = pd.read_sql_query("""
            SELECT p.nombre, cd.cantidad, cd.precio_unitario, cd.total_linea
            FROM compra_detalle cd
            JOIN productos p ON cd.id_producto = p.id
            WHERE cd.id_compra = (SELECT id_compra FROM cuentas_por_pagar WHERE id = ?)
        """, conn, params=(cuenta_id,))
        conn.close()

        if not df_productos.empty:
            st.markdown("#### Productos de esta compra")
            st.dataframe(
                df_productos,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "nombre": st.column_config.TextColumn("Producto", width="large"),
                    "cantidad": st.column_config.NumberColumn("Cantidad", width="small"),
                    "precio_unitario": st.column_config.NumberColumn("Costo Unit.", format="$ %.2f"),
                    "total_linea": st.column_config.NumberColumn("Total", format="$ %.2f"),
                }
            )
        else:
            st.info("Esta compra no tiene productos registrados.")

        st.markdown("---")

        # Formulario de abono
        with st.form("form_abono_pagar_final"):
            col_monto, col_metodo = st.columns(2)
            with col_monto:
                monto = st.number_input(
                    "Monto a abonar",
                    min_value=0.01,
                    max_value=float(saldo_actual),
                    step=0.01,
                    value=float(min(0.01, saldo_actual)),
                    key="monto_pagar_form"
                )
            with col_metodo:
                metodo = st.selectbox(
                    "Método de pago:",
                    ["Efectivo", "Tarjeta de débito", "Tarjeta de crédito", "Transferencia", "Otros"],
                    key="metodo_pagar_form"
                )

            col_aceptar, col_cancelar = st.columns(2)

            with col_aceptar:
                submitted = st.form_submit_button("✅ Aceptar Operación", type="primary", use_container_width=True)

            with col_cancelar:
                cancelar = st.form_submit_button("❌ Cancelar Operación", use_container_width=True)

            if submitted:
                if monto > saldo_actual:
                    st.error("El monto no puede ser mayor al saldo pendiente.")
                else:
                    conn = db.conectar()
                    cursor = conn.cursor()
                    try:
                        cursor.execute("""
                        INSERT INTO pagos_por_pagar (id_cuenta, monto_abonado, metodo_pago)
                        VALUES (?, ?, ?)
                        """, (cuenta_id, round(monto, 2), metodo)) 

                # Redondear a 2 decimales para evitar residuos
                        monto = round(monto, 2)
                        saldo_actual = round(saldo_actual, 2)
                        nuevo_saldo = round(saldo_actual - monto, 2)
                        if nuevo_saldo <= 0:
                            cursor.execute("""
                            UPDATE cuentas_por_pagar SET monto_pagado = monto_total, saldo_pendiente = 0, estado = 'pagado'
                            WHERE id = ?
                            """, (cuenta_id,))
                            cursor.execute("""
                            UPDATE compras SET estado = 'cancelada'
                            WHERE id = (SELECT id_compra FROM cuentas_por_pagar WHERE id = ?)
                            """, (cuenta_id,))
                        else:
                            cursor.execute("""
                            UPDATE cuentas_por_pagar SET monto_pagado = monto_pagado + ?, saldo_pendiente = saldo_pendiente - ?
                            WHERE id = ?
                            """, (monto, monto, cuenta_id))

                        conn.commit()

                        st.success(f"✅ Abono de ${monto:.2f} registrado a {proveedor_nombre}. Nuevo saldo: ${max(nuevo_saldo, 0):.2f}")
                        st.session_state.refresh_pagar = st.session_state.get('refresh_pagar', 0) + 1
                        time.sleep(1)   
                        st.rerun()

                    except Exception as e:
                        st.error(f"Error: {e}")
                    finally:
                        conn.close()

            if cancelar:
                st.warning("Operación cancelada. No se guardaron cambios.") 