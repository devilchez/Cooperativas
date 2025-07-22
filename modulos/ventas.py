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

    # Obtener ID del empleado desde el nombre de usuario
    cursor.execute("SELECT ID_empleado, Usuario FROM Empleado WHERE Usuario = %s", (usuario,))
    resultado_empleado = cursor.fetchone()
    if not resultado_empleado:
        st.error("❌ No se encontró el usuario en la tabla Empleado.")
        return
    id_empleado, usuario_mostrar = resultado_empleado

    # Mostrar mensaje después de guardar venta
    if st.session_state.get("venta_guardada"):
        st.success("✅ Venta registrada correctamente.")
        st.session_state.pop("venta_guardada", None)
        st.session_state.pop("productos_vendidos", None)
        st.rerun()

    # Fecha y usuario
    fecha_venta = datetime.now().strftime("%Y-%m-%d")
    st.text_input("🗓️ Fecha de la venta", value=fecha_venta, disabled=True)
    st.text_input("🧑‍💼 Usuario del empleado", value=usuario_mostrar, disabled=True)

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

            cursor.execute("SELECT MAX(precio_compra) FROM ProductoxCompra WHERE cod_barra = %s", (cod_barras_input,))
            max_precio_compra = cursor.fetchone()[0]

            if max_precio_compra:
                precio_sugerido = round(float(max_precio_compra) / 0.8, 2)
                st.number_input("💰 Precio sugerido", value=precio_sugerido, disabled=True)

                precio_venta = st.number_input("🧾 Precio de venta", value=precio_sugerido, min_value=0.01, step=0.01)
                cantidad = st.number_input("📦 Cantidad vendida", min_value=1, step=1)
                subtotal = round(precio_venta * cantidad, 2)
                st.number_input("💲 Subtotal", value=subtotal, disabled=True)

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

    # Mostrar productos agregados
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
                    st.success("🗑️ Producto eliminado.")
                    st.rerun()

        st.markdown(f"### 💵 Total: ${total_venta:.2f}")

        if st.button("💾 Registrar venta"):
            try:
                cursor.execute("SELECT MAX(Id_venta) FROM Venta")
                ultimo_id = cursor.fetchone()[0]
                nuevo_id = 1 if ultimo_id is None else ultimo_id + 1

                cursor.execute("""
                    INSERT INTO Venta (Id_venta, Fecha, Id_empleado, Id_cliente)
                    VALUES (%s, %s, %s, %s)
                """, (nuevo_id, fecha_venta, id_empleado, None))

                for prod in st.session_state["productos_vendidos"]:
                    cursor.execute("""
                        INSERT INTO ProductoxVenta (Id_venta, Cod_barra, Cantidad_vendida, Precio_unitario)
                        VALUES (%s, %s, %s, %s)
                    """, (
                        nuevo_id,
                        prod["cod_barra"],
                        prod["cantidad"],
                        prod["precio_venta"]
                    ))

                conn.commit()
                st.session_state["venta_guardada"] = True
                st.rerun()

            except Exception as e:
                st.error(f"❌ Error al registrar la venta: {e}")

    st.divider()
    if st.button("🔙 Volver al menú principal"):
        st.session_state["module"] = None
        st.session_state.pop("productos_vendidos", None)
        st.rerun()

