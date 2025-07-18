# modulos/dashboard.py

import streamlit as st
import pandas as pd
import plotly.express as px
from config.conexion import obtener_conexion
from datetime import datetime

def dashboard():
    st.title("📊 Dashboard de Ventas")

    id_empleado = st.session_state.get("id_empleado")  
    if not id_empleado:
        st.error("❌ No has iniciado sesión. Inicia sesión primero.")
        return

    st.sidebar.title("📅 Filtro por Fecha")
    fecha_inicio = st.sidebar.date_input("Desde", value=datetime(2024, 1, 1))
    fecha_fin = st.sidebar.date_input("Hasta", value=datetime.today())

    fecha_inicio = fecha_inicio.strftime('%Y-%m-%d')
    fecha_fin = fecha_fin.strftime('%Y-%m-%d')

    try:
        conn = obtener_conexion()

        query_ventas = f"""
            SELECT * FROM Venta
            WHERE Fecha BETWEEN '{fecha_inicio}' AND '{fecha_fin}'
        """
        df_ventas = pd.read_sql(query_ventas, conn)

        if df_ventas.empty:
            st.warning("⚠️ No hay ventas en el rango de fechas seleccionado.")
            return

        df_productos = pd.read_sql("SELECT * FROM Producto", conn)
        df_clientes = pd.read_sql("SELECT * FROM Cliente", conn)

        ventas_productos = df_ventas.merge(df_productos, on="Cod_barra", how="left")
        ventas_completas = ventas_productos.merge(df_clientes, on="Id_cliente", how="left")

        producto_mas_vendido = ventas_completas["Nombre_x"].value_counts().idxmax()
        st.metric("📦 Producto más vendido", producto_mas_vendido)

        cliente_top = ventas_completas["Nombre_y"].value_counts().idxmax()
        st.metric("👤 Cliente que más compra", cliente_top)

        st.subheader("📈 Ventas por Producto")
        ventas_por_producto = (
            ventas_completas.groupby("Nombre_x")
            .size()
            .reset_index(name="Cantidad")
            .sort_values(by="Cantidad", ascending=False)
        )
        fig = px.bar(
            ventas_por_producto,
            x="Nombre_x",
            y="Cantidad",
            labels={"Nombre_x": "Producto", "Cantidad": "Ventas"},
            title="Ventas por Producto"
        )
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("📋 Detalle de Ventas")
        st.dataframe(ventas_completas)

    except Exception as e:
        st.error(f"❌ Error al cargar el dashboard: {e}")

    finally:
        conn.close()

    if st.button("⬅ Volver al menú principal"):
        st.session_state.module = None
        st.rerun()
