import streamlit as st
import pandas as pd
import plotly.express as px
from config.conexion import obtener_conexion
from datetime import datetime

def dashboard():
    st.title("📊 Dashboard de Ventas")

    # ✅ Validación multi-tienda
    if not st.session_state.get("logueado") or "id_tienda" not in st.session_state:
        st.error("❌ No has iniciado sesión. Inicia sesión primero.")
        st.stop()

    id_tienda = st.session_state["id_tienda"]

    st.sidebar.title("📅 Filtro por Fecha")
    fecha_inicio = st.sidebar.date_input("Desde", value=datetime(2024, 1, 1).date())
    fecha_fin = st.sidebar.date_input("Hasta", value=datetime.today().date())

    if fecha_inicio > fecha_fin:
        st.warning("⚠️ La fecha 'Desde' no puede ser mayor que 'Hasta'.")
        return

    try:
        conn = obtener_conexion()
        if not conn:
            st.error("❌ No se pudo conectar a la base de datos.")
            st.stop()

        # ✅ Traer ventas (cabecera) solo de la tienda y rango de fechas
        df_ventas = pd.read_sql(
            """
            SELECT Id_venta, Fecha, Id_empleado, id_tienda
            FROM Venta
            WHERE id_tienda = %s AND Fecha BETWEEN %s AND %s
            """,
            conn,
            params=(id_tienda, fecha_inicio, fecha_fin),
        )

        if df_ventas.empty:
            st.warning("⚠️ No hay ventas en el rango de fechas seleccionado para esta tienda.")
            return

        # ✅ Traer detalle de ventas (líneas) solo de la tienda
        df_detalle = pd.read_sql(
            """
            SELECT Id_venta, Cod_barra, Cantidad_vendida, Precio_Venta, Tipo_de_cliente, id_tienda
            FROM ProductoxVenta
            WHERE id_tienda = %s
            """,
            conn,
            params=(id_tienda,),
        )

        # ✅ Productos solo de la tienda
        df_productos = pd.read_sql(
            """
            SELECT Cod_barra, Nombre, Tipo_producto, id_tienda
            FROM Producto
            WHERE id_tienda = %s
            """,
            conn,
            params=(id_tienda,),
        )

        # Unir: Ventas + Detalle + Producto
        ventas_completas = (
            df_ventas.merge(df_detalle, on=["Id_venta", "id_tienda"], how="inner")
                    .merge(df_productos, on=["Cod_barra", "id_tienda"], how="left")
        )

        # Métricas
        ventas_completas["Total_linea"] = ventas_completas["Cantidad_vendida"] * ventas_completas["Precio_Venta"]
        total_ventas = float(ventas_completas["Total_linea"].sum())
        st.metric("💵 Total vendido", f"${total_ventas:,.2f}")

        # Producto más vendido por cantidad
        top_prod = (
            ventas_completas.groupby("Nombre")["Cantidad_vendida"]
            .sum()
            .sort_values(ascending=False)
        )
        if not top_prod.empty:
            st.metric("📦 Producto más vendido", top_prod.index[0])

        # Ventas por producto (gráfico)
        st.subheader("📈 Ventas por Producto (Cantidad)")
        ventas_por_producto = (
            ventas_completas.groupby("Nombre")["Cantidad_vendida"]
            .sum()
            .reset_index()
            .sort_values(by="Cantidad_vendida", ascending=False)
        )

        fig = px.bar(
            ventas_por_producto,
            x="Nombre",
            y="Cantidad_vendida",
            labels={"Nombre": "Producto", "Cantidad_vendida": "Unidades vendidas"},
            title="Ventas por Producto"
        )
        st.plotly_chart(fig, use_container_width=True)

        # Tabla detalle
        st.subheader("📋 Detalle de Ventas")
        st.dataframe(
            ventas_completas[["Fecha", "Id_venta", "Cod_barra", "Nombre", "Cantidad_vendida", "Precio_Venta", "Tipo_de_cliente", "Total_linea"]],
            use_container_width=True
        )

    except Exception as e:
        st.error(f"❌ Error al cargar el dashboard: {e}")

    finally:
        try:
            conn.close()
        except:
            pass

    if st.button("⬅ Volver al menú principal"):
        st.session_state.module = None
        st.rerun()

    if st.button("⬅ Volver al menú principal"):
        st.session_state.module = None
        st.rerun()
