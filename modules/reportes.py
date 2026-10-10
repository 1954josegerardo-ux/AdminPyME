import streamlit as st
import pandas as pd
import database as db
import plotly.express as px
import plotly.graph_objects as go
import datetime

def mostrar():
    st.title("📈 Reportes")
    st.markdown("Análisis visual del desempeño del negocio")

    # Selector de período
    st.markdown("### 📅 Período de análisis")
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        periodo = st.selectbox(
            "Rango rápido:",
            ["Hoy", "Últimos 7 días", "Últimos 30 días", "Este mes", "Mes pasado", "Últimos 90 días", "Personalizado"],
            index=2,
            key="periodo_reporte"
        )

    hoy = datetime.date.today()

    if periodo == "Hoy":
        fecha_inicio = hoy
        fecha_fin = hoy
    elif periodo == "Últimos 7 días":
        fecha_inicio = hoy - datetime.timedelta(days=7)
        fecha_fin = hoy
    elif periodo == "Últimos 30 días":
        fecha_inicio = hoy - datetime.timedelta(days=30)
        fecha_fin = hoy
    elif periodo == "Este mes":
        fecha_inicio = hoy.replace(day=1)
        fecha_fin = hoy
    elif periodo == "Mes pasado":
        primer_dia_mes = hoy.replace(day=1)
        fecha_fin = primer_dia_mes - datetime.timedelta(days=1)
        fecha_inicio = fecha_fin.replace(day=1)
    elif periodo == "Últimos 90 días":
        fecha_inicio = hoy - datetime.timedelta(days=90)
        fecha_fin = hoy
    else:
        with col2:
            fecha_inicio = st.date_input("Desde:", hoy - datetime.timedelta(days=30), key="fecha_ini_rep")
        with col3:
            fecha_fin = st.date_input("Hasta:", hoy, key="fecha_fin_rep")

    st.caption(f"📊 Analizando del **{fecha_inicio.strftime('%d/%m/%Y')}** al **{fecha_fin.strftime('%d/%m/%Y')}**")

    st.markdown("---")

    # ==================== MÉTRICAS PRINCIPALES ====================
    st.markdown("### 💰 Resumen General")

    conn = db.conectar()
    df_ventas = pd.read_sql_query("""
        SELECT f.id, f.numero_factura, f.fecha, f.total, f.condicion_pago, c.nombre as cliente
        FROM facturas f
        LEFT JOIN clientes c ON f.id_cliente = c.id
        WHERE date(f.fecha) BETWEEN date(?) AND date(?)
        ORDER BY f.fecha DESC
    """, conn, params=(fecha_inicio.isoformat(), fecha_fin.isoformat()))

    df_compras = pd.read_sql_query("""
        SELECT id, numero_factura, fecha, total
        FROM compras
        WHERE date(fecha) BETWEEN date(?) AND date(?)
    """, conn, params=(fecha_inicio.isoformat(), fecha_fin.isoformat()))

    conn.close()

    total_ventas = df_ventas["total"].sum() if not df_ventas.empty else 0
    total_compras = df_compras["total"].sum() if not df_compras.empty else 0
    num_facturas = len(df_ventas)
    ticket_promedio = total_ventas / num_facturas if num_facturas > 0 else 0
    ganancia_bruta = total_ventas - total_compras

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💵 Ventas Totales", f"${total_ventas:,.2f}")
    col2.metric("🛒 Compras Totales", f"${total_compras:,.2f}")
    col3.metric("📊 Ganancia Bruta", f"${ganancia_bruta:,.2f}")
    col4.metric("🧾 Facturas", num_facturas)

    col5, col6, col7, col8 = st.columns(4)
    col5.metric("📈 Ticket Promedio", f"${ticket_promedio:,.2f}")

    # Ventas de contado vs crédito
    if not df_ventas.empty:
        ventas_contado = df_ventas[df_ventas["condicion_pago"] == "contado"]["total"].sum()
        ventas_credito = df_ventas[df_ventas["condicion_pago"] == "credito"]["total"].sum()
    else:
        ventas_contado = 0
        ventas_credito = 0

    col6.metric("💵 Contado", f"${ventas_contado:,.2f}")
    col7.metric("📝 Crédito", f"${ventas_credito:,.2f}")

    # ==================== REPORTE 1: VENTAS POR PERÍODO ====================
    st.markdown("---")
    st.markdown("### 📊 1. Ventas por Período")

    if df_ventas.empty:
        st.info("No hay ventas registradas en este período.")
    else:
        df_ventas["fecha"] = pd.to_datetime(df_ventas["fecha"])
        ventas_por_dia = df_ventas.groupby(df_ventas["fecha"].dt.date)["total"].sum().reset_index()
        ventas_por_dia.columns = ["Fecha", "Total"]

        fig = px.line(
            ventas_por_dia,
            x="Fecha",
            y="Total",
            title="Evolución de Ventas Diarias",
            markers=True,
            color_discrete_sequence=["#2ecc71"]
        )
        fig.update_layout(
            xaxis_title="Fecha",
            yaxis_title="Monto ($)",
            hovermode="x unified",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

    # ==================== REPORTE 2: PRODUCTOS MÁS VENDIDOS ====================
    st.markdown("---")
    st.markdown("### 🏆 2. Productos Más Vendidos")

    conn = db.conectar()
    df_top = pd.read_sql_query("""
        SELECT p.nombre, 
               SUM(fd.cantidad) as unidades_vendidas,
               SUM(fd.total_linea) as ingresos
        FROM factura_detalle fd
        JOIN productos p ON fd.id_producto = p.id
        JOIN facturas f ON fd.id_factura = f.id
        WHERE date(f.fecha) BETWEEN date(?) AND date(?)
        GROUP BY p.id, p.nombre
        ORDER BY unidades_vendidas DESC
        LIMIT 10
    """, conn, params=(fecha_inicio.isoformat(), fecha_fin.isoformat()))
    conn.close()

    if df_top.empty:
        st.info("No hay productos vendidos en este período.")
    else:
        col_graf, col_tabla = st.columns([2, 1])

        with col_graf:
            fig = px.bar(
                df_top,
                x="unidades_vendidas",
                y="nombre",
                orientation="h",
                title="Top 10 Productos por Unidades Vendidas",
                color="unidades_vendidas",
                color_continuous_scale="Blues",
                text="unidades_vendidas"
            )
            fig.update_layout(
                xaxis_title="Unidades",
                yaxis_title="",
                height=400,
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)

        with col_tabla:
            st.markdown("**Detalle**")
            df_top_show = df_top.copy()
            df_top_show["ingresos"] = df_top_show["ingresos"].apply(lambda x: f"${x:,.2f}")
            st.dataframe(df_top_show, use_container_width=True, hide_index=True)

    # ==================== REPORTE 3: CLIENTES TOP ====================
    st.markdown("---")
    st.markdown("### 👥 3. Mejores Clientes")

    conn = db.conectar()
    df_clientes_top = pd.read_sql_query("""
        SELECT c.nombre as cliente,
               COUNT(f.id) as num_compras,
               SUM(f.total) as total_comprado
        FROM facturas f
        JOIN clientes c ON f.id_cliente = c.id
        WHERE date(f.fecha) BETWEEN date(?) AND date(?)
        GROUP BY c.id, c.nombre
        ORDER BY total_comprado DESC
        LIMIT 10
    """, conn, params=(fecha_inicio.isoformat(), fecha_fin.isoformat()))
    conn.close()

    if df_clientes_top.empty:
        st.info("No hay clientes con compras en este período.")
    else:
        col_graf, col_tabla = st.columns([2, 1])

        with col_graf:
            fig = px.bar(
                df_clientes_top,
                x="total_comprado",
                y="cliente",
                orientation="h",
                title="Top 10 Clientes por Monto Comprado",
                color="total_comprado",
                color_continuous_scale="Greens",
                text="total_comprado"
            )
            fig.update_traces(texttemplate='$%{text:,.2f}', textposition='outside')
            fig.update_layout(
                xaxis_title="Total Comprado ($)",
                yaxis_title="",
                height=400,
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)

        with col_tabla:
            st.markdown("**Detalle**")
            df_clientes_show = df_clientes_top.copy()
            df_clientes_show["total_comprado"] = df_clientes_show["total_comprado"].apply(lambda x: f"${x:,.2f}")
            st.dataframe(df_clientes_show, use_container_width=True, hide_index=True)

    # ==================== REPORTE 4: ESTADO DE CUENTAS ====================
    st.markdown("---")
    st.markdown("### 💼 4. Estado de Cuentas")

    conn = db.conectar()
    df_cxc = pd.read_sql_query("""
        SELECT COUNT(*) as total, COALESCE(SUM(saldo_pendiente), 0) as saldo
        FROM creditos
        WHERE estado = 'pendiente' AND saldo_pendiente > 0
    """, conn)

    df_cxp = pd.read_sql_query("""
        SELECT COUNT(*) as total, COALESCE(SUM(saldo_pendiente), 0) as saldo
        FROM cuentas_por_pagar
        WHERE estado = 'pendiente' AND saldo_pendiente > 0
    """, conn)

    df_saldos = pd.read_sql_query("""
        SELECT COALESCE(SUM(total), 0) as total_facturado,
               COALESCE(SUM(CASE WHEN estado = 'pagada' THEN total ELSE 0 END), 0) as cobrado,
               COALESCE(SUM(CASE WHEN estado = 'credito' THEN total ELSE 0 END), 0) as por_cobrar
        FROM facturas
        WHERE date(fecha) BETWEEN date(?) AND date(?)
    """, conn, params=(fecha_inicio.isoformat(), fecha_fin.isoformat()))

    conn.close()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 💰 Cuentas por Cobrar")
        st.metric("Créditos Activos", int(df_cxc.iloc[0]["total"]))
        st.metric("Saldo Pendiente de Cobro", f"${df_cxc.iloc[0]['saldo']:,.2f}")

        # Gráfico de pastel
        if not df_saldos.empty:
            fig_pie = go.Figure(data=[go.Pie(
                labels=["Cobrado", "Por Cobrar"],
                values=[df_saldos.iloc[0]["cobrado"], df_saldos.iloc[0]["por_cobrar"]],
                hole=0.4,
                marker_colors=["#2ecc71", "#e74c3c"]
            )])
            fig_pie.update_layout(
                title="Estado de Facturación",
                height=300
            )
            st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        st.markdown("#### 📝 Cuentas por Pagar")
        st.metric("Deudas Activas", int(df_cxp.iloc[0]["total"]))
        st.metric("Saldo Pendiente de Pago", f"${df_cxp.iloc[0]['saldo']:,.2f}")

        # Balance
        balance = df_cxc.iloc[0]["saldo"] - df_cxp.iloc[0]["saldo"]
        st.markdown("#### ⚖️ Balance")
        if balance >= 0:
            st.success(f"Positivo: **${balance:,.2f}**")
        else:
            st.error(f"Negativo: **${balance:,.2f}**")

    # ==================== REPORTE 5: TENDENCIA COMPARATIVA ====================
    st.markdown("---")
    st.markdown("### 📉 5. Tendencia Comparativa: Ventas vs Compras")

    conn = db.conectar()
    df_ventas_dia = pd.read_sql_query("""
        SELECT date(fecha) as fecha, SUM(total) as total
        FROM facturas
        WHERE date(fecha) BETWEEN date(?) AND date(?)
        GROUP BY date(fecha)
    """, conn, params=(fecha_inicio.isoformat(), fecha_fin.isoformat()))

    df_compras_dia = pd.read_sql_query("""
        SELECT date(fecha) as fecha, SUM(total) as total
        FROM compras
        WHERE date(fecha) BETWEEN date(?) AND date(?)
        GROUP BY date(fecha)
    """, conn, params=(fecha_inicio.isoformat(), fecha_fin.isoformat()))
    conn.close()

    if not df_ventas_dia.empty or not df_compras_dia.empty:
        df_ventas_dia["tipo"] = "Ventas"
        df_compras_dia["tipo"] = "Compras"
        df_comp = pd.concat([df_ventas_dia, df_compras_dia])

        fig = px.line(
            df_comp,
            x="fecha",
            y="total",
            color="tipo",
            title="Ventas vs Compras en el Tiempo",
            markers=True,
            color_discrete_map={"Ventas": "#2ecc71", "Compras": "#e67e22"}
        )
        fig.update_layout(
            xaxis_title="Fecha",
            yaxis_title="Monto ($)",
            hovermode="x unified",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay datos suficientes para mostrar la tendencia.")