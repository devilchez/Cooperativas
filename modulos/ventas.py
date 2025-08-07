import streamlit as st
import pandas as pd
from datetime import datetime
from modulos.config.conexion import obtener_conexion

def modulo_ventas():
    st.title("🛒 Registro de Ventas")

    # Validación de sesión
    if "id_empleado" not in st.session_state or "usuario" not in st.session_state:
        st.error("❌ No has iniciado sesión como empleado o no se ha seleccionado cliente.")
        st.stop()

    # Mostrar información del empleado y fecha
    st.text_input("🧑‍💼 ID del empleado", value=st.session_state["id_empleado"], disabled=True)
    st.text_input("👤 Usuario", value=st.session_state["usuario"], disabled=True)
    fecha_venta = st.date_input("📅 Fecha de la venta", value=datetime.now().date())

    # Entrada de código de barras
    codigo_barras = st.text_input("📦 Ingrese el código de barras del producto")

    producto_encontrado = None
    subtotal = 0

    if codigo_barras:
        con = obtener_conexion()
        cursor = con.cursor(dictionary=True)
        cursor.execute("SELECT * FROM producto WHERE Cod_barra = %s", (codigo_barras,))
        producto_encontrado = cursor.fetchone()
        cursor.close()
        con.close()

        if producto_encontrado:
            st.success(f"✅ Producto encontrado: **{producto_encontrado['Nombre']}**")

            # Mostrar precios
            st.markdown(f"""
            - 💵 **Precio Minorista**: ${producto_encontrado['precio_minorista']:.2f}  
            - 🏪 **Precio Mayorista 1**: ${producto_encontrado['precio_mayorista1']:.2f}  
            - 🏬 **Precio Mayorista 2**: ${producto_encontrado['precio_mayorista2']:.2f}
            """)

            # Tipo de cliente
            tipo_cliente = st.radio("🧾 Seleccione el tipo de cliente", ["Detallista", "Mayorista 1", "Mayorista 2"])

            # Cantidad
            cantidad = st.number_input("📦 Cantidad vendida", min_value=1, value=1)

            # Determinar precio según tipo de cliente
            if tipo_cliente == "Detallista":
                precio = producto_encontrado['precio_minorista']
            elif tipo_cliente == "Mayorista 1":
                precio = producto_encontrado['precio_mayorista1']
            else:
                precio = producto_encontrado['precio_mayorista2']

            # Calcular subtotal
            subtotal = cantidad * precio
            st.text_input("💰 Subtotal", value=f"${subtotal:.2f}", disabled=True)

            # Botón para guardar venta
            if st.button("💾 Guardar venta"):
                try:
                    con = obtener_conexion()
                    cursor = con.cursor()

                    cursor.execute("""
                        INSERT INTO ventas (Cod_barra, Id_empleado, Fecha, cantidad, subtotal)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (
                        codigo_barras,
                        st.session_state["id_empleado"],
                        fecha_venta.strftime("%Y-%m-%d"),
                        cantidad,
                        subtotal
                    ))

                    con.commit()
                    cursor.close()
                    con.close()

                    st.success("✅ Venta guardada exitosamente.")
                except Exception as e:
                    st.error(f"❌ Error al guardar la venta: {e}")
        else:
            st.error("❌ Producto no encontrado.")



