import streamlit as st
from datetime import datetime
from config.conexion import obtener_conexion

def modulo_ventas():
    st.title("🛒 Registro de Ventas")

    conn = obtener_conexion()
    cursor = conn.cursor()

    # Validar sesión activa
    usuario = st.session_state.get("usuario")
    if not usuario:
        st.error("❌ No has iniciado sesión. Inicia sesión primero.")
        return

    # Obtener id_empleado del usuario
    cursor.execute("SELECT Id_empleado FROM Empleado WHERE Usuario = %s", (usuario,))
    resultado_empleado = cursor.fetchone()
    if not resultado_empleado:
        st.error("❌ No se encontró el usuario en la tabla Empleado.")
        return
    Usuario = resultado_empleado[0]

    # Fecha de venta
    fecha_venta = datetime.now().strftime("%Y-%m-%d")
    st.text_input("🗓️ Fecha de la venta", value=fecha_venta, disabled=True)
    st.text_input("🧑‍💼 Usuario del empleado", value=Usuario, disabled=True)

    # Inicializar lista si no existe
    if "productos_vendidos" not in st.session_state:
        st.session_state["productos_vendidos"] = []

    # Ingreso del código de barras
    cod_barras_input = st.text_input("📦 Ingrese el código de barras del producto")

    if cod_barras_input:
        cursor.execute("SELECT Nombre FROM Producto WHERE Cod_barra = %s", (cod_barras_input,))
        producto = cursor.fetchone()

        if producto:
            nombre_producto = producto[0]
            st.success(f"✅ Producto encontrado: **{nombre_producto}**")

            # Obtener precio máximo de compra
            cursor.execute("SELECT MAX(precio_compra) FROM ProductoxCompra WHERE cod_barra = %s", (cod_barras_input,))
            max_precio_compra = cursor.fetchone()[0]

            if max_precio_compra:
                precio_sugerido = round(max_precio_compra / 0.8, 2)
                st.number_input("💰 Precio sugerido (calculado)", value=precio_sugerido, disabled=True)

                precio_venta = st.number_input(
                    "🧾 Precio de venta (editable)", value=precio_sugerido, min_value=0.01, step=0.01
                )

                cantidad = st.number_input("📦 Cantidad vendida", min_value=1, step=1)

                subtotal = round(precio_venta * cantidad, 2)
                st.number_input("💲 Subtotal de esta venta", value=subtotal, disabled=True)

                # Botón para agregar a la lista
                if st.button("🛒 Agregar producto a la venta"):
                    producto_venta = {
                        "cod_barra": cod_barras_input,
                        "nombre": nombre_producto,
                        "precio_venta": precio_venta,
                        "cantidad": cantidad,
                        "subtotal": subtotal
                    }
                    st.session_state["productos_vendidos"].append(producto_venta)
                    st.success("✅ Producto agregado a la venta.")
                    st.rerun()
            else:
                st.warning("⚠️ No hay historial de compras para este producto.")
        else:
            st.warning("❌ Producto no encontrado.")

    # Mostrar productos agregados a la venta
    if st.session_state["productos_vendidos"]:
        st.subheader("🧾 Productos en esta venta")

        total_venta = 0
        for i, prod in enumerate(st.session_state["productos_vendidos"]):
            st.markdown(
                f"**{prod['nombre']}** — {prod['cantidad']} unidad(es) — "
                f"Precio: ${prod['precio_venta']:.2f} — Subtotal: ${prod['subtotal']:.2f}"
            )
            total_venta += prod["subtotal"]

            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button(f"❌ Eliminar #{i+1}", key=f"eliminar_{i}"):
                    st.session_state["productos_vendidos"].pop(i)
                    st.success("🗑️ Producto eliminado de la venta.")
                    st.rerun()

        st.markdown(f"### 💵 Total de la venta: ${total_venta:.2f}")

        # Botón para registrar la venta
        st.markdown("### ✅ Confirmar y registrar venta")

        if st.button("💾 Registrar venta"):
            try:
                # Generar nuevo ID de venta
                cursor.execute("SELECT MAX(Id_venta) FROM Venta")
                ultimo_id = cursor.fetchone()[0]
                nuevo_id_venta = 1 if ultimo_id is None else ultimo_id + 1

                # Insertar cabecera de venta
                cursor.execute("""
                    INSERT INTO Venta (Id_venta, Fecha, Id_empleado, Id_cliente)
                    VALUES (%s, %s, %s, %s)
                """, (nuevo_id_venta, fecha_venta, id_empleado, None))  # Id_cliente: None por ahora

                # Insertar productos vendidos
                for prod in st.session_state["productos_vendidos"]:
                    cursor.execute("""
                        INSERT INTO ProductoxVenta (Id_venta, Cod_barra, Cantidad_vendida, Precio_unitario)
                        VALUES (%s, %s, %s, %s)
                    """, (
                        nuevo_id_venta,
                        prod["cod_barra"],
                        prod["cantidad"],
                        prod["precio_venta"]
                    ))

                conn.commit()

                st.success(f"✅ Venta registrada exitosamente con ID {nuevo_id_venta}.")
                st.session_state["productos_vendidos"] = []
                st.rerun()

            except Exception as e:
                st.error(f"❌ Error al registrar la venta: {e}")

    st.divider()
    if st.button("🔙 Volver al menú principal"):
        st.session_state["module"] = None
        st.session_state["productos_vendidos"] = []
        st.rerun()



