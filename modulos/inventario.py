import streamlit as st
import pandas as pd
from config.conexion import obtener_conexion
from datetime import datetime, timedelta


def modulo_inventario():
    st.title("📦 Inventario Actual")

    # Selector de orden
    opcion_orden = st.selectbox(
        "📑 Ordenar inventario por:",
        (
            "Nombre (A-Z)",
            "Nombre (Z-A)",
            "Stock (Ascendente)",
            "Stock (Descendente)",
            "Más vendidos",
            "Menos vendidos"
        ),
        index=0
    )

    conn = None
    cursor = None
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT cod_barra, nombre, IFNULL(precio_venta, 0)
            FROM Producto
            """
        )
        productos = cursor.fetchall()

        inventario = []
        for cod_barra, nombre, precio_venta in productos:

            cursor.execute(
                """
                SELECT IFNULL(SUM(cantidad_comprada), 0),
                       IFNULL(AVG(precio_compra), 0)
                FROM ProductoxCompra
                WHERE cod_barra = %s
                """,
                (cod_barra,)
            )
            total_comprado, precio_promedio = cursor.fetchone()

            cursor.execute(
                """
                SELECT unidad
                FROM ProductoxCompra
                WHERE cod_barra = %s
                ORDER BY Id_compra DESC
                LIMIT 1
                """,
                (cod_barra,)
            )
            fila = cursor.fetchone()
            unidad = fila[0] if fila else "N/A"

            # Este total vendido es solamente informativo, luego se elimina antes de mostrar el frame
            cursor.execute(
                """
                SELECT IFNULL(SUM(cantidad_vendida), 0)
                FROM ProductoxVenta
                WHERE cod_barra = %s
                """,
                (cod_barra,)
            )
            total_vendido = cursor.fetchone()[0]

            stock = total_comprado - total_vendido

            inventario.append({
                "Código de barras": cod_barra,
                "Nombre": nombre,
                "Stock actual": stock,
                "Unidad": unidad,
                "Precio venta ($)": precio_venta,
                "Precio promedio compra ($)": precio_promedio,
                "_Total_vendidos": total_vendido
            })

        # 2) DataFrame y modo de visualizacion
        df = pd.DataFrame(inventario).fillna(0)
        if opcion_orden == "Nombre (A-Z)":
            df = df.sort_values("Nombre", ascending=True)
        elif opcion_orden == "Nombre (Z-A)":
            df = df.sort_values("Nombre", ascending=False)
        elif opcion_orden == "Stock (Ascendente)":
            df = df.sort_values("Stock actual", ascending=True)
        elif opcion_orden == "Stock (Descendente)":
            df = df.sort_values("Stock actual", ascending=False)
        elif opcion_orden == "Más vendidos":
            df = df.sort_values("_Total_vendidos", ascending=False)
        else:
            df = df.sort_values("_Total_vendidos", ascending=True)
        df = df.drop(columns=["_Total_vendidos"])

        # 3) Redondeo sin formula round() ya que me estaba dando problemas
        styled_df = df.style.format({
            "Precio venta ($)": "{:.2f}",
            "Precio promedio compra ($)": "{:.2f}"
        })

        # Se muestra el inventario
        st.subheader("📋 Tabla de inventario")
        st.dataframe(styled_df, use_container_width=True)

        '''
        # --- Productos próximos a vencer ---
        hoy = datetime.now().date()
        prox_mes = (datetime.now() + timedelta(days=30)).date()
        cursor.execute(
            """
            SELECT pc.cod_barra, p.nombre, pc.unidad, pc.fecha_de_vencimiento
            FROM ProductoxCompra pc
            JOIN Producto p ON pc.cod_barra = p.cod_barra
            WHERE pc.fecha_de_vencimiento BETWEEN %s AND %s
            ORDER BY pc.fecha_de_vencimiento ASC
            """,
            (hoy, prox_mes)
        )
        proximos = cursor.fetchall()

        if proximos:
            df_v = pd.DataFrame(
                proximos,
                columns=["Código de barras", "Nombre", "Unidad", "Fecha vencimiento"]
            )
            df_v["Fecha vencimiento"] = pd.to_datetime(df_v["Fecha vencimiento"]).dt.date
            st.subheader("⏳ Productos próximos a vencer (próximos 30 días)")
            st.dataframe(df_v, use_container_width=True)
        else:
            st.info("✅ No hay productos próximos a vencer en el próximo mes.")
        '''

    except Exception as e:
        st.error(f"❌ Error al cargar el inventario: {e}")
        
    finally:
        cursor.close()
        conn.close()

    st.markdown("---")
    if st.button("⬅ Volver al menú principal"):
        st.session_state.module = None
        st.rerun()
