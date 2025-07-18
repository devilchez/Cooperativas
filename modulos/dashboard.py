import streamlit as st
import pandas as pd
import plotly.express as px
from config.conexion import obtener_conexion

def dashboard():
    st.title("📊 Dashboard de Ventas")

 
    fecha_inicio = st.date_input("📅 Fecha de inicio", pd.to_datetime("2023-01-01"))
    fecha_fin = st.date_input("📅 Fecha final", pd.to_datetime("2025-12-31"))

    if fecha_inicio > fecha_fin:
        st.warning("⚠️ La fecha de inicio no puede ser mayor que la fecha final.")
    else:
        try:
            conn = obtener_conexion()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT P.nombre, SUM(PxV.cantidad_vendida) AS total_vendido
                FROM ProductoxVenta PxV
                JOIN Producto P ON PxV.cod_barra = P.cod_barra
                JOIN Venta V ON PxV.id_venta = V.id_venta
                WHERE V.Fecha BETWEEN %s AND %s
                GROUP BY P.nombre
                ORDER BY total_vendido DESC
                LIMIT 1
            """, (fecha_inicio, fecha_fin))
            producto = cursor.fetchone()

            cursor.execute("""
                SELECT C.nombre, COUNT(V.id_venta) AS compras
                FROM Venta V
                JOIN Cliente C ON V.id_cliente = C.id_cliente
                WHERE V.Fecha BETWEEN %s AND %s
                GROUP BY C.nombre
                ORDER BY compras DESC
                LIMIT 1
            """, (fecha_inicio, fecha_fin))
            cliente = cursor.fetchone()

            cursor.execute("""
                SELECT DATE(V.Fecha) AS fecha, SUM(PxV.cantidad_vendida * PxV.precio_venta) AS total
                FROM Venta V
                JOIN ProductoxVenta PxV ON V.id_venta = PxV.id_venta
                WHERE V.Fecha BETWEEN %s AND %s
                GROUP BY fecha
                ORDER BY fecha
            """, (fecha_inicio, fecha_fin))
            datos_ventas = cursor.fetchall()
            df_ventas = pd.DataFrame(datos_ventas, columns=["Fecha", "Total"])

       
            col1, col2 = st.columns(2)
            with col1:
                if producto:
                    st.metric("📦 Producto más vendido", producto[0], f"{producto[1]} unidades")
                else:
                    st.info("No hay ventas en ese periodo.")
            with col2:
                if cliente:
                    st.metric("🧑 Cliente que más compra", cliente[0], f"{cliente[1]} compras")
                else:
                    st.info("No hay clientes en ese periodo.")

            
            st.markdown("---")
            st.subheader("📈 Ventas totales por día")
            if not df_ventas.empty:
                fig = px.bar(df_ventas, x="Fecha", y="Total", labels={"Total": "Monto ($)"})
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No hay datos de ventas para graficar en el rango seleccionado.")

        except Exception as e:
            st.error(f"❌ Error al cargar el dashboard: {e}")
        finally:
            cursor.close()
            conn.close()

    
    st.markdown("---")
    if st.button("⬅ Volver al menú principal"):
        st.session_state.module = None
        st.rerun()

