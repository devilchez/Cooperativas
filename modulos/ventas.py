import streamlit as st
from datetime import datetime
from config.conexion import obtener_conexion

def modulo_ventas():
    st.title("🧾 Registro de Venta")

    id_empleado = st.session_state.get("id_empleado")
    id_cliente = st.session_state.get("id_cliente")

    if not id_empleado or not id_cliente:
        st.error("❌ No has iniciado sesión como empleado o no se ha seleccionado cliente.")
        return

    if "productos_vendidos" not in st.session_state:
        st.session_state["productos_vendidos"] = []
    if "editar_indice_venta" not in st.session_state:
        st.session_state["editar_indice_venta"] = None

    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT cod_barra, nombre, precio_venta FROM Producto")
    productos_db = cursor.fetchall()
    productos_dict = {nombre: {"cod": cod, "precio_venta": float(precio)} for cod, nombre, precio in productos_db}
    nombres_productos = list(productos_dict.keys())
    conn.close()

    st.subheader("Registrar producto en la venta")

    tipo_producto = st.radio("Tipo de producto:", ["Existente", "Nuevo"], horizontal=True)

    producto = {}

    if st.session_state["editar_indice_venta"] is not None:
        producto_edit = st.session_state["productos_vendidos"][st.session_state["editar_indice_venta"]]
        default_nombre = producto_edit["nombre"]
        default_cod = producto_edit["cod_barra"]
        default_cant = producto_edit["cantidad"]
        default_precio = producto_edit["precio_unitario"]
    else:
        default_nombre = ""
        default_cod = ""
        default_cant = 1
        default_precio = 0.0

    if tipo_producto == "Existente":
        nombre_sel = st.selectbox("Buscar producto existente", nombres_productos,
                                  index=nombres_productos.index(default_nombre) if default_nombre in nombres_productos else 0)
        cod_barra = productos_dict[nombre_sel]["cod"]
        precio_unitario = productos_dict[nombre_sel]["precio_venta"]
        producto["cod_barra"] = cod_barra
        producto["nombre"] = nombre_sel
    else:
        producto["cod_barra"] = st.text_input("Código de barras", value=default_cod)
        producto["nombre"] = st.text_input("Nombre del producto", value=default_nombre)
        precio_unitario = default_precio

    producto["cantidad"] = st.number_input("Cantidad vendida", min_value=1, step=1, value=default_cant)
    producto["precio_unitario"] = st.number_input("Precio unitario", min_value=0.01, step=0.01, value=precio_unitario)

    if producto["precio_unitario"] < 0.01:
        st.error("❌ El precio unitario debe ser mayor a 0.")

    if st.button("➕ Agregar producto"):
        campos = ["cod_barra", "nombre", "cantidad", "precio_unitario"]
        if all(producto.get(c) for c in campos):
            if st.session_state["editar_indice_venta"] is not None:
                st.session_state["productos_vendidos"][st.session_state["editar_indice_venta"]] = producto
                st.success(f"Producto '{producto['nombre']}' actualizado.")
                st.session_state["editar_indice_venta"] = None
            else:
                st.session_state["productos_vendidos"].append(producto)
                st.success(f"Producto '{producto['nombre']}' agregado a la venta.")
            st.rerun()
        else:
            st.error("❌ Por favor, completa todos los campos antes de agregar el producto.")

    if st.session_state["productos_vendidos"]:
        st.subheader("🧾 Productos seleccionados para la venta:")

        for idx, p in enumerate(st.session_state["productos_vendidos"]):
            col1, col2 = st.columns([8, 2])
            with col1:
                st.markdown(
                    f"{idx + 1}. {p['nombre']} (Código: {p['cod_barra']}) - "
                    f"Cantidad: {p['cantidad']} - Precio Unitario: ${p['precio_unitario']:.2f}"
                )
            with col2:
                if st.button("✏️ Editar", key=f"editar_venta_{idx}"):
                    st.session_state["editar_indice_venta"] = idx
                    st.rerun()
                if st.button("🗑️ Eliminar", key=f"eliminar_venta_{idx}"):
                    st.session_state["productos_vendidos"].pop(idx)
                    st.rerun()

    if st.button("✅ Registrar venta"):
        if st.session_state["productos_vendidos"]:
            try:
                conn = obtener_conexion()
                cursor = conn.cursor()

                fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute(
                    "INSERT INTO Ventas (Fecha, Id_empleado, Id_cliente) VALUES (%s, %s, %s)",
                    (fecha_actual, id_empleado, id_cliente)
                )
                id_venta = cursor.lastrowid

                for producto in st.session_state["productos_vendidos"]:
                    cursor.execute("""
                        INSERT INTO ProductoxVenta (id_venta, cod_barra, cantidad_vendida, precio_unitario)
                        VALUES (%s, %s, %s, %s)
                    """, (
                        id_venta,
                        producto["cod_barra"],
                        producto["cantidad"],
                        producto["precio_unitario"]
                    ))

                conn.commit()
                st.success(f"✅ Venta registrada correctamente con ID {id_venta}.")
                st.session_state["productos_vendidos"] = []

            except Exception as e:
                st.error(f"❌ Error al registrar la venta: {e}")
            finally:
                cursor.close()
                conn.close()
        else:
            st.error("⚠️ No has añadido productos. Por favor, agrega productos antes de registrar la venta.")

    if st.button("⬅ Volver al menú principal"):
        st.session_state.module = None
        st.rerun()

