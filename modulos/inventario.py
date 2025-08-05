import streamlit as st  
import pandas as pd
from config.conexion import obtener_conexion
from datetime import datetime, timedelta

def resaltar_stock_bajo(fila):
    color = 'background-color: #ffcccc' if fila["Stock actual"] < 10 else ''
    return ['' if col != "Stock actual" else color for col in fila.index]

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
                ORDER BY Id_compra

