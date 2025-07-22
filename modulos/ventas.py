import streamlit as st
from datetime import datetime
from config.conexion import obtener_conexion

def modulo_ventas():
    st.title("🛒 Registro de Venta")

    conn = obtener_conexion()
    cursor = conn.cursor()

    Usuario = st.session_state.get("usuario")
    if not Usuario:
        st.error("❌ No has iniciado sesión.")
        return

    cursor.execute("SELECT cod_barra, nombre, precio_venta FROM Producto")
    productos = cursor.fetchall()

    if not productos:
        st.warning("⚠️ No hay productos disponibles.")
        return

    if "productos_vendidos" not in st.session_state:
        st.session_state["productos_vendidos"] = []
    if "editar_indice_venta" not in st.session_state:
        st.session_state["editar_indice_venta"] = None
    if "codigo_barras_venta" not in st.session_state:
        st.session_state["codigo_barras_venta"] = ""
    if "cantidad_venta" not in st.session_state:
        st.session_state["cantidad_venta"] = 1

    producto = {}

    codigo_barras = st.text_input("Código de barras del producto", key="codigo_barras_venta")

    if codigo_barras:
        producto_encontrado = None
        for prod in productos:
            if prod[0] == codigo_barras:
                producto_encontrado = prod
                break

        if producto_encontrado:
            producto["cod_barra"] = producto_encontrado[0]
            producto["nombre"] = producto_encontrado[1]
            producto["precio_unitario"] = producto_encontrado[2]
            st.write(f"Producto encontrado: **{producto['nombre']}**")
        else:
            st.warning("⚠️ Producto no encontrado. Verifique el código de barras.")

    if producto.get("cod_barra"):
        if st.session_state["editar_indice_venta"] is not None:
            prod_edit = st.session_state["productos_vendidos"][st.session_state["editar_indice_venta"]]
            st.session_state["cantidad_venta"] = prod_edit["cantidad"]

            producto["cod_barra"] = prod_edit["cod_barra"]
            producto["nombre"] = prod_edit["nombre"]
            producto["precio_unitario"] = prod_edit["precio_unitario"]
        else:
            st.session_state["cantidad_venta"] = 1

        producto["cantidad"] = st.number_input(
            "Cantidad",
            min_value=1,
            max_value=10000,
            step=1,
            value=st.session_state["cantidad_venta"],
            key="cantidad_venta"
        )

        st.markdown(f"💲 Precio unitario: **${producto['precio_unitario']:.2f}**")
        st.markdown(f"📦 Subtotal: **${producto['cantidad'] * producto['precio_unitario']:.2f}**")

        if st.button("💾 Agregar producto a la venta"):
            if st.session_state["editar_indice_venta"] is not None:
                st.session_state["productos_vendidos"][st.session_state["editar_indice_venta"]] = producto
                st.success("✅ Producto editado correctamente.")
                st.session_state["editar_indice_venta"] = None
            else:
                st.session_state["productos_vendidos"].append(producto)
                st.success("✅ Producto agregado a la venta.")

            st.session_state["codigo_barras_venta"] = ""
            st.session_state["cantidad_venta"] = 1
            st.rerun()

    if st.session_state["productos_vendidos"]:
        st.subheader("🧾 Productos agregados a la venta")

        total = 0
        for i, prod in enumerate(st.session_state["productos_vendidos"]):
            subtotal = prod["cantidad"] * prod["precio_unitario"]
            total += subtotal
            st.markdown(
                f"**{prod['nombre']}** — {prod['cantidad']} unidades — Precio unitario: ${prod['precio_unitario']:.2f} — Subtotal: ${subtotal:.2f}"
            )
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button(f"✏️ Editar #{i+1}", key=f"editar_{i}"):
                    st.session_state["editar_indice_venta"] = i
                    st.rerun()
            with col2:
                if st.button(f"❌ Eliminar #{i+1}", key=f"eliminar_{i}"):
                    st.session_state["productos_vendidos"].pop(i)
                    st.success("🗑️ Producto eliminado.")
                    st.rerun()

        st.markdown(f"### 💰 Total de la venta: **${total:.2f}**")

    st.subheader("📤 Finalizar venta")

    id_cliente = st.text_input("🧍 ID del Cliente")

    if st.button("✅ Registrar venta"):
        if not st.session_state["productos_vendidos"]:
            st.error("❌ No hay productos agregados.")
        elif not id_cliente:
            st.error("⚠️ Debes ingresar el ID del cliente.")
        else:
            try:
                fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                cursor.execute(
                    "INSERT INTO Venta (Fecha, Id_empleado, Id_cliente) VALUES (%s, %s, %s)",
                    (fecha_actual, id_empleado, id_cliente)
                )
                id_venta = cursor.lastrowid

                for prod in st.session_state["productos_vendidos"]:
                    cursor.execute("""
                        INSERT INTO ProductoxVenta (id_venta, cod_barra, cantidad_vendida, precio_unitario)
                        VALUES (%s, %s, %s, %s)
                    """, (id_venta, prod["cod_barra"], prod["cantidad"], prod["precio_unitario"]))

                conn.commit()
                st.success(f"🧾 Venta registrada exitosamente con ID {id_venta}.")
                st.session_state["productos_vendidos"] = []
                st.rerun()

            except Exception as e:
                st.error(f"⚠️ Error al registrar la venta: {e}")

    st.divider()
    if st.button("🔙 Volver al menú principal"):
        st.session_state["module"] = None
        st.rerun()


