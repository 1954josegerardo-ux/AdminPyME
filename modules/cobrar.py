import streamlit as st
import pandas as pd
import database as db
import time

def mostrar():
    st.title("💰 Cuentas por Cobrar")
    st.markdown("Haz clic en una factura de la tabla para registrar un abono")

    # Cargar créditos pendientes
    conn = db.conectar()
    df_creditos = pd.read_sql_query("""
        SELECT 
            c.id as credito_id,
            cl.nombre as cliente,
            f.numero_factura,
            c.monto_total,
            c.monto_pagado,
            c.saldo_pendiente,
            c.fecha_credito,
            c.estado
        FROM creditos c
        JOIN clientes cl ON c.id_cliente = cl.id
        JOIN facturas f ON c.id_factura = f.id
        WHERE c.estado = 'pendiente' AND c.saldo_pendiente > 0.01
        ORDER BY c.fecha_credito DESC
    """, conn)
    conn.close()

    if df_creditos.empty:
        st.info("No hay créditos pendientes por cobrar.")
        return

    # Métricas
    total_pendiente = df_creditos["saldo_pendiente"].sum()
    total_creditos = len(df_creditos)
    col1, col2 = st.columns(2)
    col1.metric("Créditos Activos", total_creditos)
    col2.metric("Saldo Total Pendiente", f"${total_pendiente:.2f}")

    st.markdown("---")
    st.markdown("### 📋 Facturas a Crédito")
    st.caption("👆 Haz clic en una fila para seleccionar la factura a abonar")

    # Tabla con selección
    evento = st.dataframe(
        df_creditos,
        use_container_width=True,
        height=300,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row",
        key="tabla_creditos_cobrar",
        column_config={
            "credito_id": None,
            "cliente": st.column_config.TextColumn("Cliente", width="large"),
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
    fila = df_creditos.iloc[indice]
    credito_id = int(fila["credito_id"])

    # Consulta fresca a la base de datos
    conn = db.conectar()
    df_fresco = pd.read_sql_query("""
        SELECT c.saldo_pendiente, cl.nombre as cliente, f.numero_factura
        FROM creditos c
        JOIN clientes cl ON c.id_cliente = cl.id
        JOIN facturas f ON c.id_factura = f.id
        WHERE c.id = ?
    """, conn, params=(credito_id,))
    conn.close()

    if df_fresco.empty:
        st.error("No se encontró el crédito.")
        return

    saldo_actual = round(float(df_fresco.iloc[0]["saldo_pendiente"]), 2)
    cliente_nombre = str(df_fresco.iloc[0]["cliente"])
    numero_factura = str(df_fresco.iloc[0]["numero_factura"])

    st.markdown("---")
    st.markdown(f"### 💵 Abonar a la Factura **{numero_factura}**")

    col_info1, col_info2 = st.columns(2)
    col_info1.info(f"**Cliente:** {cliente_nombre}")
    col_info2.info(f"**Saldo pendiente:** ${saldo_actual:.2f}")

    with st.form("form_abono_cobrar"):
        col_monto, col_metodo = st.columns(2)
        with col_monto:
            monto = st.number_input(
                "Monto a abonar",
                min_value=0.01,
                max_value=float(saldo_actual),
                step=0.01,
                value=float(min(0.01, saldo_actual)),
                key="monto_cobrar_form"
            )
        with col_metodo:
            metodo = st.selectbox(
                "Método de pago:",
                ["Efectivo", "Tarjeta de débito", "Tarjeta de crédito", "Transferencia", "Otros"],
                key="metodo_cobrar_form"
            )

        submitted = st.form_submit_button("💵 Registrar Abono", type="primary", use_container_width=True)

        if submitted:
            monto = round(monto, 2)
            nuevo_saldo = round(saldo_actual - monto, 2)

            if monto > saldo_actual:
                st.error("El monto no puede ser mayor al saldo pendiente.")
            else:
                conn = db.conectar()
                cursor = conn.cursor()
                try:
                    cursor.execute("""
                    INSERT INTO pagos_creditos (id_credito, monto_abonado, metodo_pago)
                    VALUES (?, ?, ?)
                    """, (credito_id, monto, metodo))

                    if nuevo_saldo <= 0:
                        cursor.execute("""
                        UPDATE creditos SET monto_pagado = monto_total, saldo_pendiente = 0, estado = 'pagado'
                        WHERE id = ?
                        """, (credito_id,))
                        cursor.execute("""
                        UPDATE facturas SET estado = 'cancelada'
                        WHERE id = (SELECT id_factura FROM creditos WHERE id = ?)
                        """, (credito_id,))
                    else:
                        cursor.execute("""
                        UPDATE creditos SET monto_pagado = monto_pagado + ?, saldo_pendiente = saldo_pendiente - ?
                        WHERE id = ?
                        """, (monto, monto, credito_id))

                    conn.commit()
                    st.success(f"✅ Abono de ${monto:.2f} registrado a {cliente_nombre}. Nuevo saldo: ${max(nuevo_saldo, 0):.2f}")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
                finally:
                    conn.close()