import streamlit as st
import pandas as pd
from config.conexion import obtener_conexion
from datetime import datetime, timedelta

def resaltar_stock_bajo(fila):
    color = 'background-color: #ffcccc' if fila["Stock actual"] < 10 else ''
    return ['' if col != "Stock actual" else color for col in fila.index]

def modulo_inventario():
    st.title("📦 Inventario Actual (agrupado por nombre)")

    opcion_orden = st.selectbox(
        "📑 Ordenar inventario por:",
        ("Nombre (A-Z)", "Nombre (Z-A)",
         "Stock (Ascendente)", "Stock (Descendente)",
         "Más vendidos", "Menos vendidos"),
        index=0
    )

    conn = None
    cursor = None
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()

        #Obtener todos los productos
        cursor.execute("""
            SELECT cod_barra, nombre, IFNULL(tipo_producto,'N/A')
            FROM Producto
        """)
        productos = cursor.fetchall()

        inventario_detalle = []

        for cod_barra, nombre, tipo_producto in productos:
            #Compras
            cursor.execute("""
                SELECT IFNULL(SUM(cantidad_comprada),0),
                       IFNULL(AVG(precio_compra),0)
                FROM ProductoxCompra
                WHERE cod_barra = %s
            """, (cod_barra,))
            total_comprado, precio_promedio = cursor.fetchone()

            #Unidad
            cursor.execute("""
                SELECT unidad
                FROM ProductoxCompra
                WHERE cod_barra = %s
                ORDER BY Id_compra DESC
                LIMIT 1
            """, (cod_barra,))
            fila = cursor.fetchone()
            unidad = fila[0] if fila else "N/A"

            #Ventas
            cursor.execute("""
                SELECT IFNULL(SUM(cantidad_vendida),0)
                FROM ProductoxVenta
                WHERE cod_barra = %s
            """, (cod_barra,))
            total_vendido = cursor.fetchone()[0] or 0

            #Precio venta
            cursor.execute("""
                SELECT Precio_Venta
                FROM ProductoxVenta
                WHERE cod_barra = %s
                ORDER BY Id_venta DESC
                LIMIT 1
            """, (cod_barra,))
            fila_pv = cursor.fetchone()
            precio_venta = float(fila_pv[0]) if fila_pv and fila_pv[0] is not None else 0.0

            inventario_detalle.append({
                "Nombre": nombre,
                "Tipo": tipo_producto,
                "Stock actual": (total_comprado or 0) - (total_vendido or 0),
                "Unidad": unidad,
                "Precio venta ($)": precio_venta,
                "Precio promedio compra ($)": float(precio_promedio or 0),
                "_Total_vendidos": int(total_vendido or 0)
            })

        # Agrupar por nombre 
        df = pd.DataFrame(inventario_detalle)
        df_agrupado = df.groupby(df["Nombre"].str.lower(), as_index=False).agg({
            "Nombre": "first",  
            "Tipo": "first",
            "Stock actual": "sum",
            "Unidad": "first",
            "Precio venta ($)": "mean",
            "Precio promedio compra ($)": "mean",
            "_Total_vendidos": "sum"
        })

        # Ordenacion
        if opcion_orden == "Nombre (A-Z)":
            df_agrupado = df_agrupado.sort_values("Nombre", key=lambda x: x.str.lower(), ascending=True)
        elif opcion_orden == "Nombre (Z-A)":
            df_agrupado = df_agrupado.sort_values("Nombre", key=lambda x: x.str.lower(), ascending=False)
        elif opcion_orden == "Stock (Ascendente)":
            df_agrupado = df_agrupado.sort_values("Stock actual", ascending=True)
        elif opcion_orden == "Stock (Descendente)":
            df_agrupado = df_agrupado.sort_values("Stock actual", ascending=False)
        elif opcion_orden == "Más vendidos":
            df_agrupado = df_agrupado.sort_values("_Total_vendidos", ascending=False)
        else:
            df_agrupado = df_agrupado.sort_values("_Total_vendidos", ascending=True)

        # Esto es solo para quitar una columna interna
        df_agrupado = df_agrupado.drop(columns=["_Total_vendidos"])

        styled_df = df_agrupado.style.apply(resaltar_stock_bajo, axis=1).format({
            "Precio venta ($)": "{:.2f}",
            "Precio promedio compra ($)": "{:.2f}"
        })

        st.subheader("📋 Inventario agrupado por nombre")
        st.dataframe(styled_df, use_container_width=True)

        # Productos prioximos a vencer 
        hoy = datetime.now().date()
        prox_mes = (datetime.now() + timedelta(days=30)).date()
        cursor.execute("""
            SELECT pc.Cod_barra, p.nombre, pc.unidad, pc.fecha_vencimiento
            FROM ProductoxCompra pc
            JOIN Producto p ON pc.cod_barra = p.cod_barra
            WHERE pc.fecha_vencimiento BETWEEN %s AND %s
            ORDER BY pc.fecha_vencimiento ASC
        """, (hoy, prox_mes))
        proximos = cursor.fetchall()

        if proximos:
            df_v = pd.DataFrame(proximos, columns=["Código de barras", "Nombre", "Unidad", "Fecha vencimiento"])
            df_v["Fecha vencimiento"] = pd.to_datetime(df_v["Fecha vencimiento"]).dt.date
            st.subheader("⏳ Productos próximos a vencer (30 días)")
            st.dataframe(df_v, use_container_width=True)
        else:
            st.info("✅ No hay productos próximos a vencer.")

    except Exception as e:
        st.error(f"❌ Error al cargar inventario: {e}")
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

    st.markdown("---")
    if st.button("⬅ Volver al menú principal"):
        st.session_state.module = None
        st.rerun()
