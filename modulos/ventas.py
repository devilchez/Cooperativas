import streamlit as st
from datetime import datetime
from config.conexion import obtener_conexion

def modulo_ventas():
    st.title("🧾 Registro de Ventas")

    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT Cod_barra, Nombre, Precio_venta FROM Producto")
    productos = cursor.fetchall()

    if not productos:
        st.warning("⚠️ No hay productos disponibles.")
        return

    # Inicializar session_state
    if "productos_vendidos" not in st.session_state:
        st.session_state["productos_vendidos"] = []
    if "editar_venta" not in st.session_state:
        st.session_state["editar_venta"] = None
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
        if st.session_state["editar_venta"] is not None:
            producto_edit = st.session_state["productos_vendidos"][st.session_state["editar_venta"]]
            st.session_state["cantidad_venta"] = int(producto_edit["cantidad"])

            producto["cod_barra"] = producto_edit["cod_barra"]
            producto["nombre"] = producto_edit["nombre"]
            producto["precio_unitario"] = producto_edit["precio_unitario"]
        else:
            st.session_state["cantidad_venta"] = 1

        producto["cantidad"] = st.number_input(
            "Cantidad vendida",
            min_value=1,
            max_value=10000,
            step=1,
            value=st.session_state["cantidad_venta"],
            key="cantidad_venta"
        )

        if st.button("💾 Agregar producto"):
            if st.session_state["editar_venta"] is not None:
                st.session_state["productos_vendidos"][st.session_state["editar_venta"]] = producto
                st.success("✅ Producto editado correctamente.")
                st.session_state["editar_venta"] = None
            else:
                st.session_state["productos_vendidos"].append(producto)
                st.success("✅ Producto agregado a la venta.")

            # Limpiar formulario
            st.session_state["codigo_barras_venta"] = ""
            st.session_state["cantidad_venta"] = 1
            st.rerun()

    if st.session_state["productos_vendidos"]:
        st.subheader("📦 Productos en la venta actual")

        total = 0
        for i, prod in enumerate(st.session_state["productos_vendidos"]):
            subtotal = prod["cantidad"] * prod["precio_unitario"]
            total += subtotal
            st.markdown(
                f"**{prod['nombre']}** — {prod['cantidad']} unidades — Precio: ${prod['precio_unitario']:.2f} — Subtotal: ${subtotal:.2f}"
            )
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button(f"✏️ Editar #{i+1}", key=f"editar_{i}"):
                    st.session_state["editar_venta"] = i
                    st.rerun()
            with col2:
                if st.button(f"❌ Eliminar #{i+1}", key=f"eliminar_{i}"):
                    st.session_state["productos_vendidos"].pop(i)
                    st.success("🗑️ Producto eliminado.")
                    st.rerun()

        st.markdown(f"### 💰 Total: ${total:.2f}")

    st.subheader("📥 Finalizar registro de venta")

    id_cliente = st.text_input("🧍 ID del Cliente")

    if st.button("✅ Registrar venta"):
        if not st.session_state["productos_vendidos"]:
            st.error("❌ No hay productos agregados.")
        elif not id_cliente:
            st.error("⚠️ Debes ingresar el ID del cliente.")
        else:
            try:
                fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                id_empleado = 1  # Igual que en compras

                cursor.execute(
                    "INSERT INTO Venta (Fecha, Id_empleado, Id_cliente) VALUES (%s, %s, %s)",
                    (fecha, id_empleado, id_cliente)
                )
                id_venta = cursor.lastrowid

                for prod in st.session_state["productos_vendidos"]:
                    cursor.execute(
                        "INSERT INTO ProductoxVenta (id_venta, cod_barra, cantidad_vendida, precio_unitario) VALUES (%s, %s, %s, %s)",
                        (id_venta, prod["cod_barra"], prod["cantidad"], prod["precio_unitario"])
                    )

                conn.commit()
                st.success(f"✅ Venta registrada correctamente con ID {id_venta}.")
                st.session_state["productos_vendidos"] = []
                st.rerun()

            except Exception as e:
                st.error(f"⚠️ Error al guardar en la base de datos: {e}")

    st.divider()
    if st.button("🔙 Volver al menú principal"):
        st.session_state["module"] = None
        st.rerun()


