import streamlit as st
from datetime import datetime
from config.conexion import obtener_conexion
import traceback  

def modulo_ventas():
    st.title("🛒 Registro de Ventas")

    conn = obtener_conexion()
    cursor = conn.cursor()

    usuario = st.session_state.get("usuario")
    if not usuario:
        st.error("❌ No has iniciado sesión. Inicia sesión primero.")
        return

    if st.session_state.get("limpiar_cod"):
        st.session_state.pop("cod_barras_input", None)
        st.session_state.pop("limpiar_cod", None)
        st.rerun()

    fecha_venta = datetime.now().strftime("%Y-%m-%d")
    st.text_input("🗓️ Fecha de la venta", value=fecha_venta, disabled=True)
    st.text_input("🧑‍💼 Usuario del empleado", value=usuario, disabled=True)

    cursor.execute("SELECT Id_empleado FROM Empleado WHERE Usuario = %s", (usuario,))
    empleado = cursor.fetchone()
    if not empleado:
        st.error("❌ No se encontró el usuario en la tabla Empleado.")
        return

    id_empleado = empleado[0]

    if "productos_vendidos" not in st.session_state:
        st.session_state["productos_vendidos"] = []

    cod_barras_input = st.text_input("📦 Ingrese el código de barras del producto", value=st.session_state.get("cod_barras_input", ""), key="cod_barras_input")

    if cod_barras_input:
        cursor.execute("SELECT Nombre FROM Producto WHERE Cod_barra = %s", (cod_barras_input,))
        producto = cursor.fetchone()

        if producto:
            nombre_producto = producto[0]
            st.success(f"✅ Producto encontrado: **{nombre_producto}**")

            # Recuperar los precios de la tabla ProductoxCompra
            cursor.execute("""
                SELECT Precio_minorista, Precio_mayorista1, Precio_mayorista2 
                FROM ProductoxCompra 
                WHERE cod_barra = %s
            """, (cod_barras_input,))
            precios = cursor.fetchone()

            if precios:
                precio_minorista, precio_mayorista1, precio_mayorista2 = precios

                tipo_cliente = st.radio("🧾 Seleccione el tipo de cliente", ["Detallista", "Mayorista 1", "Mayorista 2"], index=0)

                # Seleccionamos el precio según el tipo de cliente
                if tipo_cliente == "Detallista":
                    precio_venta = precio_minorista
                elif tipo_cliente == "Mayorista 1":
                    precio_venta = precio_mayorista1
                else:
                    precio_venta = precio_mayorista2

                cantidad = st.number_input("📦 Cantidad vendida", min_value=1, step=1)

                # Mostrar el precio de venta directamente
                st.write(f"💲 Precio de venta: ${precio_venta:.2f}")

                if st.button("🛒 Agregar producto a la venta"):
                    producto_venta = {
                        "cod_barra": cod_barras_input,
                        "nombre": nombre_producto,
                        "precio_venta": precio_venta,
                        "cantidad": cantidad,
                        "tipo_cliente": tipo_cliente  
                    }
                    st.session_state["productos_vendidos"].append(producto_venta)
                    st.session_state["limpiar_cod"] = True
                    st.rerun()
            else:
                st.warning("⚠️ No hay historial de compras para este producto.")
        else:
            st.warning("❌ Producto no encontrado.")

    if st.session_state["productos_vendidos"]:
        st.subheader("🧾 Productos en esta venta")

        total_venta = 0
        for i, prod in enumerate(st.session_state["productos_vendidos"]):
            st.write(f"**{prod['nombre']}** | Cantidad: {prod['cantidad']} unidad(es) | Precio: ${prod['precio_venta']:.2f} | Tipo de cliente: **{prod['tipo_cliente']}**")
            total_venta += prod["precio_venta"] * prod["cantidad"]  # Calculamos el total de la venta (sin calcular subtotal por producto)

            if st.button(f"❌ Eliminar #{i+1}", key=f"eliminar_{i}"):
                st.session_state["productos_vendidos"].pop(i)
                st.success("🗑️ Producto eliminado de la venta.")
                st.rerun()

        st.markdown(f"### 💵 Total de la venta: ${total_venta:.2f}")

        if st.button("💾 Registrar venta"):
            try:
                cursor.execute("SELECT MAX(Id_venta) FROM Venta")
                ultimo_id = cursor.fetchone()[0]
                nuevo_id_venta = 1 if ultimo_id is None else ultimo_id + 1

                # Insertar en Venta
                cursor.execute("""
                    INSERT INTO Venta (Id_venta, Fecha, Id_empleado, Id_cliente)
                    VALUES (%s, %s, %s, %s)
                """, (nuevo_id_venta, fecha_venta, id_empleado, None))

                for prod in st.session_state["productos_vendidos"]:
                    cursor.execute("""
                        INSERT INTO ProductoxVenta (Id_venta, Cod_barra, Cantidad_vendida, Precio_Venta, Tipo_de_cliente)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (
                        nuevo_id_venta,
                        prod["cod_barra"],
                        prod["cantidad"],
                        prod["precio_venta"],
                        prod["tipo_cliente"]  
                    ))

                conn.commit()

                st.success("✅ Venta registrada correctamente.")
                st.session_state["productos_vendidos"] = []

            except Exception as e:
                conn.rollback()
                st.error("❌ Error al registrar la venta.")

    st.divider()
    if st.button("🔙 Volver al menú principal"):
        st.session_state["module"] = None
        st.session_state.pop("productos_vendidos", None)
        st.rerun()
