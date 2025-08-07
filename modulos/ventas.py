import streamlit as st
import pandas as pd
from datetime import datetime
from modulos.config.conexion import obtener_conexion

def modulo_ventas():
    st.title("🛒 Registro de Ventas")

    # Verificación de sesión
    if "id_empleado" not in st.session_state or "usuario" not in st.session_state:
        st.error("❌ No has iniciado sesión como empleado o no se ha seleccionado cliente.")
        st.stop()

    # Mostrar datos del empleado
    st.text_input("ID del empleado", value=st.session_state["id_empleado"], disabled=True)
    st.text_input("Usuario", value=st.session_state["usuario"], disabled=True)

    # Fecha actual
    fecha_actual = datetime.now().date()
    st.date_input("Fecha de la venta", value=fecha_actual, disabled=True)

    # Ingreso de código de barras
    cod_barra = st.text_input("Código de barras del producto")
    
    producto = None
    subtotal = 0

    if cod_barra:
        con = obtener_conexion()
        cursor = con.cursor(dictionary=True)

        cursor.execute("SELECT * FROM producto WHERE Cod_barra = %s", (cod_barra,))
        producto = cursor.fetchone()

        cursor.close()
        con.close()

        if producto:
            st.success(f"✅ Producto encontrado: {producto['Nombre']}")

            st.markdown(f"""
                - 💵 **Precio Minorista**: ${producto['precio_minorista']:.2f}  
                - 🏪 **Precio Mayorista 1**: ${producto['precio_mayorista1']:.2f}  
                - 🏬 **Precio Mayorista 2**: ${producto['precio_mayorista2']:.2f}
            """)

            tipo_cliente = st.radio("Tipo de cliente", ["Detallista", "Mayorista 1", "Mayorista 2"])
            cantidad = st.number_input("Cantidad", min_value=1, value=1)

            if tipo_cliente == "Detallista":
                precio = producto["precio_minorista"]
            elif tipo_cliente == "Mayorista 1":
                precio = producto["precio_mayorista1"]
            else:
                precio = producto["precio_mayorista2"]

            subtotal = cantidad * precio
            st.text_input("Subtotal", value=f"${subtotal:.2f}", disabled=True)

            if st.button("Guardar venta"):
                try:
                    con = obtener_conexion()
                    cursor = con.cursor()

                    cursor.execute("""
                        INSERT INTO ventas (Cod_barra, Id_empleado, Fecha, cantidad, subtotal)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (
                        cod_barra,
                        st.session_state["id_empleado"],
                        fecha_actual.strftime('%Y-%m-%d'),
                        cantidad,
                        subtotal
                    ))

                    con.commit()
                    cursor.close()
                    con.close()

                    st.success("✅ Venta guardada correctamente.")
                except Exception as e:
                    st.error(f"❌ Error al guardar la venta: {e}")
        else:
            st.warning("⚠️ Producto no encontrado.")



