import streamlit as st
import pandas as pd
import database as db
import datetime
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import time

def generar_numero_factura():
    """Genera el siguiente número consecutivo de factura."""
    conn = db.conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, numero_factura_actual FROM configuracion ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()

    if row is None:
        conn.close()
        return "F-000001"

    config_id = row[0]
    numero_actual = row[1] if row[1] else 0
    nuevo_numero = numero_actual + 1

    cursor.execute("UPDATE configuracion SET numero_factura_actual = ? WHERE id = ?", (nuevo_numero, config_id))
    conn.commit()
    conn.close()

    return f"F-{nuevo_numero:06d}"

def generar_imagen_ticket(texto_ticket):
    ancho = 500
    alto = 60 + (len(texto_ticket.split('\n')) * 18)
    img = Image.new('RGB', (ancho, alto), color='white')
    draw = ImageDraw.Draw(img)
    try:
        fuente = ImageFont.truetype("cour.ttf", 14)
    except:
        fuente = ImageFont.load_default()
    y = 20
    for linea in texto_ticket.split('\n'):
        draw.text((20, y), linea, fill='black', font=fuente)
        y += 18
    return img

def mostrar():
    st.title("🧾 Facturación")
    st.markdown("Crea facturas y consulta las registradas")

    # Obtener configuración de la empresa
    conn = db.conectar()
    df_config = pd.read_sql_query("SELECT * FROM configuracion ORDER BY id DESC LIMIT 1", conn)
    conn.close()

    if df_config.empty:
        st.warning("⚠️ Debes configurar el sistema primero. Ve a **Configuración** en el menú lateral.")
        return

    config = df_config.iloc[0]

    tab1, tab2 = st.tabs(["➕ Nueva Factura", "📄 Facturas Guardadas"])

    # ==================== NUEVA FACTURA ====================
    with tab1:
        # Si ya se aceptó una factura, mostrar el ticket
        if st.session_state.get("factura_aceptada", False) and 'ultima_factura' in st.session_state:
            factura = st.session_state.ultima_factura

            st.success(f"✅ Factura {factura['numero']} aceptada correctamente.")

            # Mostrar ticket
            lineas_productos = ""
            for item in factura["items"]:
                lineas_productos += f"{item['cantidad']:>3} x {item['nombre'][:18]:<18} ${item['total_linea']:>8.2f}\n"

            ticket_texto = f"""
================================
   {config['nombre_negocio'][:24]:^28}
   RIF: {config['rif'] if config['rif'] else 'N/A'}
   {config['direccion'][:28] if config['direccion'] else ''}
   Tel: {config['telefono'] if config['telefono'] else 'N/A'}
================================
Factura: {factura['numero']}
Cliente: {factura['cliente']}
Fecha:   {factura['fecha']}
Cond:    {factura['condicion']}
Método:  {factura['metodo'] if factura['metodo'] else 'N/A'}
--------------------------------
CANT PRODUCTO           TOTAL
--------------------------------
{lineas_productos}--------------------------------
Subtotal:        ${factura['subtotal']:>10.2f}
Impuesto ({config['impuesto_porcentaje']}%):  ${factura['impuesto']:>9.2f}
TOTAL:           ${factura['total']:>10.2f}
================================
      ¡Gracias por su visita!
        Sistema AdminPyME
================================
"""

            st.markdown("### 🧾 Ticket de Venta")
            st.code(ticket_texto, language=None)

            # Generar imagen del ticket
            img_ticket = generar_imagen_ticket(ticket_texto)
            buffer = BytesIO()
            img_ticket.save(buffer, format='PNG')
            buffer.seek(0)

            col_descargar, col_imprimir, col_nuevo = st.columns(3)

            with col_descargar:
                st.download_button(
                    label="📥 Descargar Imagen",
                    data=buffer,
                    file_name=f"ticket_{factura['numero']}.png",
                    mime="image/png",
                    use_container_width=True
                )

            with col_imprimir:
                if st.button("🖨️ Imprimir Ticket", type="primary", use_container_width=True):
                    st.info("💡 Presiona **Ctrl + P** para imprimir. Selecciona tu impresora POS.")

            with col_nuevo:
                if st.button("➕ Nuevo Cliente", use_container_width=True):
                    st.session_state.factura_aceptada = False
                    st.session_state.ultima_factura = None
                    st.session_state.items_factura = []
                    st.session_state.id_cliente_temporal = None
                    st.session_state.nombre_cliente_temporal = None
                    st.session_state.form_factura_key = st.session_state.get('form_factura_key', 0) + 1
                    st.rerun()

            return

        # ---- FORMULARIO DE NUEVA FACTURA ----
        if 'items_factura' not in st.session_state:
            st.session_state.items_factura = []
        if 'form_factura_key' not in st.session_state:
            st.session_state.form_factura_key = 0

        st.subheader("Nueva Factura de Venta")
        st.caption(f"📌 Próximo número de factura: **F-{int(config['numero_factura_actual']) + 1:06d}**")

        # ---- CLIENTE ----
        st.markdown("#### 1. Cliente")

        conn = db.conectar()
        df_clientes = pd.read_sql_query("SELECT id, nombre FROM clientes ORDER BY nombre", conn)
        conn.close()

        lista_clientes = ["➕ Registrar nuevo cliente"] + df_clientes["nombre"].tolist()

        seleccion_cliente = st.selectbox(
            "Selecciona o crea un cliente:",
            lista_clientes,
            key=f"select_cliente_factura_{st.session_state.form_factura_key}"
        )

        id_cliente = None
        cliente_nombre = None

        if seleccion_cliente == "➕ Registrar nuevo cliente":
            with st.form(f"form_nuevo_cliente_fact_{st.session_state.form_factura_key}"):
                col1, col2 = st.columns(2)
                with col1:
                    nuevo_nombre = st.text_input("Nombre completo *")
                    nuevo_cedula = st.text_input("Cédula / RIF")
                    nuevo_telefono = st.text_input("Teléfono")
                with col2:
                    nuevo_email = st.text_input("Correo")
                    nueva_direccion = st.text_input("Dirección")

                guardar_cliente = st.form_submit_button("💾 Guardar Cliente y continuar", type="primary")
                if guardar_cliente:
                    if not nuevo_nombre:
                        st.error("El nombre es obligatorio.")
                    else:
                        conn = db.conectar()
                        cursor = conn.cursor()
                        cursor.execute("""
                        INSERT INTO clientes (nombre, cedula_rif, telefono, email, direccion)
                        VALUES (?, ?, ?, ?, ?)
                        """, (nuevo_nombre, nuevo_cedula, nuevo_telefono, nuevo_email, nueva_direccion))
                        conn.commit()
                        id_cliente = cursor.lastrowid
                        conn.close()
                        st.session_state.id_cliente_temporal = id_cliente
                        st.session_state.nombre_cliente_temporal = nuevo_nombre
                        st.success(f"Cliente **{nuevo_nombre}** registrado.")
                        time.sleep(0.5)
                        st.rerun()
        else:
            id_cliente = int(df_clientes.loc[df_clientes["nombre"] == seleccion_cliente, "id"].iloc[0])
            cliente_nombre = seleccion_cliente
            st.session_state.id_cliente_temporal = id_cliente
            st.session_state.nombre_cliente_temporal = cliente_nombre
            st.success(f"Cliente seleccionado: **{cliente_nombre}**")       

        # ---- PRODUCTOS ----
        if id_cliente is not None:
            st.markdown("#### 2. Productos")

            conn = db.conectar()
            df_productos = pd.read_sql_query("""
                SELECT id, codigo, nombre, precio_venta, stock_actual
                FROM productos WHERE activo = 1 AND stock_actual > 0
                ORDER BY nombre
            """, conn)
            conn.close()

            if df_productos.empty:
                st.warning("No hay productos con stock disponible.")
            else:
                col_sel, col_cant, col_btn = st.columns([3, 1, 1])
                with col_sel:
                    producto_elegido = st.selectbox("Producto:", df_productos["nombre"].tolist(), key=f"prod_{st.session_state.form_factura_key}")
                with col_cant:
                    cantidad = st.number_input("Cantidad", min_value=1, step=1, value=1, key=f"cant_{st.session_state.form_factura_key}")
                with col_btn:
                    st.markdown("")
                    if st.button("➕ Agregar", key=f"btn_agregar_{st.session_state.form_factura_key}", use_container_width=True):
                        id_producto = df_productos.loc[df_productos["nombre"] == producto_elegido, "id"].iloc[0]
                        precio = df_productos.loc[df_productos["nombre"] == producto_elegido, "precio_venta"].iloc[0]
                        stock = df_productos.loc[df_productos["nombre"] == producto_elegido, "stock_actual"].iloc[0]

                        if cantidad > stock:
                            st.error(f"Stock insuficiente. Solo hay {stock} unidades.")
                        else:
                            item = {
                                "id_producto": int(id_producto),
                                "nombre": producto_elegido,
                                "cantidad": int(cantidad),
                                "precio": float(precio),
                                "total_linea": float(cantidad * precio)
                            }
                            st.session_state.items_factura.append(item)
                            st.success(f"Agregado: {producto_elegido} x{cantidad}")

                if st.session_state.items_factura:
                    st.markdown("#### Productos en la factura")
                    df_items = pd.DataFrame(st.session_state.items_factura)
                    st.dataframe(df_items, use_container_width=True, hide_index=True)

                    subtotal = sum(i["total_linea"] for i in st.session_state.items_factura)
                    impuesto_pct = float(config["impuesto_porcentaje"])
                    impuesto = subtotal * (impuesto_pct / 100)
                    total = subtotal + impuesto

                    col1, col2, col3 = st.columns(3)
                    col1.metric("Subtotal", f"${subtotal:.2f}")
                    col2.metric(f"Impuesto ({impuesto_pct}%)", f"${impuesto:.2f}")
                    col3.metric("TOTAL", f"${total:.2f}")

                    # ---- CONDICIÓN DE PAGO ----
                    st.markdown("#### 3. Forma de pago")
                    condicion_pago = st.radio("Condición:", ["Contado", "Crédito"], horizontal=True, key=f"cond_{st.session_state.form_factura_key}")
                    metodo_pago = ""
                    if condicion_pago == "Contado":
                        metodo_pago = st.selectbox("Método de pago:", ["Efectivo", "Tarjeta de débito", "Tarjeta de crédito", "Transferencia", "Otros"], key=f"metodo_{st.session_state.form_factura_key}")

                    # ---- BOTONES ----
                    st.markdown("#### 4. Confirmar")
                    col_aceptar, col_cancelar = st.columns(2)

                    with col_aceptar:
                        if st.button("✅ Aceptar Factura", type="primary", use_container_width=True):
                            conn = db.conectar()
                            cursor = conn.cursor()
                            try:
                                numero = generar_numero_factura()
                                ahora = datetime.datetime.now()
                                estado_factura = "credito" if condicion_pago == "Crédito" else "pagada"

                                cursor.execute("""
                                INSERT INTO facturas (numero_factura, id_cliente, fecha, subtotal, impuesto, total, estado, condicion_pago, metodo_pago)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                                """, (numero, int(id_cliente), ahora.strftime('%Y-%m-%d'), subtotal, impuesto, total, estado_factura, condicion_pago.lower(), metodo_pago))
                                id_factura = cursor.lastrowid

                                for item in st.session_state.items_factura:
                                    cursor.execute("""
                                    INSERT INTO factura_detalle (id_factura, id_producto, cantidad, precio_unitario, total_linea)
                                    VALUES (?, ?, ?, ?, ?)
                                    """, (id_factura, item["id_producto"], item["cantidad"], item["precio"], item["total_linea"]))

                                    cursor.execute("""
                                    UPDATE productos SET stock_actual = stock_actual - ?
                                    WHERE id = ?
                                    """, (item["cantidad"], item["id_producto"]))

                                if condicion_pago == "Crédito":
                                    cursor.execute("""
                                    INSERT INTO creditos (id_factura, id_cliente, monto_total, saldo_pendiente, estado)
                                    VALUES (?, ?, ?, ?, 'pendiente')
                                    """, (id_factura, int(id_cliente), total, total))

                                conn.commit()

                                st.session_state.ultima_factura = {
                                    "numero": numero,
                                    "cliente": cliente_nombre,
                                    "fecha": ahora.strftime('%d/%m/%Y %H:%M'),
                                    "items": st.session_state.items_factura.copy(),
                                    "subtotal": subtotal,
                                    "impuesto": impuesto,
                                    "total": total,
                                    "condicion": condicion_pago,
                                    "metodo": metodo_pago
                                }
                                st.session_state.items_factura = []
                                st.session_state.id_cliente_temporal = None
                                st.session_state.nombre_cliente_temporal = None
                                st.session_state.factura_aceptada = True
                                st.session_state.form_factura_key += 1
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")
                            finally:
                                conn.close()

                    with col_cancelar:
                        if st.button("❌ Cancelar Factura", use_container_width=True):
                            st.session_state.items_factura = []
                            st.session_state.id_cliente_temporal = None
                            st.session_state.nombre_cliente_temporal = None
                            st.session_state.form_factura_key += 1
                            st.warning("Factura cancelada. No se guardaron cambios.")
                            time.sleep(0.5)
                            st.rerun()

    # ==================== FACTURAS GUARDADAS ====================
    with tab2:
        st.subheader("Facturas Registradas")

        col_fecha1, col_fecha2 = st.columns(2)
        with col_fecha1:
            fecha_inicio = st.date_input("Desde:", datetime.date.today().replace(day=1), key="fecha_inicio_fact")
        with col_fecha2:
            fecha_fin = st.date_input("Hasta:", datetime.date.today(), key="fecha_fin_fact")

        conn = db.conectar()
        df_facturas = pd.read_sql_query("""
            SELECT f.id as factura_id, f.numero_factura, c.nombre as cliente, f.fecha, f.total, f.estado, f.condicion_pago, f.metodo_pago
            FROM facturas f
            LEFT JOIN clientes c ON f.id_cliente = c.id
            WHERE date(f.fecha) BETWEEN date(?) AND date(?)
            ORDER BY f.fecha DESC
        """, conn, params=(fecha_inicio.isoformat(), fecha_fin.isoformat()))
        conn.close()

        if df_facturas.empty:
            st.info("No hay facturas registradas en ese período.")
        else:
            st.caption("👆 Haz clic en una fila para ver el detalle")

            evento = st.dataframe(
                df_facturas,
                use_container_width=True,
                height=300,
                hide_index=True,
                on_select="rerun",
                selection_mode="single-row",
                key="tabla_facturas",
                column_config={
                    "factura_id": None,
                    "numero_factura": st.column_config.TextColumn("N° Factura", width="medium"),
                    "cliente": st.column_config.TextColumn("Cliente", width="large"),
                    "fecha": st.column_config.DateColumn("Fecha"),
                    "total": st.column_config.NumberColumn("Total", format="$ %.2f"),
                    "estado": st.column_config.TextColumn("Estado", width="small"),
                    "condicion_pago": st.column_config.TextColumn("Condición", width="small"),
                    "metodo_pago": st.column_config.TextColumn("Método", width="small"),
                }
            )

            filas = evento.selection.rows if hasattr(evento, "selection") else []

            if filas:
                indice = filas[0]
                fila = df_facturas.iloc[indice]
                factura_id = int(fila["factura_id"])
                numero_factura = str(fila["numero_factura"])

                st.markdown("---")
                st.markdown(f"### 🧾 Detalle de la Factura **{numero_factura}**")

                conn = db.conectar()
                df_detalle = pd.read_sql_query("""
                    SELECT p.nombre as producto, fd.cantidad, fd.precio_unitario, fd.total_linea
                    FROM factura_detalle fd
                    JOIN productos p ON fd.id_producto = p.id
                    WHERE fd.id_factura = ?
                """, conn, params=(factura_id,))
                conn.close()

                if not df_detalle.empty:
                    st.dataframe(df_detalle, use_container_width=True, hide_index=True)
                    st.metric("Total del detalle", f"${df_detalle['total_linea'].sum():.2f}")
            else:
                st.info("👆 Selecciona una factura para ver el detalle.")